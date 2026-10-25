/* SPDX-License-Identifier: BSD-2-Clause */
#include "runner-parse.h"
#include <string.h>

static int slots_valid(const struct ar_startup *startup)
{
    if (!startup || startup->count < 1 || startup->count > AR_STARTUP_ARGS)
        return 0;
    for (unsigned i = 0; i < AR_STARTUP_ARGS; ++i) {
        unsigned end = 0;
        if (i < startup->count) {
            while (end < AR_SLOT_SIZE && startup->args[i][end])
                ++end;
            if (end == AR_SLOT_SIZE)
                return 0;
        }
        for (; end < AR_SLOT_SIZE; ++end)
            if (startup->args[i][end])
                return 0;
    }
    return !strcmp(startup->args[0], "aether-run");
}
int ar_decode(const unsigned char *record, size_t record_size,
              struct ar_startup *output)
{
    if (!record || !output || record_size != AR_CARRIER_SIZE)
        return 0;
    if (memcmp(record, "AERUN001", 8))
        return 0;
    for (unsigned i = 12; i < 32; ++i)
        if (record[i])
            return 0;
    struct ar_startup candidate = {0};
    for (unsigned i = 0; i < 4; ++i)
        candidate.count |= (uint32_t)record[8 + i] << (8 * i);
    memcpy(candidate.args, record + 32, sizeof candidate.args);
    if (!slots_valid(&candidate))
        return 0;
    *output = candidate;
    return 1;
}
enum ar_action ar_select(const struct ar_startup *startup,
                         struct ar_invocation *output)
{
    if (!output || !slots_valid(startup))
        return AR_INVALID_STARTUP;
    if (startup->count == 2 && !strcmp(startup->args[1], "--help"))
        return AR_HELP;
    if (startup->count == 2 && !strcmp(startup->args[1], "--version"))
        return AR_VERSION;
    unsigned first = 1;
    if (startup->count > 1 && !strcmp(startup->args[1], "--"))
        ++first;
    else if (startup->count > 1 && startup->args[1][0] == '-')
        return AR_USAGE;
    if (first >= startup->count || startup->count - first > AR_CHILD_ARGS)
        return AR_USAGE;
    if (!startup->args[first][0] || strchr(startup->args[first], '/'))
        return AR_USAGE;
    struct ar_invocation candidate = {0};
    candidate.count = startup->count - first;
    for (unsigned i = 0; i < candidate.count; ++i)
        memcpy(candidate.args[i], startup->args[first + i], AR_SLOT_SIZE);
    memcpy(candidate.environment, "LC_ALL=C", 9);
    *output = candidate;
    return AR_LAUNCH;
}
