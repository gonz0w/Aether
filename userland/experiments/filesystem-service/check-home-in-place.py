# SPDX-License-Identifier: BSD-2-Clause
"""Check explicit two-grant in-place construction with pinned offline tools."""
from pathlib import Path
import runpy
import json
import hashlib
import re
import shutil
import sys
import time

SOURCE = Path(__file__).resolve()
S = SOURCE.parent
file_source = S / "check-file-writes.py"
file_check = runpy.run_path(str(file_source))
runner = file_check["runner"]
require = runner["require"]
COMMON = runner["COMMON"]
NATIVE = runner["NATIVE"]


def check(record, work, proc, tools, deadline=None):
    if deadline is None:
        deadline = time.monotonic() + 300
    env = proc.clean_env(work)
    env["DYLD_LIBRARY_PATH"] = str(Path(tools["rustc"]["path"]).parent.parent / "lib")
    flags = [*runner["cfg"](True), "--cfg", "fs_home_wire"]
    flags += [v for name in ("paths", "file16", "replace", "process_views", "process_writes", "path_wire", "dup2_wire", "file_write_wire", "in_place", "home_in_place") for v in ("--cfg", "fs_" + name)]
    crates = [("filesystem_metadata", "metadata-lib.rs", []),
              ("filesystem_policy", "owner.rs", ["filesystem_metadata"]),
              ("filesystem_service", "service.rs", ["filesystem_policy"]),
              ("filesystem_client", "client.rs", ["filesystem_service"]),
              ("filesystem_remote_descriptors", "remote-descriptors.rs", ["filesystem_client", "filesystem_service"]),
              ("filesystem_fd_protocol", "fd-protocol.rs", ["filesystem_client", "filesystem_service", "filesystem_remote_descriptors"])]
    def run(label, argv, expected=0):
        left = deadline - time.monotonic()
        require(left > 0, "suite deadline before " + label)
        r = proc.run(list(map(str, argv)), cwd=runner["R"], env=env, work=work, label=label, timeout=min(60,left))
        record["rows"].append({"label":label,"expected_exit":expected,"process":r.record,"stdout":r.stdout.decode(errors="replace")[-7000:],"stderr":r.stderr.decode(errors="replace")[-5000:]})
        require(r.returncode == expected and r.record["complete"] and r.record["cleanup"] == "complete", label)
        return r
    def deps(folder, names):
        return ["-Ldependency="+str(folder), *[v for n in names for v in ("--extern",n+"="+str(folder/("lib"+n+".rlib")))]]
    def build(folder, extra=(), lint=False, sources=S, selected=flags):
        folder.mkdir(exist_ok=True)
        for name, filename, imports in crates:
            common = [v for v in COMMON if v != "-Funsafe-code" or name not in ("filesystem_metadata", "filesystem_client", "filesystem_remote_descriptors")]
            run(folder.name+"-"+name+("-clippy" if lint else ""), [tools["clippy-driver" if lint else "rustc"]["path"], *common,*selected,*extra,*deps(folder,imports),"--crate-type=lib","--crate-name="+name,"-Cmetadata="+folder.name,sources/filename,"-o",folder/("lib"+name+".rlib")])
    host = work / "home-init-host"
    build(host)
    imports = [n for n,_,_ in crates]
    common = [v for v in COMMON if v != "-Funsafe-code"]
    for compiler in ("rustc", "clippy-driver"):
        run(compiler+"-home-init-test-build", [tools[compiler]["path"],*common,*flags,*deps(host,imports),"--test",S/"home-wire-tests.rs","-o",work/(compiler+"-home-init")])
    result = run("home-init-tests", [work/"rustc-home-init","home_in_place::","--test-threads=1"])
    require(b"5 passed; 0 failed" in result.stdout,"all five home in-place cases executed")
    for stage,extra in (("host",[]),("native",NATIVE)):
        folder=work/("home-init-"+stage)
        if extra: build(folder,extra=extra)
        build(folder,extra=extra,lint=True)
    # Full old in-place construction/ledger tests exercise the same raw helpers.
    old_base = [v for i,v in enumerate(runner["cfg"]()) if v != "fs_directory_contexts" and not
                (v == "--cfg" and i+1 < len(runner["cfg"]()) and runner["cfg"]()[i+1] == "fs_directory_contexts")]
    old_base += [v for n in ("paths","file16","replace","process_views","path_wire","dup2_wire","in_place") for v in ("--cfg","fs_"+n)]
    for profile,selected in (("AF07",old_base),("AF08",[*old_base,"--cfg","fs_directory_contexts","--cfg","fs_cwd","--cfg","fs_cwd_wire"])):
        for stage,extra in (("host",[]),("native",NATIVE)):
            folder=work/(profile+"-init-"+stage)
            build(folder,extra=extra,selected=selected)
            if not extra:
                run(profile+"-init-tests-build",[tools["rustc"]["path"],*common,*selected,*deps(folder,imports[:-1]),"--test",S/"remote-descriptors.rs","-o",folder/"tests"])
                old = run(profile+"-init-tests",[folder/"tests","--test-threads=1"])
                require(b"init_tests::" in old.stdout and b"0 failed" in old.stdout and b"test result: ok." in old.stdout,"old in-place tests executed")
    # Dependency/profile rejection in both directions, with exact old dependencies.
    def without(selected,omitted):
        return [v for i,v in enumerate(selected) if v not in omitted and not
                (v == "--cfg" and i+1 < len(selected) and selected[i+1] in omitted)]
    for stage,extra in (("host",[]),("native",NATIVE)):
        current=work/("home-init-"+stage)
        for name,source,omitted,marker in (
            ("client-home","client.rs",{"fs_home_wire"},b"home in-place client requires"),
            ("client-storage","client.rs",{"fs_in_place"},b"home in-place client requires"),
            ("broker-storage","remote-descriptors.rs",{"fs_in_place"},b"home in-place broker requires"),
            ("broker-writes","remote-descriptors.rs",{"fs_process_writes"},b"home in-place broker requires"),
            ("FILE-storage","fd-protocol.rs",{"fs_in_place"},b"home in-place FILE requires"),
            ("FILE-home","fd-protocol.rs",{"fs_home_wire"},b"home in-place FILE requires"),
            ("FILE-writes","fd-protocol.rs",{"fs_file_write_wire"},b"home in-place FILE requires")):
            rejected=run(stage+"-missing-"+name,[tools["rustc"]["path"],*common,*without(flags,omitted),*extra,*deps(current,imports),"--crate-type=lib",S/source,"-o",current/"absent.rlib"],expected=1)
            require(marker in rejected.stderr,"explicit local home-init profile guard")
        for profile in ("AF07","AF08"):
            old=work/(profile+"-init-"+stage)
            rejected=run(stage+profile+"-FILE-unmatched-home-init",[tools["rustc"]["path"],*common,*old_base,"--cfg","fs_home_in_place",*extra,*deps(old,imports),"--crate-type=lib",S/"fd-protocol.rs","-o",old/"absent.rlib"],expected=1)
            require(b"home in-place FILE requires" in rejected.stderr,"old FILE must reject stray home init flag")
        absent=work/(stage+"-home-init-absent.rs")
        absent.write_text("#![no_std]\nuse core::mem::MaybeUninit;\npub fn probe<T:filesystem_service::Channel>(s:&mut MaybeUninit<filesystem_client::Client<T>>,t:T){let _=filesystem_client::Client::connect_home_in_place(s,t,91); }\n")
        for profile in ("AF07","AF08"):
            old=work/(profile+"-init-"+stage)
            rejected=run(stage+profile+"-old-client-no-home-init",[tools["rustc"]["path"],*common,*extra,*deps(old,["filesystem_service","filesystem_client"]),"--crate-type=lib",absent,"-o",old/"absent.rlib"],expected=1)
            require(b"E0599" in rejected.stderr and b"connect_home_in_place" in rejected.stderr,"old home constructor absent")
    controls=[
        ("second-entry","home-client.rs","self.entry(&second, 2)?","self.entry(&first, 1)?","both_greeting_failure_stages_preserve_cleanup_and_reuse_slot","HOME_INIT_REJECT"),
        ("next-token","home-client.rs","Self::initialize_in_place(slot, channel, epoch, 3)","Self::initialize_in_place(slot, channel, epoch, 2)","client_two_grants_next_token_and_exact_drop","HOME_INIT_NEXT"),
        ("home-rights","home-client.rs","rights: 15,","rights: 3,","all_poisoned_views_are_empty_and_real_file_write_receipt_works","HOME_INIT_HOME_RIGHTS"),
        ("failure-close","home-client.rs","self.shutdown();","let _ = ();","both_greeting_failure_stages_preserve_cleanup_and_reuse_slot","HOME_INIT_CLOSES"),
        ("failure-drop","home-client.rs","unsafe { core::ptr::drop_in_place(client) };","let _ = client;","both_greeting_failure_stages_preserve_cleanup_and_reuse_slot","HOME_INIT_FAILURE_DROP"),
        ("records","process-descriptors.rs",".write(Record {\n                        process: None,\n                        last_generation: 0,",".write(Record {\n                        process: None,\n                        last_generation: 9,","all_poisoned_views_are_empty_and_real_file_write_receipt_works","HOME_INIT_RECORDS"),
    ]
    record["home_init_controls"]=[]
    for label,filename,before,after,test,marker in controls:
        original=(S/filename).read_text()
        require(original.count(before)==1,"unique home-init control: "+label)
        folder=work/("init-control-"+label);sources=folder/"source";sources.mkdir(parents=True)
        for path in S.glob("*.rs"):shutil.copy2(path,sources/path.name)
        (sources/"vendor").mkdir();shutil.copy2(S/"vendor/abi29-startup.rs",sources/"vendor/abi29-startup.rs")
        (sources/filename).write_text(original.replace(before,after,1))
        build(folder,sources=sources)
        run(label+"-init-test-build",[tools["rustc"]["path"],*common,*flags,*deps(folder,imports),"--test",sources/"home-wire-tests.rs","-o",folder/"tests"])
        name="home_in_place::"+test
        rejected=run(label+"-init-reject",[folder/"tests","--exact",name,"--nocapture"],expected=101)
        require(name.encode() in rejected.stdout and b"1 failed" in rejected.stdout and marker.encode() in rejected.stderr,"named init control: "+label)
        record["home_init_controls"].append({"label":label,"file":filename,"before":before,"after":after,"test":name,"marker":marker,"sha256":runner["sha"](sources/filename)})
    # Instantiate the actual framed native endpoint type, never execute int81.
    pins=json.loads(runner["PINS"].read_text())
    pins["tools"]["objdump"]={"path":"/opt/homebrew/Cellar/llvm@21/21.1.8/bin/llvm-objdump",
        "sha256":"57df889beb6133ffd405ffb84795941c068a13a09dba0a40546d3b740666b9b7"}
    for name in ("objdump","readelf"):
        runner["verify"](pins["tools"][name]["path"],pins["tools"][name]["sha256"]);tools[name]=pins["tools"][name]
    native=work/"home-init-native"
    transport=runner["R"].parent/"sys-init/prototypes/native-filesystem-session/af07_transport.rs"
    run("home-init-concrete-transport",[tools["rustc"]["path"],*[v for v in common if not v.startswith("--edition=")],"--edition=2024",*flags,*NATIVE,*deps(native,["filesystem_service"]),"--crate-type=lib","--crate-name=home_init_transport",transport,"-o",native/"libhome_init_transport.rlib"])
    concrete=[*deps(native,imports),"--extern","home_init_transport="+str(native/"libhome_init_transport.rlib")]
    run("home-init-concrete-object",[tools["rustc"]["path"],*common,*flags,*NATIVE,*concrete,"--crate-type=lib","-Cno-redzone=yes","--emit=obj",S/"home-init-probe.rs","-o",native/"constructor.o"])
    run("home-init-concrete-clippy",[tools["clippy-driver"]["path"],*common,*flags,*NATIVE,*concrete,"--crate-type=lib","-Cno-redzone=yes","--emit=metadata",S/"home-init-probe.rs","-o",native/"constructor.rmeta"])
    saved=env.pop("DYLD_LIBRARY_PATH")
    try:
        assembly=run("home-init-concrete-inspect",[tools["objdump"]["path"],"-d","--demangle","--no-show-raw-insn","--x86-asm-syntax=intel",native/"constructor.o"])
        layout=run("home-init-concrete-layout",[tools["readelf"]["path"],"-x",".rodata.home_init_layout",native/"constructor.o"])
    finally:env["DYLD_LIBRARY_PATH"]=saved
    raw=bytes.fromhex("".join("".join(re.findall(r"\b[0-9a-fA-F]{8}\b",line.split(maxsplit=1)[1])[:4]) for line in layout.stdout.decode().splitlines() if line.lstrip().startswith("0x")))
    require(len(raw)==16,"concrete layout bytes")
    frames=[]
    for line in assembly.stdout.decode().splitlines():
        header=re.fullmatch(r"[0-9a-f]+ <(.+)>:",line.strip())
        if header:frames.append({"function":header[1],"push_and_sub_bytes":0,"adjustments":[],"prologue":[]})
        elif frames:
            if len(frames[-1]["prologue"]) < 24 and line.strip():
                frames[-1]["prologue"].append(line.strip())
            require(re.search(r"\b(?:and|mov|lea|xchg)\s+(?:rsp|esp)\s*,",line) is None and
                    re.search(r"\b(?:enter|leave)\b",line) is None,"unsupported constructor stack adjustment")
            instruction=re.match(r"\s*[0-9a-f]+:\s+(push|sub)\s+(.*)",line)
            if instruction:
                if instruction[1]=="push" or instruction[2].startswith("rsp, "):
                    frames[-1]["adjustments"].append(line.strip())
                if instruction[1]=="push":frames[-1]["push_and_sub_bytes"]+=8
                elif instruction[2].startswith("rsp, "):
                    amount=instruction[2][5:].strip();require(re.fullmatch(r"(?:0x[0-9a-f]+|[0-9]+)",amount) is not None,"static constructor reservation")
                    frames[-1]["push_and_sub_bytes"]+=int(amount,0)
    require(frames and any(row["function"]=="home_init" for row in frames),"concrete constructor root present")
    record["home_init_measurement"]={"assembly_sha256":hashlib.sha256(assembly.stdout).hexdigest(),"object_sha256":runner["sha"](native/"constructor.o"),"broker_size":int.from_bytes(raw[:8],"little"),"alignment":int.from_bytes(raw[8:],"little"),"frames":frames,"maximum_individual_reservation":max(row["push_and_sub_bytes"] for row in frames),"scope":"Concrete Framed<Endpoints<Native>> constructor and emitted helper static reservations, no redzone. No linked owner, summed/interrupt stack, whole fit or native execution."}
    run("home-init-rustfmt",[tools["rustfmt"]["path"],"--edition=2021","--check",*[S/n for n in ("client.rs","home-client.rs","remote-descriptors.rs","process-descriptors.rs","process-writes.rs","fd-protocol.rs","home-wire-tests.rs","home-in-place-tests.rs","home-init-probe.rs")]])
    file_check["check"](record,work,proc,tools,deadline=deadline)
    # Consume the sealed producer libraries made by the shared suite as well as
    # current AF07/08 selections. They must not acquire home APIs or stray flags.
    for stage,extra in (("host",[]),("native",NATIVE)):
        sealed=work/("sealed-"+stage)
        run(stage+"-sealed-old-client",[tools["rustc"]["path"],*common,*old_base,*extra,
            *deps(sealed,["filesystem_service"]),"--crate-type=lib","--crate-name=filesystem_client",
            S/"client.rs","-o",sealed/"libfilesystem_client.rlib"])
        run(stage+"-sealed-old-broker",[tools["rustc"]["path"],*common,*old_base,*extra,
            *deps(sealed,["filesystem_client","filesystem_service"]),"--crate-type=lib","--crate-name=filesystem_remote_descriptors",
            S/"remote-descriptors.rs","-o",sealed/"libfilesystem_remote_descriptors.rlib"])
        for source,marker in (("client.rs",b"home in-place client requires"),("fd-protocol.rs",b"home in-place FILE requires")):
            rejected=run(stage+"-sealed-stray-"+source,[tools["rustc"]["path"],*common,*old_base,"--cfg","fs_home_in_place",*extra,
                *deps(sealed,imports[:-1]),"--crate-type=lib",S/source,"-o",sealed/"absent.rlib"],expected=1)
            require(marker in rejected.stderr,"sealed selection rejects stray home-init flag")
        for profile,folder in (("AF07",work/("AF07-init-"+stage)),("AF08",work/("AF08-init-"+stage)),("sealed",sealed)):
            absent=work/(stage+profile+"-broker-home-init-absent.rs")
            absent.write_text("#![no_std]\nuse core::mem::MaybeUninit;\npub fn probe<T:filesystem_service::Channel>(s:&mut MaybeUninit<filesystem_remote_descriptors::ProcessFiles<T>>,t:T){let _=filesystem_remote_descriptors::ProcessFiles::connect_home_in_place(s,t,91); }\n")
            rejected=run(stage+profile+"-old-broker-no-home-init",[tools["rustc"]["path"],*common,*extra,
                *deps(folder,["filesystem_service","filesystem_remote_descriptors"]),"--crate-type=lib",absent,"-o",folder/"absent.rlib"],expected=1)
            require(b"E0599" in rejected.stderr and b"connect_home_in_place" in rejected.stderr,"old broker constructor absent")



if __name__ == "__main__":
    sys.exit(runner["main"](check_function=check, program="aether-home-in-place-check",
        evidence=runner["R"] / "docs/evidence/filesystem-home-in-place-2026-10-24",
        description=__doc__, example="python3 -B experiments/filesystem-service/check-home-in-place.py",
        scope="two-grant in-place host construction and no_std libraries only",
        extra_sources=(SOURCE,file_source,S/"check-process-writes.py",S/"check-client-mutations.py",S/"vendor/abi29-startup.rs", runner["R"].parent/"sys-init/prototypes/native-filesystem-session/af07_transport.rs", runner["R"].parent/"sys-init/prototypes/native-filesystem-session/af07_native.rs", *S.glob("*.c"), *S.glob("*.h"), runner["R"] / "docs/quality/clang-format.yaml")))
