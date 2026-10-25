/* SPDX-License-Identifier: BSD-2-Clause */
/* A real command: no protocol, native traps or fixed expected output. */
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
extern int command_bootstrap(void);
#ifdef FORWARD_OBSERVER
extern char **environ;
#endif
static _Thread_local volatile unsigned tls = 23;
#ifdef CONSUMER_HELPER
extern int consumer_helper_main(int, char **);
#endif
int main(int argc, char **argv) {
#ifdef CONSUMER_HELPER
  if (!command_bootstrap() || tls != 23)
    return 80;
  tls = 37;
#ifdef CONSUMER_HELPER_SKIP
  int status = 0;
  (void)argc;
  (void)argv;
#else
  int status = consumer_helper_main(argc, argv);
#endif
#ifndef CONSUMER_HELPER_SKIP_CLOSE
  if (close(0) || close(1))
    return 83;
#endif
  return status;
#else
  if (!command_bootstrap() || tls != 23 ||
      argc !=
#ifdef WIDE_STARTUP
          4
#else
          2
#endif
      || strcmp(argv[0], "bytecount") || strcmp(argv[1], "--decimal") ||
      !getenv("LC_ALL") || strcmp(getenv("LC_ALL"), "C"))
    return 80;
#ifdef FORWARD_OBSERVER
  if (!environ || !environ[0] || strcmp(environ[0], "LC_ALL=C") || environ[1])
    return 80;
#ifdef WIDE_STARTUP
  if (strcmp(argv[2], "") ||
      strcmp(argv[3], "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx") || argv[4])
    return 80;
#else
  if (argv[2])
    return 80;
#endif
#endif
  char input[23];
  unsigned total = 0;
  ssize_t n;
  while ((n = read(0, input, sizeof input)) > 0)
    total += (unsigned)n;
  if (n < 0)
    return 81;
  char digits[16];
  unsigned used = 0;
  digits[used++] = '\n';
  do {
    digits[used++] = (char)('0' + total % 10);
    total /= 10;
  } while (total);
  for (unsigned i = 0; i < used / 2; i++) {
    char c = digits[i];
    digits[i] = digits[used - 1 - i];
    digits[used - 1 - i] = c;
  }
  for (unsigned sent = 0; sent < used;) {
    n = write(1, digits + sent, used - sent);
    if (n <= 0)
      return 82;
    sent += (unsigned)n;
  }
#ifdef CHILD_FAULT
  __builtin_trap(); /* Test-only #UD after output, with both aliases still live.
                     */
#endif
#ifdef CHILD_STATUS
  return CHILD_STATUS; /* Test-only normal terminal, before alias close. */
#endif
#ifdef CHILD_NONZERO
  return 134; /* Same detail as #UD: the terminal kind must distinguish them. */
#endif
  if (close(0) || close(1))
    return 83;
  return 0;
#endif
}
