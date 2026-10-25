/* SPDX-License-Identifier: BSD-2-Clause */
/* Exact opt-in codec interoperability; supplied observations are host fixtures.
 */
#include "fd-fork-frame.h"
#include <stdio.h>
int main(int argc, char **argv) {
  if (argc != 4)
    return 64;
  FILE *in = fopen(argv[1], "rb"), *out = fopen(argv[2], "wb"),
       *errors = fopen(argv[3], "rb");
  if (!in || !out || !errors)
    return 1;
  unsigned char record[680], ready[32];
  unsigned count = 0, denials = 0, negatives = 0;
  size_t got;
  while ((got = fread(record, 1, sizeof record, in)) == sizeof record) {
    struct aefd_startup_auxv parent = {aefd_word(record, 0), 71, 72};
    struct aefd_startup_auxv child = {aefd_word(record, 2), 81, 82};
    long pid = (long)aefd_word(record, 1),
         child_pid = (long)aefd_word(record, 3);
    uint64_t sequence = aefd_word(record, 4);
    const unsigned char *request = record + 40, *startup = record + 344;
    struct aefd_fork_view view;
    struct aether_fs_session_identity identity;
    int64_t result = 999;
    if (!aefd_fork_decode(request, 304, parent, pid, 7, &view) ||
        view.sequence != sequence ||
        !aefd_fork_child_match(request, 304, parent, pid, startup, 304, child,
                               child_pid, &identity) ||
        identity.slot < 2 ||
        !aefd_fork_parent_reply(record + 648, 32, sequence, child_pid,
                                &result) ||
        result != child_pid ||
        !aefd_fork_ready_encode(ready, 32, sequence, child_pid) ||
        fwrite(ready, 1, sizeof ready, out) != sizeof ready)
      return 2;
    const unsigned offsets[] = {0, 8, 12, 40, 72, 115, 188, 288};
    for (size_t j = 0; j < sizeof offsets / sizeof offsets[0]; ++j) {
      unsigned char bad[304];
      memcpy(bad, request, sizeof bad);
      bad[offsets[j]] ^= 1;
      view.sequence = 999;
      if (aefd_fork_decode(bad, sizeof bad, parent, pid, 7, &view) ||
          view.sequence != 999)
        return 3;
      ++denials;
    }
    ++count;
  }
  if (got || ferror(in) || fclose(in) || fclose(out) || count != 135 ||
      denials != 1080)
    return 4;
  for (int64_t error = -1; error >= -4095; --error) {
    unsigned char raw[32];
    int64_t result = 999;
    if (fread(raw, 1, sizeof raw, errors) != sizeof raw ||
        !aefd_fork_parent_reply(raw, sizeof raw, 1, -11, &result) ||
        result != error)
      return 5;
    result = 999;
    if (aefd_fork_parent_reply(raw, sizeof raw, 1, 10, &result) ||
        result != 999)
      return 6;
    ++negatives;
  }
  if (fgetc(errors) != EOF || ferror(errors) || fclose(errors) ||
      negatives != 4095)
    return 7;
  fprintf(stderr,
          "fork codec:135 children/1080 corrupt requests/4095 refusals pass\n");
  return 0;
}
