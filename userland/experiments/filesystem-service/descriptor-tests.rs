// SPDX-License-Identifier: BSD-2-Clause
use super::*;
use filesystem_policy::{Completion, Lost, Namespace, Node, Utc};
use std::{cell::RefCell, rc::Rc};

#[derive(Default)]
struct Observed {
    lookups: usize,
    reads: usize,
    drops: usize,
    error: Option<Error>,
    bad_count: bool,
    conflict: bool,
}
struct Provider(Rc<RefCell<Observed>>);
impl Drop for Provider {
    fn drop(&mut self) {
        self.0.borrow_mut().drops += 1;
    }
}
impl Backend for Provider {
    fn root(&mut self) -> core::result::Result<Node, Error> {
        Ok(Node::new(1, 1, 0, Kind::Directory))
    }
    fn lookup(&mut self, _: Node, name: &[u8]) -> core::result::Result<Node, Error> {
        let mut state = self.0.borrow_mut();
        state.lookups += 1;
        match name {
            b"file" | b"alias" => Ok(Node::new(
                2,
                1,
                if state.conflict { 7 } else { 6 },
                Kind::File,
            )),
            b"dir" => Ok(Node::new(3, 1, 0, Kind::Directory)),
            _ => Err(Error::Backend(2)),
        }
    }
    fn read(&mut self, _: Node, offset: u64, out: &mut [u8]) -> core::result::Result<usize, Error> {
        let mut state = self.0.borrow_mut();
        state.reads += 1;
        out.fill(0x55);
        if let Some(error) = state.error {
            return Err(error);
        }
        if state.bad_count {
            return Ok(out.len() + 1);
        }
        let bytes = b"abcdef";
        let start = offset.min(bytes.len() as u64) as usize;
        let length = (bytes.len() - start).min(out.len());
        out[..length].copy_from_slice(&bytes[start..start + length]);
        Ok(length)
    }
    fn write(
        &mut self,
        _: Node,
        _: u64,
        _: &[u8],
        _: Utc,
    ) -> core::result::Result<Completion, Lost> {
        panic!("read-only facade must not call write")
    }
    fn mutate(
        &mut self,
        _: Node,
        _: Namespace<'_>,
        _: Utc,
    ) -> core::result::Result<Completion, Lost> {
        panic!("read-only facade must not mutate namespace")
    }
}
struct Time;
impl Clock for Time {
    fn utc(&mut self) -> core::result::Result<Utc, Error> {
        panic!("read-only facade must not request write time")
    }
}
type Files = Descriptors<Provider, Time>;
fn setup() -> (Files, Rc<RefCell<Observed>>) {
    let state = Rc::new(RefCell::new(Observed::default()));
    let owner = Owner::new(Provider(state.clone()), Time, 91).unwrap();
    (Descriptors::new(owner, 17).unwrap(), state)
}

#[test]
fn duplicate_shares_offset_but_separate_open_does_not() {
    let (mut files, state) = setup();
    let first = files.open_read(b"file", false).unwrap();
    let alias = files.duplicate(first, 0, false).unwrap();
    let other = files.open_read(b"alias", false).unwrap();
    assert_eq!((first, alias, other), (3, 4, 5));
    let mut out = [0x77; MAX_READ];
    assert_eq!(files.read(first, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"ab");
    assert!(out[2..].iter().all(|&x| x == 0));
    assert_eq!(files.position(alias), Ok(2));
    assert_eq!(files.position(other), Ok(0));
    assert_eq!(files.read(alias, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"cd");
    assert_eq!(files.seek(first, Seek::Current(-1)), Ok(3));
    assert_eq!(files.position(alias), Ok(3));
    assert_eq!(state.borrow().lookups, 2);
    files.disconnect().unwrap();
    assert_eq!(state.borrow().drops, 1);
}

#[test]
fn final_close_only_consumes_handle_and_fd_reuse_is_not_handle_reuse() {
    let (mut files, _) = setup();
    let fd = files.open_read(b"file", false).unwrap();
    let duplicate = files.duplicate(fd, 10, false).unwrap();
    let handle = files.descriptions[files.binding_in(0, fd).unwrap().1.description]
        .unwrap()
        .handle;
    files.close(fd).unwrap();
    assert!(files
        .source
        .owner
        .stat(files.source.peer, files.source.attachment.session, handle)
        .is_ok());
    assert_eq!(files.position(fd), Err(Failure::BadFd));
    assert_eq!(files.read(duplicate, 1, &mut [0; MAX_READ]), Ok(1));
    files.close(duplicate).unwrap();
    assert_eq!(
        files
            .source
            .owner
            .stat(files.source.peer, files.source.attachment.session, handle),
        Err(Error::Stale)
    );
    assert_eq!(files.open_read(b"file", false), Ok(fd));
    assert_eq!(
        files
            .source
            .owner
            .stat(files.source.peer, files.source.attachment.session, handle),
        Err(Error::Stale)
    );
}

#[test]
fn eof_and_seek_end_keep_zero_tail_and_shared_position() {
    let (mut files, _) = setup();
    let fd = files.open_read(b"file", false).unwrap();
    assert_eq!(files.seek(fd, Seek::End(-2)), Ok(4));
    let mut out = [0x77; MAX_READ];
    assert_eq!(files.read(fd, 4, &mut out), Ok(2));
    assert_eq!(&out[..2], b"ef");
    assert!(out[2..].iter().all(|&x| x == 0));
    out.fill(0x77);
    assert_eq!(files.read(fd, 4, &mut out), Ok(0));
    assert!(out.iter().all(|&x| x == 0));
    assert_eq!(files.position(fd), Ok(6));
    assert_eq!(files.seek(fd, Seek::Set(20)), Ok(20));
    assert_eq!(files.read(fd, 1, &mut out), Ok(0));
}

#[test]
fn full_table_rejects_before_lookup_and_duplicate_exhaustion() {
    let (mut files, state) = setup();
    for expected in FIRST_FILE_FD..MAX_FDS {
        assert_eq!(files.open_read(b"file", false), Ok(expected));
    }
    assert_eq!(files.open_read(b"file", false), Err(Failure::Full));
    assert_eq!(state.borrow().lookups, 13);
    assert_eq!(files.duplicate(3, 0, false), Err(Failure::Full));
    files.close(8).unwrap();
    assert_eq!(files.duplicate(3, 8, false), Ok(8));
    assert_eq!(files.duplicate(3, -1, false), Err(Failure::Invalid));
    assert_eq!(files.duplicate(3, 16, false), Err(Failure::Invalid));
}

#[test]
fn invalid_names_have_no_lookup_effect_and_directory_opens_release_handles() {
    let (mut files, state) = setup();
    for name in [b"".as_slice(), b"a/b", b".", b"..", b"a\0b", &[b'x'; 256]] {
        assert_eq!(
            files.open_read(name, false),
            Err(Failure::Source(Error::Invalid))
        );
    }
    assert_eq!(state.borrow().lookups, 0);
    for _ in 0..40 {
        assert_eq!(
            files.open_read(b"dir", false),
            Err(Failure::Source(Error::IsDirectory))
        );
    }
    assert_eq!(files.open_read(b"file", false), Ok(3));
    assert_eq!(
        files.open_read(b"missing", false),
        Err(Failure::Source(Error::Backend(2)))
    );
    assert_eq!(files.position(3), Ok(0));
}

#[test]
fn close_on_exec_is_per_fd_and_preserves_unflagged_alias() {
    let (mut files, _) = setup();
    let fd = files.open_read(b"file", true).unwrap();
    let alias = files.duplicate(fd, 0, false).unwrap();
    let other = files.open_read(b"file", false).unwrap();
    files.set_close_on_exec(other, true).unwrap();
    files.read(fd, 2, &mut [0; MAX_READ]).unwrap();
    files.commit_exec_close().unwrap();
    assert_eq!(files.position(fd), Err(Failure::BadFd));
    assert_eq!(files.position(other), Err(Failure::BadFd));
    assert_eq!(files.position(alias), Ok(2));
    assert_eq!(files.read(alias, 1, &mut [0; MAX_READ]), Ok(1));
    files.set_close_on_exec(alias, true).unwrap();
    files.commit_exec_close().unwrap();
    assert_eq!(files.position(alias), Err(Failure::BadFd));
}

#[test]
fn offset_range_and_invalid_fd_reject_before_provider_effects() {
    let (mut files, state) = setup();
    let fd = files.open_read(b"file", false).unwrap();
    assert_eq!(files.seek(fd, Seek::Set(-1)), Err(Failure::Invalid));
    assert_eq!(
        files.seek(fd, Seek::Current(i64::MIN)),
        Err(Failure::Invalid)
    );
    assert_eq!(files.position(fd), Ok(0));
    assert_eq!(files.seek(fd, Seek::Set(i64::MAX)), Ok(i64::MAX as u64));
    assert_eq!(files.seek(fd, Seek::Current(1)), Err(Failure::Overflow));
    let mut out = [0x77; MAX_READ];
    assert_eq!(files.read(fd, 1, &mut out), Err(Failure::Overflow));
    assert_eq!(
        files.read(fd, MAX_READ + 1, &mut out),
        Err(Failure::Invalid)
    );
    assert_eq!(state.borrow().reads, 0);
    for fd in [i32::MIN, -1, 0, 1, 2, 16, i32::MAX] {
        out.fill(0x77);
        assert_eq!(files.read(fd, 1, &mut out), Err(Failure::BadFd));
        assert!(out.iter().all(|&x| x == 0));
        assert_eq!(files.close(fd), Err(Failure::BadFd));
    }
}

#[test]
fn known_provider_error_clears_reply_and_keeps_offset() {
    let (mut files, state) = setup();
    let fd = files.open_read(b"file", false).unwrap();
    files.seek(fd, Seek::Set(2)).unwrap();
    state.borrow_mut().error = Some(Error::Backend(5));
    let mut out = [0x77; MAX_READ];
    assert_eq!(
        files.read(fd, 2, &mut out),
        Err(Failure::Source(Error::Backend(5)))
    );
    assert!(out.iter().all(|&x| x == 0));
    assert_eq!(files.position(fd), Ok(2));
    state.borrow_mut().error = None;
    assert_eq!(files.read(fd, 2, &mut out), Ok(2));
    assert_eq!(&out[..2], b"cd");
}

#[test]
fn bad_count_retires_context_and_denies_all_future_work() {
    let (mut files, state) = setup();
    let fd = files.open_read(b"file", false).unwrap();
    state.borrow_mut().bad_count = true;
    let mut out = [0x77; MAX_READ];
    assert_eq!(
        files.read(fd, 2, &mut out),
        Err(Failure::Source(Error::InvalidCompletion))
    );
    assert!(out.iter().all(|&x| x == 0));
    assert_eq!(state.borrow().drops, 1);
    assert_eq!(files.open_read(b"file", false), Err(Failure::Retired));
    assert_eq!(files.close(fd), Err(Failure::Retired));
    assert_eq!(files.seek(fd, Seek::Set(0)), Err(Failure::Retired));
    assert_eq!(files.commit_exec_close(), Err(Failure::Retired));
    assert_eq!(files.read(fd, 1, &mut out), Err(Failure::Retired));
    assert_eq!(state.borrow().reads, 1);
    drop(files);
    assert_eq!(state.borrow().drops, 1);
}

#[test]
fn conflicting_lookup_and_failed_final_close_are_not_clean_recovery() {
    let (mut files, state) = setup();
    files.open_read(b"file", false).unwrap();
    state.borrow_mut().conflict = true;
    assert_eq!(
        files.open_read(b"alias", false),
        Err(Failure::Source(Error::InvalidMetadata))
    );
    assert_eq!(files.position(3), Err(Failure::Retired));
    assert_eq!(state.borrow().drops, 1);
    let (mut files, state) = setup();
    let fd = files.open_read(b"file", false).unwrap();
    // Host-only owner teardown injection, no production fault selector.
    files.source.owner.shutdown();
    assert_eq!(files.close(fd), Err(Failure::Source(Error::Closed)));
    assert_eq!(files.open_read(b"file", false), Err(Failure::Retired));
    drop(files);
    assert_eq!(state.borrow().drops, 1);
}

#[test]
fn file_handle_has_only_read_right_and_bad_bootstrap_drops_context() {
    let (mut files, _) = setup();
    let fd = files.open_read(b"file", false).unwrap();
    let handle = files.descriptions[files.binding_in(0, fd).unwrap().1.description]
        .unwrap()
        .handle;
    assert_eq!(
        files.source.owner.write(
            files.source.peer,
            files.source.attachment.session,
            handle,
            0,
            b"x"
        ),
        Err(Error::Denied)
    );
    let state = Rc::new(RefCell::new(Observed::default()));
    let owner = Owner::new(Provider(state.clone()), Time, 92).unwrap();
    assert!(matches!(
        Descriptors::new(owner, 0),
        Err(Failure::Source(Error::Invalid))
    ));
    assert_eq!(state.borrow().drops, 1);
}

#[test]
fn dropped_table_consumes_sole_context_even_with_live_aliases() {
    let (mut files, state) = setup();
    let fd = files.open_read(b"file", false).unwrap();
    files.duplicate(fd, 0, false).unwrap();
    drop(files);
    assert_eq!(state.borrow().drops, 1);
}
