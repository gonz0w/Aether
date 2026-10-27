const std = @import("std");
const Af09Mode = @import("kernel/native_af09_drain.zig").Mode;

pub fn build(b: *std.Build) void {
    if (!std.mem.eql(u8, @import("builtin").zig_version_string, "0.16.0"))
        @panic("Aether requires Zig 0.16.0");
    const release_artifact = b.option(bool, "release-artifact", "Exclude all intentional negative-test controls from this artifact") orelse false;
    const native_af09_drain = b.option([]const u8, "native-af09-drain", "Approved private AF09 admission/drain diagnostic case; none disables") orelse "none";
    const native_af09_drain_mode = std.meta.stringToEnum(Af09Mode, native_af09_drain) orelse @panic("unknown native-af09-drain case");
    const af09_diagnostic = native_af09_drain_mode != .none;
    const target = b.resolveTargetQuery(.{
        .cpu_arch = .x86_64,
        .os_tag = .freestanding,
        .abi = .none,
        .cpu_features_sub = std.Target.x86.featureSet(&.{ .mmx, .sse, .sse2, .avx, .avx2 }),
        .cpu_features_add = std.Target.x86.featureSet(&.{.soft_float}),
    });
    const options = b.addOptions();
    options.addOption([]const u8, "native_af09_drain", native_af09_drain);
    const smp = b.option(bool, "smp", "Run the two-core kernel bring-up probe after M2") orelse true;
    options.addOption(bool, "smp_test", smp);
    const native_c_image = b.option([]const u8, "native-c-image", "Explicit native C experiment envelope; separate from lifecycle v1");
    const native_fs_session = b.option(bool, "native-fs-session", "Private seven-domain filesystem/SESSION composition") orelse false;
    options.addOption(bool, "native_fs_session", native_fs_session);
    const native_fs_session_init = b.option(bool, "native-fs-session-init", "Separate private four-page filesystem/sys-init owner") orelse false;
    if (native_fs_session_init and !native_fs_session) @panic("filesystem init owner requires the combined profile");
    options.addOption(bool, "native_fs_session_init", native_fs_session_init);
    const native_fs_owner_data = b.option(bool, "native-fs-owner-data", "Separate ABI30 init owner with two private data pages inside its existing quota") orelse false;
    if (native_fs_owner_data and !native_fs_session_init) @panic("filesystem owner data requires the separate init profile");
    options.addOption(bool, "native_fs_owner_data", native_fs_owner_data);
    const native_fs_owner_stack = b.option(bool, "native-fs-owner-stack", "Separate ABI31 boot owner with an 8 KiB guarded stack inside its existing quota") orelse false;
    if (native_fs_owner_stack and !native_fs_owner_data) @panic("filesystem owner stack requires the separate data profile");
    options.addOption(bool, "native_fs_owner_stack", native_fs_owner_stack);
    const native_fs_application_profile = b.option(bool, "native-fs-application-profile", "Separate bounded Zsh application composition; existing ABI31 owner") orelse false;
    if (native_fs_application_profile and (!native_fs_owner_stack or release_artifact)) @panic("filesystem application profile requires its private ABI31 owner-stack profile");
    options.addOption(bool, "native_fs_application_profile", native_fs_application_profile);
    const block_test = b.option([]const u8, "block-test", "Disposable disk bring-up: write or verify");
    if (block_test) |mode| {
        if (smp or native_c_image != null or (!std.mem.eql(u8, mode, "write") and !std.mem.eql(u8, mode, "verify"))) @panic("block test requires write/verify, -Dsmp=false and no native image");
    }
    const entropy_test = b.option([]const u8, "entropy-test", "Isolated BSP entropy lab: draw/partial/head/length/index/timeout/accept_length");
    const entropy_mode = if (entropy_test) |mode| std.meta.stringToEnum(enum { draw, partial, head, length, index, timeout, accept_length }, mode) orelse @panic("invalid entropy test mode") else .draw;
    if (entropy_test != null and (smp or native_c_image != null or block_test != null)) @panic("entropy test requires -Dsmp=false and no native image or block test");
    if (entropy_test != null and release_artifact) @panic("release artifact contains an entropy lab control");
    options.addOption(bool, "entropy_test", entropy_test != null);
    options.addOption(@TypeOf(entropy_mode), "entropy_mode", entropy_mode);
    const backing_test = b.option([]const u8, "backing-test", "Isolated BSP backing reservation and fresh-root alias lab (see NATIVE-BACKING)");
    const backing_mode = if (backing_test) |mode| std.meta.stringToEnum(enum { reserve, overlap, corrupt, skip_clear, alias, alias_ro, alias_nx, alias_user, alias_detach, alias_skip_ro, alias_skip_nx, alias_skip_user, alias_skip_detach }, mode) orelse @panic("invalid backing test mode") else .reserve;
    if (backing_test != null and (smp or native_c_image != null or block_test != null or entropy_test != null)) @panic("backing test requires -Dsmp=false and no native image, block or entropy test");
    if (backing_test != null and release_artifact) @panic("release artifact contains a backing lab control");
    const backing_alias = backing_test != null and switch (backing_mode) {
        .reserve, .overlap, .corrupt, .skip_clear => false,
        else => true,
    };
    options.addOption(bool, "backing_alias", backing_alias);
    options.addOption(bool, "backing_test", backing_test != null);
    options.addOption(@TypeOf(backing_mode), "backing_mode", backing_mode);
    options.addOption(bool, "block_test", block_test != null);
    options.addOption(bool, "block_verify", if (block_test) |mode| std.mem.eql(u8, mode, "verify") else false);
    options.addOption(bool, "native_c_test", native_c_image != null);
    const native_init_sustained = b.option(bool, "native-init-sustained", "Opt-in serial sustained init profile") orelse false;
    if (native_init_sustained and (native_c_image == null or smp)) @panic("sustained init requires a native image and -Dsmp=false");
    options.addOption(bool, "native_init_sustained", native_init_sustained);
    const native_process_freeze = b.option(bool, "native-process-freeze", "Opt-in cooperating process freeze boundary") orelse false;
    if (native_process_freeze and (native_c_image == null or smp)) @panic("native process freeze requires a native image and -Dsmp=false");
    options.addOption(bool, "native_process_freeze", native_process_freeze);
    options.addOption(bool, "native_freeze_skip_park", negativeOption(b, release_artifact, af09_diagnostic, "native-freeze-skip-park", "Skip process parking for rejection witness"));
    options.addOption(bool, "native_freeze_ignore_token", negativeOption(b, release_artifact, af09_diagnostic, "native-freeze-ignore-token", "Ignore freeze token for rejection witness"));
    const native_runner_local = b.option(bool, "native-runner-local", "Select four-reclaim runner-only fixture oracle") orelse false;
    if (native_runner_local and (native_c_image == null or smp)) @panic("native runner local requires a native image and -Dsmp=false");
    options.addOption(bool, "native_runner_local", native_runner_local);
    const native_runner_files = b.option(bool, "native-runner-files", "Select six-reclaim runner and file-service composition") orelse false;
    if (native_runner_files and !native_runner_local) @panic("native runner files requires runner-local fixture");
    options.addOption(bool, "native_runner_files", native_runner_files);
    const native_parent_identity = b.option(bool, "native-parent-identity", "Select bounded direct-launcher parent identity") orelse false;
    if (native_parent_identity and !native_runner_local) @panic("native parent identity requires runner-local fixture");
    options.addOption(bool, "native_parent_identity", native_parent_identity);
    const native_signal_actions = b.option(bool, "native-signal-actions", "Select private action-copy qualification") orelse false;
    if (native_signal_actions and !native_runner_local) @panic("native signal actions require runner-local fixture");
    options.addOption(bool, "native_signal_actions", native_signal_actions);
    const native_signal_public = b.option(bool, "native-signal-public", "Select experimental musl action routing") orelse false;
    if (native_signal_public and !native_signal_actions) @panic("native public actions require private actions");
    options.addOption(bool, "native_signal_public", native_signal_public);
    const native_signal_suspend = b.option(bool, "native-signal-suspend", "Select bounded single-context child notification and suspension") orelse false;
    if (native_signal_suspend and !native_signal_public) @panic("native suspension requires public signal actions");
    options.addOption(bool, "native_signal_suspend", native_signal_suspend);
    const native_signal_mask_delivery = b.option(bool, "native-signal-mask-delivery", "Select private handler delivery on successful mask return") orelse false;
    if (native_signal_mask_delivery and !native_signal_actions) @panic("native mask delivery requires private actions");
    options.addOption(bool, "native_signal_mask_delivery", native_signal_mask_delivery);
    const native_signal_termination = b.option(bool, "native-signal-termination", "Select private signal-capable owner qualification") orelse false;
    if (native_signal_termination and !native_signal_actions) @panic("native signal termination requires private actions");
    options.addOption(bool, "native_signal_termination", native_signal_termination);
    options.addOption(bool, "native_signal_actions_shared", negativeOption(b, release_artifact, af09_diagnostic, "native-signal-actions-shared", "Share action records for isolation rejection testing"));
    const native_memory = b.option(bool, "native-memory", "Enable scoped native anonymous memory v1") orelse false;
    if (native_memory and (native_c_image == null or smp)) @panic("native memory requires a native image and -Dsmp=false");
    options.addOption(bool, "native_memory", native_memory);
    const native_backing = b.option(bool, "native-backing", "Private external backing at unchanged native quotas") orelse false;
    if (native_backing and !native_memory) @panic("native backing requires the memory profile");
    options.addOption(bool, "native_backing", native_backing);
    const backing_skip_ro = negativeOption(b, release_artifact, af09_diagnostic, "native-backing-skip-alias-ro", "Omit external immutable alias narrowing for rejection");
    if (backing_skip_ro and !native_backing) @panic("native backing alias control requires the external profile");
    options.addOption(bool, "native_backing_skip_alias_ro", backing_skip_ro);
    const native_process_copy = b.option(bool, "native-process-copy", "Opt-in private copy of a frozen worker") orelse false;
    if (native_process_copy and (!native_process_freeze or !native_memory)) @panic("native process copy requires freeze and memory");
    options.addOption(bool, "native_process_copy", native_process_copy);
    options.addOption(bool, "native_copy_slot_tid", negativeOption(b, release_artifact, af09_diagnostic, "native-copy-slot-tid", "Return legacy slot TID in the copy profile for rejection"));
    options.addOption(bool, "native_copy_fail_stage", negativeOption(b, release_artifact, af09_diagnostic, "native-copy-fail-stage", "Fail after staging private pages"));
    options.addOption(bool, "native_copy_skip_zero", negativeOption(b, release_artifact, af09_diagnostic, "native-copy-skip-zero", "Skip failed-copy zeroing"));
    options.addOption(bool, "native_copy_share", negativeOption(b, release_artifact, af09_diagnostic, "native-copy-share", "Share writable anonymous pages for isolation rejection"));
    options.addOption(bool, "native_copy_lose_anonymous", negativeOption(b, release_artifact, af09_diagnostic, "native-copy-lose-anonymous", "Lose anonymous ownership for rejection"));
    const native_threads = b.option(bool, "native-threads", "One additional native context per worker") orelse false;
    if (native_threads and !native_memory) @panic("native threads require native memory");
    const native_entropy = b.option(bool, "native-entropy", "Explicit bounded per-worker entropy grant in the memory/thread fixture") orelse false;
    if (native_entropy and (!native_memory or !native_threads)) @panic("native entropy requires memory and threads");
    options.addOption(bool, "native_entropy", native_entropy);
    options.addOption(bool, "native_entropy_skip_quota", negativeOption(b, release_artifact, af09_diagnostic, "native-entropy-skip-quota", "Omit entropy quota consumption for semantic rejection"));
    if (native_parent_identity and native_threads and !native_fs_session) @panic("native parent identity requires single-context workers");
    options.addOption(bool, "native_threads", native_threads);
    const native_copy_signals = b.option(bool, "native-copy-signals", "Opt-in single-context signal-copy experiment") orelse false;
    if (native_copy_signals and (!native_process_copy or !native_signal_actions or (native_threads and !native_fs_session))) @panic("native signal copy requires private actions, process copy and one context");
    options.addOption(bool, "native_copy_signals", native_copy_signals);
    options.addOption(bool, "native_copy_signals_drop", negativeOption(b, release_artifact, af09_diagnostic, "native-copy-signals-drop", "Drop inherited dispositions for rejection"));
    options.addOption(bool, "native_copy_signals_pending", negativeOption(b, release_artifact, af09_diagnostic, "native-copy-signals-pending", "Duplicate pending occurrences for rejection"));
    options.addOption(bool, "native_copy_signals_parent", negativeOption(b, release_artifact, af09_diagnostic, "native-copy-signals-parent", "Clear parent pending state for rejection"));

    options.addOption(bool, "native_threads_skip_pin", negativeOption(b, release_artifact, af09_diagnostic, "native-threads-skip-pin", "Omit child mapping pins for rejection test"));
    options.addOption(bool, "native_wait_skip_compare", negativeOption(b, release_artifact, af09_diagnostic, "native-wait-skip-compare", "Omit wait value comparison for rejection test"));
    options.addOption(bool, "native_init_large_dirty_tail", negativeOption(b, release_artifact, af09_diagnostic, "native-init-large-dirty-tail", "Corrupt init v2 code tail for rejection testing"));
    options.addOption(bool, "native_requeue_skip_move", negativeOption(b, release_artifact, af09_diagnostic, "native-requeue-skip-move", "Break requeue destination for rejection testing"));
    options.addOption(bool, "native_wake_unlimited", negativeOption(b, release_artifact, af09_diagnostic, "native-wake-unlimited", "Break bounded wake for semantic rejection testing"));
    const native_thread_pair = b.option(bool, "native-thread-pair", "Enable bounded two-child native experiment") orelse false;
    options.addOption(bool, "native_thread_pair", native_thread_pair);
    const native_clock = b.option(bool, "native-clock", "Opt-in BSP q35 elapsed clock and absolute wait") orelse false;
    if (native_clock and (!native_threads or !native_thread_pair)) @panic("native clock requires memory, threads and pair");
    options.addOption(bool, "native_clock", native_clock);
    const native_rtc = b.option(bool, "native-rtc", "Opt-in BSP q35 TCG raw RTC observation") orelse false;
    if (native_rtc and !native_clock) @panic("native RTC requires native clock");
    options.addOption(bool, "native_rtc", native_rtc);
    options.addOption(bool, "native_clock_ticks", negativeOption(b, release_artifact, af09_diagnostic, "native-clock-ticks", "Substitute delivered interrupts for elapsed time rejection"));
    options.addOption(bool, "native_clock_skip_wait", negativeOption(b, release_artifact, af09_diagnostic, "native-clock-skip-wait", "Complete a future wait immediately for rejection"));

    const native_thread_reuse = b.option(bool, "native-thread-reuse", "Allow 512 owner-local lifetime admissions; live slots unchanged") orelse false;
    if (native_thread_reuse and (!native_memory or !native_threads or !native_thread_pair)) @panic("native thread reuse requires memory, threads and pair");
    options.addOption(bool, "native_thread_reuse", native_thread_reuse);
    const native_thread_origin = b.option(bool, "native-thread-origin", "Allow granted worker-origin creation and exact-ID reaping") orelse false;
    if (native_thread_origin and !native_thread_reuse) @panic("native thread origin requires the reuse profile");
    options.addOption(bool, "native_thread_origin", native_thread_origin);
    options.addOption(bool, "native_child_same_id", negativeOption(b, release_artifact, af09_diagnostic, "native-child-same-id", "Reuse child identity for rejection test"));
    options.addOption(bool, "native_mask_skip_inherit", negativeOption(b, release_artifact, af09_diagnostic, "native-mask-skip-inherit", "Omit child mask inheritance for rejection test"));
    options.addOption(bool, "native_wait_skip_pin", negativeOption(b, release_artifact, af09_diagnostic, "native-wait-skip-pin", "Omit blocked-word pins for rejection test"));
    const native_memory_large = b.option(bool, "native-memory-large", "Opt-in 8 MiB native backing experiment") orelse false;
    if (native_memory_large and !native_memory) @panic("large backing requires native memory");
    options.addOption(bool, "native_memory_large", native_memory_large);
    const native_image_large = b.option(bool, "native-image-large", "Opt-in large static startup/supervision image") orelse false;
    if (native_image_large and !native_memory_large) @panic("large image requires large backing");
    options.addOption(bool, "native_image_large", native_image_large);
    const native_service_memory = b.option(bool, "native-service-memory", "Private single larger service memory owner") orelse false;
    if (native_service_memory and (!native_backing or !native_image_large)) @panic("service memory requires external backing and the large image profile");
    options.addOption(bool, "native_service_memory", native_service_memory);
    const native_service_block = b.option(bool, "native-service-block", "Compose region-v2 with explicit large service backing") orelse false;
    if (native_service_block and !native_service_memory) @panic("service block requires service memory");
    options.addOption(bool, "native_service_block", native_service_block);
    const native_service_workers = b.option(bool, "native-service-workers", "Private 82-live-worker service owner with small peers") orelse false;
    if (native_service_workers and (!native_service_memory or !native_thread_origin)) @panic("service workers require service memory and thread origin/reuse");
    options.addOption(bool, "native_service_workers", native_service_workers);
    const native_service_channel = b.option(bool, "native-service-channel", "Private storage worker with admission-bound request/reply channels") orelse false;
    if (native_service_channel and (!native_service_block or !native_service_workers or !native_entropy)) @panic("service channel requires block, workers and entropy");
    options.addOption(bool, "native_service_channel", native_service_channel);
    const native_service_channel_wait = b.option(bool, "native-service-channel-wait", "Private primary-only storage channel waits; helpers remain schedulable") orelse false;
    if (native_service_channel_wait and !native_service_channel) @panic("storage channel wait requires storage channel profile");
    options.addOption(bool, "native_service_channel_wait", native_service_channel_wait);
    const native_service_activation = b.option(bool, "native-service-activation", "Private storage readiness witness with at most two supervisor code pages") orelse false;
    if (native_service_activation and !native_service_channel_wait) @panic("storage activation requires primary channel waits");
    options.addOption(bool, "native_service_activation", native_service_activation);
    const service_cleanup_trace = b.option(bool, "native-service-cleanup-trace", "Private service terminal/reclaim boundary diagnostics") orelse false;
    if (service_cleanup_trace and (native_c_image == null or smp or !native_service_workers or !native_service_block)) @panic("cleanup trace requires BSP native service workers and block");
    options.addOption(bool, "native_service_cleanup_trace", service_cleanup_trace);
    const service_skip_workers = negativeOption(b, release_artifact, af09_diagnostic, "native-service-workers-skip-rebind", "Omit worker view reconstruction after reset");
    if (service_skip_workers and !native_service_workers) @panic("worker rebind control requires the service workers profile");
    options.addOption(bool, "native_service_workers_skip_rebind", service_skip_workers);
    const service_skip_budget = negativeOption(b, release_artifact, af09_diagnostic, "native-service-skip-image-budget", "Omit small owner image budget preflight for rejection");
    if (service_skip_budget and !native_service_memory) @panic("service image control requires the service memory profile");
    options.addOption(bool, "native_service_skip_image_budget", service_skip_budget);
    const native_process_exec = b.option(bool, "native-process-exec", "Bounded frozen image replacement with explicit publication") orelse false;
    if (native_process_exec and (!native_process_freeze or !native_memory or ((native_threads or native_memory_large or native_image_large) and !native_fs_session))) @panic("native exec requires bounded single-context memory and freeze");
    options.addOption(bool, "native_process_exec", native_process_exec);
    const native_pipeline_capacity = b.option(bool, "native-pipeline-capacity", "Opt-in five-worker connections capacity witness") orelse false;
    if (native_pipeline_capacity and (!native_memory or ((native_threads or native_memory_large or native_image_large) and !native_fs_session))) @panic("pipeline capacity requires bounded single-context native memory");
    options.addOption(bool, "native_pipeline_capacity", native_pipeline_capacity);
    const native_session_lifecycle = b.option(bool, "native-session-lifecycle", "Opt-in serial SESSION owner lifecycle profile") orelse false;
    if (native_session_lifecycle and (!native_pipeline_capacity or !native_process_copy or !native_process_exec or !native_copy_signals or !native_signal_public or !native_runner_local or !native_parent_identity or native_init_sustained)) @panic("SESSION lifecycle requires capacity, copy, exec, signal copy/public, local runner and parent identity; excludes sustained init");
    options.addOption(bool, "native_session_lifecycle", native_session_lifecycle);
    if ((native_service_channel_wait or native_service_activation) and (release_artifact or native_c_image == null or smp or !service_cleanup_trace or native_init_sustained or (native_session_lifecycle and !native_fs_session))) @panic("storage channel wait requires private BSP storage cleanup profile");
    const service_zpl_budget = b.option(bool, "native-service-zpl-budget", "Approved private ZPL writer6000-tick diagnostic") orelse false;
    if (service_zpl_budget and (release_artifact or native_c_image == null or smp or !service_cleanup_trace or !native_service_workers or !native_service_block or !native_clock or !native_rtc or !native_entropy or native_init_sustained or (native_session_lifecycle and !native_fs_session))) @panic("ZPL tick budget requires the private BSP service writer diagnostic");
    options.addOption(bool, "native_service_zpl_budget", service_zpl_budget);
    const service_lifetime = b.option(bool, "native-service-lifetime", "Separate private storage idle lifetime; AENBD005 owner ABI27") orelse false;
    if (service_lifetime and (!native_service_activation or !service_zpl_budget or release_artifact or native_c_image == null or smp or !service_cleanup_trace or !native_service_workers or !native_service_block or !native_clock or !native_rtc or !native_entropy or native_init_sustained or native_session_lifecycle)) @panic("storage lifetime requires the separate private activation writer closure");
    options.addOption(bool, "native_service_lifetime", service_lifetime);
    if (native_fs_session and (release_artifact or native_c_image == null or smp or
        !native_session_lifecycle or !native_service_activation or !service_zpl_budget or
        !native_service_workers or !native_service_block or !service_cleanup_trace or
        !native_clock or !native_rtc or !native_entropy or !native_threads or
        native_init_sustained or service_lifetime))
        @panic("filesystem SESSION requires its exact private BSP writer and process closure");
    if (native_fs_application_profile and (!native_process_copy or !native_process_exec or !native_memory or !native_backing or !native_service_memory or !native_image_large or !native_pipeline_capacity))
        @panic("filesystem application profile requires its bounded memory, copy, exec and process closure");
    if (af09_diagnostic and (release_artifact or smp or native_c_image == null or
        !native_fs_owner_stack or native_fs_application_profile or service_lifetime or
        !native_fs_session or !native_service_channel_wait or !native_process_copy or
        !native_process_exec or !native_parent_identity))
        @panic("AF09 drain requires its private BSP ABI31 filesystem owner and process closure");
    const native_exec_denial = b.option(bool, "native-exec-denial", "Select exact four-reclaim failed-exec fixture completion") orelse false;
    if (native_exec_denial and (!native_process_copy or !native_process_exec or !native_copy_signals or !native_runner_local)) @panic("native exec denial requires copy, exec, signal copy and local runner");
    options.addOption(bool, "native_exec_denial", native_exec_denial);

    options.addOption(bool, "native_exec_copy", negativeOption(b, release_artifact, af09_diagnostic, "native-exec-copy", "Copy an unpublished replacement for rejection testing"));
    options.addOption(bool, "native_exec_early", negativeOption(b, release_artifact, af09_diagnostic, "native-exec-early", "Publish replacement before owner confirmation"));
    options.addOption(bool, "native_exec_token", negativeOption(b, release_artifact, af09_diagnostic, "native-exec-token", "Ignore replacement publication token"));

    options.addOption(bool, "native_memory_no_grant", negativeOption(b, release_artifact, af09_diagnostic, "native-memory-no-grant", "Withhold native memory authority"));
    options.addOption(bool, "native_memory_skip_protect", negativeOption(b, release_artifact, af09_diagnostic, "native-memory-skip-protect", "Skip native PTE protection for negative test"));
    options.addOption(bool, "native_memory_deny_protect_once", negativeOption(b, release_artifact, af09_diagnostic, "native-memory-deny-protect-once", "Deny first native protect for metadata retry witness"));
    options.addOption(bool, "native_memory_skip_zero", negativeOption(b, release_artifact, af09_diagnostic, "native-memory-skip-zero", "Skip runtime unmap zeroing for negative test"));
    options.addOption(bool, "native_no_output", negativeOption(b, release_artifact, af09_diagnostic, "native-no-output", "Withhold native output grant"));
    options.addOption(bool, "native_skip_fp", negativeOption(b, release_artifact, af09_diagnostic, "native-skip-fp", "Omit native context FP restoration"));
    options.addOption(bool, "native_skip_zero", negativeOption(b, release_artifact, af09_diagnostic, "native-skip-zero", "Omit native backing zeroing"));
    options.addOption(bool, "native_coexist_small_pool", negativeOption(b, release_artifact, af09_diagnostic, "native-coexist-small-pool", "Restrict coexist channels for capacity negative test"));
    options.addOption(bool, "native_init_skip_deadline", negativeOption(b, release_artifact, af09_diagnostic, "native-init-skip-deadline", "Ignore init wait deadline for semantic negative test"));
    if (native_c_image != null and smp) @panic("native C experiment currently requires -Dsmp=false");
    options.addOption(bool, "skip_ap_test", negativeOption(b, release_artifact, af09_diagnostic, "skip-ap-test", "Do not release the AP for negative SMP testing"));
    options.addOption(bool, "panic_test", negativeOption(b, release_artifact, af09_diagnostic, "panic-test", "Build intentional panic image for negative smoke testing"));
    options.addOption(bool, "no_timer_test", negativeOption(b, release_artifact, af09_diagnostic, "no-timer-test", "Mask the timer for negative preemption testing"));
    options.addOption(bool, "skip_zero_test", negativeOption(b, release_artifact, af09_diagnostic, "skip-zero-test", "Omit backing cleanup for negative reuse testing"));
    options.addOption(bool, "skip_unmap_test", negativeOption(b, release_artifact, af09_diagnostic, "skip-unmap-test", "Retain old user mappings for negative teardown testing"));
    options.addOption(bool, "skip_ap_timer_test", negativeOption(b, release_artifact, af09_diagnostic, "skip-ap-timer-test", "Mask the AP local timer for negative user testing"));
    options.addOption(bool, "wide_transport_test", negativeOption(b, release_artifact, af09_diagnostic, "wide-transport-test", "Retain a forbidden transport alias"));
    options.addOption(bool, "no_framebuffer_grant", negativeOption(b, release_artifact, af09_diagnostic, "no-framebuffer-grant", "Withhold display map rights"));
    options.addOption(bool, "drop_terminal_test", negativeOption(b, release_artifact, af09_diagnostic, "drop-terminal-test", "Erase terminal state during destruction"));
    options.addOption(bool, "skip_remote_unmap", negativeOption(b, release_artifact, af09_diagnostic, "skip-remote-unmap", "Retain AP user mappings during reclaim"));
    options.addOption(bool, "skip_remote_zero", negativeOption(b, release_artifact, af09_diagnostic, "skip-remote-zero", "Retain AP backing contents during reclaim"));
    const remote_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/remote_lifetime.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    options.addOption(bool, "skip_remote_discard", negativeOption(b, release_artifact, af09_diagnostic, "skip-remote-discard", "Retain old publisher transport during cleanup"));
    options.addOption(bool, "drop_remote_terminal", negativeOption(b, release_artifact, af09_diagnostic, "drop-remote-terminal", "Erase the AP terminal record during reclaim"));
    const kernel = b.addExecutable(.{
        .name = "aether",
        .use_llvm = true,
        .use_lld = true,
        .root_module = b.createModule(.{
            .root_source_file = b.path("kernel/main.zig"),
            .target = target,
            .optimize = .Debug,
            .code_model = .kernel,
            .red_zone = false,
            .stack_check = false,
            .stack_protector = false,
            .single_threaded = false,
            .pic = false,
            .unwind_tables = .none,
        }),
    });
    if (block_test == null and entropy_test == null and (backing_test == null or backing_alias)) kernel.root_module.addAssemblyFile(b.path("kernel/arch/x86_64/protection.S"));
    if (smp) kernel.root_module.addAssemblyFile(b.path("kernel/arch/x86_64/smp.S"));
    kernel.root_module.addOptions("build_options", options);
    kernel.entry = .{ .symbol_name = "_start" };
    kernel.setLinkerScript(b.path("kernel/arch/x86_64/linker.ld"));
    b.step("kernel-check", "Compile the selected kernel without install, image assembly or execution").dependOn(&kernel.step);
    b.installArtifact(kernel);
    const user = b.addSystemCommand(&.{ "python3", "scripts/user.py" });
    const user_image = user.addOutputFileArg("protection.bin");
    user.addArg(if (negativeOption(b, release_artifact, af09_diagnostic, "bad-user-test", "Make the protection fixture exit unexpectedly")) "true" else "false");
    user.addArg(if (negativeOption(b, release_artifact, af09_diagnostic, "bad-ipc-test", "Make the receiver expect an incorrect message")) "true" else "false");
    user.addArg(if (negativeOption(b, release_artifact, af09_diagnostic, "bad-smp-ipc-test", "Corrupt the Rust cross-core expected result")) "true" else "false");
    user.addArg(if (negativeOption(b, release_artifact, af09_diagnostic, "bad-display-message", "Corrupt a publisher result for the Rust display consumer")) "true" else "false");
    user.addArg(if (negativeOption(b, release_artifact, af09_diagnostic, "bad-stream-generation", "Tag a replacement result with its old generation")) "true" else "false");
    // Track inputs explicitly for Zig's command cache.
    user.addFileInput(b.path("user/protection/main.rs"));
    user.addFileInput(b.path("user/protection/linker.ld"));
    user.addFileInput(b.path("scripts/user.py"));
    user.addFileInput(b.path("rust-toolchain.toml"));
    const display = b.addSystemCommand(&.{ "python3", "scripts/display.py" });
    const display_image = display.addOutputFileArg("display.bin");
    display.addArg(if (negativeOption(b, release_artifact, af09_diagnostic, "skip-display-draw", "Skip Rust rendering for negative screenshot testing")) "true" else "false");
    display.addFileInput(b.path("user/display/main.rs"));
    display.addFileInput(b.path("user/protection/linker.ld"));
    display.addFileInput(b.path("scripts/display.py"));
    display.addFileInput(b.path("rust-toolchain.toml"));
    const bad_lifecycle_abi = negativeOption(b, release_artifact, af09_diagnostic, "bad-lifecycle-abi", "Pack an unsupported supervisor ABI");
    const fail_supervisor = negativeOption(b, release_artifact, af09_diagnostic, "fail-lifecycle-supervisor", "Fault the lifecycle supervisor at entry");
    const lifecycle_image: std.Build.LazyPath = if (b.option([]const u8, "lifecycle-image", "Explicit externally authored lifecycle v1 envelope")) |path| blk: {
        if (bad_lifecycle_abi or fail_supervisor) @panic("external lifecycle image cannot use built-in client fault flags");
        break :blk .{ .cwd_relative = path };
    } else blk: {
        const client = b.addSystemCommand(&.{ "python3", "scripts/lifecycle.py", "build" });
        const output = client.addOutputFileArg("lifecycle.bin");
        client.addArg(if (bad_lifecycle_abi) "true" else "false");
        client.addArg(if (fail_supervisor) "true" else "false");
        client.addFileInput(b.path("user/lifecycle/main.rs"));
        client.addFileInput(b.path("user/protection/linker.ld"));
        client.addFileInput(b.path("scripts/lifecycle.py"));
        client.addFileInput(b.path("rust-toolchain.toml"));
        break :blk output;
    };
    const smp_supervisor = b.addSystemCommand(&.{ "python3", "scripts/smp_supervisor.py" });
    const smp_supervisor_image = smp_supervisor.addOutputFileArg("smp-supervisor.bin");
    smp_supervisor.addArg(if (negativeOption(b, release_artifact, af09_diagnostic, "fail-smp-supervisor", "Fault the separate SMP supervisor")) "true" else "false");
    smp_supervisor.addFileInput(b.path("user/smp_supervisor/main.rs"));
    smp_supervisor.addFileInput(b.path("user/protection/linker.ld"));
    smp_supervisor.addFileInput(b.path("scripts/smp_supervisor.py"));
    smp_supervisor.addFileInput(b.path("rust-toolchain.toml"));
    // Export the exact matching module set for explicit package transport.
    b.getInstallStep().dependOn(&b.addInstallFile(user_image, "boot/protection.bin").step);
    b.getInstallStep().dependOn(&b.addInstallFile(display_image, "boot/display.bin").step);
    b.getInstallStep().dependOn(&b.addInstallFile(lifecycle_image, "boot/lifecycle.bin").step);
    b.getInstallStep().dependOn(&b.addInstallFile(smp_supervisor_image, "boot/smp-supervisor.bin").step);
    const image = b.addSystemCommand(&.{ "python3", "scripts/image.py" });
    image.addArtifactArg(kernel);
    image.addArg(b.getInstallPath(.prefix, "aether.iso"));
    image.addFileArg(user_image);
    image.addFileArg(display_image);
    image.addFileArg(lifecycle_image);
    image.addFileArg(smp_supervisor_image);
    if (native_c_image) |path| image.addFileArg(.{ .cwd_relative = path });
    b.getInstallStep().dependOn(&image.step);

    for ([_][]const u8{ "run", "smoke" }) |mode| {
        const run = b.addSystemCommand(&.{ "python3", "scripts/emulator.py", mode });
        run.addArg(b.getInstallPath(.prefix, "aether.iso"));
        run.addArgs(&.{ "--cpus", if (smp) "2" else "1" });
        run.step.dependOn(&image.step);
        b.step(mode, if (std.mem.eql(u8, mode, "run")) "Boot graphical QEMU" else "Check boot with timeout and capture framebuffer").dependOn(&run.step);
    }
    const native_elf_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/native_elf.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    const tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/framebuffer.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    const byte_stream_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/byte_stream.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    const test_step = b.step("test", "Check kernel, smoke harness and pinned standards");
    // Standards are offline development inputs, never a sibling-tree dependency.
    for ([_][]const u8{ "experience", "standards", "distribution" }) |standard| {
        const check = b.addSystemCommand(&.{ "python3", b.fmt("docs/check-{s}.py", .{standard}) });
        test_step.dependOn(&check.step);
    }
    test_step.dependOn(&b.addRunArtifact(byte_stream_tests).step);
    test_step.dependOn(&b.addRunArtifact(tests).step);
    test_step.dependOn(&b.addRunArtifact(native_elf_tests).step);
    test_step.dependOn(&b.addRunArtifact(remote_tests).step);
    const queue_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/arch/x86_64/run_queue.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(queue_tests).step);
    const execution_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/arch/x86_64/native_execution.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(execution_tests).step);
    const cap_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/capability.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(cap_tests).step);
    const lifetime_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/lifetime.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(lifetime_tests).step);
    const mailbox_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/mailbox.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(mailbox_tests).step);
    const cross_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/cross_core.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(cross_tests).step);
    const display_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/display_grant.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(display_tests).step);
    const lifecycle_image_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/lifecycle_image.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(lifecycle_image_tests).step);
    const boot_backing_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/boot_backing.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(boot_backing_tests).step);
    const backing_geometry_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/arch/x86_64/backing_geometry.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(backing_geometry_tests).step);
    const backing_pool_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/arch/x86_64/backing_pool.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(backing_pool_tests).step);
    const memory_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/native_memory.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(memory_tests).step);
    const launch_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/native_launch.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(launch_tests).step);
    const fs_session_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/native_fs_session.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(fs_session_tests).step);
    const channel_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/native_channel.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(channel_tests).step);

    const observation_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/native_session_observation.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(observation_tests).step);

    const sustained_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/native_sustained.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(sustained_tests).step);

    const clock_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/native_clock.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(clock_tests).step);
    const rtc_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/native_rtc.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(rtc_tests).step);

    const wait_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/native_wait.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(wait_tests).step);
    const entropy_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/entropy_completion.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(entropy_tests).step);
    const native_entropy_tests = b.addTest(.{ .root_module = b.createModule(.{
        .root_source_file = b.path("kernel/native_entropy.zig"),
        .target = b.graph.host,
        .optimize = .Debug,
    }) });
    test_step.dependOn(&b.addRunArtifact(native_entropy_tests).step);
    const workflow = b.addSystemCommand(&.{ "python3", "scripts/check_workflow.py" });
    test_step.dependOn(&workflow.step);
    const harness = b.addSystemCommand(&.{ "python3", "-m", "unittest", "discover", "-s", "tests", "-v" });
    test_step.dependOn(&harness.step);
}

// Build-graph gate only; do not add this selection to the kernel runtime ABI.
fn negativeOption(b: *std.Build, release_artifact: bool, af09_diagnostic: bool, name: []const u8, description: []const u8) bool {
    const enabled = b.option(bool, name, description) orelse false;
    if (release_artifact and enabled) {
        std.debug.print("release artifact rejects negative-test option: {s}\n", .{name});
        @panic("release artifact contains a negative-test control");
    }
    if (af09_diagnostic and enabled) {
        std.debug.print("AF09 diagnostic rejects negative-test option: {s}\n", .{name});
        @panic("AF09 diagnostic contains an incompatible negative-test control");
    }
    return enabled;
}
