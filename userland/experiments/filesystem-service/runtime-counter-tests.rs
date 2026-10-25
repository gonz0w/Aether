// SPDX-License-Identifier: BSD-2-Clause
//! Actual policy counter state at representation exhaustion; no long-running guest.
use super::*;
use std::{cell::Cell, rc::Rc};
struct Provider(Rc<Cell<usize>>);
impl Backend for Provider {
    #[cfg(fs_directories)]
    fn directory(&mut self, directory: Node) -> Result<Node, Error> {
        Ok(directory)
    }
    fn root(&mut self) -> Result<Node, Error> {
        Ok(Node::new(34, 45, 1, Kind::Directory))
    }
    fn lookup(&mut self, _: Node, _: &[u8]) -> Result<Node, Error> {
        Ok(Node::new(99, 788, 4096, Kind::File))
    }
    fn read(&mut self, _: Node, _: u64, out: &mut [u8]) -> Result<usize, Error> {
        out.fill(0);
        Ok(out.len())
    }
    fn write(&mut self, _: Node, _: u64, bytes: &[u8], _: Utc) -> Result<Completion, Lost> {
        self.0.set(self.0.get() + 1);
        Ok(Completion {
            error: 0,
            txg: self.0.get() as u64,
            bytes_staged: bytes.len() as u64,
            state: 2,
        })
    }
    fn mutate(&mut self, _: Node, _: Namespace<'_>, _: Utc) -> Result<Completion, Lost> {
        self.0.set(self.0.get() + 1);
        Ok(Completion {
            error: 0,
            txg: self.0.get() as u64,
            bytes_staged: 0,
            state: 2,
        })
    }
}
struct Time;
impl Clock for Time {
    fn utc(&mut self) -> Result<Utc, Error> {
        Ok(Utc {
            seconds: 1791290040,
            nanoseconds: 123,
        })
    }
}
#[test]
fn last_representable_write_and_namespace_attempt_never_wrap_or_dispatch_again() {
    for namespace in [false, true] {
        let calls = Rc::new(Cell::new(0));
        let mut owner = Owner::new(Provider(calls.clone()), Time, 1)
            .unwrap()
            .with_namespace_identity(Identity::new(1000, 1000).unwrap());
        let a = owner.attach(7, Rights::ALL).unwrap();
        let file = owner
            .lookup(7, a.session, a.root.handle, b"p", Rights::new(6).unwrap())
            .unwrap();
        owner.writes = MutationCount::MAX - 1;
        if namespace {
            owner
                .namespace(7, a.session, a.root.handle, Mutation::Create(b"p"))
                .unwrap();
        } else {
            owner
                .write(7, a.session, file.handle, 0, &[71; 16])
                .unwrap();
        }
        assert_eq!(
            owner.mutation_attempts(),
            MutationCount::MAX,
            "RUNTIME_COUNTER_MAX"
        );
        for _ in 0..3 {
            assert_eq!(
                owner.write(7, a.session, file.handle, 0, &[71; 16]),
                Err(Error::WriteLimit),
                "RUNTIME_WRITE_OVERFLOW"
            );
            assert_eq!(
                owner.namespace(7, a.session, a.root.handle, Mutation::Create(b"p")),
                Err(Error::WriteLimit),
                "RUNTIME_NAMESPACE_OVERFLOW"
            );
        }
        assert_eq!(calls.get(), 1, "RUNTIME_OVERFLOW_NO_DISPATCH");
        assert_eq!(owner.mutation_attempts(), MutationCount::MAX);
        owner.shutdown();
        assert_eq!(owner.attach(7, Rights::ALL), Err(Error::Closed));
    }
}
