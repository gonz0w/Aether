// SPDX-License-Identifier: BSD-2-Clause
//! Atomic two-grant greeting admission using the existing client binding table.
use super::*;
impl<T: Channel> Client<T> {
    /// Caller supplies authenticated AF09 endpoints and a nonreused epoch.
    /// Neither binding is published until both exact greetings validate.
    pub fn connect_home(channel: T, epoch: u64) -> core::result::Result<Self, ConnectFailure> {
        let mut client = Self {
            channel,
            epoch,
            bindings: [None; SLOTS],
            next: 3,
            cleanup: None,
        };
        client.greet_home()?;
        Ok(client)
    }
    fn greet_home(&mut self) -> core::result::Result<(), ConnectFailure> {
        let result = (|| {
            if self.epoch == 0 {
                return Err(Error::Invalid);
            }
            let first = self.receive()?;
            self.status(&first)?;
            let root = self.entry(&first, 1)?;
            if root.kind != Kind::Directory {
                return Err(Error::Protocol);
            }
            let second = self.receive()?;
            self.status(&second)?;
            let home = self.entry(&second, 2)?;
            if home.kind != Kind::Directory {
                return Err(Error::Protocol);
            }
            self.bindings[0] = Some(Binding {
                entry: root,
                rights: 3,
            });
            self.bindings[1] = Some(Binding {
                entry: home,
                rights: 15,
            });
            Ok(())
        })();
        if let Err(error) = result {
            self.shutdown();
            return Err(ConnectFailure {
                error,
                cleanup: self.cleanup.unwrap_or([-5; 2]),
            });
        }
        Ok(())
    }
    /// Initialize in the final exclusive slot; both grants validate before the
    /// caller gets a borrow. On error the slot is not initialized for the caller.
    #[cfg(fs_home_in_place)]
    pub fn connect_home_in_place(
        slot: &mut core::mem::MaybeUninit<Self>,
        channel: T,
        epoch: u64,
    ) -> core::result::Result<&mut Self, ConnectFailure> {
        let client = Self::initialize_in_place(slot, channel, epoch, 3);
        if let Err(error) = client.greet_home() {
            // SAFETY: initialize wrote every Client field; greet closed both
            // endpoints. No reference escapes; drop the sole channel once.
            unsafe { core::ptr::drop_in_place(client) };
            return Err(error);
        }
        Ok(client)
    }
    /// Borrow the permanent home grant; individual close is refused.
    pub fn home(&self) -> Result<Handle> {
        self.active()?;
        self.bindings[1]
            .map(|binding| binding.entry.handle)
            .ok_or(Error::Closed)
    }
}
