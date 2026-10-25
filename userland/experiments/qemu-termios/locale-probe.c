/* SPDX-License-Identifier: BSD-2-Clause */
#include <ctype.h>
#include <langinfo.h>
#include <locale.h>
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    int accepted = setlocale(LC_ALL, "") != NULL;
    if (printf("%d\t%s\t%zu\t%d\t%d\n", accepted, nl_langinfo(CODESET),
               (size_t)MB_CUR_MAX, !!isalpha(0xe9), toupper(0xe9)) < 0) {
        return 2;
    }
    return 0;
}
