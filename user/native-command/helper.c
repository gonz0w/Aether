/* SPDX-License-Identifier: BSD-2-Clause */
#if HELPER == 2
#include "../native-process/helper.c"
/* Private file-service fault fixture: close only its admitted reply endpoint. */
long bridge_close_output(void) {
  return memtrap(0x24003, output, 0, 0, 0);
}
#else
#include "transport.h"
#include <unistd.h>
static _Thread_local volatile unsigned tls = 23;
#ifdef PUBLIC_RESULT
#include "result.h"
#define FAILURE(n) 1
#else
#define FAILURE(n) (n)
#endif
#define CHECK(x, n)                                                            \
  do {                                                                         \
    if (!(x))                                                                  \
      return FAILURE(n);                                                       \
  } while (0)
#ifdef RUNNER_FORWARD
/* Validated private carrier storage; FORWARD_FIRST is a fixture input, not CLI
 * parsing. */
static char forwarded[6][32];
static unsigned forwarded_count;
#endif
static void request(unsigned char *b) {
  memset(b, 0, 384);
  put(b, 0, 4);
  put(b, 4, 1);
  put(b, 8, 2);
  put(b, 12, 1);
  put(b, 16, 2);
  memcpy(b + 32, "bytecount", 9);
  for (unsigned j = 0; j < 2; j++) {
    unsigned o = 64 + j * 32;
    put(b, o, refs[j]);
    put(b, o + 4, fds[j]);
    put(b, o + 8, j);
    put(b, o + 12, j ? 2 : 1);
  }
#ifdef RUNNER_FORWARD
  unsigned count = forwarded_count - FORWARD_FIRST;
  put(b, 8, count);
  memcpy(b + 32, forwarded[FORWARD_FIRST], 32);
  for (unsigned j = 0; j < count; j++)
    memcpy(b + 128 + j * 32, forwarded[FORWARD_FIRST + j], 32);
  memcpy(b + 128 + count * 32, "LC_ALL=C", 8);
#ifdef CORRUPT_FORWARDED
  b[224] = 'Y'; /* Test-only corruption of the fourth child argument. */
#endif
#else
  memcpy(b + 128, "bytecount", 9);
  memcpy(b + 160, "--decimal", 9);
  memcpy(b + 192, "LC_ALL=C", 8);
#endif
}
#ifdef MALFORMED_LAUNCH
#include "launch-probe.h"
#endif
#ifdef LAUNCH_PREFIX
#include "eof-probe.h"
#endif
#ifdef RUNNER_STARTUP
#include "startup-probe.h"
#endif
int main(int argc, char **argv) {
#ifdef PUBLIC_RESULT
  CHECK(result_policy_probe(), 112);
#endif
#ifdef RUNNER_STARTUP
  if (!startup_probe()) {
    unsigned char discard[32];
    CHECK(move(discard, sizeof discard, 0), 111);
    return 110; /* Drain the following frame without publishing its bindings. */
  }
#endif
  CHECK(tls == 23 && argc == 1 && !strcmp(argv[0], "client") && bootstrap(),
        60);
  unsigned char b[384];
#ifdef RUNNER_LOCAL_EMPTY
#ifdef LOCAL_LAUNCH
  request(b);
  (void)move(b, 32, 1);
#elif defined(LOCAL_STALE)
  memset(b, 0, 32);
  put(b, 0, 3);
  put(b, 4, refs[0] ^ 4);
  put(b, 8, 3);
  (void)exchange(b, 32);
#endif
#ifndef LOCAL_SKIP_CLOSE
  CHECK(close(3) == 0, 113);
#endif
  CHECK(close(4) == 0, 114);
#ifdef LOCAL_AFTER_CLOSE
  memset(b, 0, 32);
  put(b, 0, 5);
  (void)move(b, 32, 1);
#endif
#ifdef LOCAL_BAD_STATUS
  return 1;
#else
  return 0;
#endif
#endif
#ifdef LAUNCH_PREFIX
  eof_probe();
#endif
#ifdef MALFORMED_LAUNCH
  CHECK(launch_probe(), 103);
#endif
  request(b);
  b[32] = 'X';
  CHECK(exchange(b, 384) && (int)get(b, 0) == -2, 61);
  request(b);
  put(b, 104, 0);
  CHECK(exchange(b, 384) && (int)get(b, 0) == -22, 62);
  request(b);
  put(b, 108, 3);
  CHECK(exchange(b, 384) && (int)get(b, 0) == -13, 63);
  request(b);
  put(b, 96, refs[0]);
  CHECK(exchange(b, 384) && (int)get(b, 0) == -9, 64);
  request(b);
  put(b, 8, 5);
  CHECK(exchange(b, 384) && (int)get(b, 0) == -22, 65);
#ifdef REJECT_LAUNCH
  if (memtrap(0x20005, 0, 0, 0, 0) == 1) {
    request(b);
    CHECK(exchange(b, 384) && (int)get(b, 0) == -22, 74);
  }
#endif
#ifdef REJECT_CAPACITY
  if (memtrap(0x20005, 0, 0, 0, 0) == 1) {
    request(b);
    CHECK(exchange(b, 384) && (int)get(b, 0) == -16, 74);
  }
#endif
  request(b);
  CHECK(exchange(b, 384) && get(b, 0) == 0, 66);
  unsigned receipt = get(b, 4);
  CHECK(receipt == (0x73000000u | (unsigned)memtrap(0x20005, 0, 0, 0, 0)), 66);
  memset(b, 0xa5,
         sizeof b); /* Native child must retain the copied startup bytes. */
  CHECK(close(3) == 0, 67); /* Child retains its input after parent close. */
  int result = -11;
  for (unsigned t = 0; t < 100000 && result == -11; t++) {
    memset(b, 0, 32);
    put(b, 0, 5);
    put(b, 4, receipt);
    CHECK(exchange(b, 32), 68);
    result = (int)get(b, 0);
  }
  CHECK(result == 0 && get(b, 4) == receipt &&
            get(b, 8) ==
#ifdef CHILD_STATUS
                CHILD_STATUS
#elif defined(CHILD_FAULT) || defined(CHILD_NONZERO)
                134
#elif defined(FULL_OUTPUT)
            82
#else
            0
#endif
            && get(b, 12) ==
#ifdef CHILD_FAULT
                   2,
#else
                   1,
#endif
        69);
#if defined(PUBLIC_RESULT) && !defined(PUBLIC_FORCE_ZERO)
  unsigned child_detail = get(b, 8);
#ifndef PUBLIC_IGNORE_KIND
  unsigned child_kind = get(b, 12);
#endif
#endif
  memset(b, 0, 32);
  put(b, 0, 5);
  put(b, 4, receipt);
  CHECK(exchange(b, 32) && (int)get(b, 0) == -10, 70);
  char data[17];
  errno = 97;
  ssize_t n = read(4, data, sizeof data);
  CHECK(n == 0 && errno == 97, 71);
  CHECK(read(4, data, sizeof data) == 0 && close(4) == 0, 72);
  errno = 0;
  CHECK(read(4, data, 0) == -1 && errno == EBADF, 73);
#ifdef PUBLIC_FORCE_ZERO
  return 0;
#elif defined(PUBLIC_IGNORE_KIND)
  return (int)child_detail;
#elif defined(PUBLIC_RESULT)
  return (int)runner_result(child_kind, child_detail, 1);
#else
  return 29;
#endif
}
#endif
