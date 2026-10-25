// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use std::vec;

fn ok() -> Message {
    frame(0, 0, 0, 0)
}

#[test]
fn actual_service_nested_absolute_relative_read_and_parent_cleanup() {
    for path in [
        b"dir/dir/file".as_slice(),
        b"/dir/dir/file",
        b"file",
        b"/file",
    ] {
        let mut h = Harness::new();
        let c = h.client.as_mut().unwrap();
        let root = c.root().unwrap();
        let file = c.open_root_path(path).unwrap();
        assert_eq!((file.kind, file.size), (Kind::File, 5003));
        let mut out = [0xff; MAX_READ];
        assert_eq!(c.read(file.handle, 4999, 73, &mut out), Ok(4));
        assert_eq!(&out[..4], &[135, 136, 137, 138]);
        assert!(out[4..].iter().all(|&b| b == 0));
        assert_eq!(c.bindings.iter().flatten().count(), 2);
        assert_eq!(c.root(), Ok(root));
        c.close(file.handle).unwrap();
        assert_eq!(c.disconnect(), Ok([0; 2]));
        let report = h.worker.take().unwrap().join().unwrap();
        assert_eq!(report.stop, filesystem_service::Stop::Disconnected);
        assert_eq!(report.cleanup, [0; 2]);
        let closes = h.local.lock().unwrap().closes;
        assert_eq!(closes, 1);
    }
}

#[test]
fn exact_component_rights_tokens_close_order_and_root_retention() {
    let (io, seen) = script(vec![
        frame(0, 1, 1, 0),
        frame(0, 2, 1, 0),
        frame(0, 3, 1, 0),
        ok(),
        frame(0, 4, 2, 9),
        ok(),
    ]);
    let mut c = connect(io);
    let root = c.root().unwrap();
    let file = c.open_root_path(b"/a/b/c").unwrap();
    assert_eq!((file.handle.token, file.size), (4, 9));
    let rows = seen.lock().unwrap().sent.clone();
    assert_eq!(rows.len(), 8);
    let observed: Vec<_> = [0, 2, 4, 5, 7]
        .map(|i| (word(&rows[i], 1), word(&rows[i], 3), word(&rows[i], 4)))
        .into();
    assert_eq!(
        observed,
        vec![(1, 1, 3), (1, 2, 3), (3, 2, 0), (1, 3, 2), (3, 3, 0)]
    );
    for (i, byte) in [(1, b'a'), (3, b'b'), (6, b'c')] {
        assert_eq!(rows[i][0], byte);
        assert!(rows[i][1..].iter().all(|&b| b == 0));
    }
    assert_eq!(c.root(), Ok(root));
    assert_eq!(c.bindings.iter().flatten().count(), 2);
}

#[test]
fn whole_path_denials_and_root_directory_have_no_requests() {
    let (io, seen) = script(vec![frame(0, 1, 1, 0)]);
    let mut c = connect(io);
    for path in [
        b"".as_slice(),
        b"//x",
        b"a//b",
        b"a/",
        b".",
        b"..",
        b"a/./b",
        b"a/../b",
        b"/../x",
        b"a\0b",
        &[b'x'; 256],
    ] {
        assert_eq!(c.open_root_path(path), Err(Error::Invalid));
    }
    assert_eq!(c.open_root_path(b"/"), Err(Error::Remote(-21)));
    let empty = seen.lock().unwrap().sent.is_empty();
    assert!(empty);
    for rights in [1, 2] {
        let (io, seen) = script(vec![frame(0, 1, 1, 0)]);
        let mut c = Client::connect(io, 91, rights).ok().unwrap();
        assert_eq!(c.open_root_path(b"a/b"), Err(Error::Invalid));
        let empty = seen.lock().unwrap().sent.is_empty();
        assert!(empty);
    }
}

#[test]
fn deep_maximum_path_uses_rolling_handles_without_touching_existing_files() {
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let retained = c.open_root_path(b"retained").unwrap();
    let mut path = Vec::new();
    for _ in 0..63 {
        path.extend_from_slice(b"dir/");
    }
    path.extend_from_slice(b"end");
    assert_eq!(path.len(), 255);
    let file = c.open_root_path(&path).unwrap();
    assert_eq!(c.bindings.iter().flatten().count(), 3);
    let mut out = [0; MAX_READ];
    assert_eq!(c.read(retained.handle, 7, 1, &mut out), Ok(1));
    assert_eq!(out[0], 7);
    c.close(file.handle).unwrap();
    c.close(retained.handle).unwrap();
    assert_eq!(c.disconnect(), Ok([0; 2]));
}

#[test]
fn capacity_and_counter_preflight_precede_any_path_lookup() {
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let mut files = Vec::new();
    for _ in 0..14 {
        files.push(c.open_root_path(b"file").unwrap());
    }
    let before = h.local.lock().unwrap().sent.len();
    assert_eq!(c.open_root_path(b"dir/file"), Err(Error::Full));
    let sent = h.local.lock().unwrap().sent.len();
    assert_eq!(sent, before);
    assert_eq!(c.bindings.iter().flatten().count(), 15);
    c.close(files.pop().unwrap().handle).unwrap();
    assert!(c.open_root_path(b"dir/file").is_ok());
    for count in [u64::MAX, u64::MAX - 1] {
        let (io, seen) = script(vec![frame(0, 1, 1, 0)]);
        let mut c = connect(io);
        c.next = count;
        assert_eq!(c.open_root_path(b"a/b"), Err(Error::Full));
        let empty = seen.lock().unwrap().sent.is_empty();
        assert!(empty);
    }
}

#[test]
fn lookup_error_preserved_after_temporary_close_and_existing_file_stays_live() {
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let retained = c.open_root_path(b"file").unwrap();
    assert_eq!(c.open_root_path(b"dir/missing"), Err(Error::Remote(-2)));
    assert_eq!(c.bindings.iter().flatten().count(), 2);
    let mut out = [0; MAX_READ];
    assert_eq!(c.read(retained.handle, 7, 1, &mut out), Ok(1));
    assert_eq!(out[0], 7);
    c.close(retained.handle).unwrap();
    assert_eq!(c.disconnect(), Ok([0; 2]));
}

#[test]
fn wrong_intermediate_and_final_types_close_all_temporaries() {
    for (path, errno) in [(b"file/next".as_slice(), -20), (b"dir/dir", -21)] {
        let mut h = Harness::new();
        let c = h.client.as_mut().unwrap();
        assert_eq!(c.open_root_path(path), Err(Error::Remote(errno)));
        assert_eq!(c.bindings.iter().flatten().count(), 1);
        assert_eq!(c.disconnect(), Ok([0; 2]));
    }
}

#[test]
fn close_failures_override_prior_errors_and_never_publish_new_handles() {
    for result in [frame(-2, 0, 0, 0), frame(0, 3, 2, 9)] {
        let (io, seen) = script(vec![
            frame(0, 1, 1, 0),
            frame(0, 2, 1, 0),
            result,
            frame(-13, 0, 0, 0),
        ]);
        let mut c = connect(io);
        assert_eq!(c.open_root_path(b"dir/file"), Err(Error::Remote(-13)));
        assert_eq!(c.root(), Err(Error::Closed));
        let closes = seen.lock().unwrap().closes;
        assert_eq!(closes, 1);
        assert_eq!(c.open_root_path(b"file"), Err(Error::Closed));
        let sent = seen.lock().unwrap().sent.len();
        assert_eq!(sent, 5);
    }
    let (io, seen) = script(vec![
        frame(0, 1, 1, 0),
        frame(0, 2, 1, 0),
        frame(-13, 0, 0, 0),
    ]);
    let mut c = connect(io);
    assert_eq!(c.open_root_path(b"dir"), Err(Error::Remote(-13)));
    assert_eq!(c.root(), Err(Error::Closed));
    let closes = seen.lock().unwrap().closes;
    assert_eq!(closes, 1);
}

#[test]
fn fatal_lookup_does_not_replay_close_on_retired_connection() {
    for reply in [Err(-32), Ok(frame(0, 99, 2, 9)), Ok(frame(-5, 0, 0, 0))] {
        let (mut io, seen) = script(vec![frame(0, 1, 1, 0), frame(0, 2, 1, 0)]);
        io.input.push_back(reply);
        let mut c = connect(io);
        assert!(c.open_root_path(b"dir/file").is_err());
        assert_eq!(c.root(), Err(Error::Closed));
        let sent = seen.lock().unwrap().sent.len();
        assert_eq!(sent, 4);
        let closes = seen.lock().unwrap().closes;
        assert_eq!(closes, 1);
        drop(c);
        let closes = seen.lock().unwrap().closes;
        assert_eq!(closes, 1);
    }
}

#[test]
fn actual_directory_walk_retains_base_and_reads_through_new_handle() {
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let root = c.root().unwrap();
    let directory = c.open_directory_from(root, b"dir/dir").unwrap();
    let file = c.open_file_from(directory.handle, b"dir/file").unwrap();
    assert_eq!(c.bindings.iter().flatten().count(), 3);
    let mut out = [0; MAX_READ];
    assert_eq!(c.read(file.handle, 7, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], &[7, 8]);
    c.close(file.handle).unwrap();
    // The borrowed base outlives a completed walk and can be used again.
    let next = c.open_file_from(directory.handle, b"file").unwrap();
    c.close(next.handle).unwrap();
    assert_eq!(c.stat(directory.handle).unwrap().kind, Kind::Directory);
    c.close(directory.handle).unwrap();
    assert_eq!(c.root(), Ok(root));
    assert_eq!(c.disconnect(), Ok([0; 2]));
    assert_eq!(h.worker.take().unwrap().join().unwrap().cleanup, [0; 2]);
}

#[test]
fn anchored_directory_requests_exact_base_and_rights_without_root_fallback() {
    let (io, seen) = script(vec![
        frame(0, 1, 1, 0),
        frame(0, 2, 1, 0),
        frame(0, 3, 1, 0),
        frame(0, 4, 1, 0),
        ok(),
    ]);
    let mut c = connect(io);
    let root = c.root().unwrap();
    let base = c.lookup(root, b"base", 3).unwrap().handle;
    seen.lock().unwrap().sent.clear();
    let directory = c.open_directory_from(base, b"child/next").unwrap();
    assert_eq!(directory.handle.token, 4);
    let rows = seen.lock().unwrap().sent.clone();
    let observed: Vec<_> = [0, 2, 4]
        .map(|i| (word(&rows[i], 1), word(&rows[i], 3), word(&rows[i], 4)))
        .into();
    assert_eq!(observed, vec![(1, 2, 3), (1, 3, 3), (3, 3, 0)]);
    assert_eq!(c.bindings.iter().flatten().count(), 3);
    assert_eq!(c.binding(base).unwrap().1.entry.kind, Kind::Directory);
}

#[test]
fn anchored_syntax_stale_foreign_rights_and_file_bases_have_no_effects() {
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let root = c.root().unwrap();
    let directory = c.open_directory_from(root, b"dir").unwrap().handle;
    let file = c.open_root_path(b"file").unwrap().handle;
    let before = h.local.lock().unwrap().sent.len();
    for path in [
        b"".as_slice(),
        b"/",
        b"/file",
        b"//file",
        b"a//b",
        b"a/",
        b".",
        b"..",
        b"a/./b",
        b"a/../b",
        b"a\0b",
        &[b'a'; 256],
    ] {
        assert_eq!(c.open_file_from(directory, path), Err(Error::Invalid));
        assert_eq!(c.open_directory_from(directory, path), Err(Error::Invalid));
    }
    for base in [
        Handle {
            epoch: 90,
            token: directory.token,
        },
        Handle {
            epoch: 91,
            token: 999,
        },
    ] {
        assert_eq!(c.open_file_from(base, b"file"), Err(Error::Invalid));
        assert_eq!(c.open_directory_from(base, b"dir"), Err(Error::Invalid));
    }
    assert_eq!(c.open_file_from(file, b"file"), Err(Error::Remote(-20)));
    assert_eq!(c.open_directory_from(file, b"dir"), Err(Error::Remote(-20)));
    let index = c.binding(directory).unwrap().0;
    for rights in [1, 2] {
        c.bindings[index].as_mut().unwrap().rights = rights;
        assert_eq!(c.open_file_from(directory, b"file"), Err(Error::Invalid));
        assert_eq!(
            c.open_directory_from(directory, b"dir"),
            Err(Error::Invalid)
        );
    }
    c.bindings[index].as_mut().unwrap().rights = 3;
    let after = h.local.lock().unwrap().sent.len();
    assert_eq!(after, before);
    c.close(directory).unwrap();
    let before = h.local.lock().unwrap().sent.len();
    assert_eq!(
        c.open_directory_from(directory, b"dir"),
        Err(Error::Invalid)
    );
    assert_eq!(c.open_file_from(directory, b"file"), Err(Error::Invalid));
    let after = h.local.lock().unwrap().sent.len();
    assert_eq!(after, before);
    c.close(file).unwrap();
    assert_eq!(c.disconnect(), Ok([0; 2]));
}

#[test]
fn anchored_directory_wrong_kind_closes_result_and_preserves_base() {
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let root = c.root().unwrap();
    let base = c.open_directory_from(root, b"dir").unwrap().handle;
    for path in [b"file".as_slice(), b"dir/file", b"file/dir"] {
        assert_eq!(c.open_directory_from(base, path), Err(Error::Remote(-20)));
        assert_eq!(c.bindings.iter().flatten().count(), 2);
        assert_eq!(c.stat(base).unwrap().kind, Kind::Directory);
    }
    assert_eq!(c.open_file_from(base, b"dir"), Err(Error::Remote(-21)));
    assert_eq!(c.bindings.iter().flatten().count(), 2);
    c.close(base).unwrap();
    assert_eq!(c.disconnect(), Ok([0; 2]));
}

#[test]
fn anchored_capacity_and_token_exhaustion_precede_requests() {
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let root = c.root().unwrap();
    let base = c.open_directory_from(root, b"dir").unwrap().handle;
    let mut files = Vec::new();
    for _ in 0..13 {
        files.push(c.open_file_from(base, b"file").unwrap().handle);
    }
    let before = h.local.lock().unwrap().sent.len();
    assert_eq!(c.open_directory_from(base, b"dir/dir"), Err(Error::Full));
    assert_eq!(c.open_file_from(base, b"dir/file"), Err(Error::Full));
    let after = h.local.lock().unwrap().sent.len();
    assert_eq!(after, before);
    let last = c.open_directory_from(base, b"dir").unwrap().handle;
    let before = h.local.lock().unwrap().sent.len();
    assert_eq!(c.open_directory_from(base, b"dir"), Err(Error::Full));
    let after = h.local.lock().unwrap().sent.len();
    assert_eq!(after, before);
    c.close(last).unwrap();
    for file in files {
        c.close(file).unwrap();
    }
    for next in [u64::MAX, u64::MAX - 1] {
        c.next = next;
        let before = h.local.lock().unwrap().sent.len();
        assert_eq!(c.open_directory_from(base, b"dir/dir"), Err(Error::Full));
        assert_eq!(c.open_file_from(base, b"dir/file"), Err(Error::Full));
        let after = h.local.lock().unwrap().sent.len();
        assert_eq!(after, before);
    }
    c.close(base).unwrap();
    assert_eq!(c.disconnect(), Ok([0; 2]));
}

#[test]
fn anchored_known_lookup_error_closes_only_temporary_directory() {
    let mut h = Harness::new();
    let c = h.client.as_mut().unwrap();
    let root = c.root().unwrap();
    let base = c.open_directory_from(root, b"dir").unwrap().handle;
    assert_eq!(
        c.open_directory_from(base, b"dir/missing"),
        Err(Error::Remote(-2))
    );
    assert_eq!(
        c.open_file_from(base, b"dir/missing"),
        Err(Error::Remote(-2))
    );
    assert_eq!(c.bindings.iter().flatten().count(), 2);
    assert_eq!(c.stat(base).unwrap().kind, Kind::Directory);
    c.close(base).unwrap();
    assert_eq!(c.disconnect(), Ok([0; 2]));
}

#[test]
fn anchored_unknown_lookup_retires_once_without_base_close_or_replay() {
    for reply in [Err(-32), Ok(frame(0, 99, 1, 0)), Ok(frame(-5, 0, 0, 0))] {
        let (mut io, seen) = script(vec![frame(0, 1, 1, 0), frame(0, 2, 1, 0)]);
        io.input.push_back(reply);
        let mut c = connect(io);
        let base = c
            .open_directory_from(c.root().unwrap(), b"base")
            .unwrap()
            .handle;
        assert!(c.open_directory_from(base, b"child/next").is_err());
        assert_eq!(c.root(), Err(Error::Closed));
        let before = seen.lock().unwrap().sent.len();
        assert_eq!(c.open_file_from(base, b"file"), Err(Error::Closed));
        let after = seen.lock().unwrap().sent.len();
        assert_eq!(after, before);
        drop(c);
        assert_eq!(seen.lock().unwrap().closes, 1);
        assert_eq!(
            seen.lock()
                .unwrap()
                .sent
                .iter()
                .filter(|row| word(row, 1) == 3)
                .count(),
            0
        );
    }
}

#[test]
fn anchored_failed_close_overrides_lookup_or_directory_publication() {
    for next in [frame(-2, 0, 0, 0), frame(0, 4, 1, 0)] {
        let (io, seen) = script(vec![
            frame(0, 1, 1, 0),
            frame(0, 2, 1, 0),
            frame(0, 3, 1, 0),
            next,
            frame(-13, 0, 0, 0),
        ]);
        let mut c = connect(io);
        let base = c
            .open_directory_from(c.root().unwrap(), b"base")
            .unwrap()
            .handle;
        assert_eq!(
            c.open_directory_from(base, b"child/next"),
            Err(Error::Remote(-13))
        );
        assert_eq!(c.root(), Err(Error::Closed));
        let rows = seen.lock().unwrap().sent.clone();
        assert_eq!(
            (word(rows.last().unwrap(), 1), word(rows.last().unwrap(), 3)),
            (3, 3)
        );
        assert_eq!(seen.lock().unwrap().closes, 1);
    }
}
