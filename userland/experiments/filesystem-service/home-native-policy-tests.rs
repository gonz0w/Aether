// SPDX-License-Identifier: BSD-2-Clause
//! Real Owner observations and finite service limits over typed host storage.
use filesystem_policy as p;
use filesystem_service::{message, put, Channel, Message, Stop};
use std::{cell::RefCell, rc::Rc};

#[derive(Default)]
struct State {
    calls: usize,
    clocks: usize,
    drops: usize,
    result: Option<Result<p::Completion, p::Lost>>,
    refresh_bad: bool,
    clock_bad: bool,
}
type Shared = Rc<RefCell<State>>;
struct Storage(Shared);
struct Time(Shared);
fn node(id: u64) -> p::Node {
    p::Node::new(
        id,
        id + 10,
        0,
        if id == 3 {
            p::Kind::File
        } else {
            p::Kind::Directory
        },
    )
}
impl Drop for Storage {
    fn drop(&mut self) {
        self.0.borrow_mut().drops += 1;
    }
}
impl p::Backend for Storage {
    fn root(&mut self) -> Result<p::Node, p::Error> {
        Ok(node(1))
    }
    fn directory(&mut self, at: p::Node) -> Result<p::Node, p::Error> {
        if self.0.borrow().refresh_bad {
            Err(p::Error::Backend(19))
        } else {
            Ok(at)
        }
    }
    fn lookup(&mut self, _: p::Node, name: &[u8]) -> Result<p::Node, p::Error> {
        Ok(node(match name {
            b"alias" => 1,
            b"file" => 3,
            _ => 2,
        }))
    }
    fn read(&mut self, _: p::Node, _: u64, _: &mut [u8]) -> Result<usize, p::Error> {
        Ok(0)
    }
    fn mutate(
        &mut self,
        _: p::Node,
        _: p::Namespace<'_>,
        _: p::Utc,
    ) -> Result<p::Completion, p::Lost> {
        let mut state = self.0.borrow_mut();
        state.calls += 1;
        state.result.unwrap_or(Ok(done(state.calls as u64)))
    }
    fn write(
        &mut self,
        _: p::Node,
        _: u64,
        bytes: &[u8],
        _: p::Utc,
    ) -> Result<p::Completion, p::Lost> {
        let mut state = self.0.borrow_mut();
        state.calls += 1;
        Ok(p::Completion {
            bytes_staged: bytes.len() as u64,
            ..done(state.calls as u64)
        })
    }
}
impl p::Clock for Time {
    fn utc(&mut self) -> Result<p::Utc, p::Error> {
        let mut state = self.0.borrow_mut();
        state.clocks += 1;
        if state.clock_bad {
            Err(p::Error::Clock)
        } else {
            Ok(p::Utc {
                seconds: 1,
                nanoseconds: 0,
            })
        }
    }
}
fn done(txg: u64) -> p::Completion {
    p::Completion {
        error: 0,
        txg,
        bytes_staged: 0,
        state: 2,
    }
}
fn setup() -> (Shared, p::Owner<Storage, Time>, p::Attachment) {
    let state = Shared::default();
    let mut owner = p::Owner::new(Storage(state.clone()), Time(state.clone()), 91)
        .unwrap()
        .with_namespace_identity(p::Identity::new(1000, 1000).unwrap());
    let attachment = owner.attach(7, p::Rights::new(15).unwrap()).unwrap();
    (state, owner, attachment)
}
#[test]
fn typed_provider_and_returned_outcomes_remain_distinct() {
    let values = [
        Ok(done(81)),
        Ok(p::Completion {
            error: 28,
            txg: 0,
            bytes_staged: 0,
            state: 0,
        }),
        Ok(p::Completion {
            error: 5,
            txg: 0,
            bytes_staged: 0,
            state: 1,
        }),
        Ok(p::Completion {
            error: 5,
            ..done(82)
        }),
        Ok(p::Completion {
            bytes_staged: 99,
            ..done(83)
        }),
        Err(p::Lost),
    ];
    for original in values {
        let (state, mut owner, a) = setup();
        state.borrow_mut().result = Some(original);
        let observed = owner.namespace_observed(
            7,
            a.session,
            a.root.handle,
            p::Mutation::MakeDirectory(b"home"),
        );
        assert_eq!(
            observed.provider,
            Some(original),
            "HOME_NATIVE_PROVIDER_RETENTION"
        );
        let expected = match original {
            Ok(value) if value.bytes_staged != 0 => Err(p::Error::InvalidCompletion),
            Ok(value) if value.error == 0 => Ok(value),
            Ok(value) if value.state == 0 => Err(p::Error::Backend(value.error)),
            Ok(value) => Err(p::Error::WriteFailed(value)),
            Err(p::Lost) => Err(p::Error::Uncertain),
        };
        assert_eq!(observed.result, expected);
        assert_eq!(owner.mutation_attempts(), 1);
        drop(owner);
        assert_eq!(state.borrow().drops, 1);
    }
    let (state, mut owner, a) = setup();
    state.borrow_mut().refresh_bad = true;
    let observed =
        owner.namespace_observed(7, a.session, a.root.handle, p::Mutation::Create(b"probe"));
    assert_eq!(
        observed.provider,
        Some(Ok(done(1))),
        "HOME_NATIVE_PRE_NORMALIZATION"
    );
    assert_eq!(
        observed.result,
        Err(p::Error::WriteFailed(p::Completion {
            error: 5,
            ..done(1)
        }))
    );
}
#[test]
fn local_failures_do_not_claim_provider_invocation() {
    let (state, mut owner, a) = setup();
    for bad_name in [b"".as_slice(), b"..", b"x/y"] {
        let observed =
            owner.namespace_observed(7, a.session, a.root.handle, p::Mutation::Create(bad_name));
        assert_eq!(observed.result, Err(p::Error::Invalid));
        assert_eq!(observed.provider, None);
    }
    let observed =
        owner.namespace_observed(8, a.session, a.root.handle, p::Mutation::Create(b"probe"));
    assert_eq!(observed.provider, None);
    assert!(observed.result.is_err());
    state.borrow_mut().clock_bad = true;
    let observed =
        owner.namespace_observed(7, a.session, a.root.handle, p::Mutation::Create(b"probe"));
    assert_eq!(observed.result, Err(p::Error::Clock));
    assert_eq!(observed.provider, None);
    assert_eq!(owner.mutation_attempts(), 0);
    assert_eq!(state.borrow().calls, 0);
}
#[test]
fn home_source_validation_uses_node_identity_and_original_checks() {
    let (_, mut owner, a) = setup();
    let all = p::Rights::new(15).unwrap();
    let alias = owner
        .lookup(7, a.session, a.root.handle, b"alias", all)
        .unwrap();
    assert_ne!(alias.handle, a.root.handle);
    assert_eq!(
        owner.validate_home_source(7, a.session, alias.handle),
        Err(p::Error::Denied),
        "HOME_NATIVE_ROOT_IDENTITY"
    );
    let file = owner
        .lookup(
            7,
            a.session,
            a.root.handle,
            b"file",
            p::Rights::new(7).unwrap(),
        )
        .unwrap();
    assert_eq!(
        owner.validate_home_source(7, a.session, file.handle),
        Err(p::Error::NotDirectory)
    );
    let weak = owner
        .lookup(
            7,
            a.session,
            a.root.handle,
            b"home",
            p::Rights::new(3).unwrap(),
        )
        .unwrap();
    assert_eq!(
        owner.validate_home_source(7, a.session, weak.handle),
        Err(p::Error::Denied)
    );
    let home = owner
        .lookup(7, a.session, a.root.handle, b"home", all)
        .unwrap();
    assert_eq!(
        owner.validate_home_source(7, a.session, home.handle),
        Ok(())
    );
    assert!(owner
        .validate_home_source(8, a.session, home.handle)
        .is_err());
    owner.close(7, a.session, home.handle).unwrap();
    assert_eq!(
        owner.validate_home_source(7, a.session, home.handle),
        Err(p::Error::Stale)
    );
    // Old recipient-zero precedence remains before directory/type/rights checks.
    assert_eq!(
        owner.attach_home(7, a.session, file.handle, 0),
        Err(p::Error::Invalid)
    );
}
#[test]
fn bootstrap_and_later_calls_share_nine_attempts() {
    let (state, mut owner, a) = setup();
    for _ in 0..2 {
        assert!(owner
            .namespace_observed(7, a.session, a.root.handle, p::Mutation::Create(b"probe"))
            .result
            .is_ok());
    }
    let file = owner
        .lookup(
            7,
            a.session,
            a.root.handle,
            b"file",
            p::Rights::new(7).unwrap(),
        )
        .unwrap();
    for _ in 2..9 {
        assert!(owner.write(7, a.session, file.handle, 0, b"x").is_ok());
    }
    let observed =
        owner.namespace_observed(7, a.session, a.root.handle, p::Mutation::Create(b"extra"));
    assert_eq!(
        observed.result,
        Err(p::Error::WriteLimit),
        "HOME_NATIVE_MUTATION_CAP"
    );
    assert_eq!(observed.provider, None);
    assert_eq!(state.borrow().calls, 9);
    assert_eq!(owner.mutation_attempts(), 9);
}
#[derive(Default)]
struct Transport {
    received: usize,
    sent: usize,
    closed: usize,
}
struct Stream(Rc<RefCell<Transport>>);
impl Channel for Stream {
    fn receive(&mut self, frame: &mut Message) -> Result<(), i64> {
        let mut state = self.0.borrow_mut();
        state.received += 1;
        assert!(state.received <= 96, "HOME_NATIVE_REQUEST_CAP");
        *frame = message(91, 12);
        put(frame, 3, 1);
        Ok(())
    }
    fn send(&mut self, _: &Message) -> Result<(), i64> {
        self.0.borrow_mut().sent += 1;
        Ok(())
    }
    fn close(&mut self) -> [i64; 2] {
        self.0.borrow_mut().closed += 1;
        [0, 0]
    }
}
#[test]
fn finite_loop_preserves_pre_loop_mutation_count_and_stops_before_receive_97() {
    let (state, mut owner, a) = setup();
    for _ in 0..2 {
        owner
            .namespace(7, a.session, a.root.handle, p::Mutation::Create(b"probe"))
            .unwrap();
    }
    let home = owner
        .lookup(
            7,
            a.session,
            a.root.handle,
            b"home",
            p::Rights::new(15).unwrap(),
        )
        .unwrap();
    let transport = Rc::new(RefCell::new(Transport::default()));
    let report = filesystem_service::run_home(
        owner,
        Stream(transport.clone()),
        7,
        a.session,
        home.handle,
        8,
        91,
    );
    assert_eq!(filesystem_service::REQUESTS, 96, "HOME_NATIVE_REQUEST_CAP");
    assert_eq!(report.stop, Stop::Limit);
    assert_eq!(report.requests, 96);
    assert_eq!(report.mutation_attempts, 2, "HOME_NATIVE_REPORT_COUNT");
    assert!(report.ready);
    assert_eq!(report.last_write, None);
    let t = transport.borrow();
    assert_eq!((t.received, t.sent, t.closed), (96, 98, 1));
    assert_eq!(state.borrow().drops, 1);
}
