// SPDX-License-Identifier: BSD-2-Clause
#[path = "../prototypes/native-command/byte_compare.rs"] mod byte_compare;
use std::cmp::Ordering;
fn sign(value: i32) -> Ordering { value.cmp(&0) }
#[test]
fn unsigned_order_all_byte_values() {
    for a in 0..=255u8 { for b in 0..=255u8 {
        assert_eq!(sign(unsafe { byte_compare::memcmp(&a,&b,1) }),a.cmp(&b));
    } }
}
#[test]
fn offsets_lengths_equal_and_first_difference() {
    let mut left=[0u8;1056];let mut right=[0u8;1056];
    for offset in 0..32 { for len in [0,1,2,7,15,16,17,31,32,33,63,64,65,127,256,1024] {
        for i in 0..len {left[offset+i]=(i%251) as u8;right[offset+i]=left[offset+i];}
        assert_eq!(unsafe {byte_compare::memcmp(left.as_ptr().add(offset),right.as_ptr().add(offset),len)},0);
        for i in 0..len {
            right[offset+i]=left[offset+i].wrapping_add(1);
            assert_eq!(sign(unsafe {byte_compare::memcmp(left.as_ptr().add(offset),right.as_ptr().add(offset),len)}),left[offset..offset+len].cmp(&right[offset..offset+len]));
            right[offset+i]=left[offset+i];
        }
    } }
}
#[test]
fn zero_length_overlap_and_first_difference_wins() {
    assert_eq!(unsafe {byte_compare::memcmp(std::ptr::null(),std::ptr::null(),0)},0);
    let bytes=[0,1,255,0,0];
    for a in 0..3 { for b in 0..3 {
        assert_eq!(sign(unsafe {byte_compare::memcmp(bytes.as_ptr().add(a),bytes.as_ptr().add(b),3)}),bytes[a..a+3].cmp(&bytes[b..b+3]));
    } }
    let left=[1,255];let right=[2,0];
    assert!(unsafe {byte_compare::memcmp(left.as_ptr(),right.as_ptr(),2)}<0);
}
