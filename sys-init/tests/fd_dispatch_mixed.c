/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only live pipe client. Typed file-only facade; no native shell or target
 * workspace. */
#include "fd-pipe.h"
#include "fd-replace.h"
#include "fd-routing.h"
#include "fd-write.h"
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
  int unknown, effect;
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
int main(int argc, char **argv) {
  const char *mode = argc == 2 ? argv[1] : "positive";
  int lost = strcmp(mode, "lost-body") == 0;
  int stale = strcmp(mode, "stale-map") == 0;
  int unknown = strncmp(mode, "unknown-close", 13) == 0;
  if (argc > 2 || (!lost && !stale && !unknown && strcmp(mode, "positive")))
    return 1;
  (void)setvbuf(stdin, NULL, _IONBF, 0);
  (void)setvbuf(stdout, NULL, _IONBF, 0);
  struct context io = {0};
  struct aefd_client client;
  unsigned char workspace[AEFD_READ_MAX], output_bytes[AEFD_READ_MAX];
  memset(workspace, 0xa5, sizeof workspace);
  memset(output_bytes, 0x91, sizeof output_bytes);
  if (aefd_client_init(&client,
                       (struct aefd_io){&io, input, output, ready, close_io},
                       workspace, 77) != 1)
    return 2;
  unsigned char startup[AEFD_BINDINGS_BYTES] = {0};
  memcpy(startup, "AEFDT001", 8);
  aefd_put(startup, 1, 77);
  aefd_put(startup, 2, AEFD_BINDINGS_COUNT);
  for (unsigned i = 0; i < 3; ++i) {
    startup[64U + i * 4U] = AEFD_BIND_CONSOLE;
    startup[65U + i * 4U] = (unsigned char)i;
  }
  struct aefd_bindings map;
  if (!aefd_bindings_decode(startup, sizeof startup, 77, &map))
    return 3;
  struct streams streams = {.ends = {-1, -1},
                            .unknown = unknown,
                            .effect =
                                strcmp(mode, "unknown-close-effect") == 0};
  struct aefd_pipe_creator creator = {&streams, make_pipe};
  struct aefd_stream_reader reader = {&streams, stream_read};
  struct aefd_stream_writer writer = {&streams, stream_write};
  struct aefd_stream_closer closer = {&streams, stream_close};
  int pair[2] = {-1, -1};
  if (aefd_table_pipe(&map, &client, &creator, pair, 1) != 0 || pair[0] != 3 ||
      pair[1] != 4 || streams.creates != 1 || io.calls != 0)
    return 4;
  if (aefd_table_open(&map, &client, (const unsigned char *)"file", 4, 0) !=
          5 ||
      map.slots[5].kind != AEFD_BIND_FILE || map.slots[5].selector != 3 ||
      map.slots[3].kind != AEFD_BIND_PIPE || map.slots[3].selector != 3)
    return 5;
  struct aefd_bindings before = map;
  if (unknown || stale) {
    int64_t result;
    if (unknown) {
      result = aefd_mixed_close(&map, &client, &closer, 3);
      if (result != -5 || memcmp(&map, &before, sizeof map) ||
          streams.closes != 1)
        return 21;
    } else {
      ++map.generation;
      before = map;
      result = aefd_routed_read(&map, &client, &reader, 5, output_bytes, 1);
      if (result != -5 || memcmp(&map, &before, sizeof map) || streams.reads)
        return 22;
    }
    size_t calls = io.calls;
    if (client.live ||
        aefd_routed_read(&map, &client, &reader, 3, output_bytes, 1) != -5 ||
        io.calls != calls)
      return 23;
  } else if (lost) {
    if (aefd_routed_read(&map, &client, &reader, 5, output_bytes,
                         sizeof output_bytes) != -5 ||
        memcmp(&map, &before, sizeof map) || streams.reads)
      return 24;
    size_t calls = io.calls;
    if (aefd_routed_read(&map, &client, &reader, 5, output_bytes, 1) != -5 ||
        io.calls != calls)
      return 25;
  } else {
    if (aefd_routed_read(&map, &client, &reader, 5, output_bytes, 3) != 3 ||
        memcmp(output_bytes, "abc", 3) || streams.reads)
      return 7;
    if (aefd_mixed_dup(&map, &client, 5, 0, 1) != 6 ||
        map.slots[6].kind != AEFD_BIND_FILE || map.slots[6].selector != 4 ||
        map.slots[6].cloexec != 1 ||
        aefd_table_seek(&map, &client, 6, 0, 1) != 3)
      return 8;
    if (aefd_routed_read(&map, &client, &reader, 6, output_bytes,
                         sizeof output_bytes) != 3 ||
        memcmp(output_bytes, "def", 3) || streams.reads)
      return 9;
    for (size_t i = 3; i < sizeof output_bytes; ++i)
      if (output_bytes[i] != 0x91)
        return 10;
    if (aefd_routed_read(&map, &client, &reader, 6, output_bytes,
                         sizeof output_bytes) != 0 ||
        memcmp(output_bytes, "def", 3) || streams.reads)
      return 11;
    size_t calls = io.calls;
    if (aefd_routed_write(&map, &client, &writer, 5, (const unsigned char *)"F",
                          1) != -30 ||
        aefd_stream_replace(&map, &client, &closer, 4, 5) != -38 ||
        io.calls != calls || streams.writes || streams.closes ||
        aefd_table_seek(&map, &client, 3, 0, 0) != -38)
      return 12;
    if (aefd_routed_write(&map, &client, &writer, 4, (const unsigned char *)"P",
                          1) != 1 ||
        aefd_routed_read(&map, &client, &reader, 3, output_bytes, 1) != 1 ||
        output_bytes[0] != 'P' || streams.reads != 1 || streams.writes != 1 ||
        io.calls != calls)
      return 13;
    if (aefd_mixed_dup(&map, &client, 3, 7, 1) != 7 ||
        aefd_mixed_close(&map, &client, &closer, 3) != 0 || streams.closes ||
        map.slots[3].kind != AEFD_BIND_EMPTY)
      return 18;
    if (aefd_stream_replace(&map, &client, &closer, 4, 8) != 8 ||
        map.slots[4].cloexec != 1 || map.slots[8].cloexec != 0 ||
        aefd_mixed_set_cloexec(&map, &client, 8, 1) != 0 ||
        aefd_stream_replace(&map, &client, &closer, 8, 8) != 8 ||
        map.slots[8].cloexec != 1 ||
        aefd_mixed_close(&map, &client, &closer, 4) != 0 || streams.closes)
      return 14;
    if (aefd_routed_write(&map, &client, &writer, 8, (const unsigned char *)"Q",
                          1) != 1 ||
        aefd_routed_read(&map, &client, &reader, 7, output_bytes, 1) != 1 ||
        output_bytes[0] != 'Q' ||
        aefd_mixed_close(&map, &client, &closer, 8) != 0 ||
        streams.closes != 1 ||
        aefd_routed_read(&map, &client, &reader, 7, output_bytes, 1) != 0 ||
        aefd_mixed_close(&map, &client, &closer, 7) != 0 || streams.closes != 2)
      return 15;
    if (aefd_mixed_set_cloexec(&map, &client, 6, 0) != 0 ||
        map.slots[6].cloexec ||
        aefd_mixed_close(&map, &client, &closer, 5) != 0 || map.slots[5].kind ||
        aefd_mixed_close(&map, &client, &closer, 6) != 0 || map.slots[6].kind ||
        streams.closes != 2)
      return 16;
    calls = io.calls;
    if (aefd_routed_read(&map, &client, &reader, 5, output_bytes, 0) != -9 ||
        aefd_mixed_close(&map, &client, &closer, 5) != -9 || io.calls != calls)
      return 17;
    aefd_client_abort(&client);
  }
  if (lost || stale || unknown)
    for (size_t i = 0; i < sizeof output_bytes; ++i)
      if (output_bytes[i] != 0x91)
        return 26;
  for (size_t i = 0; i < sizeof workspace; ++i)
    if (workspace[i] != 0)
      return 27;
  aefd_client_abort(&client);
  if (!settle_streams(&streams) || io.closes != 1 || client.closed.input ||
      client.closed.output || !io.read_waits || !io.write_waits)
    return 28;
  fprintf(stderr,
          "mixed FD %s passed: file-io=%zu stream=%u/%u/%u physical-close=%u\n",
          mode, io.calls, streams.reads, streams.writes, streams.closes,
          streams.physical_closes);
  return 0;
}
