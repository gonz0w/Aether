/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only live pipe client. Typed file-only facade; no native shell or target
 * workspace. */
#include "fd-facade.h"
#include <stdio.h>
#include <string.h>
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
int main(int argc, char **argv) {
  int negative = argc == 2 && strcmp(argv[1], "lost-body") == 0;
  if (argc > 2)
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
  /* Local denials must not consume the first sequence or touch endpoints. */
  if (aefd_file_read(&client, 3, NULL, 1) != -22 ||
      aefd_file_read(&client, 3, output_bytes, AEFD_READ_MAX + 1U) != -22 ||
      aefd_file_open(&client, (const unsigned char *)"file", 4, 2) != -22 ||
      io.calls != 0)
    return 18;
  if (aefd_file_open(&client, (const unsigned char *)"file", 4, 0) != 3)
    return 3;
  if (negative) {
    if (aefd_file_read(&client, 3, output_bytes, sizeof output_bytes) != -5)
      return 4;
    for (size_t i = 0; i < sizeof workspace; ++i)
      if (workspace[i] != 0 || output_bytes[i] != 0x91)
        return 5;
    size_t calls = io.calls;
    if (aefd_file_read(&client, 3, output_bytes, 1) != -5 ||
        io.calls != calls || io.closes != 1)
      return 6;
  } else {
    if (aefd_file_read(&client, 3, output_bytes, 3) != 3 ||
        memcmp(output_bytes, "abc", 3))
      return 7;
    for (size_t i = 3; i < sizeof output_bytes; ++i)
      if (output_bytes[i] != 0x91)
        return 11;
    if (aefd_file_dup(&client, 3, 3, 1) != 4)
      return 8;
    if (aefd_file_seek(&client, 4, 0, 1) != 3)
      return 9;
    if (aefd_file_read(&client, 4, output_bytes, sizeof output_bytes) != 3 ||
        memcmp(output_bytes, "def", 3))
      return 10;
    for (size_t i = 3; i < sizeof output_bytes; ++i)
      if (output_bytes[i] != 0x91)
        return 11;
    if (aefd_file_set_cloexec(&client, 4, 0) != 0)
      return 12;
    if (aefd_file_close(&client, 3) != 0)
      return 13;
    if (aefd_file_close(&client, 4) != 0)
      return 14;
    /* A zero read must still validate the closed binding at the server. */
    if (aefd_file_read(&client, 3, NULL, 0) != -9)
      return 15;
    if (aefd_file_close(&client, 3) != -9)
      return 16;
    aefd_client_abort(&client);
  }
  aefd_client_abort(&client);
  if (io.closes != 1 || client.closed.input != 0 || client.closed.output != 0 ||
      io.read_waits == 0 || io.write_waits == 0)
    return 17;
  fprintf(stderr,
          "live typed C facade: %s calls=%zu read-waits=%u write-waits=%u "
          "closes=%u\n",
          negative ? "lost-body retired/output preserved"
                   : "10 exchanges passed",
          io.calls, io.read_waits, io.write_waits, io.closes);
  return 0;
}
