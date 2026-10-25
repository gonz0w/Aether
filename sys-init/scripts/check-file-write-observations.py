# SPDX-License-Identifier: BSD-2-Clause
"""Check FILE mutation observations independently of reply delivery."""
from pathlib import Path
import re
import runpy
import shutil
import sys
import time

SOURCE = Path(__file__).resolve()
SYSTEM = SOURCE.parents[2]
SYS = SYSTEM / "sys-init"
S = SYSTEM / "userland/experiments/filesystem-service"
P = SYS / "prototypes/native-filesystem-session"
home_source = S / "check-home-in-place.py"
home = runpy.run_path(str(home_source))
runner = home["runner"]
require = runner["require"]
COMMON = ["--edition=2024", "-Dwarnings", "-Dunsafe_op_in_unsafe_fn", "-Funsafe-code"]
NATIVE = runner["NATIVE"]

OLD_TESTS=("native_fork_gate","native_fork_streams","native_fork_capture","native_owner_region","native_fork_publish","native_owner_dispatch","native_fork_refusal","native_broker_init", "native_owner_runtime","native_fd_dispatch")

OWNER_CRATES=[
        ("abi29_dispatch_core","lib.rs",[]),
        ("fd_startup","fd_startup.rs",["abi29_dispatch_core"]),
        ("fork_frames","fork_frames.rs",["abi29_dispatch_core","fd_startup"]),
        ("exec_frames","exec_frames.rs",["abi29_dispatch_core","fd_startup","fork_frames"]),
        ("fork_gate","fork_gate.rs",["fd_startup","filesystem_remote_descriptors","filesystem_service","filesystem_client"]),
        ("fork_streams","fork_streams.rs",["fd_startup","fork_gate"]),
        ("fd_dispatch","fd_dispatch.rs",["filesystem_fd_protocol","filesystem_remote_descriptors","filesystem_service"]),
        ("af07_transport","af07_transport.rs",["filesystem_service"]),
        ("fork_transport","fork_transport.rs",["abi29_dispatch_core","af07_transport","fd_startup","filesystem_service","fork_gate","fork_frames"]),
        ("owner_region","owner_region.rs",[]),
        ("owner_dispatch","owner_dispatch.rs",["abi29_dispatch_core","fd_dispatch","fd_startup","filesystem_remote_descriptors","filesystem_service","fork_gate","fork_frames","exec_frames"]),
        ("owner_control","owner_control.rs",["af07_transport"]),
        ("owner_runtime","owner_runtime.rs",["abi29_dispatch_core","af07_transport","fd_dispatch","fd_startup","filesystem_client","filesystem_remote_descriptors","filesystem_service","fork_gate","fork_streams","fork_transport","owner_control","owner_dispatch","exec_frames"]),
    ]


def check(record, work, proc, tools, deadline=None):
    if deadline is None:
        deadline = time.monotonic() + 300
    env = proc.clean_env(work)
    env["DYLD_LIBRARY_PATH"] = str(Path(tools["rustc"]["path"]).parent.parent / "lib")
    flags = [*runner["cfg"](True), "--cfg", "fs_home_wire"]
    flags += [v for n in ("paths", "file16", "replace", "process_views", "process_writes", "path_wire", "dup2_wire", "file_write_wire") for v in ("--cfg", "fs_" + n)]
    imports = ["filesystem_metadata", "filesystem_policy", "filesystem_service", "filesystem_client", "filesystem_remote_descriptors", "filesystem_fd_protocol"]
    def run(label, argv, expected=0):
        left = deadline - time.monotonic()
        require(left > 0, "suite deadline before " + label)
        r = proc.run(list(map(str, argv)), cwd=SYS, env=env, work=work, label=label, timeout=min(60,left))
        record["rows"].append({"label":label,"expected_exit":expected,"process":r.record,"stdout":r.stdout.decode(errors="replace")[-7000:],"stderr":r.stderr.decode(errors="replace")[-5000:]})
        require(r.returncode == expected and r.record["complete"] and r.record["cleanup"] == "complete", label)
        return r
    def deps(folder,names):
        return ["-Ldependency="+str(folder),*[v for n in names for v in ("--extern",n+"="+str(folder/("lib"+n+".rlib")))]]
    producer_flags=[*flags,"--cfg","fs_in_place","--cfg","fs_home_in_place"]
    producer_crates=[("filesystem_metadata","metadata-lib.rs",[]),
        ("filesystem_policy","owner.rs",["filesystem_metadata"]),
        ("filesystem_service","service.rs",["filesystem_policy"]),
        ("filesystem_client","client.rs",["filesystem_service"]),
        ("filesystem_remote_descriptors","remote-descriptors.rs",["filesystem_client","filesystem_service"]),
        ("filesystem_fd_protocol","fd-protocol.rs",["filesystem_client","filesystem_service","filesystem_remote_descriptors"])]
    for stage,extra in (("host",[]),("native",NATIVE)):
        folder=work/("observed-"+stage);folder.mkdir()
        for name,filename,needs in producer_crates:
            common=[v for v in runner["COMMON"] if v != "-Funsafe-code" or name not in ("filesystem_metadata","filesystem_client","filesystem_remote_descriptors")]
            run(stage+"-focused-"+name,[tools["rustc"]["path"],*common,*producer_flags,*extra,*deps(folder,needs),"--crate-type=lib","--crate-name="+name,"-Cmetadata="+folder.name,S/filename,"-o",folder/("lib"+name+".rlib")])
    for stage,extra in (("host",[]),("native",NATIVE)):
        folder=work/("observed-"+stage)
        run(stage+"-observed-peer",[tools["rustc"]["path"],*COMMON,*flags,*extra,*deps(folder,imports),"--crate-type=lib","--crate-name=fd_dispatch",P/"fd_dispatch.rs","-o",folder/"libfd_dispatch.rlib"])
        run(stage+"-observed-peer-clippy",[tools["clippy-driver"]["path"],*COMMON,*flags,*extra,*deps(folder,imports),"--crate-type=lib","--crate-name=fd_dispatch",P/"fd_dispatch.rs","--emit=metadata","-o",folder/"peer.rmeta"])
    wrapper=work/"observations.rs"
    original=(S/"home-wire-tests.rs").read_text()
    original=re.sub(r'#\[path = "([^"/]+)"\]',lambda m:'#[path = "'+str(S/m[1])+'"]',original)
    wrapper.write_text(original+'\n#[path="'+str(SYS/"tests/file_write_observations.rs")+'"] mod observations;\n')
    host=work/"observed-host"
    for compiler in ("rustc","clippy-driver"):
        run(compiler+"-observations-build",[tools[compiler]["path"],*COMMON,*flags,*deps(host,[*imports,"fd_dispatch"]),"--test",wrapper,"-o",work/(compiler+"-observations")])
    result=run("observations-tests",[work/"rustc-observations","observations::","--test-threads=1"])
    require(b"6 passed; 0 failed" in result.stdout,"all six observation cases executed")
    controls=[
        ("capture","fd_dispatch.rs","*observation = reply\n                        .write_receipt()\n                        .map(|receipt| ObservedWrite { process, receipt });","let _ = process; *observation = None;","success_copy_survives_delivery_peer_drop_and_real_readback","PEER_WRITE_CAPTURE"),
        ("context","fd_dispatch.rs",".map(|receipt| ObservedWrite { process, receipt });",".map(|mut receipt| { receipt.generation ^= 1; ObservedWrite { process, receipt } });","success_copy_survives_delivery_peer_drop_and_real_readback","PEER_WRITE_CONTEXT"),
        ("terminal-receipt","fd_dispatch.rs","if files.cleanup().is_some() {\n                    self.close();","if files.cleanup().is_some() {\n                    *observation = None; self.close();","terminal_source_progress_delivers_then_closes_peer_without_erasing_receipt","PEER_TERMINAL_RECEIPT"),
        ("source-retire","fd_dispatch.rs","self.connection.abort(files);","let _ = files;","inbound_loss_or_malformed_request_has_no_mutation_observation","PEER_PREFLIGHT_RETIRE"),
        ("terminal-close","fd_dispatch.rs","if files.cleanup().is_some() {\n                    self.close();","if files.cleanup().is_some() {\n                    let _ = ();","terminal_source_progress_delivers_then_closes_peer_without_erasing_receipt","PEER_TERMINAL_CLOSE"),
        ("close-identity","file_write_observations.rs","cleanup: self.cleanup(),","cleanup: self.cleanup().map(|_| [0, 0]),","terminal_source_progress_delivers_then_closes_peer_without_erasing_receipt","PEER_SEPARATE_CLOSES"),
        ("false-delivery","file_write_observations.rs","let delivery = self.serve_inner(files, header, workspace, &mut observation);","let delivery = self.serve_inner(files, header, workspace, &mut observation).or(Ok(()));","every_reply_byte_loss_and_complete_physical_error_keep_one_effect","PEER_DELIVERY_IDENTITY"),
    ]
    record["peer_controls"]=[]
    for label,filename,before,after,test,marker in controls:
        original=(P/filename).read_text();require(original.count(before)==1,"unique peer control: "+label)
        folder=work/("peer-control-"+label);folder.mkdir()
        for name in ("fd_dispatch.rs","file_write_observations.rs"):shutil.copy2(P/name,folder/name)
        (folder/filename).write_text(original.replace(before,after,1))
        run(label+"-peer-control-build",[tools["rustc"]["path"],*COMMON,*flags,*deps(host,imports),"--crate-type=lib","--crate-name=fd_dispatch","-Cmetadata="+label,folder/"fd_dispatch.rs","-o",folder/"libfd_dispatch.rlib"])
        run(label+"-peer-tests-build",[tools["rustc"]["path"],*COMMON,*flags,*deps(host,imports),"--extern","fd_dispatch="+str(folder/"libfd_dispatch.rlib"),"--test",wrapper,"-o",folder/"tests"])
        name="observations::"+test
        rejected=run(label+"-peer-reject",[folder/"tests","--exact",name,"--nocapture"],expected=101)
        require(name.encode() in rejected.stdout and b"1 failed" in rejected.stdout and marker.encode() in rejected.stderr,"named peer semantic rejection: "+label)
        record["peer_controls"].append({"label":label,"file":filename,"before":before,"after":after,"test":name,"marker":marker,"sha256":runner["sha"](folder/filename)})
    # Qualification of unchanged producer behavior follows focused peer checks.
    home["check"](record,work,proc,tools,deadline=deadline)
    for stage,extra in (("host",[]),("native",NATIVE)):
        current=work/("observed-"+stage)
        rejected=run(stage+"-unselected-peer-rejects-write-wire",[tools["rustc"]["path"],*COMMON,*extra,*deps(current,imports),"--crate-type=lib",P/"fd_dispatch.rs","-o",current/"absent.rlib"],expected=1)
        require(b"FILE peer requires an explicit matched write-observation selection" in rejected.stderr,"unselected peer rejects AEFW")
        for method in ("serve_one","serve_received"):
            absent=work/(stage+"-old-"+method+".rs")
            args="files, workspace" if method=="serve_one" else "files, &[0;64], workspace"
            absent.write_text("#![no_std]\npub fn probe<C:filesystem_service::Channel,T:filesystem_service::Channel>(p:&mut fd_dispatch::Peer<C>,files:&mut filesystem_remote_descriptors::ProcessFiles<T>,workspace:&mut[u8;4096]){let _=p."+method+"("+args+");}\n")
            rejected=run(stage+"-reject-discarding-"+method,[tools["rustc"]["path"],*COMMON,*extra,*deps(current,[*imports,"fd_dispatch"]),"--crate-type=lib",absent,"-o",current/"absent.rlib"],expected=1)
            require(b"E0599" in rejected.stderr and method.encode() in rejected.stderr,"old discard API absent")
        escape=work/(stage+"-peer-borrow.rs")
        escape.write_text("#![no_std]\npub fn leak<C:filesystem_service::Channel>(p:&mut fd_dispatch::Peer<C>)->Result<&mut C,fd_dispatch::Error>{p.with_channel(|c|c)}\n")
        rejected=run(stage+"-reject-peer-borrow-escape",[tools["rustc"]["path"],*COMMON,*extra,*deps(current,[*imports,"fd_dispatch"]),"--crate-type=lib",escape,"-o",current/"absent.rlib"],expected=1)
        require(b"lifetime may not live long enough" in rejected.stderr,"scoped peer borrow cannot escape")
        for profile in ("AF07","AF08"):
            old=work/(profile+"-init-"+stage)
            rejected=run(stage+profile+"-reject-matched-write-peer",[tools["rustc"]["path"],*COMMON,*flags,*extra,*deps(old,imports),"--crate-type=lib",P/"fd_dispatch.rs","-o",old/"absent.rlib"],expected=1)
            require((b"E0432" in rejected.stderr and b"FileWriteReceipt" in rejected.stderr) or b"FILE peer requires an explicit matched write-observation selection" in rejected.stderr,"old wire cannot supply observed peer")

    owner_crates=OWNER_CRATES
    def owner_deps(folder,producer,names,observed=False):
        values=["-Ldependency="+str(folder),"-Ldependency="+str(producer)]
        for name in names:
            path=producer if name.startswith("filesystem_") else folder
            if observed and name=="fd_dispatch":path=work/("observed-native" if producer.name.endswith("native") else "observed-host")
            values.extend(("--extern",name+"="+str(path/("lib"+name+".rlib"))))
        return values
    old_base=[v for i,v in enumerate(runner["cfg"]()) if v!="fs_directory_contexts" and not
        (v=="--cfg" and i+1<len(runner["cfg"]()) and runner["cfg"]()[i+1]=="fs_directory_contexts")]
    old_base += [v for n in ("paths","file16","replace","process_views","path_wire","dup2_wire","in_place") for v in ("--cfg","fs_"+n)]
    old_common=[v for v in COMMON if v!="-Funsafe-code"]
    record["old_owner_tests"]={}
    old_wrapper=work/"old-owner-tests.rs"
    old_wrapper.write_text('use filesystem_remote_descriptors::ProcessFiles; use filesystem_service::Channel;\nmod tests {\n'
        +'#[path="'+str(S/"process-fd-fixture.rs")+'"] mod fixture;\n'
        +''.join('mod '+name+' { use super::fixture; include!("'+str(SYS/"tests"/(name+".rs"))+'"); }\n'
            for name in OLD_TESTS[:7])
        +'mod native_owner_runtime { include!("'+str(SYS/"tests/native_owner_runtime.rs")+'"); }\n'
        +'mod native_fd_dispatch { use super::fixture; use filesystem_service::Channel; include!("'+str(SYS/"tests/native_fd_dispatch.rs")+'"); }\n'
        +'mod broker { include!("'+str(SYS/"tests/native_broker_init.rs")+'"); }\n}\n')
    for profile,selected in (("AF07",old_base),("AF08",[*old_base,"--cfg","fs_directory_contexts","--cfg","fs_cwd","--cfg","fs_cwd_wire"])):
        for stage,extra in (("host",[]),("native",NATIVE)):
            producer=work/(profile+"-init-"+stage)
            folder=work/("old-owner-"+profile+"-"+stage);folder.mkdir()
            for name,filename,needs in owner_crates:
                common=COMMON if name=="fd_dispatch" else old_common
                run(profile+stage+"-old-owner-"+name,[tools["rustc"]["path"],*common,*selected,*extra,
                    *owner_deps(folder,producer,needs),"--crate-type=lib","--crate-name="+name,"-Cmetadata="+folder.name,P/filename,"-o",folder/("lib"+name+".rlib")])
            if not extra:
                all_imports=[*imports,*[name for name,_,_ in owner_crates]]
                for compiler in ("rustc","clippy-driver"):
                    run(profile+compiler+"-old-owner-tests-build",[tools[compiler]["path"],*old_common,*selected,
                        *owner_deps(folder,producer,all_imports),"--test",old_wrapper,"-o",folder/(compiler+"-tests")])
                result=run(profile+"-old-owner-tests",[folder/"rustc-tests","--test-threads=1"])
                require(b"56 passed; 0 failed" in result.stdout,"all old composed owner cases executed")
                record["old_owner_tests"][profile]=56
    # The current router now owns File events. Preserve the old call shape as a
    # compact negative consumer; historical actual-router evidence stays intact.
    old_router=work/"old-router-call.rs"
    old_router.write_text("#![no_std]\npub fn old<C:filesystem_service::Channel,T:filesystem_service::Channel>(p:&mut fd_dispatch::Peer<C>,f:&mut filesystem_remote_descriptors::ProcessFiles<T>,w:&mut[u8;4096]){let _=p.serve_received(f,&[0;64],w); }\n")
    for stage,extra in (("host",[]),("native",NATIVE)):
        current=work/("observed-"+stage)
        rejected=run(stage+"-preserved-old-router-call-rejected",[tools["rustc"]["path"],*COMMON,*flags,*extra,
            *deps(current,[*imports,"fd_dispatch"]),"--crate-type=lib",old_router,"-o",current/"absent.rlib"],expected=1)
        require(b"E0599" in rejected.stderr and b"serve_received" in rejected.stderr,"preserved old router call cannot discard receipts")
    run("observed-peer-rustfmt",[tools["rustfmt"]["path"],"--edition=2024","--check",P/"fd_dispatch.rs",P/"file_write_observations.rs",SYS/"tests/file_write_observations.rs"])



if __name__ == "__main__":
    sys.exit(runner["main"](check_function=check,program="aether-file-write-observations-check",
        evidence=SYS/"docs/evidence/file-write-observations-2026-10-24",description=__doc__,
        example="python3 -B sys-init/scripts/check-file-write-observations.py",
        scope="matched FILE peer host observations and no_std libraries only",
        extra_sources=(SOURCE,home_source,S/"check-file-writes.py",S/"check-process-writes.py",S/"check-client-mutations.py",
            S/"vendor/abi29-startup.rs",*S.glob("*.c"),*S.glob("*.h"),SYSTEM/"userland/docs/quality/clang-format.yaml",
            *P.glob("*.rs"),SYS/"tests/file_write_observations.rs",SYS/"tests/native_fd_dispatch.rs",
            *[SYS/"tests"/(name+".rs") for name in OLD_TESTS])))
