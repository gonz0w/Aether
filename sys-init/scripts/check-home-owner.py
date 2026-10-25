# SPDX-License-Identifier: BSD-2-Clause
"""Check matched home owner and offline fit; resource blockage exits 2."""
from pathlib import Path
import runpy
import json
import re
import sys
import time

SOURCE=Path(__file__).resolve()
SYSTEM=SOURCE.parents[2]
SYS=SYSTEM/"sys-init"
P=SYS/"prototypes/native-filesystem-session"
S=SYSTEM/"userland/experiments/filesystem-service"
observation_source=SYS/"scripts/check-file-write-observations.py"
observations=runpy.run_path(str(observation_source))
runner=observations["runner"]
require=runner["require"]
NATIVE=[*runner["NATIVE"],"-Copt-level=z","-Cjump-tables=no"]
COMMON=["--edition=2024","-Dwarnings","-Dunsafe_op_in_unsafe_fn"]


def check(record,work,proc,tools):
    deadline=time.monotonic()+300
    env=proc.clean_env(work)
    env["DYLD_LIBRARY_PATH"]=str(Path(tools["rustc"]["path"]).parent.parent/"lib")
    flags=[*runner["cfg"](True),"--cfg","fs_home_wire"]
    flags += [v for name in ("paths","file16","replace","process_views","process_writes","path_wire","dup2_wire","file_write_wire","in_place","home_in_place","home_owner") for v in ("--cfg","fs_"+name)]
    def run(label,argv,expected=0):
        left=deadline-time.monotonic();require(left>0,"suite deadline before "+label)
        child_env=env.copy()
        if Path(str(argv[0])).name not in ("rustc","clippy-driver","rust-lld"):
            child_env.pop("DYLD_LIBRARY_PATH",None)
        r=proc.run(list(map(str,argv)),cwd=SYS,env=child_env,work=work,label=label,timeout=min(60,left))
        record["rows"].append({"label":label,"expected_exit":expected,"process":r.record,"stdout":r.stdout.decode(errors="replace")[-7000:],"stderr":r.stderr.decode(errors="replace")[-5000:]})
        require(r.returncode==expected and r.record["complete"] and r.record["cleanup"]=="complete",label)
        return r
    def deps(folder,producer,names):
        result=["-Ldependency="+str(folder),"-Ldependency="+str(producer)]
        for name in names:
            root=producer if name.startswith("filesystem_") else folder
            result.extend(("--extern",name+"="+str(root/("lib"+name+".rlib"))))
        return result
    producer_crates=[("filesystem_metadata","metadata-lib.rs",[]),
        ("filesystem_policy","owner.rs",["filesystem_metadata"]),
        ("filesystem_service","service.rs",["filesystem_policy"]),
        ("filesystem_client","client.rs",["filesystem_service"]),
        ("filesystem_remote_descriptors","remote-descriptors.rs",["filesystem_client","filesystem_service"]),
        ("filesystem_fd_protocol","fd-protocol.rs",["filesystem_client","filesystem_service","filesystem_remote_descriptors"])]
    for stage,extra in (("host",[]),("native",NATIVE)):
        folder=work/("matched-"+stage);folder.mkdir()
        for name,filename,imports in producer_crates:
            common=[v for v in runner["COMMON"] if v != "-Funsafe-code" or name not in ("filesystem_metadata","filesystem_client","filesystem_remote_descriptors")]
            run(stage+"-matched-"+name,[tools["rustc"]["path"],*common,*flags,*([*runner["NATIVE"],"-Cjump-tables=no"] if extra else []),*deps(folder,folder,imports),"--crate-type=lib","--crate-name="+name,"-Cmetadata="+folder.name,S/filename,"-o",folder/("lib"+name+".rlib")])
    crates=observations["OWNER_CRATES"]
    for stage,extra in (("host",[]),("native",NATIVE)):
        producer=work/("matched-"+stage)
        folder=work/("home-owner-"+stage);folder.mkdir()
        for name,filename,imports in crates:
            run(stage+"-home-owner-"+name,[tools["rustc"]["path"],*COMMON,*flags,*extra,*deps(folder,producer,imports),"--crate-type=lib","--crate-name="+name,"-Cmetadata="+folder.name,P/filename,"-o",folder/("lib"+name+".rlib")])
            run(stage+"-home-owner-clippy-"+name,[tools["clippy-driver"]["path"],*COMMON,*flags,*extra,*deps(folder,producer,imports),"--crate-type=lib","--crate-name="+name,"-Cmetadata="+folder.name,P/filename,"--emit=metadata","-o",folder/(name+".rmeta")])
    folder=work/"home-owner-host";producer=work/"matched-host"
    imports=[n for n,_,_ in crates]+[n for n,_,_ in home_producer_crates()]
    for compiler in ("rustc","clippy-driver"):
        run(compiler+"-home-owner-test-build",[tools[compiler]["path"],*COMMON,*flags,*deps(folder,producer,imports),"--test",P/"owner_runtime.rs","-o",work/(compiler+"-home-owner-tests")])
    result=run("home-owner-tests",[work/"rustc-home-owner-tests","home_tests::","--test-threads=1"])
    require(b"9 passed; 0 failed" in result.stdout,"nine matched home-owner cases executed")
    # Compiling omission controls exercise named behavior, not generic panics.
    test="runtime_keeps_whole_file_event_before_error_and_never_overwrites_on_second_run"
    independent="independent_admission_and_delivery_errors_are_retained_before_return"
    controls=[
        ("home-selection","fork_gate.rs","ProcessFiles::connect_home_in_place(files, channel, epoch)?;","ProcessFiles::connect_in_place(files, channel, epoch)?;","final_slot_home_constructor_initializes_every_record_and_outcome","OWNER_HOME_INIT"),
        ("router-failed-event","owner_dispatch.rs","return Ok(Event::File(file));","return file.admission.map(|_| Event::Complete);",test,"OWNER_FILE_RETENTION"),
        ("router-cleanup","owner_dispatch.rs","file.exchange.cleanup = peer.cleanup();","file.exchange.cleanup = None;",test,"OWNER_FILE_CLOSES"),
        ("runtime-retention","owner_runtime.rs","Event::File(event) => self.file_event(index, id, generation, event),","Event::File(event) => { let _=event; Err(Error::Gate) },",test,"OWNER_FILE_RETENTION"),
        ("runtime-admission","owner_runtime.rs","retained.event.admission.as_ref().map_err(|_| Error::Gate)?;","let _=retained.event.admission.as_ref();",independent,"OWNER_INDEPENDENT_STATUS"),
        ("runtime-delivery","owner_runtime.rs",".map_err(|_| Error::Source)?;\n        Ok(true)",".map_err(|_| Error::Source).ok();\n        Ok(true)",independent,"OWNER_INDEPENDENT_STATUS"),
        ("runtime-context","owner_runtime.rs","identity,\n            generation,\n            event,","identity,\n            generation:{let _=generation;31},\n            event,",test,"OWNER_NATIVE_CONTEXT"),
        ("source-cleanup","owner_runtime.rs","self.gate.cleanup()","None",test,"OWNER_SOURCE_CLEANUP"),
        ("runtime-once","owner_runtime.rs","require(!self.started)?;","let _=self.started;",test,"OWNER_ONCE_ONLY"),
        ("parent-terminal-admission","owner_runtime.rs","let mut progress = self.poll(0, workspace)?;","let mut progress = self.poll(0, workspace)?; for index in 1..4 { progress |= self.poll(index, workspace)?; }","parent_terminal_cuts_off_queued_child_file_exec_fork_and_stream","DRAIN_NO_CHILD_BYTES"),
        ("parent-terminal-pipe-retire","owner_runtime.rs",".admit(|_, streams| streams.retire_idle([false; 4]))",".admit(|_, streams| { let _ = streams; })","pending_no_effect_read_and_reserved_wait_settle_then_retire_pipe","DRAIN_FINAL_PIPE_RETIRE"),
    ]
    record["home_owner_controls"]=[]
    for label,filename,before,after,case,marker in controls:
        original=(P/filename).read_text();require(original.count(before)==1,"unique home-owner control: "+label)
        control=work/("owner-control-"+label);control.mkdir()
        source=control/"source";source.mkdir()
        # Unchanged modules remain the frozen source inputs, not copied trees.
        for path in P.glob("*.rs"):
            if path.name != filename:
                (source/path.name).symlink_to(path)
        (source/filename).write_text(original.replace(before,after,1))
        # Rebuild dependent Sys crates only for the Gate mutation; other controls
        # replace a single router or the directly compiled runtime test crate.
        selected=folder
        if filename=="fork_gate.rs":
            selected=control
            for name,filename2,needs in crates:
                run(label+"-"+name,[tools["rustc"]["path"],*COMMON,*flags,*deps(selected,producer,needs),"--crate-type=lib","--crate-name="+name,"-Cmetadata="+label,source/filename2,"-o",selected/("lib"+name+".rlib")])
        elif filename=="owner_dispatch.rs":
            run(label+"-router-build",[tools["rustc"]["path"],*COMMON,*flags,*deps(folder,producer,next(needs for name,_,needs in crates if name=="owner_dispatch")),"--crate-type=lib","--crate-name=owner_dispatch","-Cmetadata="+label,source/filename,"-o",control/"libowner_dispatch.rlib"])
        arguments=deps(selected,producer,imports)
        if filename=="owner_dispatch.rs":
            arguments=[v.replace(str(folder/"libowner_dispatch.rlib"),str(control/"libowner_dispatch.rlib")) for v in arguments]
        run(label+"-tests-build",[tools["rustc"]["path"],*COMMON,*flags,*arguments,"--test",source/"owner_runtime.rs","-o",control/"tests"])
        name="home_tests::"+case
        rejected=run(label+"-rejected",[control/"tests","--exact",name,"--nocapture"],expected=101)
        require(name.encode() in rejected.stdout and b"1 failed" in rejected.stdout and marker.encode() in rejected.stderr,"named home-owner control: "+label)
        record["home_owner_controls"].append({"label":label,"file":filename,"before":before,"after":after,"test":name,"marker":marker,"sha256":runner["sha"](source/filename)})
    # Reject incomplete construction selections before either host or target use.
    for stage,extra in (("host",[]),("native",NATIVE)):
        folder=work/("home-owner-"+stage);producer=work/("matched-"+stage)
        for missing in ("in_place","home_in_place","home_wire","file_write_wire"):
            incomplete=[];i=0
            while i<len(flags):
                if flags[i:i+2]==["--cfg","fs_"+missing]:i+=2
                else:incomplete.append(flags[i]);i+=1
            rejected=run(stage+"-missing-"+missing,[tools["rustc"]["path"],*COMMON,*incomplete,*extra,*deps(folder,producer,next(needs for n,_,needs in crates if n=="fork_gate")),"--crate-type=lib",P/"fork_gate.rs","-o",folder/"absent.rlib"],expected=1)
            require(b"home owner requires matched home/in-place/write selections" in rejected.stderr,"exact missing-selection guard")
        for crate,method,args in (("fork_gate","connect_in_place","slot,channel,77,streams"),("owner_runtime","connect_in_place","slot,kernel,99,channel,77,5000")):
            probe=work/(stage+"-old-"+crate+".rs")
            if crate=="fork_gate":
                body="pub fn old<T:filesystem_service::Channel,S>(slot:&mut core::mem::MaybeUninit<fork_gate::Owner<T,S>>,channel:T,streams:S){let _=fork_gate::Owner::"+method+"("+args+");}"
            else:
                body="pub fn old<K:owner_control::Control>(slot:&mut core::mem::MaybeUninit<owner_runtime::Runtime<K>>,kernel:K,channel:owner_runtime::Channel<K>){let _=owner_runtime::Runtime::"+method+"("+args+");}"
            probe.write_text("#![no_std]\n"+body+"\n")
            rejected=run(stage+"-old-"+crate+"-api-absent",[tools["rustc"]["path"],*COMMON,*extra,*deps(folder,producer,imports),"--crate-type=lib",probe,"-o",folder/"absent.rlib"],expected=1)
            require(b"E0599" in rejected.stderr and b"connect_in_place" in rejected.stderr,"old owner constructor absent under home selection")
    # Pin the additional inspection/link binaries before concrete measurement.
    supplemental={
        "objdump": {"path":"/opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-objdump","sha256":"57df889beb6133ffd405ffb84795941c068a13a09dba0a40546d3b740666b9b7"},
        "size": {"path":"/opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-size","sha256":"84f8a66f8a83bca2f5d013f318068488a5d40edc033b779cc5029ecc2f6d8b85"},
        "rust-lld": {"path":"/Users/cam/.rustup/toolchains/1.98.0-aarch64-apple-darwin/lib/rustlib/aarch64-apple-darwin/bin/rust-lld","sha256":"6f44b61e91d6d7b6ba80bb75391587bb4fa832b248281bd67d519516cde43f98"}}
    for name,pin in supplemental.items():
        runner["verify"](pin["path"],pin["sha256"]);tools[name]=pin
    pins=json.loads(runner["PINS"].read_text())
    for name in ("clang","clang-format","nm","readelf"):
        pin=pins["tools"][name];runner["verify"](pin["path"],pin["sha256"]);tools[name]=pin
    runtime=Path("/opt/homebrew/Cellar/llvm@21/21.1.8/lib/clang/21/lib/darwin/libclang_rt.ubsan_osx_dynamic.dylib")
    runner["verify"](runtime,"7bfe170b03e5b9fb208d8568250aa84c35454933c306fe322c978295874c3746")
    record["sources"][str(runtime)]=runner["sha"](runtime)
    record["tools"].update(supplemental)
    folder=work/"home-owner-native";producer=work/"matched-native"
    run("native-home-owner-entry",[tools["rustc"]["path"],*COMMON,*flags,*NATIVE,"--crate-type=lib","--crate-name=owner_entry",P/"owner_entry.rs","-o",folder/"libowner_entry.rlib"])
    def byte_run(label,argv,expected=0):
        argv=list(map(str,argv))
        # Freeze each actual C translation unit's include closure before compile.
        if Path(argv[0]).name=="clang" and any(v.endswith(".c") for v in argv):
            removed=[];skip=False
            for arg in argv[1:]:
                if skip:skip=False;continue
                if arg=="-o":skip=True;continue
                if arg=="-c" or arg.endswith(".o"):continue
                removed.append(arg)
            output=run(label+"-dependencies",[argv[0],*removed,"-M"]).stdout.decode()
            paths=output.replace("\\\n", " ").split(":",1)[1].split()
            for value in paths:
                path=Path(value)
                if not path.is_absolute():path=SYS/path
                record["sources"][str(path)]=runner["sha"](path)
        saved=None
        if not (Path(argv[0]).name in ("rustc","clippy-driver","rust-lld")):
            saved=env.pop("DYLD_LIBRARY_PATH",None)
        try:
            result=run(label,argv,expected)
            if label=="owner-disassembly":
                lines=result.stdout.decode().splitlines();fragments=[]
                for i,line in enumerate(lines):
                    if re.search(r"\b(?:call|jmp)\s+qword ptr \[",line) and "[rip " not in line:
                        fragments.append("\n".join(lines[max(0,i-14):i+6]))
                record["indirect_edge_fragments"]=fragments
            return result.stdout+result.stderr
        finally:
            if saved is not None:env["DYLD_LIBRARY_PATH"]=saved
    compare=runpy.run_path(str(SYS/"scripts/owner_compare.py"))
    obj,record["comparison"]=compare["prepare"](SYSTEM,work,byte_run,tools)
    measure=runpy.run_path(str(SYS/"scripts/owner_measure.py"))["measure"]
    imports=[n for n,_,_ in crates]+[n for n,_,_ in producer_crates]+["owner_entry"]
    record["home_owner_measurement"]=measure(SYSTEM,work,Path(tools["rustc"]["path"]),tools,byte_run,
        deps(folder,producer,imports),["-Clink-arg="+str(obj)],True,extra_cfg=flags,file_layout=True)
    measured=record["home_owner_measurement"]
    # Preceding producer/Peer and both old composed-owner profiles on final bytes.
    observations["check"](record,work,proc,tools,deadline=deadline)
    record["old_owner_measurements"]={}
    for profile in ("AF07","AF08"):
        producer=work/(profile+"-init-native")
        old=work/("old-fit-"+profile);old.mkdir()
        old_flags=[v for i,v in enumerate(runner["cfg"]()) if v!="fs_directory_contexts" and not (v=="--cfg" and i+1<len(runner["cfg"]()) and runner["cfg"]()[i+1]=="fs_directory_contexts")]
        old_flags += [v for name in ("paths","file16","replace","process_views","path_wire","dup2_wire","in_place") for v in ("--cfg","fs_"+name)]
        if profile=="AF08":old_flags += ["--cfg","fs_directory_contexts","--cfg","fs_cwd","--cfg","fs_cwd_wire"]
        for name,filename,needs in crates:
            run(profile+"-fit-"+name,[tools["rustc"]["path"],*COMMON,*old_flags,*NATIVE,*deps(old,producer,needs),"--crate-type=lib","--crate-name="+name,"-Cmetadata="+old.name,P/filename,"-o",old/("lib"+name+".rlib")])
        # execute's four internal exec/readiness/decoder cases are distinct from the external56-case
        # wrapper: run them on both affected old profiles after Plan borrowing.
        host=work/("old-owner-"+profile+"-host");host_producer=work/(profile+"-init-host")
        for compiler in ("rustc","clippy-driver"):
            run(profile+"-"+compiler+"-internal-exec-tests-build",[tools[compiler]["path"],*COMMON,*old_flags,*deps(host,host_producer,imports[:-1]),"--test",P/"owner_runtime.rs","-o",host/(compiler+"-exec-tests")])
        tested=run(profile+"-internal-exec-tests",[host/"rustc-exec-tests","exec_tests::","--test-threads=1"])
        require(b"4 passed; 0 failed" in tested.stdout,"four actual internal exec/readiness/decoder methods executed: "+profile)
        output=work/("measure-"+profile);output.mkdir()
        run(profile+"-owner-entry",[tools["rustc"]["path"],*COMMON,*NATIVE,"--crate-type=lib","--crate-name=owner_entry",P/"owner_entry.rs","-o",old/"libowner_entry.rlib"])
        result=measure(SYSTEM,output,Path(tools["rustc"]["path"]),tools,byte_run,deps(old,producer,imports),["-Clink-arg="+str(obj)],True)
        record["old_owner_measurements"][profile]=result
        require(result["resident_fits"] and result["code_fits"] and result["stack"]["status"]=="pass",profile+" old complete owner fits")
    run("home-owner-rustfmt",[tools["rustfmt"]["path"],"--edition=2024","--check",*[P/n for n in ("fork_gate.rs","owner_dispatch.rs","owner_runtime.rs","owner_exec_tests.rs","native_owner.rs","home_owner_tests.rs")]])
    if not (measured["resident_fits"] and measured["code_fits"] and measured["stack"]["status"]=="pass"):
        raise runner["PreconditionError"]("complete home owner exceeds resource gate; inspect retained measurement")


def home_producer_crates():
    return [(n,None,None) for n in ("filesystem_metadata","filesystem_policy","filesystem_service","filesystem_client","filesystem_remote_descriptors","filesystem_fd_protocol")]


if __name__=="__main__":
    sys.exit(runner["main"](check_function=check,program="aether-home-owner-check",
        evidence=SYS/"docs/evidence/home-owner-fit-2026-10-24",description=__doc__,
        example="python3 -B sys-init/scripts/check-home-owner.py",
        scope="home owner host/no_std and offline complete fit only; no guest",
        limitations="Complete linked owner code/resident/conservative-stack fit is inspected offline. No guest, native authority, peak-stack or recovery qualification.",
        extra_sources=(SOURCE,observation_source,SYS/"scripts/owner_measure.py",SYS/"scripts/owner_compare.py",SYSTEM/"scripts/owner_stack.py",SYS/"tests/owner_compare.c",SYSTEM/"kernel/arch/x86_64/native_fs_roles.zig",SYSTEM/"docs/native-fs-owner-stack-v1.json",SYSTEM/".deps/native-current/sdk/musl-1.2.6.tar.gz",*[SYSTEM/".deps/native-current/sdk/stage/usr/include"/n for n in ("string.h","features.h","bits/alltypes.h")],S/"check-home-in-place.py",S/"check-file-writes.py",S/"check-process-writes.py",S/"check-client-mutations.py",S/"vendor/abi29-startup.rs",
            *S.glob("*.c"),*S.glob("*.h"),*P.glob("*.rs"),*[SYS/"tests"/(n+".rs") for n in observations["OLD_TESTS"]],SYS/"tests/file_write_observations.rs",SYSTEM/"userland/docs/quality/clang-format.yaml")))
