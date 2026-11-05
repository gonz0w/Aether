// SPDX-License-Identifier: BSD-2-Clause
//! Tests consume the current bootstrap body over a populated typed provider.
use super::*;
use filesystem_policy as p;
use std::{cell::RefCell, rc::Rc};
#[derive(Default)]
struct State {
    mode: u8,
    mutations: usize,
    drops: usize,
}
struct Storage(Rc<RefCell<State>>);
struct Time;
impl Drop for Storage {
    fn drop(&mut self) {
        self.0.borrow_mut().drops += 1;
    }
}
fn node(id: u64, size: u64, kind: Kind) -> p::Node {
    p::Node::new(id, id + 10, size, kind)
}
impl p::Backend for Storage {
    fn root(&mut self) -> Result<p::Node, Error> {
        Ok(node(1, 0, Kind::Directory))
    }
    fn directory(&mut self, at: p::Node) -> Result<p::Node, Error> {
        Ok(at)
    }
    fn lookup(&mut self, _: p::Node, name: &[u8]) -> Result<p::Node, Error> {
        let m = self.0.borrow().mode;
        if name == b"home" {
            return match m {
                1 => Err(Error::Backend(2)),
                2 => Ok(node(1, 0, Kind::Directory)),
                3 => Ok(node(2, 0, Kind::File)),
                _ => Ok(node(2, 0, Kind::Directory)),
            };
        }
        assert_eq!(name, b"probe");
        match m {
            4 => Err(Error::Backend(2)),
            5 => Ok(node(3, 3548, Kind::Directory)),
            6 => Ok(node(3, 0, Kind::File)),
            7 => Ok(node(3, 3549, Kind::File)),
            8 => Ok(node(3, 3547, Kind::File)),
            _ => Ok(node(3, 3548, Kind::File)),
        }
    }
    fn read(&mut self, _: p::Node, _: u64, _: &mut [u8]) -> Result<usize, Error> {
        panic!("bootstrap must not read ELF")
    }
    fn mutate(
        &mut self,
        _: p::Node,
        _: p::Namespace<'_>,
        _: p::Utc,
    ) -> Result<p::Completion, p::Lost> {
        self.0.borrow_mut().mutations += 1;
        panic!("COLD_BOOTSTRAP_MUTATION")
    }
    fn write(&mut self, _: p::Node, _: u64, _: &[u8], _: p::Utc) -> Result<p::Completion, p::Lost> {
        self.0.borrow_mut().mutations += 1;
        panic!("COLD_BOOTSTRAP_WRITE")
    }
}
impl p::Clock for Time {
    fn utc(&mut self) -> Result<p::Utc, Error> {
        panic!("cold lookup requires no mutation timestamp")
    }
}
#[test]
fn cold_bootstrap_reopens_actual_existing_nodes_without_mutation() {
    let shared = Rc::new(RefCell::new(State::default()));
    let mut owner = Owner::new(Storage(shared.clone()), Time, 91).unwrap();
    let mut result = HomeResult::initial();
    let (session, home) = bootstrap(&mut owner, 7, &mut result).unwrap();
    owner.validate_home_source(7, session, home).unwrap();
    assert_eq!(owner.mutation_attempts(), 0);
    assert!(result.mkdir.is_zero() && result.create.is_zero());
    owner.shutdown();
    drop(owner);
    assert_eq!((shared.borrow().mutations, shared.borrow().drops), (0, 1));
}
#[test]
fn cold_bootstrap_refuses_missing_alias_wrong_type_and_size_without_repairs() {
    for mode in 1..=8 {
        let shared = Rc::new(RefCell::new(State {
            mode,
            ..State::default()
        }));
        let mut owner = Owner::new(Storage(shared.clone()), Time, 91).unwrap();
        let mut result = HomeResult::initial();
        let error = bootstrap(&mut owner, 7, &mut result).err().unwrap();
        assert_eq!(error.0, if mode <= 3 { 5 } else { 7 });
        assert!(result.mkdir.is_zero() && result.create.is_zero());
        assert_eq!(owner.mutation_attempts(), 0);
        owner.shutdown();
        drop(owner);
        assert_eq!((shared.borrow().mutations, shared.borrow().drops), (0, 1));
    }
}
