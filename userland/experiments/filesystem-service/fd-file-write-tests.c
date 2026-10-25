/* SPDX-License-Identifier: BSD-2-Clause */
/* Host-only buffers and stdio. No native stack-fit claim. */
#include "fd-facade.h"
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#define CHECK(x, marker)                                                       \
    do {                                                                       \
        if (!(x)) {                                                            \
            fprintf(stderr, "%s:%d\n", marker, __LINE__);                      \
            exit(1);                                                           \
        }                                                                      \
    } while (0)
struct script {
    unsigned char input[128], output[4160];
    size_t received, sent, stop_in, stop_out, chunk;
    unsigned closes, calls, waits;
    int again;
};
static unsigned char workspace[4096];
static int64_t rd(void *p, unsigned char *out, size_t length)
{
    struct script *s = p;
    ++s->calls;
    if (s->again)
        return -11;
    if (s->received == s->stop_in)
        return 0;
    size_t count = s->stop_in - s->received;
    if (count > length)
        count = length;
    if (count > s->chunk)
        count = s->chunk;
    memcpy(out, s->input + s->received, count);
    s->received += count;
    return (int64_t)count;
}
static int64_t wr(void *p, const unsigned char *in, size_t length)
{
    struct script *s = p;
    ++s->calls;
    if (s->again)
        return -11;
    if (s->sent == s->stop_out)
        return -5;
    size_t count = s->stop_out - s->sent;
    if (count > length)
        count = length;
    if (count > s->chunk)
        count = s->chunk;
    memcpy(s->output + s->sent, in, count);
    s->sent += count;
    return (int64_t)count;
}
static int wait_io(void *p, int writing)
{
    struct script *s = p;
    (void)writing;
    ++s->waits;
    return 0;
}
static struct aefd_close_result close_io(void *p)
{
    struct script *s = p;
    ++s->closes;
    return (struct aefd_close_result){-7, -8};
}
static void reply(unsigned char raw[128], int64_t status, uint64_t count,
                  uint64_t flags, uint64_t offset, uint64_t txg,
                  uint64_t staged, uint64_t kind, int64_t value)
{
    memset(raw, 0, 128);
    memcpy(raw, "AEFW0001", 8);
    aefd_put(raw, 1, (uint64_t)status);
    aefd_put(raw, 2, 31);
    aefd_put(raw, 3, 1);
    aefd_put(raw, 4, count);
    aefd_put(raw, 5, 64);
    aefd_put(raw + 64, 0, flags);
    aefd_put(raw + 64, 1, offset);
    aefd_put(raw + 64, 2, txg);
    aefd_put(raw + 64, 3, staged);
    if (flags & 16U) {
        aefd_put(raw + 64, 4, (uint64_t)-9);
        aefd_put(raw + 64, 5, (uint64_t)-5);
    }
    aefd_put(raw + 64, 6, kind);
    aefd_put(raw + 64, 7, (uint64_t)value);
}
static struct aefd_client connect(struct script *s)
{
    struct aefd_client c;
    struct aefd_io io = {s, rd, wr, wait_io, close_io};
    CHECK(aefd_client_init(&c, io, workspace, 31), "FILE_C_INIT");
    return c;
}
static void unit(void)
{
    unsigned char valid[128], bad[128];
    struct aefd_write_receipt out, saved;
    reply(valid, 0, 4, 14, 3, 8, 4, 0, 0);
    CHECK(aefd_write_decode(valid, valid + 64, 64, 31, 1, 4, &out),
          "FILE_C_RECEIPT");
    CHECK(out.status == 0 && out.count == 4 && out.offset == 3 && out.txg == 8,
          "FILE_C_RECEIPT");
    for (unsigned lane = 0; lane < 16; ++lane) {
        memcpy(bad, valid, 128);
        if (lane == 0)
            bad[0] ^= 1U;
        else
            aefd_put(bad + (lane >= 8 ? 64 : 0), lane % 8U,
                     lane == 8    ? 46
                     : lane == 9  ? UINT64_MAX
                     : lane == 10 ? 0
                     : lane == 11 ? 3
                                  : 99);
        memset(&out, 0xa5, sizeof out);
        memcpy(&saved, &out, sizeof out);
        CHECK(!aefd_write_decode(bad, bad + 64, 64, 31, 1, 4, &out),
              "FILE_C_RECEIPT_MATRIX");
        CHECK(!memcmp(&out, &saved, sizeof out), "FILE_C_ATOMIC_PUBLICATION");
    }
    CHECK(!aefd_write_decode(valid, valid + 64, 63, 31, 1, 4, &out),
          "FILE_C_RECEIPT_MATRIX");
    for (uint64_t tag = 1; tag <= 4; ++tag) {
        uint64_t txg = tag == 3 ? 5U : 0U;
        uint64_t staged = tag == 2 || tag == 3 ? 4U : 0U;
        reply(valid, -5, 0, tag | 24U, 3, txg, staged, 12, -5);
        CHECK(aefd_write_decode(valid, valid + 64, 64, 31, 1, 4, &out),
              "FILE_C_PROGRESS");
        CHECK(out.flags == (tag | 24U) && out.txg == txg &&
                  out.staged == staged,
              "FILE_C_PROGRESS");
        aefd_put(valid + 64, 3, 2);
        CHECK(!aefd_write_decode(valid, valid + 64, 64, 31, 1, 4, &out),
              "FILE_C_NO_PARTIAL_SUCCESS");
    }
    for (uint64_t kind = 10; kind <= 11; ++kind) {
        reply(valid, -5, 0, 29, 3, 0, 0, kind, kind == 11 ? INT64_MIN : 0);
        CHECK(aefd_write_decode(valid, valid + 64, 64, 31, 1, 4, &out),
              "FILE_C_UNKNOWN");
        CHECK(out.error_kind == kind &&
                  out.error_value == (kind == 11 ? INT64_MIN : 0),
              "FILE_C_RAW_CAUSE");
    }
    reply(valid, -INT64_C(2147483647), 0, 26, 3, 0, 4, 12,
          -INT64_C(2147483647));
    CHECK(aefd_write_decode(valid, valid + 64, 64, 31, 1, 4, &out),
          "FILE_C_ERRNO_BOUND");
    aefd_put(valid, 1, (uint64_t)-INT64_C(2147483648));
    aefd_put(valid + 64, 7, (uint64_t)-INT64_C(2147483648));
    CHECK(!aefd_write_decode(valid, valid + 64, 64, 31, 1, 4, &out),
          "FILE_C_ERRNO_BOUND");
    const int64_t errors[17] = {0,   -9, -24, -22, -75, -5, -5,  -22, -5,
                                -28, -5, -5,  0,   -9,  -9, -16, -9};
    for (uint64_t kind = 1; kind <= 16; ++kind) {
        if (kind >= 10 && kind <= 12)
            continue;
        reply(valid, errors[kind], 0, 0, 0, 0, 0, kind,
              kind == 13 ? INT32_MIN : 0);
        CHECK(aefd_write_decode(valid, valid + 64, 64, 31, 1, 4, &out),
              "FILE_C_CAUSE");
        CHECK(out.error_kind == kind &&
                  out.error_value == (kind == 13 ? INT32_MIN : 0),
              "FILE_C_RAW_CAUSE");
    }
    reply(valid, -5, 0, 29, 3, 0, 0, 11, INT64_MIN);
    aefd_put(valid + 64, 4, (uint64_t)INT64_MIN);
    aefd_put(valid + 64, 5, (uint64_t)INT64_MAX);
    CHECK(aefd_write_decode(valid, valid + 64, 64, 31, 1, 4, &out) &&
              out.source_cleanup.input == INT64_MIN &&
              out.source_cleanup.output == INT64_MAX,
          "FILE_C_RAW_CLOSES");
    struct script s = {.stop_in = 128, .stop_out = 4160, .chunk = 64};
    reply(s.input, -5, 0, 26, 3, 0, 4, 12, -5);
    struct aefd_client c = connect(&s);
    struct aefd_write_result result;
    CHECK(aefd_client_write(&c, 0, (const unsigned char *)"data", 4, &result) ==
              1,
          "FILE_C_TERMINAL_RECEIPT");
    CHECK(result.observation == AEFD_WRITE_REMOTE && result.status == -5 &&
              result.remote.txg == 0 && result.remote.staged == 4,
          "FILE_C_TERMINAL_RECEIPT");
    CHECK(result.remote.source_cleanup.input == -9 &&
              result.remote.source_cleanup.output == -5,
          "FILE_C_SOURCE_CLOSES");
    CHECK(result.file_closed && result.file_cleanup.input == -7 &&
              result.file_cleanup.output == -8 && s.closes == 1,
          "FILE_C_SEPARATE_CLOSES");
    CHECK(!c.live && !c.workspace && result.generation == 31 &&
              result.sequence == 1 && result.requested == 4,
          "FILE_C_CONTEXT");
    CHECK(aefd_client_write(&c, 0, (const unsigned char *)"data", 4, &result) ==
                  -1 &&
              result.observation == AEFD_WRITE_NOT_SENT,
          "FILE_C_NO_REPLAY");
    CHECK(s.closes == 1, "FILE_C_NO_REPLAY");
    unsigned char data[4096];
    memset(data, 0x5a, sizeof data);
    s = (struct script){.stop_in = 128, .stop_out = 4160, .chunk = 7};
    reply(s.input, 0, 4096, 14, 0, 7, 4096, 0, 0);
    c = connect(&s);
    CHECK(aefd_client_write(&c, 0, data, sizeof data, &result) == 1 && c.live &&
              result.remote.count == 4096 && s.sent == 4160 &&
              !memcmp(s.output + 64, data, sizeof data),
          "FILE_C_MAXIMUM");
    aefd_client_abort(&c);
    for (unsigned lane = 0; lane < 16; ++lane) {
        s = (struct script){.stop_in = 128, .stop_out = 4160, .chunk = 7};
        reply(s.input, 0, 4, 14, 0, 7, 4, 0, 0);
        aefd_put(s.input + (lane >= 8 ? 64 : 0), lane % 8U,
                 lane == 10 ? 0 : UINT64_MAX);
        c = connect(&s);
        CHECK(aefd_client_write(&c, 0, data, 4, &result) == -1 &&
                  result.observation == AEFD_WRITE_UNKNOWN &&
                  !result.remote.flags && !result.remote.count && s.closes == 1,
              "FILE_C_MALFORMED_UNKNOWN");
    }
    for (size_t prefix = 0; prefix < 4160; ++prefix) {
        s = (struct script){.stop_in = 128, .stop_out = prefix, .chunk = 64};
        reply(s.input, 0, 4096, 14, 0, 7, 4096, 0, 0);
        c = connect(&s);
        CHECK(aefd_client_write(&c, 0, data, sizeof data, &result) == -1,
              "FILE_C_SEND_LOSS");
        CHECK(result.observation == AEFD_WRITE_UNKNOWN &&
                  !result.remote.flags && result.file_closed &&
                  s.sent == prefix,
              "FILE_C_SEND_LOSS");
        CHECK(s.closes == 1, "FILE_C_NO_REPLAY");
    }
    for (size_t prefix = 0; prefix < 128; ++prefix) {
        s = (struct script){.stop_in = prefix, .stop_out = 4160, .chunk = 7};
        reply(s.input, 0, 4, 14, 0, 7, 4, 0, 0);
        c = connect(&s);
        CHECK(aefd_client_write(&c, 0, data, 4, &result) == -1,
              "FILE_C_RECEIVE_LOSS");
        CHECK(result.observation == AEFD_WRITE_UNKNOWN &&
                  !result.remote.flags && s.received == prefix && s.closes == 1,
              "FILE_C_RECEIVE_LOSS");
    }
    s = (struct script){.stop_in = 128, .stop_out = 4160, .chunk = 1};
    reply(s.input, 0, 4, 14, 0, 7, 4, 0, 0);
    c = connect(&s);
    CHECK(aefd_client_write(&c, 0, data, 4, &result) == 1 && c.live,
          "FILE_C_PARTIAL_TRANSFER");
    CHECK(s.sent == 128 && s.received == 128 && !memcmp(s.output + 64, data, 4),
          "FILE_C_PARTIAL_TRANSFER");
    aefd_client_abort(&c);
    s = (struct script){
        .stop_in = 128, .stop_out = 4160, .chunk = 64, .again = 1};
    c = connect(&s);
    CHECK(aefd_client_write(&c, 0, data, 4, &result) == -1 &&
              s.calls == AEFD_IO_BUDGET && s.waits == AEFD_IO_BUDGET,
          "FILE_C_BUDGET");
    s = (struct script){.stop_in = 128, .stop_out = 4160, .chunk = 64};
    c = connect(&s);
    CHECK(aefd_client_write(&c, 16, data, 4, &result) == 0 && !s.calls &&
              result.observation == AEFD_WRITE_NOT_SENT,
          "FILE_C_LOCAL");
    CHECK(aefd_client_write(&c, 0, data, 0, &result) == 0 && !s.calls,
          "FILE_C_LOCAL");
    const uint64_t args[4] = {0, 0, 0, 0};
    struct aefd_reply regular;
    CHECK(aefd_client_exchange(&c, 11, args, NULL, 0, &regular) == 0 &&
              !s.calls,
          "FILE_C_GENERIC_DENY");
    CHECK(aefd_file_open_home(&c, (const unsigned char *)"a/b", 3, 2, 0) ==
                  -22 &&
              !s.calls,
          "FILE_C_HOME_COMPONENT");
    aefd_client_abort(&c);
    puts("FILE_C_UNIT_PASS receipt matrix / 4160 send prefixes / 128 receive "
         "prefixes");
}
static void emit(void)
{
    unsigned char h[64], body[64] = {0};
    const uint64_t args[5][4] = {
        {0, 4, 2, 0}, {0, 4, 0, 0}, {0, 0, 0, 0}, {0, 4, 0, 0}, {0, 0, 0, 0}};
    const uint64_t ops[5] = {10, 11, 3, 2, 5};
    for (size_t i = 0; i < 5; ++i) {
        CHECK(aefd_request(h, 31, i + 1, ops[i], args[i]), "FILE_C_EMIT");
        CHECK(fwrite(h, 1, 64, stdout) == 64, "FILE_C_EMIT");
        if (i < 2) {
            memcpy(body, i ? "home" : "data", 4);
            CHECK(fwrite(body, 1, 64, stdout) == 64, "FILE_C_EMIT");
        }
    }
}
static void verify(const char *path)
{
    FILE *in = fopen(path, "rb");
    CHECK(in, "FILE_C_VERIFY");
    unsigned char header[64], body[64];
    const uint64_t ops[5] = {10, 11, 3, 2, 5};
    for (size_t i = 0; i < 5; ++i) {
        CHECK(fread(header, 1, 64, in) == 64, "FILE_C_VERIFY");
        if (i == 1) {
            struct aefd_write_receipt r;
            CHECK(fread(body, 1, 64, in) == 64 &&
                      aefd_write_decode(header, body, 64, 31, i + 1, 4, &r),
                  "FILE_C_RUST_RECEIPT");
            CHECK(r.count == 4 && r.flags == 14 && r.txg == 1,
                  "FILE_C_RUST_RECEIPT");
        } else {
            struct aefd_reply r;
            CHECK(aefd_decode(header, 64, 31, i + 1, ops[i], i == 3 ? 4 : 0,
                              &r) &&
                      !r.status,
                  "FILE_C_RUST_REPLY");
            if (r.body) {
                CHECK(fread(body, 1, 64, in) == 64 && !memcmp(body, "home", 4),
                      "FILE_C_RUST_DATA");
            }
        }
    }
    CHECK(fgetc(in) == EOF && !fclose(in), "FILE_C_VERIFY");
    puts("FILE_C_RUST_INTEROP_PASS");
}
static void errors(const char *path)
{
    FILE *in = fopen(path, "rb");
    CHECK(in, "FILE_C_RUST_ERRORS");
    const uint64_t tags[4] = {4, 1, 2, 3};
    const uint64_t txgs[4] = {0, 0, 0, 17};
    const uint64_t staged[4] = {0, 0, 1, 1};
    for (size_t i = 0; i < 4; ++i) {
        unsigned char h[64], b[64];
        struct aefd_write_receipt r;
        CHECK(fread(h, 1, 64, in) == 64 && fread(b, 1, 64, in) == 64 &&
                  aefd_write_decode(h, b, 64, 31, 2, 1, &r),
              "FILE_C_RUST_ERRORS");
        CHECK(r.status == (i == 1 ? -28 : -5) && !r.count &&
                  r.flags == (tags[i] | 24U) && r.offset == 2 &&
                  r.txg == txgs[i] && r.staged == staged[i] &&
                  !r.source_cleanup.input && !r.source_cleanup.output &&
                  r.error_kind == 12 && r.error_value == r.status,
              "FILE_C_RUST_ERRORS");
    }
    CHECK(fgetc(in) == EOF && !fclose(in), "FILE_C_RUST_ERRORS");
    puts("FILE_C_RUST_ERRORS_PASS");
}
static int64_t pipe_read(void *p, unsigned char *b, size_t n)
{
    (void)p;
    size_t got = fread(b, 1, n, stdin);
    return (int64_t)got;
}
static int64_t pipe_write(void *p, const unsigned char *b, size_t n)
{
    (void)p;
    size_t put = fwrite(b, 1, n, stdout);
    CHECK(!fflush(stdout), "FILE_C_PIPE");
    return (int64_t)put;
}
static int pipe_wait(void *p, int writing)
{
    (void)p;
    (void)writing;
    return -5;
}
static struct aefd_close_result pipe_close(void *p)
{
    (void)p;
    int input = fclose(stdin);
    int output = fclose(stdout);
    return (struct aefd_close_result){input, output};
}
static void live(void)
{
    struct aefd_client c;
    struct aefd_io io = {NULL, pipe_read, pipe_write, pipe_wait, pipe_close};
    CHECK(aefd_client_init(&c, io, workspace, 31), "FILE_C_LIVE");
    int64_t fd =
        aefd_file_open_home(&c, (const unsigned char *)"data", 4, 2, 0);
    CHECK(fd == 0, "FILE_C_LIVE_OPEN");
    struct aefd_write_result r;
    CHECK(aefd_file_write(&c, 0, (const unsigned char *)"home", 4, &r) == 4 &&
              r.observation == AEFD_WRITE_REMOTE,
          "FILE_C_LIVE_WRITE");
    CHECK(aefd_file_seek(&c, 0, 0, 0) == 0, "FILE_C_LIVE_SEEK");
    unsigned char out[4];
    CHECK(aefd_file_read(&c, 0, out, 4) == 4 && !memcmp(out, "home", 4),
          "FILE_C_LIVE_READ");
    CHECK(aefd_file_close(&c, 0) == 0, "FILE_C_LIVE_CLOSE");
    aefd_client_abort(&c);
}
static void live_error(void)
{
    struct aefd_client c;
    struct aefd_io io = {NULL, pipe_read, pipe_write, pipe_wait, pipe_close};
    CHECK(aefd_client_init(&c, io, workspace, 31), "FILE_C_LIVE");
    CHECK(aefd_file_open_home(&c, (const unsigned char *)"data", 4, 2, 0) == 0,
          "FILE_C_LIVE_OPEN");
    struct aefd_write_result r;
    CHECK(aefd_file_write(&c, 0, (const unsigned char *)"home", 4, &r) == -5 &&
              r.observation == AEFD_WRITE_REMOTE && r.remote.flags == 26 &&
              !r.remote.txg && r.remote.staged == 4 && !r.remote.count &&
              !r.remote.source_cleanup.input &&
              !r.remote.source_cleanup.output && r.file_closed &&
              !r.file_cleanup.input && !r.file_cleanup.output && !c.live,
          "FILE_C_LIVE_TERMINAL");
}
int main(int argc, char **argv)
{
    if (argc == 1)
        unit();
    else if (!strcmp(argv[1], "emit"))
        emit();
    else if (argc == 3 && !strcmp(argv[1], "verify"))
        verify(argv[2]);
    else if (argc == 3 && !strcmp(argv[1], "errors"))
        errors(argv[2]);
    else if (!strcmp(argv[1], "live"))
        live();
    else if (!strcmp(argv[1], "live-error"))
        live_error();
    else
        return 64;
    return 0;
}
