// SPDX-License-Identifier: BSD-2-Clause
use core::{ffi::c_void, ptr::NonNull};
use metadata::{Error, Metadata, Time};
unsafe extern "C" {
    fn metadata_fixture_case(value: i32);
    fn metadata_fixture_calls() -> u32;
    fn metadata_fixture_layout(index: u32) -> usize;
}

#[test]
fn metadata_oracle() {
    // SAFETY: this single host test serially owns the C fixture state. Its dummy
    // view is an opaque non-dereferenced tag, never an original ZPL context.
    unsafe {
        for (i, value) in [136, 8, 32, 72, 120, 8].iter().enumerate() {
            assert_eq!(
                metadata_fixture_layout(i as u32),
                *value,
                "metadata oracle: C ABI"
            );
        }
        let view = NonNull::<c_void>::dangling();
        metadata_fixture_case(0);
        let value = metadata::read(view, 2, 47).expect("metadata oracle: positive");
        assert_eq!(
            value.node,
            metadata::Node {
                object: 2,
                generation: 47,
                size: 780248,
                mode: 0o106755
            },
            "metadata oracle: node"
        );
        assert_eq!(
            (value.parent, value.links, value.uid, value.gid, value.flags),
            (34, 3, u64::MAX, 0x8000000100000001, 0x8000000000000104),
            "metadata oracle: raw labels"
        );
        assert_eq!(
            [value.atime, value.mtime, value.ctime, value.birthtime],
            [
                Time {
                    seconds: i64::MIN,
                    nanoseconds: 999999999
                },
                Time {
                    seconds: i64::MAX,
                    nanoseconds: 1
                },
                Time {
                    seconds: -1,
                    nanoseconds: 2
                },
                Time {
                    seconds: 0,
                    nanoseconds: 3
                }
            ],
            "metadata oracle: times"
        );
        for case in 1..=12 {
            metadata_fixture_case(case);
            let expected = match case {
                11 => Error::Backend(116),
                12 => Error::InvalidCompletion,
                _ => Error::InvalidMetadata,
            };
            assert_eq!(
                metadata::read(view, 2, 47),
                Err(expected),
                "metadata oracle: rejected case {case}"
            );
        }
        metadata_fixture_case(13);
        assert_eq!(
            metadata::read(view, 34, 45).unwrap().node.mode,
            0o040755,
            "metadata oracle: directory"
        );
        let calls = metadata_fixture_calls();
        assert_eq!(
            metadata::read(view, 0, 47),
            Err(Error::InvalidInput),
            "metadata oracle: zero object"
        );
        assert_eq!(
            metadata::read(view, 2, 0),
            Err(Error::InvalidInput),
            "metadata oracle: zero generation"
        );
        assert_eq!(
            metadata_fixture_calls(),
            calls,
            "metadata oracle: no invalid provider call"
        );
        assert_eq!(core::mem::size_of::<Metadata>(), 136);
        metadata_fixture_case(14);
        assert!(
            metadata_check::check(view, (34, 45), (2, 47)),
            "metadata oracle: disk probe positive"
        );
        for case in 15..=18 {
            metadata_fixture_case(case);
            assert!(
                !metadata_check::check(view, (34, 45), (2, 47)),
                "metadata oracle: disk probe denial {case}"
            );
        }
    }
}
