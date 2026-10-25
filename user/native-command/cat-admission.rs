// SPDX-License-Identifier: BSD-2-Clause
// Owner-selected image; the name gate never creates execution authority.
use super::*;
fn template() -> Args {
    let mut a = args(b"cat");
    a.envc = 1;
    a.strings[4][..8].copy_from_slice(b"LC_ALL=C");
    #[cfg(cat_usage)]
    {
        a.argc = 2;
        a.strings[1].copy_from_slice(include_bytes!(env!("AETHER_CAT_ARGUMENT")));
        let end = a.strings[1]
            .iter()
            .position(|v| *v == 0)
            .unwrap_or_else(|| end(1510));
        check(a.strings[1][end..].iter().all(|v| *v == 0), 1510);
    }
    a
}
fn validate(a: &Args) -> Result<(), i32> {
    let expected = template();
    if a.argc != expected.argc || a.envc != 1 {
        return Err(-22);
    }
    if a.strings[0] != expected.strings[0] && !cfg!(cat_accept_name) {
        return Err(-2);
    }
    if a.strings[1..] != expected.strings[1..] {
        return Err(-22);
    }
    Ok(())
}
pub fn launch_cat(factory: u64, image: u64) -> Connection {
    let mut startup = template();
    // All gate probes precede channel allocation and native admission.
    startup.strings[0][0] = b'X';
    check(validate(&startup) == Err(-2), 1510);
    startup.strings[0][0] = b'c';
    startup.argc += 1;
    check(validate(&startup) == Err(-22), 1510);
    startup.argc -= 1;
    startup.strings[4][7] = b'X';
    check(validate(&startup) == Err(-22), 1510);
    startup.strings[4][7] = b'C';
    startup.strings[7][31] = 1;
    check(validate(&startup) == Err(-22), 1510);
    startup.strings[7][31] = 0;
    check(validate(&startup) == Ok(()), 1510);
    let req = ctl(0x24000, 0xd001);
    check(req.0 > 0, 1511);
    let rep = ctl(0x24000, 0xd001);
    if rep.0 < 0 {
        check(
            ctl(0x24003, req.0 as u64).0 == 0 && ctl(0x24003, req.1).0 == 0,
            1511,
        );
        end(1511);
    }
    startup.argc = 5;
    check(
        call(
            0x23002,
            factory,
            image,
            0,
            &startup as *const Args as u64,
            req.0 as u64,
            rep.1,
        )
        .0 == -22,
        1511,
    );
    check(
        call(0x24001, req.0 as u64, 0, 0, 0, 0, 0).0 == 0
            && call(0x24002, rep.1, 0, 0, 0, 0, 0).0 == 0,
        1511,
    );
    startup.argc = if cfg!(cat_usage) { 2 } else { 1 };
    if cfg!(cat_wrong_startup) {
        startup.strings[0][0] = b'X';
    }
    let child = call(
        0x23002,
        factory,
        image,
        0,
        &startup as *const Args as u64,
        req.0 as u64,
        rep.1,
    )
    .0;
    if child < 0 {
        for h in [req.0 as u64, req.1, rep.0 as u64, rep.1] {
            check(ctl(0x24003, h).0 == 0, 1511);
        }
        end(1511);
    }
    startup.argc = 4;
    startup.envc = 0;
    startup.strings.fill([0xa5; 32]);
    core::hint::black_box(&startup);
    check(
        ctl(0x24003, req.0 as u64).0 == -13 && ctl(0x24003, rep.1).0 == -13,
        1511,
    );
    Connection {
        reader: rep.0 as u64,
        writer: req.1,
        child: child as u64,
    }
}
