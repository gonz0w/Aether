/* SPDX-License-Identifier: BSD-2-Clause */
#include <math.h>

int main(void)
{
    volatile double finite = 1.0;
    volatile double infinity = INFINITY;
    volatile double nan_value = NAN;
    return !(isnan(nan_value) && !isnan(finite) && !isnan(infinity) &&
             isinf(infinity) && !isinf(finite) && !isinf(nan_value));
}
