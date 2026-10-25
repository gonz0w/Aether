#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <string.h>
#include <sys/time.h>
#include <unistd.h>

static volatile sig_atomic_t signalled;
static void tick(int sig) { (void)sig; signalled = 1; }
static char block[8192];
static char received[4096];

static int drain(int fd, size_t bytes, char value)
{
    while (bytes) {
        size_t n = bytes < sizeof received ? bytes : sizeof received;
        ssize_t got = read(fd, received, n);
        if (got <= 0) return -1;
        for (ssize_t i = 0; i < got; i++) if (received[i] != value) return -1;
        bytes -= (size_t)got;
    }
    return 0;
}
int main(int argc, char **argv)
{
    if (argc != 2 || (strcmp(argv[1], "pass") && strcmp(argv[1], "no-retry"))) return 10;
    int p[2];
    if (pipe2(p, O_NONBLOCK | O_CLOEXEC)) return 11;
    memset(block, 'f', sizeof block);
    size_t filled = 0;
    for (unsigned i = 0; i < 256; i++) {
        ssize_t n = write(p[1], block, 4096);
        if (n < 0) { if (errno != EAGAIN) return 12; break; }
        if (n != 4096) return 13;
        filled += (size_t)n;
    }
    if (filled < 8192 || filled >= 256u * 4096u) return 14;
    /* Free exactly one pipe page; a larger nonblocking write must be short. */
    if (drain(p[0], 4096, 'f')) return 15;
    memset(block, 'p', sizeof block);
    if (write(p[1], block, sizeof block) != 4096) return 16;
    if (drain(p[0], filled - 4096, 'f') || drain(p[0], 4096, 'p')) return 17;
    memset(block, 'f', sizeof block);
    for (size_t i = 0; i < filled; i += 4096)
        if (write(p[1], block, 4096) != 4096) return 18;
    if (fcntl(p[1], F_SETFL, 0)) return 19;
    struct sigaction action = {0};
    action.sa_handler = tick;
    if (sigemptyset(&action.sa_mask) || sigaction(SIGALRM, &action, 0)) return 21;
    struct itimerval timer = {{0, 10000}, {0, 10000}}, stopped = {0};
    if (setitimer(ITIMER_REAL, &timer, 0)) return 22;
    errno = 0;
    ssize_t n = write(p[1], "r", 1);
    int saved_errno = errno;
    if (setitimer(ITIMER_REAL, &stopped, 0)) return 23;
    if (n != -1 || saved_errno != EINTR || !signalled) return 24;
    /* Interrupted write copied nothing; drain original bytes and verify empty. */
    if (drain(p[0], filled, 'f')) return 25;
    if (read(p[0], received, 1) != -1 || errno != EAGAIN) return 26;
    if (!strcmp(argv[1], "pass") && write(p[1], "r", 1) != 1) return 27;
    n = read(p[0], received, 1);
    if (n != 1 || received[0] != 'r') return 20;
    if (read(p[0], received, 1) != -1 || errno != EAGAIN) return 28;
    if (close(p[0]) || close(p[1])) return 29;
    static const char result[] = "AETHER INTERRUPTED OUTPUT PASS\n";
    return write(1, result, sizeof result - 1) == sizeof result - 1 ? 0 : 30;
}
