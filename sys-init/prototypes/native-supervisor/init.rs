// SPDX-License-Identifier: BSD-2-Clause
#![no_std]
#![no_main]
mod adapter;
mod terminal;
mod sample_receipts;
mod raw_sampling;
mod binding;
mod attempt;
mod service; mod service_owner; mod owner_fixture; mod service_pair; mod pair_fixture;
use adapter::{Adapter, Completion, Read, Wait, WaitState, Worker, finish, probes};
fn require(ok: bool, code: u64) { if !ok { finish(code); } }
fn accepted<T>(result: adapter::Result<T>, code: u64) -> T {
    match result { Ok(value) => value, Err(_) => finish(code) }
}
fn release(a: &mut Adapter, wait: Wait) {
    accepted(a.release(wait), 802); require(probes::released(wait), 802);
}
fn await_status(a: &Adapter, wait: Wait) -> Completion {
    for _ in 0..100000 {
        let result = accepted(a.status(wait), 803);
        if result.state != WaitState::Pending { return result; }
        adapter::yield_now();
    }
    finish(803)
}
fn terminal(a: &Adapter, worker: Worker, expected: u64) {
    for _ in 0..100000 {
        let result = accepted(a.observe(worker), 804);
        if result.terminal != 0 { require(result.terminal == expected, 804); return; }
        adapter::yield_now();
    }
    finish(805)
}
fn deadline(a: &Adapter, ticks: u64) -> adapter::InterruptTick {
    accepted(accepted(a.clock(), 800).after(ticks), 800)
}
fn reclaim(a: &mut Adapter, worker: Worker) {
    accepted(a.reclaim(worker), 810); require(probes::reclaimed(worker), 810);
}
#[unsafe(no_mangle)]
#[unsafe(link_section = ".text.entry")]
pub extern "C" fn _start(abi: u64, factory: u64, image: u64, other: u64, channels: u64, observer: u64) -> ! {
    let mut a = accepted(Adapter::new(abi, factory, image, other, channels, observer), 811); if cfg!(simple_pair) || cfg!(pair_provider_loss) || cfg!(pair_stop_error) || cfg!(pair_cleanup_error) { pair_fixture::run(&mut a); } if cfg!(simple_owner) || cfg!(owner_launch_denial) || cfg!(owner_close_error) { owner_fixture::run(&mut a); } if cfg!(native_pair_teardown) || cfg!(provider_skip_owner) || cfg!(provider_skip_seal) || cfg!(provider_interrupt) || cfg!(native_cleaned) || cfg!(cleaned_skip_resources) || cfg!(cleaned_skip_transition) || cfg!(native_issued_reclaim) || cfg!(reclaim_skip_token) || cfg!(reclaim_early_ack) || cfg!(reclaim_keep_reader) || cfg!(reclaim_keep_worker) || cfg!(reclaim_close_error) || cfg!(reclaim_worker_error) || cfg!(native_terminal_application) || cfg!(terminal_skip_owner) || cfg!(terminal_skip_seal) || cfg!(terminal_drop_capture) || cfg!(terminal_corrupt_capture) || cfg!(terminal_source_interrupt) { binding::run_terminal_application(&mut a); } if cfg!(dependent_launch) || cfg!(retire_skip_retain) || cfg!(retire_skip_ack) || cfg!(retire_forget_count) || cfg!(dependent_skip_source) { binding::run_dependent_launch(&mut a); } if cfg!(generated_launch) || cfg!(effect_skip_token) || cfg!(effect_early_ack) || cfg!(effect_keep_writer) || cfg!(effect_busy) { binding::run_generated_launch(&mut a); } if cfg!(native_application) || cfg!(application_skip_transition) || cfg!(application_drop_capture) || cfg!(application_corrupt_capture) { binding::run_native_application(&mut a); } if cfg!(bound_reservation) || cfg!(bound_skip_owner) || cfg!(bound_skip_qualification) || cfg!(bound_skip_token) { binding::run_bound_reservation(&mut a); } if cfg!(composed_history) || cfg!(composed_skip_launch) || cfg!(composed_keep_writer) || cfg!(composed_forget_reader) || cfg!(composed_skip_token) { binding::run_composed_history(&mut a); }
    if cfg!(history_closed) || cfg!(closed_forget_primary) || cfg!(closed_forget_diagnostic) || cfg!(closed_reopen) || cfg!(closed_clear_pending) { binding::run_history_closed(&mut a); }
    if cfg!(history_errno_first) || cfg!(history_errno_middle) || cfg!(history_errno_last) || cfg!(history_errno_forget) || cfg!(history_errno_error) { binding::run_history_errno(&mut a); }
    if cfg!(seal_live) || cfg!(seal_partial_one) || cfg!(seal_partial_two) || cfg!(seal_failed) || cfg!(seal_interrupt_one) || cfg!(seal_interrupt_two) || cfg!(seal_promote) || cfg!(seal_forget_sample) || cfg!(seal_forget_reader) { binding::run_history_sealing(&mut a); }
    if cfg!(history_capacity) || cfg!(capacity_forget_live) || cfg!(capacity_recycle_primary) || cfg!(capacity_recycle_diagnostic) { binding::run_history_capacity(&mut a); }
    if cfg!(guard_denial_unsealed) || cfg!(guard_denial_occupied) || cfg!(guard_denial_forget_reader) || cfg!(guard_denial_clear_spare) { binding::run_guard_denial(&mut a); }
    if cfg!(guard_reoffer) || cfg!(guard_reoffer_produce) { binding::run_guard_reoffer(&mut a); }
    if cfg!(guard_resources) || cfg!(guard_conflict) || cfg!(guard_skip_close) || cfg!(guard_forget_reader) || cfg!(conflict_overwrite_primary) { binding::run_conflict_guard(&mut a); }
    if cfg!(history_index) || cfg!(history_service) || cfg!(history_context) || cfg!(history_target) || cfg!(history_unsealed) || cfg!(history_replay) || cfg!(history_identity) || cfg!(history_skip_token) { binding::run_history(&mut a); }
    if cfg!(interrupt_empty) || cfg!(interrupt_after_first) || cfg!(interrupt_after_status) || cfg!(interrupt_skip_close) || cfg!(interrupt_forget_prefix) || cfg!(interrupt_invent_fact) || cfg!(interrupt_forget_reader) { binding::run_interrupted_sampling(&mut a); }
    if cfg!(sample_bad_boolean) || cfg!(sample_bad_kind) || cfg!(sample_bad_result) || cfg!(sample_bad_live) || cfg!(sample_bad_revision) || cfg!(sample_bad_readiness) || cfg!(sample_skip_close) || cfg!(sample_forget_reader) || cfg!(sample_invent_errno) { binding::run_malformed_sampling(&mut a); }
    if cfg!(raw_terminal) || cfg!(raw_first_stale) || cfg!(raw_status_stale) || cfg!(raw_observe_stale) || cfg!(raw_forget_prefix) { raw_sampling::run(&mut a); }
    if cfg!(sampling_status_stale) || cfg!(sampling_observe_stale) || cfg!(sampling_preflight) || cfg!(sampling_target) || cfg!(sampling_held) || cfg!(sampling_stale) || cfg!(sampling_skip_token) || cfg!(sampling_skip_pending) { binding::run_sampling(&mut a); }
    if cfg!(terminal_fault_collision) || cfg!(terminal_stop_collision) || cfg!(terminal_live) || cfg!(terminal_ignore_kind) { terminal::run(&mut a); }
    if cfg!(missing_channel) || cfg!(missing_launch) || cfg!(missing_skip_close) || cfg!(missing_invent_error) || cfg!(missing_forget_writer) { binding::run_missing_return(&mut a); }
    if cfg!(launch_receipt) || cfg!(launch_receipt_close) || cfg!(launch_keep_writer) || cfg!(launch_early_generation) { binding::run_launch_receipt(&mut a); }
    if cfg!(receipt_channel) || cfg!(receipt_identity) || cfg!(receipt_close) || cfg!(receipt_skip_phase) || cfg!(receipt_forget_writer) { binding::run_channel_receipt(&mut a); }
    if cfg!(generation_exhaustion) || cfg!(generation_skip_guard) || cfg!(generation_consume_denied) { binding::run_generation_exhaustion(&mut a); }
    if cfg!(expected_target) { binding::run_expected_target(&mut a); }
    if cfg!(target_mismatch) || cfg!(target_wrong_generation) || cfg!(target_skip_match) || cfg!(target_forget_worker) { binding::run_target_mismatch(&mut a); }
    if cfg!(binding_creation_busy) || cfg!(binding_reopen_token) { binding::run_creation_busy(&mut a); }
    if cfg!(binding_launch_busy) || cfg!(binding_busy_forget) { binding::run_launch_busy(&mut a); }
    if cfg!(binding_failure) || cfg!(binding_forget_writer) { binding::run_binding_failure(&mut a); }
    if cfg!(binding_preflight) || cfg!(binding_skip_pending) { binding::run_preflight(&mut a); }
    if cfg!(binding_admission) || cfg!(binding_skip_token) { binding::run(&mut a); }
    if cfg!(service_loss_stop) || cfg!(service_loss_return) ||
       cfg!(service_loss_bad_stop) || cfg!(service_loss_bad_admission) {
        service::run_dependency_loss(&mut a);
    }
    if cfg!(service_cancel_retry) || cfg!(service_cancel_ready) ||
       cfg!(service_cancel_bad_retry) || cfg!(service_cancel_bad_ready) {
        service::run_retry_cancellation(&mut a);
    }
    if cfg!(service_budget_silent) || cfg!(service_budget_malformed) ||
       cfg!(service_budget_extra) || cfg!(service_budget_short) {
        service::run_retry_budget(&mut a);
    }
    if cfg!(service_retry_silent) || cfg!(service_retry_malformed) ||
       cfg!(service_retry_bad_cleanup) || cfg!(service_retry_no_fresh) {
        service::run_readiness_retry(&mut a);
    }
    if cfg!(service_silent) || cfg!(service_malformed) { service::run_readiness_failure(&mut a); }
    if cfg!(service_return) || cfg!(service_return_early) || cfg!(service_return_bad_dependency) {
        service::run_return(&mut a);
    }
    if cfg!(service_lifecycle) || cfg!(service_bad_deadline) || cfg!(service_bad_terminal) ||
        cfg!(service_bad_dependency) || cfg!(service_bad_generation) { service::run(&mut a); }
    if cfg!(routed_partial_cleanup) || cfg!(route_cleanup_event) || cfg!(route_cleanup_forget) { attempt::run_routed_partial_cleanup(&mut a); }
    if cfg!(routed_stop_error) || cfg!(route_error_drop) || cfg!(route_error_swallow) { attempt::run_routed_stop_error(&mut a); }
    if cfg!(routed_live_stop) || cfg!(route_stop_event) || cfg!(route_stop_ack) { attempt::run_routed_live_stop(&mut a); }
    if cfg!(routed_cancellation) || cfg!(route_cancel_drop) || cfg!(route_cancel_reset) { attempt::run_routed_cancellation(&mut a); }
    if cfg!(routed_replacement) || cfg!(replacement_events) || cfg!(route_skip_delivery) || cfg!(route_old_generation) { attempt::run_routed_replacement(&mut a); }
    if cfg!(rejected_events) || cfg!(event_wrong_error) || cfg!(event_failure_early) { attempt::run_rejected_events(&mut a); }
    if cfg!(native_events) || cfg!(event_drop_busy) || cfg!(event_keep_launch) { attempt::run_events(&mut a); }
    if cfg!(attempt_reader_error) || cfg!(attempt_reader_forget) { attempt::run_reader_error(&mut a); }
    if cfg!(attempt_release_error) || cfg!(attempt_release_forget) { attempt::run_release_error(&mut a); }
    if cfg!(attempt_partial_cleanup) || cfg!(attempt_partial_forget) { attempt::run_partial_cleanup(&mut a); }
    if cfg!(attempt_stop_error) || cfg!(attempt_stop_forget) { attempt::run_stop_error(&mut a); }
    if cfg!(attempt_deadline) || cfg!(attempt_bad_precedence) { attempt::run_deadline(&mut a); }
    if cfg!(attempt_intent) || cfg!(attempt_bad_intent) { attempt::run_intent(&mut a); }
    if cfg!(attempt_wait) || cfg!(attempt_wait_forget) || cfg!(attempt_wait_skip_release) {
        attempt::run_wait(&mut a);
    }
    if cfg!(attempt_retry) || cfg!(attempt_bad_writer) || cfg!(attempt_bad_guard) {
        attempt::run(&mut a);
    }
    if cfg!(acquisition_cleanup) || cfg!(acquisition_bad_writer) || cfg!(acquisition_bad_wait) {
        acquisition_cleanup(&mut a);
    }
    if cfg!(adapter_edges) || cfg!(bad_clean) { adapter_edges(&mut a); }
    require(probes::foreign_clock(), 812);
    let (owner_read, owner_write) = accepted(a.channel(), 808);
    let owner = accepted(a.launch(0, owner_write, b"exit"), 806);
    require(probes::transferred(owner_write), 807);
    // Revision zero predates any readiness/terminal transition.
    let end = deadline(&a, 100);
    let changed = accepted(a.register(owner, 0, end), 801);
    require(await_status(&a, changed).state == WaitState::Changed, 813); release(&mut a, changed);
    terminal(&a, owner, 18);
    let snapshot = accepted(a.observe(owner), 814);
    require(snapshot.revision == 2 && snapshot.terminal == 18 && snapshot.historical_ready, 814);
    let now = deadline(&a, 0);
    let expired = accepted(a.register(owner, snapshot.revision, now), 801);
    require(accepted(a.status(expired), 821).state ==
        if cfg!(bad_deadline) { WaitState::Changed } else { WaitState::Timeout }, 821);
    release(&mut a, expired);
    let future = deadline(&a, 2);
    let timed = accepted(a.register(owner, 2, future), 801); let result = await_status(&a, timed);
    require(result.state == WaitState::Timeout && result.tick >= future, 815);
    require(accepted(a.cancel(timed), 816) == result && accepted(a.status(timed), 816) == result, 816);
    release(&mut a, timed);
    let end = deadline(&a, 100);
    let canceled = accepted(a.register(owner, 2, end), 801);
    require(probes::busy(owner, 2, end), 817);
    require(matches!(a.register(owner, 2, end), Err(adapter::Error { operation: 0x25002, errno: 16 })), 817);
    require(accepted(a.cancel(canceled), 818).state == WaitState::Cancelled &&
        accepted(a.status(canceled), 818).state == WaitState::Cancelled, 818); release(&mut a, canceled);
    let (helper_read, helper_write) = accepted(a.channel(), 808);
    let helper = accepted(a.launch(1, helper_write, b"live"), 806);
    require(probes::transferred(helper_write), 807);
    let end = deadline(&a, 100);
    let helper_wait = accepted(a.register(helper, 0, end), 801);
    require(await_status(&a, helper_wait).state == WaitState::Changed, 819); release(&mut a, helper_wait);
    let snapshot = accepted(a.observe(helper), 820);
    require(snapshot.terminal == 0 && snapshot.historical_ready, 820);
    let end = deadline(&a, 100);
    let pending = accepted(a.register(owner, 2, end), 801);
    if cfg!(owner_exit) { adapter::exit_owner(); }
    if cfg!(owner_fault) { adapter::fault_owner(); }
    // A queued byte does not establish current liveness or authority.
    require(matches!(accepted(a.read(owner_read), 823), Read::Byte(42)), 823);
    let admissible = accepted(a.observe(owner), 822).terminal == 0;
    require(admissible == cfg!(bad_late), 822);
    require(matches!(accepted(a.read(owner_read), 824), Read::Eof), 824);
    accepted(a.close(owner_read), 809); reclaim(&mut a, owner);
    require(accepted(a.status(pending), 825).state == WaitState::Reclaimed, 825); release(&mut a, pending);
    require(accepted(a.observe(helper), 826).terminal == 0 &&
        matches!(accepted(a.read(helper_read), 826), Read::Byte(42)), 826);
    require(accepted(a.observe(helper), 826).terminal == 0, 826);
    accepted(a.stop(helper), 827); terminal(&a, helper, 144);
    require(matches!(accepted(a.read(helper_read), 827), Read::Eof), 827);
    accepted(a.close(helper_read), 809); reclaim(&mut a, helper);
    let (fresh, writer) = accepted(a.channel(), 808);
    require(fresh != owner_read && probes::closed(owner_read) &&
        matches!(accepted(a.read(fresh), 828), Read::Pending), 828);
    let replacement = accepted(a.launch(0, writer, b"stale"), 806);
    require(probes::transferred(writer), 807); require(replacement != owner, 828);
    terminal(&a, replacement, 34);
    require(!accepted(a.observe(replacement), 828).historical_ready, 828);
    accepted(a.close(fresh), 809); reclaim(&mut a, replacement);
    require(a.clean(), 830); finish(100)
}
#[panic_handler]
fn panic(_: &core::panic::PanicInfo) -> ! { finish(899) }

// Separate bounded workload keeps edge checks within the immutable code page.
fn adapter_edges(a: &mut Adapter) -> ! {
    require(a.clean(), 831);
    let now = accepted(a.clock(), 800);
    let one = accepted(now.after(1), 800);
    require(matches!(one.after(u64::MAX), Err(adapter::Error { operation: 0x25000, errno: 75 })), 832);
    let (reader, writer) = accepted(a.channel(), 808);
    require(!a.clean(), 831);
    require(matches!(a.launch(2, writer, b"exit"), Err(adapter::Error { operation: 0x23001, errno: 22 })), 833);
    accepted(a.close_writer(writer), 833);
    accepted(a.close(reader), 833);
    require(a.clean(), 831);
    for (index, slot) in [0, 0].into_iter().enumerate() {
        let (reader, writer) = accepted(a.channel(), 808);
        let worker = accepted(a.launch(slot, writer, b"exit"), 806);
        require(!a.clean(), 831);
        terminal(a, worker, 18);
        if index == 0 {
            for _ in 0..64 {
                let end = deadline(a, 0);
                let wait = accepted(a.register(worker, 2, end), 834);
                require(accepted(a.status(wait), 834).state == WaitState::Timeout, 834);
                require(!a.clean(), 831);
                release(a, wait);
                require(matches!(a.release(wait), Err(adapter::Error { operation: 0x25005, errno: 9 })), 835);
            }
            let end = deadline(a, 0);
            require(matches!(a.register(worker, 2, end), Err(adapter::Error { operation: 0x25002, errno: 28 })), 836);
            require(probes::exhausted(worker, end), 836);
        }
        // Preserve the consumed two-worker overlap. Sequential cross-slot reuse
        // is separately retained as a failing producer-order probe.
        if index == 0 {
            let (peer_reader, peer_writer) = accepted(a.channel(), 808);
            let peer = accepted(a.launch(1, peer_writer, b"exit"), 806);
            terminal(a, peer, 18);
            accepted(a.close(reader), 809); reclaim(a, worker);
            accepted(a.close(peer_reader), 809); reclaim(a, peer);
        } else {
            accepted(a.close(reader), 809); reclaim(a, worker);
        }
        require(matches!(a.observe(worker), Err(adapter::Error { operation: 0x25001, errno: 9 })), 837);
        require(a.clean(), 831);
    }
    finish(100)
}

// A distinct bounded witness: factory failure, retained endpoints and retained wait.
fn acquisition_cleanup(a: &mut Adapter) -> ! {
    let (first_read, first_write) = accepted(a.channel(), 950);
    let (second_read, second_write) = accepted(a.channel(), 950);
    require(matches!(a.channel(), Err(adapter::Error { operation: 0x24000, errno: 16 })), 950);
    require(probes::rejected_launch(first_write), 954);
    if !cfg!(acquisition_bad_writer) { accepted(a.close_writer(first_write), 951); }
    accepted(a.close(first_read), 951);
    accepted(a.close_writer(second_write), 951);
    accepted(a.close(second_read), 951);
    require(a.clean(), 951);
    for (index, slot) in [0, 1, 0].into_iter().enumerate() {
        let (reader, writer) = accepted(a.channel(), 950);
        let worker = accepted(a.launch(slot, writer, b"exit"), 950);
        if index == 0 { require(probes::first_generation(worker), 954); }
        terminal(a, worker, 18);
        let snapshot = accepted(a.observe(worker), 952);
        let end = deadline(a, 100000);
        let wait = accepted(a.register(worker, snapshot.revision, end), 952);
        accepted(a.close(reader), 952);
        reclaim(a, worker);
        require(accepted(a.status(wait), 952).state == WaitState::Reclaimed, 952);
        if !cfg!(acquisition_bad_wait) { release(a, wait); }
        require(a.clean(), 953);
    }
    finish(100)
}
