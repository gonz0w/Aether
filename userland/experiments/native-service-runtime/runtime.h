/* SPDX-License-Identifier: BSD-2-Clause */
#ifndef AETHER_SERVICE_RUNTIME_H
#define AETHER_SERVICE_RUNTIME_H
/* Private x86-64 service profile. Errors are positive errno values. */
int aether_runtime_init(void);
int aether_runtime_finish(void);
unsigned aether_runtime_live(void);
unsigned aether_runtime_admissions(void);
#endif
