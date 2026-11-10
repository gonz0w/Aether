/* SPDX-License-Identifier: BSD-2-Clause */
#include "filesystem-runner.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

struct fixture {
    unsigned char carrier[AR_CARRIER_SIZE];
    struct ar_fs_io io;
    enum ar_fs_delivery delivery;
    struct ar_fs_child child;
    struct ar_fs_terminal terminal;
    int collection;
    unsigned admits, collects;
};
static enum ar_fs_delivery admit(void *context,
                                 const struct ar_invocation *invocation,
                                 const struct ar_fs_io *io,
                                 struct ar_fs_child *child)
{
    struct fixture *f = context;
    ++f->admits;
    memset(f->carrier, 0xa5, sizeof f->carrier);
    assert(invocation->count == 1 && !strcmp(invocation->args[0], "probe"));
    assert(!strcmp(invocation->environment, "LC_ALL=C"));
    assert(io->input_read == 17 && io->output_write == 27);
    *child = f->child;
    return f->delivery;
}
static int collect(void *context, struct ar_fs_child child,
                   struct ar_fs_terminal *terminal)
{
    struct fixture *f = context;
    ++f->collects;
    assert(child.slot == 2 && child.generation == 4);
    *terminal = f->terminal;
    return f->collection;
}
static const struct ar_fs_owner owner = {admit, collect};
static struct fixture fixture(const char *name)
{
    struct fixture f = {.io = {17, 27},
                        .delivery = AR_FS_ADMITTED,
                        .child = {2, 4},
                        .terminal = {{2, 4}, 1, 23, 1},
                        .collection = 1};
    memcpy(f.carrier, "AERUN001", 8);
    f.carrier[8] = 2;
    memcpy(f.carrier + 32, "aether-run", 11);
    memcpy(f.carrier + 64, name, strlen(name) + 1);
    return f;
}
static struct ar_fs_run check(struct fixture *f, enum ar_fs_state state,
                              unsigned code, unsigned admits, unsigned collects)
{
    struct ar_fs_run run = {0};
    ar_fs_run(&run, f->carrier, sizeof f->carrier, &f->io, &owner, f);
    assert(run.state == state && run.exit_status == code);
    ar_fs_run(&run, f->carrier, sizeof f->carrier, &f->io, &owner, f);
    assert(f->admits == admits && f->collects == collects);
    return run;
}
int main(void)
{
    struct fixture f = fixture("probe");
    check(&f, AR_FS_COMPLETE, 23, 1, 1);
    f = fixture("probe");
    f.terminal.cleanup_complete = 0;
    struct ar_fs_run failed = check(&f, AR_FS_CLEANUP_FAILED, 1, 1, 1);
    assert(failed.terminal.detail == 23 && failed.terminal.child.generation == 4);
    f = fixture("probe");
    f.terminal.kind = 2;
    check(&f, AR_FS_COMPLETE, 1, 1, 1);
    f = fixture("probe");
    f.terminal.child.generation = 3;
    check(&f, AR_FS_COLLECTION_UNCERTAIN, 1, 1, 1);
    f = fixture("probe");
    f.collection = 0;
    assert(check(&f, AR_FS_COLLECTION_UNCERTAIN, 1, 1, 1).child.generation == 4);
    f = fixture("probe");
    f.delivery = AR_FS_UNKNOWN;
    assert(check(&f, AR_FS_ADMISSION_UNCERTAIN, 1, 1, 0).child.generation == 4);
    f = fixture("probe");
    f.delivery = AR_FS_DENIED;
    check(&f, AR_FS_ADMISSION_UNCERTAIN, 1, 1, 0);
    f = fixture("probe");
    f.delivery = AR_FS_DENIED;
    f.child = (struct ar_fs_child){0};
    check(&f, AR_FS_REJECTED, 2, 1, 0);
    f = fixture("missing");
    check(&f, AR_FS_REJECTED, 2, 0, 0);
    f = fixture("probe");
    f.io.output_write = 0;
    check(&f, AR_FS_REJECTED, 2, 0, 0);
    f = fixture("probe");
    f.carrier[8] = 3;
    memcpy(f.carrier + 96, "argument", 9);
    check(&f, AR_FS_REJECTED, 2, 0, 0);
    f = fixture("/home/probe");
    check(&f, AR_FS_INVALID, 64, 0, 0);
    f = fixture("--help");
    check(&f, AR_FS_INVALID, 1, 0, 0);
    f = fixture("probe");
    f.carrier[223] = 1;
    check(&f, AR_FS_INVALID, 1, 0, 0);
    f = fixture("probe");
    f.child.slot = 3;
    check(&f, AR_FS_ADMISSION_UNCERTAIN, 1, 1, 0);
    f = fixture("probe");
    f.terminal.kind = 4;
    check(&f, AR_FS_COLLECTION_UNCERTAIN, 1, 1, 1);
    f = fixture("probe");
    f.terminal.detail = 256;
    check(&f, AR_FS_COMPLETE, 1, 1, 1);
    f = fixture("--");
    f.carrier[8] = 3;
    memcpy(f.carrier + 96, "probe", 6);
    check(&f, AR_FS_COMPLETE, 23, 1, 1);
    f = fixture("probe");
    f.child.generation = 16;
    check(&f, AR_FS_ADMISSION_UNCERTAIN, 1, 1, 0);
    f = fixture("probe");
    f.child.generation = 0;
    check(&f, AR_FS_ADMISSION_UNCERTAIN, 1, 1, 0);
    puts("PASS: 20 persistent runner host cases");
}
