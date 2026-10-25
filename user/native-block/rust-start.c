/* SPDX-License-Identifier: BSD-2-Clause */
/* Strict-musl TLS/startup witness; all block work belongs to Rust. */
static _Thread_local volatile unsigned int witness = 17;
unsigned int block_tls_witness(void) { return witness; }
