/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only live pipe client. Typed file-only facade; no native shell or target
 * workspace. */
#include "fd-session.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>
struct context {
  size_t calls;
  unsigned read_waits, write_waits, closes;
};
static int64_t input(void *raw, unsigned char *out, size_t size) {
  struct context *c = raw;
  if (++c->calls % 3U == 0U)
    return -11;
  return (int64_t)fread(out, 1, size < 7U ? size : 7U, stdin);
}
static int64_t output(void *raw, const unsigned char *in, size_t size) {
  struct context *c = raw;
  if (++c->calls % 3U == 0U)
    return -11;
  return (int64_t)fwrite(in, 1, size < 7U ? size : 7U, stdout);
}
static int ready(void *raw, int writing) {
  struct context *c = raw;
  if (writing)
    ++c->write_waits;
  else
    ++c->read_waits;
  return 0;
}
static struct aefd_close_result close_io(void *raw) {
  struct context *c = raw;
  ++c->closes;
  int in = fclose(stdin);
  int out = fclose(stdout);
  return (struct aefd_close_result){in == 0 ? 0 : -5, out == 0 ? 0 : -5};
}
struct streams {
  int ends[2];
  unsigned creates, reads, writes, closes, physical_closes;
  int unknown, effect, deny;
};
static struct aefd_pipe_result make_pipe(void *raw) {
  struct streams *s = raw;
  ++s->creates;
  if (pipe(s->ends) != 0)
    return (struct aefd_pipe_result){1, -5, 0, 0};
  return (struct aefd_pipe_result){1, 0, 3, 4};
}
static struct aefd_stream_result stream_read(void *raw, unsigned kind,
                                             unsigned selector,
                                             unsigned char *out, size_t count) {
  struct streams *s = raw;
  ++s->reads;
  if (kind != AEFD_BIND_PIPE || selector != 3 || s->ends[0] < 0)
    return (struct aefd_stream_result){1, -9};
  ssize_t got = read(s->ends[0], out, count);
  return (struct aefd_stream_result){1, got < 0 ? -5 : (int64_t)got};
}
static struct aefd_stream_result stream_write(void *raw, unsigned kind,
                                              unsigned selector,
                                              const unsigned char *in,
                                              size_t count) {
  struct streams *s = raw;
  ++s->writes;
  if (kind != AEFD_BIND_PIPE || selector != 4 || s->ends[1] < 0)
    return (struct aefd_stream_result){1, -9};
  ssize_t sent = write(s->ends[1], in, count);
  return (struct aefd_stream_result){1, sent < 0 ? -5 : (int64_t)sent};
}
static struct aefd_stream_close_result stream_close(void *raw, unsigned kind,
                                                    unsigned selector) {
  struct streams *s = raw;
  ++s->closes;
  if (s->deny)
    return (struct aefd_stream_close_result){1, 0, -13};
  if (kind != AEFD_BIND_PIPE || selector < 3 || selector > 4)
    return (struct aefd_stream_close_result){1, 0, -9};
  unsigned end = selector - 3U;
  if (!s->unknown || s->effect) {
    if (s->ends[end] < 0 || close(s->ends[end]) != 0)
      return (struct aefd_stream_close_result){1, 0, -5};
    s->ends[end] = -1;
    ++s->physical_closes;
  }
  if (s->unknown)
    return (struct aefd_stream_close_result){0, 0, 0};
  return (struct aefd_stream_close_result){1, 1, 0};
}
static int settle_streams(struct streams *s) {
  /* Actual resource-owner cleanup; retired map metadata is not settlement. */
  for (unsigned i = 0; i < 2; ++i)
    if (s->ends[i] >= 0) {
      if (close(s->ends[i]) != 0)
        return 0;
      s->ends[i] = -1;
      ++s->physical_closes;
    }
  return s->physical_closes == 2;
}
static int same_finish(struct aefd_finish a, struct aefd_finish b) {
  return a.attempted == b.attempted && a.removed == b.removed &&
         a.remaining == b.remaining && a.first_error == b.first_error &&
         a.unknown == b.unknown && a.transport.input == b.transport.input &&
         a.transport.output == b.transport.output;
}
int main(int argc, char **argv) {
  const char *mode = argc == 2 ? argv[1] : "positive";
  int rollback = strcmp(mode, "rollback") == 0;
  int lost_dup = strcmp(mode, "lost-dup-header") == 0;
  int lost_cleanup = strcmp(mode, "lost-cleanup-header") == 0;
  int unknown = strcmp(mode, "unknown-close") == 0 ||
                strcmp(mode, "unknown-close-effect") == 0;
  if (argc > 2 || (!rollback && !lost_dup && !lost_cleanup && !unknown &&
                   strcmp(mode, "positive")))
    return 1;
  (void)setvbuf(stdin, NULL, _IONBF, 0);
  (void)setvbuf(stdout, NULL, _IONBF, 0);
  struct context io = {0};
  struct aefd_client client = {0};
  struct aefd_session session = {0};
  struct aefd_bindings map = {0};
  unsigned char workspace[AEFD_READ_MAX], output_bytes[AEFD_READ_MAX];
  memset(workspace, 0xa5, sizeof workspace);
  memset(output_bytes, 0x91, sizeof output_bytes);
  unsigned char startup[AEFD_BINDINGS_BYTES] = {0};
  struct streams streams = {.ends = {-1, -1},
                            .unknown = unknown,
                            .effect = strcmp(mode, "unknown-close-effect") == 0,
                            .deny = rollback || lost_cleanup};
  struct aefd_adapters adapters = {{&streams, stream_read},
                                   {&streams, stream_write},
                                   {&streams, stream_close},
                                   {&streams, make_pipe}};
  struct aefd_io channel = {&io, input, output, ready, close_io};
  /* A failed startup must publish nothing or clear caller workspace. */
  if (aefd_session_init(&session, &map, &client, startup, sizeof startup, 77,
                        channel, workspace, adapters) != -22 ||
      session.initialized || client.generation || map.generation || io.calls ||
      workspace[0] != 0xa5 || workspace[AEFD_READ_MAX - 1U] != 0xa5)
    return 2;
  memcpy(startup, "AEFDT001", 8);
  aefd_put(startup, 1, 77);
  aefd_put(startup, 2, AEFD_BINDINGS_COUNT);
  if (aefd_session_init(&session, &map, &client, startup, sizeof startup, 77,
                        channel, workspace, adapters) != 0 ||
      aefd_session_init(&session, &map, &client, startup, sizeof startup, 77,
                        channel, workspace, adapters) != -16 ||
      io.calls)
    return 3;
  int pair[2] = {-1, -1};
  if (aefd_session_pipe(&session, pair, 1) != 0 || pair[0] != 0 ||
      pair[1] != 1 || streams.creates != 1 ||
      aefd_session_seek(&session, 0, 0, 0) != -29 || io.calls)
    return 4;
  if (aefd_session_open(&session, (const unsigned char *)"file", 4, 1) != 2 ||
      map.slots[2].selector != 3 || map.slots[0].selector != 3 ||
      map.slots[2].kind != AEFD_BIND_FILE ||
      map.slots[0].kind != AEFD_BIND_PIPE)
    return 5;
  struct aefd_bindings before = map;
  if (rollback || lost_dup || lost_cleanup || unknown) {
    struct aefd_redirect_result result = aefd_session_redirect(&session, 2, 1);
    if (memcmp(&map, &before, sizeof map) || result.committed ||
        result.target_removed)
      return 31;
    if (rollback || lost_cleanup) {
      if (result.target_status != -13 || !result.target_attempted ||
          result.prepared_selector != 4 || !result.cleanup_attempted)
        return 32;
      if (rollback) {
        if (result.status != -13 || result.cleanup_status ||
            result.unresolved || result.unknown ||
            aefd_file_read(&client, 4, NULL, 0) != -9)
          return 33;
        streams.deny = 0;
        if (aefd_session_read(&session, 2, output_bytes, 3) != 3 ||
            memcmp(output_bytes, "abc", 3) || streams.reads)
          return 36;
      } else if (result.status != -5 || result.cleanup_status != -5 ||
                 !result.unresolved || !result.unknown)
        return 37;
    } else if (lost_dup) {
      if (result.status != -5 || result.prepared_selector != -1 ||
          !result.unresolved || !result.unknown || result.target_attempted ||
          result.cleanup_attempted || streams.closes)
        return 34;
    } else {
      if (result.status != -5 || result.target_status != -5 ||
          result.prepared_selector != 4 || !result.unresolved ||
          !result.unknown || !result.target_attempted ||
          result.cleanup_attempted || streams.closes != 1)
        return 35;
    }
  } else {
    if (aefd_session_read(&session, 2, output_bytes, 2) != 2 ||
        memcmp(output_bytes, "ab", 2) || streams.reads)
      return 6;
    struct aefd_redirect_result result = aefd_session_redirect(&session, 2, 1);
    if (result.status != 1 || result.prepared_selector != 4 ||
        !result.committed || !result.target_attempted ||
        !result.target_removed || result.target_status ||
        result.cleanup_attempted || result.unknown || result.unresolved ||
        map.slots[1].kind != AEFD_BIND_FILE || map.slots[1].selector != 4 ||
        map.slots[0].kind != AEFD_BIND_PIPE || streams.physical_closes != 1)
      return 7;
    if (aefd_session_read(&session, 0, output_bytes, 1) != 0 ||
        memcmp(output_bytes, "ab", 2) || streams.reads != 1 ||
        aefd_session_read(&session, 1, output_bytes, 2) != 2 ||
        memcmp(output_bytes, "cd", 2) || streams.reads != 1 ||
        aefd_session_seek(&session, 2, 0, 1) != 4 ||
        aefd_session_read(&session, 2, output_bytes, sizeof output_bytes) !=
            2 ||
        memcmp(output_bytes, "ef", 2))
      return 8;
    for (size_t i = 2; i < sizeof output_bytes; ++i)
      if (output_bytes[i] != 0x91)
        return 9;
    unsigned char full[AEFD_BINDINGS_BYTES], projected[AEFD_BINDINGS_BYTES];
    struct aefd_bindings roundtrip, omitted;
    before = map;
    size_t calls = io.calls;
    if (aefd_session_flags(&session, 2) != 1 ||
        aefd_session_flags(&session, 1) != 0 ||
        aefd_session_snapshot(&session, full, sizeof full, 0) != 0 ||
        aefd_session_snapshot(&session, projected, sizeof projected, 1) != 0 ||
        !aefd_bindings_decode(full, sizeof full, 77, &roundtrip) ||
        !aefd_bindings_decode(projected, sizeof projected, 77, &omitted) ||
        memcmp(&map, &before, sizeof map) ||
        memcmp(&roundtrip, &map, sizeof map) || omitted.slots[0].kind ||
        omitted.slots[2].kind || omitted.slots[1].kind != AEFD_BIND_FILE ||
        io.calls != calls)
      return 10;
  }
  int retired = lost_dup || lost_cleanup || unknown;
  unsigned closes = streams.closes;
  size_t calls = io.calls;
  struct aefd_finish receipt = aefd_session_finish(&session);
  if (receipt.transport.input || receipt.transport.output || io.closes != 1)
    return 11;
  if (retired) {
    if (!receipt.unknown || receipt.first_error != -5 || receipt.attempted ||
        receipt.removed || receipt.remaining != 3 || streams.closes != closes ||
        io.calls != calls)
      return 12;
    for (size_t i = 0; i < sizeof output_bytes; ++i)
      if (output_bytes[i] != 0x91)
        return 13;
  } else if (receipt.unknown || receipt.first_error || receipt.attempted != 3 ||
             receipt.removed != 3 || receipt.remaining)
    return 14;
  calls = io.calls;
  closes = streams.closes;
  if (!same_finish(receipt, aefd_session_finish(&session)) ||
      io.calls != calls || streams.closes != closes ||
      aefd_session_read(&session, 2, output_bytes, 1) != -5 ||
      aefd_session_init(&session, &map, &client, startup, sizeof startup, 77,
                        channel, workspace, adapters) != -16)
    return 15;
  for (size_t i = 0; i < sizeof workspace; ++i)
    if (workspace[i] != 0)
      return 16;
  if (!settle_streams(&streams) || streams.physical_closes != 2)
    return 17;
  fprintf(stderr,
          "session redirect %s passed: io=%zu close=%u actual-close=%u "
          "receipt=%u/%u/%u unknown=%d\n",
          mode, io.calls, streams.closes, streams.physical_closes,
          receipt.attempted, receipt.removed, receipt.remaining,
          receipt.unknown);
  return 0;
}
