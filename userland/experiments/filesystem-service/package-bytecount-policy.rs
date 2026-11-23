// SPDX-License-Identifier: BSD-2-Clause
//! Closed mutation plan for the dedicated bytecount seed and cold trial.
use super::*;

const fn image_size(bytes: &[u8]) -> usize {
    let mut result = 0;
    let mut index = 0;
    while index < bytes.len() {
        let digit = bytes[index];
        assert!(digit >= b'0' && digit <= b'9');
        result = result * 10 + (digit - b'0') as usize;
        index += 1;
    }
    assert!(result > 10 * MAX_READ && result <= 11 * MAX_READ);
    result
}

pub const PACKAGE_BYTECOUNT_BYTES: usize =
    image_size(env!("AETHER_PACKAGE_BYTECOUNT_BYTES").as_bytes());
pub const PACKAGE_BYTECOUNT_COLD: bool = cfg!(fs_package_bytecount_cold);
pub const PACKAGE_MUTATIONS: usize = if PACKAGE_BYTECOUNT_COLD { 1 } else { 17 };

impl<B: Backend, C: Clock> Owner<B, C> {
    /// Trusted bootstrap selects the actual held package directory once.
    pub fn select_package_root(
        &mut self,
        peer: u64,
        session: Session,
        root: Handle,
    ) -> Result<(), Error> {
        self.validate_home_source(peer, session, root)?;
        let node = self.handles[self.open(peer, session, root)?]
            .ok_or(Error::Stale)?
            .node;
        let expected = usize::from(!PACKAGE_BYTECOUNT_COLD);
        if self.package_root.is_some() || self.writes != expected {
            return Err(Error::Denied);
        }
        self.package_root = Some(node);
        Ok(())
    }

    pub(super) fn package_namespace(
        &self,
        parent: Node,
        operation: &Mutation<'_>,
    ) -> Result<(), Error> {
        if PACKAGE_BYTECOUNT_COLD {
            return Err(Error::Denied);
        }
        match (self.writes, operation) {
            (0, Mutation::MakeDirectory(b"pkg"))
                if self.package_root.is_none() && parent.identity() == self.root.identity() =>
            {
                Ok(())
            }
            (1, Mutation::Create(b"bytecount"))
            | (2, Mutation::Create(b"input"))
            | (3, Mutation::Create(b"output"))
                if self
                    .package_root
                    .is_some_and(|node| node.identity() == parent.identity()) =>
            {
                Ok(())
            }
            _ => Err(Error::Denied),
        }
    }

    pub(super) fn package_write(
        &mut self,
        file: Node,
        offset: u64,
        bytes: &[u8],
    ) -> Result<(), Error> {
        let root = self.package_root.ok_or(Error::Denied)?;
        let component = match self.writes {
            0 if PACKAGE_BYTECOUNT_COLD && offset == 0 && bytes == b"6\n" && file.size == 2 => {
                &b"output"[..]
            }
            4..=14 if !PACKAGE_BYTECOUNT_COLD => {
                let expected = (self.writes - 4) * MAX_READ;
                let length = (PACKAGE_BYTECOUNT_BYTES - expected).min(MAX_READ);
                if offset != expected as u64 || file.size != offset || bytes.len() != length {
                    return Err(Error::Denied);
                }
                &b"bytecount"[..]
            }
            15 if !PACKAGE_BYTECOUNT_COLD
                && offset == 0
                && file.size == 0
                && bytes == b"abcdef" =>
            {
                &b"input"[..]
            }
            16 if !PACKAGE_BYTECOUNT_COLD && offset == 0 && file.size == 0 && bytes == b"6\n" => {
                &b"output"[..]
            }
            _ => return Err(Error::Denied),
        };
        let backend = self.backend.as_mut().ok_or(Error::Closed)?;
        let current = backend.directory(root)?;
        if !current.valid()
            || current.identity() != root.identity()
            || current.kind != Kind::Directory
        {
            return Err(Error::InvalidMetadata);
        }
        let named = backend.lookup(current, component)?;
        if named.identity() != file.identity()
            || named.kind != Kind::File
            || named.size != file.size
        {
            return Err(Error::Denied);
        }
        if PACKAGE_BYTECOUNT_COLD {
            let mut before = [0; 2];
            if backend.read(named, 0, &mut before)? != 2 || before != *b"6\n" {
                return Err(Error::InvalidMetadata);
            }
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use core::cell::Cell;

    struct Store<'a> {
        effects: &'a Cell<usize>,
        output_before: [u8; 2],
        present: u8,
        sizes: [u64; 3],
    }
    fn directory(id: u64) -> Node {
        Node::new(id, 1, 2, Kind::Directory)
    }
    fn file(index: usize, size: u64) -> Node {
        Node::new((index + 3) as u64, 1, size, Kind::File)
    }
    impl Store<'_> {
        fn done(&mut self, size: usize) -> Completion {
            let txg = self.effects.get() + 1;
            self.effects.set(txg);
            Completion {
                error: 0,
                txg: txg as u64,
                bytes_staged: size as u64,
                state: 2,
            }
        }
    }
    impl Backend for Store<'_> {
        fn root(&mut self) -> Result<Node, Error> {
            Ok(directory(1))
        }
        fn directory(&mut self, at: Node) -> Result<Node, Error> {
            Ok(at)
        }
        fn lookup(&mut self, at: Node, name: &[u8]) -> Result<Node, Error> {
            match (at.object, name) {
                (1, b"pkg") => Ok(directory(2)),
                (1, b"foreign") => Ok(file(3, 0)),
                (2, b"bytecount") if self.present >= 1 => Ok(file(0, self.sizes[0])),
                (2, b"input") if self.present >= 2 => Ok(file(1, self.sizes[1])),
                (2, b"output") if self.present >= 3 => Ok(file(2, self.sizes[2])),
                _ => Err(Error::Backend(2)),
            }
        }
        fn read(&mut self, at: Node, offset: u64, bytes: &mut [u8]) -> Result<usize, Error> {
            assert_eq!((at.object, offset, bytes.len()), (5, 0, 2));
            bytes.copy_from_slice(&self.output_before);
            Ok(2)
        }
        fn mutate(&mut self, _: Node, op: Namespace<'_>, _: Utc) -> Result<Completion, Lost> {
            if matches!(op, Namespace::Create { .. }) {
                self.present += 1;
            }
            Ok(self.done(0))
        }
        fn write(
            &mut self,
            at: Node,
            offset: u64,
            bytes: &[u8],
            _: Utc,
        ) -> Result<Completion, Lost> {
            self.sizes[at.object as usize - 3] = at.size.max(offset + bytes.len() as u64);
            Ok(self.done(bytes.len()))
        }
    }
    struct TestClock;
    impl Clock for TestClock {
        fn utc(&mut self) -> Result<Utc, Error> {
            Ok(Utc {
                seconds: 1,
                nanoseconds: 0,
            })
        }
    }

    #[test]
    #[cfg(not(fs_package_bytecount_cold))]
    fn seed_only_permits_the_fixed_seventeen_effects() {
        let effects = Cell::new(0);
        let store = Store {
            effects: &effects,
            output_before: [0; 2],
            present: 0,
            sizes: [0; 3],
        };
        let mut owner = Owner::new(store, TestClock, 11)
            .unwrap()
            .with_namespace_identity(Identity::new(0, 0).unwrap());
        let rights = Rights::new(15).unwrap();
        let auth = owner.attach(7, rights).unwrap();
        let root = auth.root.handle;
        let session = auth.session;
        assert!(owner
            .namespace(7, session, root, Mutation::MakeDirectory(b"other"))
            .is_err());
        assert_eq!(effects.get(), 0);
        owner
            .namespace(7, session, root, Mutation::MakeDirectory(b"pkg"))
            .unwrap();
        let pkg = owner
            .lookup(7, session, root, b"pkg", rights)
            .unwrap()
            .handle;
        owner.select_package_root(7, session, pkg).unwrap();
        assert!(owner.select_package_root(7, session, pkg).is_err());
        assert!(owner
            .namespace(7, session, root, Mutation::Create(b"bytecount"))
            .is_err());
        assert!(owner
            .namespace(7, session, pkg, Mutation::Create(b"output"))
            .is_err());
        assert_eq!(effects.get(), 1);
        for name in [&b"bytecount"[..], b"input", b"output"] {
            owner
                .namespace(7, session, pkg, Mutation::Create(name))
                .unwrap();
        }
        let rw = Rights::new(7).unwrap();
        let exe = owner
            .lookup(7, session, pkg, b"bytecount", rw)
            .unwrap()
            .handle;
        let input = owner.lookup(7, session, pkg, b"input", rw).unwrap().handle;
        let output = owner.lookup(7, session, pkg, b"output", rw).unwrap().handle;
        let foreign = owner
            .lookup(7, session, root, b"foreign", rw)
            .unwrap()
            .handle;
        let block = [0; MAX_READ];
        assert!(owner.write(7, session, foreign, 0, &block).is_err());
        assert!(owner.write(7, session, exe, 0, &block[..1]).is_err());
        assert_eq!(effects.get(), 4);
        for offset in (0..PACKAGE_BYTECOUNT_BYTES).step_by(MAX_READ) {
            let size = (PACKAGE_BYTECOUNT_BYTES - offset).min(MAX_READ);
            owner
                .write(7, session, exe, offset as u64, &block[..size])
                .unwrap();
        }
        assert!(owner.write(7, session, input, 0, b"ABCDEF").is_err());
        assert_eq!(effects.get(), 15);
        owner.write(7, session, input, 0, b"abcdef").unwrap();
        assert!(owner.write(7, session, input, 0, b"6\n").is_err());
        assert!(owner.write(7, session, output, 0, b"7\n").is_err());
        owner.write(7, session, output, 0, b"6\n").unwrap();
        assert_eq!(effects.get(), 17);
        assert_eq!(owner.mutation_attempts(), 17);
        assert!(owner.write(7, session, output, 0, b"6\n").is_err());
        assert_eq!(effects.get(), 17);
    }

    #[test]
    #[cfg(fs_package_bytecount_cold)]
    fn cold_requires_actual_preimage_and_allows_one_exact_output_write() {
        for before in [*b"6\n", *b"7\n"] {
            let effects = Cell::new(0);
            let store = Store {
                effects: &effects,
                output_before: before,
                present: 3,
                sizes: [PACKAGE_BYTECOUNT_BYTES as u64, 6, 2],
            };
            let mut owner = Owner::new(store, TestClock, 12)
                .unwrap()
                .with_namespace_identity(Identity::new(0, 0).unwrap());
            let auth = owner.attach(7, Rights::new(15).unwrap()).unwrap();
            let session = auth.session;
            let pkg = owner
                .lookup(
                    7,
                    session,
                    auth.root.handle,
                    b"pkg",
                    Rights::new(15).unwrap(),
                )
                .unwrap()
                .handle;
            owner.select_package_root(7, session, pkg).unwrap();
            assert!(owner
                .namespace(7, session, pkg, Mutation::Create(b"output"))
                .is_err());
            let rw = Rights::new(7).unwrap();
            let input = owner.lookup(7, session, pkg, b"input", rw).unwrap().handle;
            let output = owner.lookup(7, session, pkg, b"output", rw).unwrap().handle;
            assert!(owner.write(7, session, input, 0, b"6\n").is_err());
            assert!(owner.write(7, session, output, 0, b"0\n").is_err());
            assert_eq!(effects.get(), 0);
            let result = owner.write(7, session, output, 0, b"6\n");
            if before == *b"6\n" {
                assert!(result.is_ok());
                assert!(owner.write(7, session, output, 0, b"6\n").is_err());
                assert_eq!(effects.get(), 1);
            } else {
                assert_eq!(result, Err(Error::InvalidMetadata));
                assert_eq!(effects.get(), 0);
            }
        }
    }
}
