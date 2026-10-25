#define _GNU_SOURCE
#include <errno.h>
#include <signal.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

static void *fault_address;
static int fault_code;
static void fault(int sig, siginfo_t *info, void *context)
{
    (void)context;
    _exit(sig == SIGSEGV && info->si_addr == fault_address &&
          info->si_code == fault_code ? 40 : 41);
}
int main(int argc, char **argv)
{
    if (argc != 2) return 10;
    int mode = !strcmp(argv[1], "pass") ? 0 : !strcmp(argv[1], "readonly-write") ? 1 :
        !strcmp(argv[1], "none-read") ? 2 : !strcmp(argv[1], "unmapped-read") ? 3 :
        !strcmp(argv[1], "skip-protection") ? 4 : -1;
    if (mode < 0 || sysconf(_SC_PAGESIZE) != 4096) return 11;
    unsigned char *p = mmap(0, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    if (p == MAP_FAILED) return 12;
    memset(p, 0x5a, 8192);
    if (mode) {
        struct sigaction action = {0};
        action.sa_sigaction = fault;
        action.sa_flags = SA_SIGINFO;
        if (sigemptyset(&action.sa_mask) || sigaction(SIGSEGV, &action, 0)) return 13;
        fault_address = p;
        fault_code = mode == 3 ? SEGV_MAPERR : SEGV_ACCERR;
        if (mode == 3) { if (munmap(p, 8192)) return 14; }
        else if (mode != 4 && mprotect(p, 8192, mode == 1 ? PROT_READ : PROT_NONE)) return 15;
        if (mode == 1 || mode == 4) *(volatile unsigned char *)p = 0x31;
        else { volatile unsigned char observed = *(volatile unsigned char *)p; (void)observed; }
        if (mode != 3 && munmap(p, 8192)) return 16;
        return 20; /* Access succeeded: fault oracle must reject. */
    }
    errno = 0;
    if (mprotect(p, 4096, 0x40000000) != -1 || errno != EINVAL) return 21;
    /* Failed request must leave both pages accessible and unchanged. */
    for (unsigned i = 0; i < 8192; i++)
        if (((volatile unsigned char *)p)[i] != 0x5a) return 22;
    /* musl rounds this one-byte request to the containing page. */
    if (mprotect(p + 1, 1, PROT_READ)) return 32;
    ((volatile unsigned char *)p)[4096] = 0x5a;
    if (mprotect(p, 8192, PROT_READ)) return 23;
    for (unsigned i = 0; i < 8192; i++)
        if (((volatile unsigned char *)p)[i] != 0x5a) return 24;
    if (mprotect(p + 4096, 4096, PROT_NONE)) return 25;
    errno = 0;
    if (write(1, p + 4096, 1) != -1 || errno != EFAULT) return 26;
    if (mprotect(p, 8192, PROT_READ|PROT_WRITE)) return 27;
    memset(p, 0x6b, 8192);
    for (unsigned i = 0; i < 8192; i++)
        if (((volatile unsigned char *)p)[i] != 0x6b) return 28;
    uintptr_t unmapped = (uintptr_t)p;
    if (munmap(p, 8192)) return 29;
    errno = 0;
    if (mprotect((void *)unmapped, 4096, PROT_READ) != -1 || errno != ENOMEM) return 30;
    static const char result[] = "AETHER PROTECTION PASS\n";
    return write(1, result, sizeof result - 1) == sizeof result - 1 ? 0 : 31;
}
