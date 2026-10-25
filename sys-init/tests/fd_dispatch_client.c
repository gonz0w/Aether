/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only live pipe client. Not a native shell facade or target workspace. */
#include "fd-client.h"
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
static int call(struct aefd_client *c, uint64_t op, uint64_t a, uint64_t b,
                uint64_t d, struct aefd_reply *r) {
  uint64_t args[4] = {a, b, d, 0};
  return aefd_client_exchange(c, op, args,
                              op == 1 ? (const unsigned char *)"file" : NULL,
                              op == 1 ? 4U : 0U, r);
}
int main(int argc, char **argv) {
  int negative = argc == 2 && strcmp(argv[1], "lost-body") == 0;
  if (argc > 2)
    return 1;
  (void)setvbuf(stdin, NULL, _IONBF, 0);
  (void)setvbuf(stdout, NULL, _IONBF, 0);
  struct context io = {0};
  struct aefd_client client;
  unsigned char workspace[AEFD_READ_MAX];
  struct aefd_reply r = {0};
  if (aefd_client_init(&client,
                       (struct aefd_io){&io, input, output, ready, close_io},
                       workspace, 77) != 1)
    return 2;
  if (call(&client, 1, 0, 4, 0, &r) != 1 || r.status != 0 || r.result != 3)
    return 3;
  if (negative) {
    r = (struct aefd_reply){91, 92, 93};
    if (call(&client, 2, 3, 4096, 0, &r) != -1 || r.status != 91 ||
        r.result != 92 || r.body != 93)
      return 4;
    for (size_t i = 0; i < sizeof workspace; ++i)
      if (workspace[i] != 0)
        return 5;
    size_t calls = io.calls;
    if (call(&client, 2, 3, 1, 0, &r) != -1 || io.calls != calls ||
        io.closes != 1)
      return 6;
  } else {
    if (call(&client, 2, 3, 3, 0, &r) != 1 || r.status != 0 || r.body != 3 ||
        memcmp(workspace, "abc", 3))
      return 7;
    if (call(&client, 4, 3, 3, 1, &r) != 1 || r.status != 0 || r.result != 4)
      return 8;
    if (call(&client, 3, 4, 0, 1, &r) != 1 || r.status != 0 || r.result != 3)
      return 9;
    if (call(&client, 2, 4, 4096, 0, &r) != 1 || r.status != 0 || r.body != 3 ||
        memcmp(workspace, "def", 3))
      return 10;
    for (size_t i = 3; i < sizeof workspace; ++i)
      if (workspace[i] != 0)
        return 11;
    if (call(&client, 6, 4, 0, 0, &r) != 1 || r.status != 0)
      return 12;
    if (call(&client, 5, 3, 0, 0, &r) != 1 || r.status != 0)
      return 13;
    if (call(&client, 5, 4, 0, 0, &r) != 1 || r.status != 0)
      return 14;
    if (call(&client, 5, 3, 0, 0, &r) != 1 || r.status != -9)
      return 15;
    if (call(&client, 77, 0, 0, 0, &r) != 1 || r.status != -38)
      return 16;
    aefd_client_abort(&client);
  }
  aefd_client_abort(&client);
  if (io.closes != 1 || client.closed.input != 0 || client.closed.output != 0 ||
      io.read_waits == 0 || io.write_waits == 0)
    return 17;
  fprintf(
      stderr,
      "live C client: %s calls=%zu read-waits=%u write-waits=%u closes=%u\n",
      negative ? "lost-body retired" : "10 exchanges passed", io.calls,
      io.read_waits, io.write_waits, io.closes);
  return 0;
}
