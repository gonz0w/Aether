# SPDX-License-Identifier: BSD-2-Clause
"""Execute the actual fixture move() body with scripted trap outcomes."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLANG = Path('/opt/homebrew/Cellar/llvm@21/21.1.8/bin/clang')

HARNESS = r'''
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
static unsigned long input = 11, output = 22;
static int poisoned;
static unsigned char buffer[32];
struct event { unsigned long op; long result; unsigned offset; };
static struct event events[16];
static unsigned at, total, yields;
static int writing;
static long memtrap(unsigned long op, unsigned long cap, unsigned long a,
                    unsigned long b, unsigned long c) {
    assert(c == 0);
    if (op == 0x1fffe) {
        assert(cap == 0 && a == 0 && b == 0);
        yields++;
        return 0;
    }
#ifndef SESSION_CHANNEL_WAIT
    if (total == 0) {
        assert(op == 0x24001);
        at++;
        return -11;
    }
#endif
    assert(at < total);
    struct event e = events[at++];
    assert(op == e.op && cap == (writing ? output : input));
    if (op == 0x24004) {
        assert(a == 0 && b == 0);
    } else {
        assert(a == (uintptr_t)(buffer + e.offset));
        assert(b == (32 - e.offset > 16 ? 16 : 32 - e.offset));
        if (!writing && e.result > 0)
            for (long i = 0; i < e.result; ++i)
                buffer[e.offset + i] = (unsigned char)(e.offset + i);
    }
    return e.result;
}
'''
TAIL = r'''
int main(int argc, char **argv) {
    assert(argc == 2);
    unsigned mode = (unsigned)atoi(argv[1]);
    writing = mode == 1;
#ifdef SESSION_CHANNEL_WAIT
    unsigned long op = writing ? 0x24002 : 0x24001;
    events[0] = (struct event){op, 5, 0};
    events[1] = (struct event){op, -11, 5};
    events[2] = (struct event){0x24004, mode == 2 ? -4 : mode == 3 ? -13 : 0, 0};
    total = 3;
    if (mode < 2) {
        events[3] = (struct event){op, -11, 5}; // Spurious hint: still blocked.
        events[4] = (struct event){0x24004, 0, 0};
        events[5] = (struct event){op, 11, 5};
        events[6] = (struct event){op, -11, 16};
        events[7] = (struct event){0x24004, 0, 0};
        events[8] = (struct event){op, 16, 16};
        total = 9;
    } else if (mode == 4) {
        events[3] = (struct event){op, 0, 5}; // EOF after partial frame.
        total = 4;
    } else if (mode == 5) {
        events[3] = (struct event){op, -32, 5}; // Peer loss after hint.
        total = 4;
    }
    assert(move(buffer, 32, writing) == (mode < 2));
    assert(at == total && yields == 0);
    if (mode < 2) {
        assert(!poisoned);
        if (!writing)
            for (unsigned i = 0; i < 32; ++i) assert(buffer[i] == i);
    } else {
        assert(poisoned);
        unsigned before = at;
        assert(!move(buffer, 32, writing) && at == before);
    }
#else
    assert(!move(buffer, 32, 0));
    assert(poisoned && at == 100000 && yields == 100000);
#endif
    return 0;
}
'''


class SessionChannelWait(unittest.TestCase):
    def test_partial_rescan_and_fail_closed_transport(self):
        self.assertTrue(CLANG.is_file(), 'required pinned host C runner missing')
        sdk = subprocess.check_output(['xcrun', '--show-sdk-path'], text=True, timeout=10).strip()
        source = (ROOT / 'user/native-command/transport.h').read_text()
        body = source[source.index('static int move('):source.index('static int exchange(')]
        with tempfile.TemporaryDirectory(prefix='aether-channel-wait-') as directory:
            work = Path(directory)
            fixture = work / 'move.c'
            fixture.write_text(HARNESS + body + TAIL)
            for selected in (False, True):
                executable = work / ('wait' if selected else 'legacy')
                command = [str(CLANG), '--no-default-config', '-isysroot', sdk, '-std=c11', '-O2',
                           '-Wall', '-Wextra', '-Werror']
                if selected:
                    command += ['-DSESSION_CHANNEL_WAIT']
                compiled = subprocess.run(command + [str(fixture), '-o', str(executable)],
                                          capture_output=True, timeout=30)
                self.assertEqual(compiled.returncode, 0, compiled.stderr.decode())
                for case in range(6) if selected else (0,):
                    with self.subTest(selected=selected, case=case):
                        subprocess.run([str(executable), str(case)], check=True,
                                       capture_output=True, timeout=5)


if __name__ == '__main__':
    unittest.main()
