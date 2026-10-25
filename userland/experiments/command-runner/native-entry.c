/* SPDX-License-Identifier: BSD-2-Clause */
#include "native-io.h"
extern int bytecount_main(int, char **);
int main(int argc, char **argv)
{
    if (!native_bootstrap(1))
        return 120;
    return bytecount_main(argc, argv);
}
