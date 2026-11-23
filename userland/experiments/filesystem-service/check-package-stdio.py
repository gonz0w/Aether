#!/usr/bin/env python3
# SPDX-License-Identifier: BSD-2-Clause
"""Exercise the actual closed bytecount startup FILE admission."""
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    text = (HERE / 'fd-libc-bindings.c').read_text()
    start = text.index('int64_t aefd_shell_bytecount_stdio(void)')
    end = text.index('\n#endif', start)
    body = text[start:end]
    harness = """
#include <assert.h>
#include <stdint.h>
#include <string.h>
#define AEFD_BINDINGS_COUNT 16
#define AEFD_BIND_FILE 3
struct aefd_binding { unsigned char kind, selector, cloexec, reserved; };
static struct {
    unsigned phase;
    struct { unsigned slot; } identity;
    struct { uint16_t note_writers; struct { struct aefd_binding slots[16]; } map; } context;
} shell;
BODY
static void reset(void) {
    memset(&shell,0,sizeof shell);
    shell.phase=2; shell.identity.slot=2;
    shell.context.map.slots[0]=(struct aefd_binding){3,3,0,0};
    shell.context.map.slots[1]=(struct aefd_binding){3,4,0,0};
}
int main(void) {
    reset(); assert(aefd_shell_bytecount_stdio()==0);
    assert(shell.context.note_writers==(1U<<4));
    assert(aefd_shell_bytecount_stdio()==-13);
    for(unsigned fd=0;fd<2;fd++) {
        for(unsigned kind=0;kind<6;kind++) {
            if(kind==3)continue;
            reset(); shell.context.map.slots[fd].kind=kind;
            assert(aefd_shell_bytecount_stdio()==-13 && !shell.context.note_writers);
        }
        for(unsigned selector=0;selector<16;selector++) {
            if(selector==fd+3)continue;
            reset(); shell.context.map.slots[fd].selector=selector;
            assert(aefd_shell_bytecount_stdio()==-13 && !shell.context.note_writers);
        }
    }
    for(unsigned fd=2;fd<16;fd++) {
        reset(); shell.context.map.slots[fd]=(struct aefd_binding){3,5,0,0};
        assert(aefd_shell_bytecount_stdio()==-13 && !shell.context.note_writers);
    }
    reset(); shell.identity.slot=1; assert(aefd_shell_bytecount_stdio()==-13);
    reset(); shell.phase=1; assert(aefd_shell_bytecount_stdio()==-13);
}
""".replace('BODY', body)
    with tempfile.TemporaryDirectory(prefix='aether-bytecount-stdio-') as work:
        source = Path(work) / 'stdio.c'
        binary = Path(work) / 'stdio'
        source.write_text(harness)
        subprocess.run(['/usr/bin/cc', '-std=c17', '-O2', '-Wall', '-Wextra', '-Werror',
                        str(source), '-o', str(binary)], check=True, timeout=30,
                       env={'PATH':'/usr/bin:/bin','TMPDIR':work})
        subprocess.run([str(binary)], check=True, timeout=5)
    print('PASS: actual bytecount startup binding, denied maps, roles and replay')


if __name__ == '__main__':
    main()
