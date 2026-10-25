/* SPDX-License-Identifier: BSD-2-Clause */
#define COMMAND_CHILD
#include "transport.h"
#include <unistd.h>
#ifdef REPLY_PROBE
#include "reply-probe.h"
#endif
#ifdef BOOTSTRAP_PROBE
#include "bootstrap-probe.h"
#endif
int command_bootstrap(void) {
#ifdef BOOTSTRAP_PROBE
  bootstrap_probe();
#endif
  if (!bootstrap())
    return 0;
  errno = 0;
  if (write(0, 0, 0) != -1 || errno != EACCES)
    return 0;
  errno = 0;
  if (read(1, 0, 0) != -1 || errno != EACCES)
    return 0;
  errno = 0;
  if (read(2, 0, 0) != -1 || errno != EBADF)
    return 0;
  errno = 97;
  if (read(0, 0, 0) != 0 || errno != 97)
    return 0;
#ifdef REPLY_PROBE
  reply_probe();
#endif
  return 1;
}
