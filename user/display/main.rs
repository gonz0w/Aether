#![no_std]
#![no_main]
use core::arch::asm;

unsafe fn call(op: u64, cap: u64, payload: u64) -> (u64, u64) {
    let status: u64;
    let value: u64;
    unsafe {
        asm!("int 0x80", inlateout("rax") op => status, in("rdi") cap, in("rsi") payload, lateout("rdx") value);
    }
    (status, value)
}
fn expect(op: u64, cap: u64, status: u64) -> u64 {
    let result = unsafe { call(op, cap, 0) };
    if result.0 != status {
        finish(1);
    }
    result.1
}
fn finish(value: u64) -> ! {
    loop {
        if unsafe { call(0, value, 0) }.0 != 6 {
            unsafe {
                asm!("ud2", options(noreturn));
            }
        }
    }
}
fn message(op: u64, cap: u64, value: u64) -> u64 {
    loop {
        let result = unsafe { call(op, cap, value) };
        if result.0 == 0 {
            return result.1;
        }
        if result.0 != if op == 1 { 4 } else { 5 } {
            finish(4);
        }
        expect(20, 0, 0);
    }
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! {
    finish(2)
}

#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(
    grant: u64,
    width: usize,
    height: usize,
    stride: usize,
    masks: u64,
    mut link: u64,
) -> ! {
    let binding = masks & 0xffffffff00000000;
    expect(50, (1u64 << 32) | 0x100, 1);
    unsafe {
        (0x800000 as *mut u64).write_volatile(0xd15);
    }
    expect(2, 0, 1);
    expect(2, 1u64 << 32, 1);
    expect(1, link | 1, 2);
    expect(40, 0, 1);
    expect(40, grant ^ (1 << 32), 1);
    expect(40, grant | 1, 2);
    let bytes = expect(41, grant | 1, 0);
    let base = expect(40, grant, 0);
    expect(40, grant, 6);
    if bytes != (stride * height * 4) as u64 {
        finish(3);
    }
    if !cfg!(skip_draw) {
        for y in 0..height {
            for x in 0..width {
                let (r, g, b) = if x < 8 || y < 8 || x + 8 >= width || y + 8 >= height {
                    (255u32, 255u32, 255u32)
                } else if y < height / 3 {
                    if y >= 160 && y < 168 {
                        (80, 220, 180)
                    } else {
                        (24, 32, 48)
                    }
                } else if y < height * 2 / 3 {
                    match x * 3 / width {
                        0 => (255, 0, 0),
                        1 => (0, 255, 0),
                        _ => (0, 0, 255),
                    }
                } else if y >= 436 {
                    (24, 32, 48)
                } else if (x / 32 + y / 32) % 2 == 0 {
                    (40, 180, 180)
                } else {
                    (16, 70, 90)
                };
                let color =
                    (r << (masks & 31)) | (g << ((masks >> 8) & 31)) | (b << ((masks >> 16) & 31));
                unsafe {
                    ((base as usize + (y * stride + x) * 4) as *mut u32).write_volatile(color);
                }
            }
        }
        for (line, text) in [
            b"AETHER".as_slice(),
            b"RUST DISPLAY".as_slice(),
            b"AP RESULTS".as_slice(),
            b"DISPLAY".as_slice(),
        ]
        .iter()
        .enumerate()
        {
            for (column, ch) in text.iter().enumerate() {
                let glyph: [u8; 7] = match ch {
                    b'A' => [14, 17, 17, 31, 17, 17, 17],
                    b'E' => [31, 16, 16, 30, 16, 16, 31],
                    b'T' => [31, 4, 4, 4, 4, 4, 4],
                    b'H' => [17, 17, 17, 31, 17, 17, 17],
                    b'R' => [30, 17, 17, 30, 20, 18, 17],
                    b'U' => [17, 17, 17, 17, 17, 17, 14],
                    b'S' => [15, 16, 16, 14, 1, 1, 30],
                    b'D' => [30, 17, 17, 17, 17, 17, 30],
                    b'I' => [31, 4, 4, 4, 4, 4, 31],
                    b'P' => [30, 17, 17, 30, 16, 16, 16],
                    b'L' => [16, 16, 16, 16, 16, 16, 31],
                    b'Y' => [17, 17, 10, 4, 4, 4, 4],
                    _ => [0; 7],
                };
                for y in 0..28 {
                    for x in 0..20 {
                        let px = 32 + column * 24 + x;
                        let py = (if line < 2 {
                            32 + line * 48
                        } else {
                            440 + (line - 2) * 56
                        }) + y;
                        if px < width && py < height && glyph[y / 4] & (16 >> (x / 4)) != 0 {
                            unsafe {
                                ((base as usize + (py * stride + px) * 4) as *mut u32)
                                    .write_volatile(
                                        (255 << (masks & 31))
                                            | (255 << ((masks >> 8) & 31))
                                            | (255 << ((masks >> 16) & 31)),
                                    );
                            }
                        }
                    }
                }
            }
        }
    }
    let mut last_sum = 0;
    for sequence in 1u64..=100 {
        let result = message(2, link | 1, 0);
        let generation = (sequence - 1) / 20 + 1;
        if result >> 56 != generation
            || (result >> 32) & 0xffffff != sequence
            || result & 0xffffffff != sequence * (sequence + 1) / 2
        {
            finish(5);
        }
        last_sum = result & 0xffffffff;
        if !cfg!(skip_draw) {
            for (bar, rgb) in [(80u32, 220u32, 180u32), (80, 140, 240)].iter().enumerate() {
                let top = 472 + bar * 56;
                for y in top..(top + 20).min(height) {
                    for x in 32..width.saturating_sub(32) {
                        let (r, g, b) =
                            if x - 32 < width.saturating_sub(64) * sequence as usize / 100 {
                                *rgb
                            } else {
                                (24, 32, 48)
                            };
                        let color = (r << (masks & 31))
                            | (g << ((masks >> 8) & 31))
                            | (b << ((masks >> 16) & 31));
                        unsafe {
                            ((base as usize + (y * stride + x) * 4) as *mut u32)
                                .write_volatile(color);
                        }
                    }
                }
            }
        }
        message(1, link, sequence);
        if sequence % 20 == 0 && sequence < 100 {
            loop {
                let response = unsafe { call(54, binding, 0) };
                if response.0 == 0 && response.1 != link {
                    expect(2, link | 1, 1);
                    link = response.1;
                    break;
                }
                if response.0 != 0 && response.0 != 6 {
                    finish(6);
                }
                expect(20, 0, 0);
            }
        }
    }

    if !cfg!(skip_draw) {
        let digits = [
            [14u8, 17, 19, 21, 25, 17, 14],
            [4, 12, 4, 4, 4, 4, 14],
            [14, 17, 1, 2, 4, 8, 31],
            [30, 1, 1, 14, 1, 1, 30],
            [2, 6, 10, 18, 31, 2, 2],
            [31, 16, 16, 30, 1, 1, 30],
            [14, 16, 16, 30, 17, 17, 14],
            [31, 1, 2, 4, 8, 8, 8],
            [14, 17, 17, 14, 17, 17, 14],
            [14, 17, 17, 15, 1, 1, 14],
        ];
        for (row, mut value) in [last_sum, 100].into_iter().enumerate() {
            for column in 0..4 {
                let glyph = digits[(value % 10) as usize];
                for y in 0..28 {
                    for x in 0..20 {
                        let px = width.saturating_sub(52 + column * 24) + x;
                        let py = 440 + row * 56 + y;
                        if px < width && py < height && glyph[y / 4] & (16 >> (x / 4)) != 0 {
                            let white = (255 << (masks & 31))
                                | (255 << ((masks >> 8) & 31))
                                | (255 << ((masks >> 16) & 31));
                            unsafe {
                                ((base as usize + (py * stride + px) * 4) as *mut u32)
                                    .write_volatile(white);
                            }
                        }
                    }
                }
                value /= 10;
                if value == 0 {
                    break;
                }
            }
        }
    }
    let end = base + ((bytes + 4095) & !4095);
    unsafe {
        asm!("mov byte ptr [rax], 0", in("rax") end, options(nostack));
    }
    if unsafe { (0x800000 as *const u64).read_volatile() } != 0xd15 {
        finish(7);
    }
    finish(0)
}
