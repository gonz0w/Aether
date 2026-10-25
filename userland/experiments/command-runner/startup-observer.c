/* SPDX-License-Identifier: BSD-2-Clause */
/* Independent child witness: expected strings are not derived from the parent.
 */
#include "native-io.h"
#include <string.h>
extern char **environ;
extern int bytecount_main(int, char **);
int main(int argc, char **argv)
{
    if (!native_bootstrap(1))
        return 120;
    if (argc != 4 || !argv || !argv[0] || !argv[1] || !argv[2] || !argv[3] ||
        argv[4] || strcmp(argv[0], "bytecount") ||
        strcmp(argv[1], "--decimal") || strcmp(argv[2], "") ||
        strcmp(argv[3], "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx") || !environ ||
        !environ[0] || strcmp(environ[0], "LC_ALL=C") || environ[1])
        return 80;
    /* The real utility accepts two arguments. This observer alone consumes the
     * wider test vector; it does not claim bytecount accepts extra arguments.
     */
    char *command[] = {argv[0], argv[1], NULL};
    return bytecount_main(2, command);
}
