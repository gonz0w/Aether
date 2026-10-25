/* SPDX-License-Identifier: BSD-2-Clause */
#include "../native-memory/adapter.h"
#include <errno.h>
#include <limits.h>
#include <string.h>
#include <sys/auxv.h>
static unsigned long input, output;
static int poisoned;
#if defined(SESSION_CHANNEL_WAIT) && (!defined(SESSION_SERIAL) || !defined(PIPELINE_STREAMS))
#error "channel waiting requires the selected serial SESSION client"
#endif
#ifdef STARTUP_GUARD_TEST
static unsigned startup_guard_transfers, startup_guard_exposed;
#endif
#ifdef REPLY_PROBE
/* Test-only counters: count actual channel traps, including partial transfers.
 */
static unsigned reply_injections;
#endif
#if defined(STARTUP_FILES_POISON) || defined(STARTUP_FILES_BOUNDARIES) || defined(REPLY_PROBE) || defined(BOOTSTRAP_PROBE) || defined(STREAM_AMBIGUOUS) || defined(CAT_UNKNOWN) || defined(CAT_FINAL_TEST)
static unsigned channel_calls;
#endif
#if defined(STREAM_AMBIGUOUS) || defined(CAT_UNKNOWN)
static unsigned poison_calls;
#endif
#if defined(SCRATCH_CLIENT) && (defined(FORK_NULL) || defined(FORK_PIPE) || defined(STARTUP_FILES))
#error "scratch bindings require a dedicated profile"
#endif
#if defined(FORK_NULL) && (defined(STARTUP_FILES) || defined(FORK_PIPE))
#error "null bindings require their dedicated profile"
#endif
#if defined(STARTUP_FILES) && defined(FORK_PIPE)
#error "pipe and file bindings overlap"
#endif
#if defined(SESSION_SCRATCH)
#ifndef PIPELINE_STREAMS
#error "session scratch requires pipeline streams"
#endif
#define BINDINGS 9
#elif defined(PIPELINE_STREAMS)
#define BINDINGS 7
#elif defined(FORK_NULL)
#define BINDINGS 4
#elif defined(STARTUP_FILES) || defined(FORK_PIPE) || defined(SCRATCH_CLIENT)
#define BINDINGS 5
#elif defined(CAT_ROLES)
#define BINDINGS 3
#elif defined(RUNNER_DENIAL) || defined(RUNNER_SUCCESS)
#define BINDINGS 4
#else
#define BINDINGS 2
#endif
static unsigned refs[BINDINGS], fds[BINDINGS], rights[BINDINGS];
static int live[BINDINGS];
static unsigned get(const unsigned char *b, unsigned i) {
  return (unsigned)b[i] | (unsigned)b[i + 1] << 8 | (unsigned)b[i + 2] << 16 |
         (unsigned)b[i + 3] << 24;
}
static void put(unsigned char *b, unsigned i, unsigned v) {
  for (unsigned j = 0; j < 4; j++)
    b[i + j] = (unsigned char)(v >> (8 * j));
}
static int move(unsigned char *b, unsigned len, int write) {
#ifndef ALLOW_POISON_TRAFFIC
  if (poisoned)
    return 0;
#endif
  unsigned n = 0;
#ifdef SESSION_CHANNEL_WAIT
  for (;;) {
#else
  for (unsigned t = 0; t < 100000; t++) {
#endif
#if defined(STARTUP_FILES_POISON) || defined(STARTUP_FILES_BOUNDARIES) || defined(REPLY_PROBE) || defined(BOOTSTRAP_PROBE) || defined(STREAM_AMBIGUOUS) || defined(CAT_UNKNOWN) || defined(CAT_FINAL_TEST)
    channel_calls++;
#endif
#ifdef STARTUP_GUARD_TEST
    uint64_t observed = 0;
    startup_guard_transfers++;
    if (memtrap(0x1000e, 0, 0, (uintptr_t)&observed, 8) ||
        observed != (UINT64_MAX & ~((UINT64_C(1) << 8) | (UINT64_C(1) << 18))))
      startup_guard_exposed++;
#endif
    long r = memtrap(write ? 0x24002 : 0x24001, write ? output : input,
                     (uintptr_t)(b + n), len - n > 16 ? 16 : len - n, 0);
    if (r == -11) {
#ifdef SESSION_CHANNEL_WAIT
      /* Preserve partial frame ownership. Completion is only a readiness hint;
         interruption/authority loss cannot authorize replay of the request. */
      if (memtrap(0x24004, write ? output : input, 0, 0, 0) != 0)
        break;
#else
      memtrap(0x1fffe, 0, 0, 0, 0);
#endif
      continue;
    }
    if (r <= 0 || (unsigned long)r > len - n)
      break;
    n += (unsigned)r;
    if (n == len)
      return 1;
  }
  poisoned = 1;
  return 0;
}
static int exchange(unsigned char *b, unsigned size) {
  return move(b, size, 1) && move(b, 32, 0);
}
#ifdef RUNNER_STREAMS
#include "stream-bootstrap.h"
#endif
#ifdef CAT_ROLES
#include "cat-bootstrap.h"
#endif
static int bootstrap(void) {
#ifdef PIPELINE_STREAMS
  return pipeline_bootstrap();
#elif defined(CAT_ROLES)
  return cat_bootstrap();
#elif defined(RUNNER_STREAMS)
  return stream_bootstrap();
#else
  input = getauxval(0xa001);
  output = getauxval(0xa002);
  unsigned char b[32];
  if (!input || !output || input == output || !move(b, 32, 0) || get(b, 0) ||
      get(b, 28))
    return 0;
#ifdef BOOTSTRAP_PROBE
  /* Corrupt only the second binding after the complete real frame arrives. */
  b[BOOTSTRAP_FIELD] ^= 1;
#endif
  unsigned gen = (unsigned)memtrap(0x20005, 0, 0, 0, 0);
  for (unsigned j = 0; j < 2; j++) {
    unsigned base = 4 + j * 12;
    refs[j] = get(b, base);
    fds[j] = get(b, base + 4);
    rights[j] = get(b, base + 8);
#ifdef COMMAND_CHILD
    if (refs[j] != (0x72000000u | (j << 16) | gen) || fds[j] != j ||
        rights[j] != (j ? 2u : 1u))
      return 0;
#else
    if (refs[j] != (0x71000000u | (j << 16) | gen) || fds[j] != 3 + j ||
        rights[j] != (j ? 3u : 1u))
      return 0;
#endif
#ifdef EARLY_PUBLICATION
    live[j] = 1;
#endif
  }
  live[0] = live[1] = 1;
  return 1;
#endif
}
static long file_io(unsigned long op, unsigned long fd, unsigned long pointer,
                    unsigned long count) {
  if (op != 0 && op != 1 && op != 3)
    return -ENOSYS;
  unsigned j = 0;
  while (j < BINDINGS && fds[j] != fd)
    j++;
  if (fd > INT_MAX || j == BINDINGS || !live[j])
    return -EBADF;
  if (op == 3)
    live[j] = 0;
  if (poisoned)
    return -EIO;
  if (op != 3) {
    if (!(rights[j] & (op == 0 ? 1 : 2)))
      return -EACCES;
    if (count > SSIZE_MAX)
      return -EINVAL;
    if (count && !pointer)
      return -EFAULT;
  }
  unsigned n = op == 3 ? 0 : count > 16 ? 16 : (unsigned)count;
  unsigned char b[32] = {0};
  put(b, 0, op == 0 ? 1 : op == 1 ? 2 : 3);
#ifdef STARTUP_FILES
  if (j >= 3)
    put(b, 0, op == 0 ? 7 : 8);
#endif
  put(b, 4, refs[j]);
  put(b, 8, (unsigned)fd);
  put(b, 12, n);
  if (op == 1 && n)
    memcpy(b + 16, (void *)pointer, n);
  if (!exchange(b, 32)) {
#if defined(STREAM_AMBIGUOUS) || defined(CAT_UNKNOWN)
    poison_calls = channel_calls;
#endif
    return -EIO;
  }
#ifdef REPLY_PROBE
  if (!reply_injections && (int)get(b, 0) >= 0 &&
#ifdef DROP_CLOSE
      op == 3
#else
      op == 0 && n != 0
#endif
  ) {
    reply_injections++;
#ifdef CORRUPT_READ
    b[12] = 1;
#else
    poisoned = 1;
    return -EIO;
#endif
  }
#endif
  int result = (int)get(b, 0), bad = result < -4095 || result > (int)n;
  for (unsigned i = 4; i < 16; i++)
    if (b[i])
      bad = 1;
  unsigned start =
      op == 0 && result > 0 && result <= (int)n ? 16 + (unsigned)result : 16;
  for (unsigned i = start; i < 32; i++)
    if (b[i])
      bad = 1;
  int close_bad = op == 3 && result;
#if defined(RUNNER_STREAMS) || defined(CAT_ROLES)
  /* AEOUT001/AECAT001: complete EIO close confirms alias consumption. Other roles
   * remain usable for cleanup; malformed/unknown replies still poison. */
  if (op == 3 && result == -EIO
#ifdef SCRATCH_CLIENT
      && j < 3
#endif
  )
    close_bad = 0;
#endif
  if (bad || close_bad) {
    poisoned = 1;
#ifdef CAT_UNKNOWN
    poison_calls = channel_calls;
#endif
    return -EIO;
  }
  if (op == 0 && result > 0)
    memcpy((void *)pointer, b + 16, (unsigned)result);
  return result;
}
#ifdef SHELL_STARTUP
#include "startup-adapter.h"
#endif
long __aether_io(unsigned long op, unsigned long fd, unsigned long p,
                 unsigned long n) {
  int saved = errno;
  #ifdef SHELL_STARTUP
  long result = startup_io(op, fd, p, n);
#else
  long result = file_io(op, fd, p, n);
#endif
  errno = saved;
  return result;
}
