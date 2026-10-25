# SPDX-License-Identifier: BSD-2-Clause
"""Independent observations for the UP-01 host ownership oracle."""
from copy import deepcopy
import unittest
from up01_model import Owner, Session, Reference, Rejected, READ, WRITE


class InheritedOwnership(unittest.TestCase):
    def setUp(self):
        self.owner = Owner()
        self.parent = self.owner.parent
        self.file = self.owner.open(self.parent, 3, READ | WRITE)

    def unchanged(self, operation):
        before = deepcopy(self.owner.__dict__)
        with self.assertRaises(Rejected):
            operation()
        self.assertEqual(self.owner.__dict__, before)

    def test_parent_child_share_position_but_separate_open_does_not(self):
        child, (ref,) = self.owner.admit(self.parent, [(self.file, 10, READ)])
        self.assertEqual(self.owner.complete_io(self.parent, self.file, READ, 3), 0)
        self.assertEqual(self.owner.complete_io(child, ref, READ, 2), 3)
        self.assertEqual(self.owner.complete_io(self.parent, self.file, READ, 1), 5)
        other = self.owner.open(self.parent, 4, READ)
        self.assertEqual(self.owner.complete_io(self.parent, other, READ, 1), 0)

    def test_restricted_child_cannot_write_or_open_namespace(self):
        child, (ref,) = self.owner.admit(self.parent, [(self.file, 10, READ)])
        self.unchanged(lambda: self.owner.complete_io(child, ref, WRITE, 1))
        self.unchanged(lambda: self.owner.open(child, 0, READ))
        self.assertEqual(self.owner.complete_io(child, ref, READ, 1), 0)

    def test_foreign_and_forged_references_are_denied(self):
        child, (ref,) = self.owner.admit(self.parent, [(self.file, 10, READ)])
        self.unchanged(lambda: self.owner.complete_io(child, self.file, READ, 1))
        self.unchanged(lambda: self.owner.complete_io(self.parent, ref, READ, 1))
        self.unchanged(lambda: self.owner.close(child, Reference(child, 3, 1)))

    def test_inheritance_validation_and_native_failure_are_atomic(self):
        for entries in ([(self.file, 10, READ), (self.file, 10, READ)],
                        [(self.file, 10, READ), (self.file, 16, READ)],
                        [(self.file, 10, READ), (self.file, 11, 4)]):
            self.unchanged(lambda: self.owner.admit(self.parent, entries))
        self.unchanged(lambda: self.owner.admit(self.parent, [(self.file, 10, READ)], native_accepted=False))
        child, _ = self.owner.admit(self.parent, [(self.file, 10, READ)])
        self.assertEqual(child.generation, 1)

    def test_rights_cannot_widen_from_read_only_parent(self):
        readonly = self.owner.open(self.parent, 4, READ)
        self.unchanged(lambda: self.owner.admit(self.parent, [(self.file, 10, READ), (readonly, 11, WRITE)]))

    def test_child_exit_leaves_parent_live_and_final_close_once(self):
        child, refs = self.owner.admit(self.parent, [(self.file, 10, READ), (self.file, 11, READ)])
        self.owner.close(child, refs[0])
        self.assertEqual(self.owner.closed, [])
        self.owner.exit(child)
        self.assertEqual(self.owner.closed, [])
        self.assertEqual(self.owner.complete_io(self.parent, self.file, READ, 1), 0)
        self.owner.close(self.parent, self.file)
        self.assertEqual(self.owner.closed, [0])
        self.unchanged(lambda: self.owner.close(self.parent, self.file))

    def test_parent_exit_does_not_revoke_child_reference(self):
        child, (ref,) = self.owner.admit(self.parent, [(self.file, 10, READ)])
        self.owner.exit(self.parent)
        self.assertEqual(self.owner.complete_io(child, ref, READ, 1), 0)
        self.assertEqual(self.owner.closed, [])
        self.owner.exit(child)
        self.assertEqual(self.owner.closed, [0])

    def test_child_session_reuse_does_not_revive_old_reference(self):
        child, (ref,) = self.owner.admit(self.parent, [(self.file, 10, READ)])
        self.owner.exit(child)
        replacement, _ = self.owner.admit(self.parent, [(self.file, 10, READ)])
        self.unchanged(lambda: self.owner.complete_io(replacement, ref, READ, 1))
        self.unchanged(lambda: self.owner.complete_io(child, ref, READ, 1))

    def test_session_generation_retires_and_busy_admission_rolls_back(self):
        for _ in range(3):
            child, _ = self.owner.admit(self.parent, [(self.file, 10, READ)])
            self.unchanged(lambda: self.owner.admit(self.parent, []))
            self.owner.exit(child)
        self.unchanged(lambda: self.owner.admit(self.parent, []))

    def test_descriptor_reuse_retires_and_old_reference_stays_stale(self):
        original = self.file
        for generation in range(1, 4):
            self.owner.close(self.parent, self.file)
            if generation < 3:
                self.file = self.owner.open(self.parent, 3, READ)
                self.unchanged(lambda: self.owner.close(self.parent, original))
        self.unchanged(lambda: self.owner.open(self.parent, 3, READ))
        self.assertEqual(len(self.owner.closed), 3)

    def test_open_capacity_and_invalid_io_preserve_position(self):
        self.owner.open(self.parent, 4, READ)
        self.unchanged(lambda: self.owner.open(self.parent, 5, READ))
        for count in (-1, 17):
            self.unchanged(lambda: self.owner.complete_io(self.parent, self.file, READ, count))
        self.unchanged(lambda: self.owner.complete_io(self.parent, self.file, READ, 1, reply='error'))
        self.assertEqual(self.owner.complete_io(self.parent, self.file, READ, 0), 0)

    def test_unknown_reply_poisoning_blocks_aliases_and_replay(self):
        child, (ref,) = self.owner.admit(self.parent, [(self.file, 10, READ)])
        with self.assertRaises(Rejected):
            self.owner.complete_io(self.parent, self.file, WRITE, 1, reply='unknown')
        self.unchanged(lambda: self.owner.complete_io(child, ref, READ, 1))
        self.unchanged(lambda: self.owner.admit(self.parent, []))
        self.owner.close(self.parent, self.file)
        self.owner.exit(child)
        self.assertEqual(self.owner.closed, [0])


if __name__ == '__main__':
    unittest.main()
