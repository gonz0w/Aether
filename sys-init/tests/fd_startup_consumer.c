/* SPDX-License-Identifier: BSD-2-Clause */
/* Exact delivered C consumer with injected host observations, not native IPC.
 */
#include "fd-startup.h"
#include <stdio.h>
struct model {
  const unsigned char *frame;
  size_t offset;
  unsigned calls, reads, waits, closes, masks, restores;
  uint64_t memory;
  int64_t pid, parent;
};
static int64_t call(void *raw, uint64_t op, uint64_t cap, uint64_t a,
                    uint64_t b, uint64_t c) {
  struct model *m = raw;
  ++m->calls;
  if (op == 0x1000e) {
    if (!a || c != 8)
      return -22;
    if (!cap) {
      if (!b || *(uint64_t *)(uintptr_t)a != UINT64_MAX)
        return -22;
      *(uint64_t *)(uintptr_t)b = 0x1234;
      ++m->masks;
      return 0;
    }
    if (cap != 2 || b || *(uint64_t *)(uintptr_t)a != 0x1234)
      return -22;
    ++m->restores;
    return 0;
  }
  if (op == 0x10027 || op == 0x1006e) {
    if (cap || a || b || c || m->masks != m->restores + 1U)
      return -5;
    return op == 0x10027 ? m->pid : m->parent;
  }
  if (op == 0x24003) {
    if (a || b || c || cap != (m->closes ? 72U : 71U))
      return -22;
    ++m->closes;
    return cap == 71 ? -9 : -5;
  }
  if (op == 0x24004) {
    if (cap != 71 || a || b || c)
      return -22;
    ++m->waits;
    return 0;
  }
  if (op != 0x24001 || cap != 71 || !a || !b || b > 16 || c ||
      m->masks != m->restores + 1U)
    return -5;
  if (++m->reads % 3U == 0)
    return -11;
  size_t count = (size_t)b;
  if (count > 7)
    count = 7;
  if (count > AEFD_STARTUP_BYTES - m->offset)
    count = AEFD_STARTUP_BYTES - m->offset;
  memcpy((void *)(uintptr_t)a, m->frame + m->offset, count);
  m->offset += count;
  return (int64_t)count;
}
static int consume(const unsigned char frame[304], const unsigned char obs[16],
                   int valid, int early) {
  struct aefd_startup boot = {0};
  struct model m = {.frame = frame,
                    .memory = aefd_word(obs, 0),
                    .pid = aether_fs_session_u32(obs + 8),
                    .parent = aether_fs_session_u32(obs + 12)};
  int64_t result = aefd_startup_start(
      &boot, call, &m, (struct aefd_startup_auxv){m.memory, 71, 72});
  if (m.masks != 1 || m.restores != 1 || !m.waits ||
      m.offset != (early ? 16U : 304U))
    return 1;
  for (size_t i = 0; i < sizeof boot.scratch; ++i)
    if (boot.scratch[i])
      return 2;
  if (valid) {
    if (result || boot.phase != 2 || boot.context.state != 1 ||
        boot.identity.slot != aether_fs_session_u32(frame + 32) ||
        boot.identity.epoch != aether_fs_session_u32(frame + 36) ||
        boot.context.client.generation != aefd_word(frame + 48, 1) || m.closes)
      return 3;
    for (unsigned i = 0; i < 7; ++i)
      if (boot.context.native.sources[i].reference !=
          aether_fs_session_u32(frame + 176U + i * 16U))
        return 4;
    for (unsigned i = 0; i < 2; ++i)
      if (boot.context.native.generations[i] !=
          aether_fs_session_u32(frame + 288U + i * 4U))
        return 5;
    /* Local borrowed-channel closure only; no source/native settlement claim.
     */
    aefd_client_abort(&boot.context.client);
    aefd_client_abort(&boot.context.client);
    if (boot.context.client.closed.input != -9 ||
        boot.context.client.closed.output != -5)
      return 6;
  } else if (result != -22 || boot.phase != 3 || boot.identity.slot ||
             boot.context.state || !boot.close_attempted ||
             boot.closed.input != -9 || boot.closed.output != -5)
    return 7;
  if (m.closes != 2)
    return 8;
  unsigned calls = m.calls;
  if (aefd_startup_start(&boot, call, &m,
                         (struct aefd_startup_auxv){m.memory, 71, 72}) != -16 ||
      calls != m.calls)
    return 9;
  return 0;
}
int main(int argc, char **argv) {
  if (argc != 2)
    return 64;
  FILE *in = fopen(argv[1], "rb");
  if (!in)
    return 1;
  unsigned char record[320];
  unsigned valid = 0, bad = 0;
  size_t count;
  const unsigned offsets[] = {0, 8, 12, 16, 40, 56, 64, 188, 288, 296, 300};
  while ((count = fread(record, 1, sizeof record, in)) == sizeof record) {
    int error = consume(record + 16, record, 1, 0);
    if (error) {
      fprintf(stderr, "valid frame %u error %d\n", valid, error);
      return 2;
    }
    ++valid;
    for (size_t j = 0; j < sizeof offsets / sizeof offsets[0]; ++j) {
      unsigned char frame[304];
      memcpy(frame, record + 16, sizeof frame);
      unsigned offset = offsets[j];
      if (offset == 56)
        memset(frame + offset, 0, 8);
      else if (offset == 288)
        memset(frame + offset, 0, 4);
      else
        frame[offset] ^= 1;
      error = consume(frame, record, 0, offset < 16);
      if (error) {
        fprintf(stderr, "corrupt frame %u offset %u error %d\n", valid, offset,
                error);
        return 3;
      }
      ++bad;
    }
  }
  int failed = count != 0 || ferror(in);
  if (fclose(in) || failed || valid != 138 || bad != 1518)
    return 4;
  fprintf(stderr, "Rust producer/exact C startup: %u valid/%u corrupt pass\n",
          valid, bad);
  return 0;
}
