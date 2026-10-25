#define _GNU_SOURCE
#include <errno.h>
#include <signal.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

static unsigned brk_calls, denied;
static int deny_error;
static void *denied_page;
uintptr_t aether_test_brk(uintptr_t request)
{
    (void)request;
    brk_calls++;
    return (uintptr_t)-ENOSYS; /* Raw syscall convention, not libc errno. */
}
int __real_mprotect(void *, size_t, int);
int __wrap_mprotect(void *p, size_t n, int prot)
{
    if (deny_error) {
        if (n != 4096 || prot != (PROT_READ|PROT_WRITE)) _exit(11);
        denied_page = p;
        int error = deny_error;
        deny_error = 0;
        denied++;
        errno = error;
        return -1;
    }
    return __real_mprotect(p, n, prot);
}
static void fault(int sig, siginfo_t *info, void *ctx)
{
    (void)ctx;
    uintptr_t a = (uintptr_t)info->si_addr, p = (uintptr_t)denied_page;
    _exit(sig == SIGSEGV && info->si_code == SEGV_ACCERR &&
        p && a >= p && a-p < 4096 && denied == 1 ? 40 : 41);
}
int main(int argc, char **argv)
{
    if (argc != 2) return 10;
    if (!strcmp(argv[1], "enosys")) deny_error = ENOSYS;
    else if (!strcmp(argv[1], "eacces")) deny_error = EACCES;
    else if (strcmp(argv[1], "pass")) return 10;
    struct sigaction action = {0};
    action.sa_sigaction = fault;
    action.sa_flags = SA_SIGINFO;
    if (sigemptyset(&action.sa_mask) || sigaction(SIGSEGV, &action, 0)) return 12;
    int expected_error = deny_error;
    unsigned char *p = malloc(1024);
    if (expected_error) {
        if (p || errno != expected_error || denied != 1) { free(p); return 20; }
        p = malloc(1024);
    }
    if (!p || brk_calls != 2) { free(p); return 21; }
    memset(p, 0x6b, 1024);
    for (unsigned i = 0; i < 1024; i++)
        if (((volatile unsigned char *)p)[i] != 0x6b) return 22;
    free(p);
    static const char result[] = "AETHER ADAPTER ERRORS PASS\n";
    return write(1, result, sizeof result-1) == sizeof result-1 ? 0 : 23;
}
