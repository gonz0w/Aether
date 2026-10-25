/* SPDX-License-Identifier: BSD-2-Clause */
/* Observed terminal mapping only. This does not infer admission or recovery
 * from a numeric exit, and never manufactures POSIX signal encoding.
 */
static unsigned runner_result(unsigned kind, unsigned detail, int cleanup_ok)
{
    return cleanup_ok && kind == 1 && detail <= 255 ? detail : 1;
}

static int result_policy_probe(void)
{
    return runner_result(1, 0, 1) == 0 && runner_result(1, 255, 1) == 255 &&
           runner_result(1, 256, 1) == 1 && runner_result(1, ~0u, 1) == 1 &&
           runner_result(2, 134, 1) == 1 && runner_result(0, 0, 1) == 1 &&
           runner_result(1, 0, 0) == 1;
}
