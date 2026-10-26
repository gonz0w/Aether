# SPDX-License-Identifier: BSD-2-Clause
"""Native header prefix controls; no compiler, native or guest execution."""
from contextlib import ExitStack
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import fs_host_dependencies as dependencies
import source_paths

SOURCE = (ROOT / "userland/experiments/filesystem-service/"
          "home_native_c_checks.py")
SPEC = importlib.util.spec_from_file_location("home_c_prefix", SOURCE)
checks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checks)
OLD = Path("/Users/cam/DEV/Aether")
OVERLAYS = [OLD / "zig-out/fs-metadata-launch-ppqz1x6m/base/port" / name
            for name in ("resources", "allocation")]
DELIVERY = OLD / ("userland/build/service-deliveries/"
                  "filesystem-service-directories-2026-10-20-v1/source")


class NativeHeaderPrefix(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="home-c-prefix-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.public = self.base / "public"
        self.retained = self.base / "retained"
        self.volume = self.public / "user/storage/openzfs-volume"
        self.service = self.public / "userland/experiments/filesystem-service"
        self.resources = self.base / "llvm/lib/clang/21/include"
        for directory in (self.volume, self.service, self.resources):
            directory.mkdir(parents=True)
        (self.volume / "volume.h").write_text("CURRENT PUBLIC HEADER\n")
        self.tool = self.base / "llvm/bin/clang"
        self.tool.parent.mkdir(parents=True)
        self.tool.write_bytes(b"synthetic compiler identity; never executed")
        self.compiler = {"path": str(self.tool),
                         "sha256": checks.sha(self.tool)}
        self.work = self.base / "owned"
        self.empty = self.work / "home-c/empty-root"
        self.empty.mkdir(parents=True)
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(patch.object(checks, "ROOT", self.public))
        self.stack.enter_context(patch.object(checks, "S", self.service))
        self.stack.enter_context(
            patch.object(source_paths, "ROOT", self.public))
        self.stack.enter_context(
            patch.object(dependencies, "ROOT", self.public))
        self.retained.mkdir()
        self.stack.enter_context(patch.dict(os.environ, {
            dependencies.ENV: str(self.retained)}))

    def route(self, *args, **kwargs):
        return checks.native_header_prefix(
            [str(self.tool), *map(str, args)], self.compiler, **kwargs)

    def dependency(self, member, *, file=False):
        path = self.retained / ".deps/native-current" / member
        if file:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("retained config\n")
        else:
            path.mkdir(parents=True, exist_ok=True)
        return path

    def test_live_product_and_exact_delivery_select_current_headers(self):
        routed, omitted = self.route(
            "-I" + str(OLD / "user/storage/openzfs-volume"),
            "-I", DELIVERY, "-O2", "-DROOT=/historical/macro-data")
        self.assertEqual(routed, [str(self.tool), "-I" + str(self.volume),
                                  "-I", str(self.service), "-O2",
                                  "-DROOT=/historical/macro-data"])
        self.assertEqual((Path(routed[1][2:]) / "volume.h").read_text(),
                         "CURRENT PUBLIC HEADER\n")
        self.assertEqual(omitted, [])

    def test_separate_paths_use_declared_retained_inputs(self):
        include = self.dependency("baseline/headers/include")
        config = self.dependency("baseline/source/zfs/zfs_config.h", file=True)
        original = OLD / ".deps/native-current/baseline"
        routed, _ = self.route(
            "-I", original / "headers/include",
            "-isystem", self.resources, "-include",
            original / "source/zfs/zfs_config.h")
        self.assertEqual(routed, [str(self.tool), "-I", str(include),
                                  "-isystem", str(self.resources),
                                  "-include", str(config)])

    def test_only_exact_disposed_include_overlays_may_be_omitted(self):
        routed, omitted = self.route(
            "-I" + str(OVERLAYS[0]), "-I", OVERLAYS[1])
        self.assertEqual(routed, [str(self.tool)])
        self.assertEqual(omitted, [{"flag": "-I", "path": str(path)}
                                   for path in OVERLAYS])
        for path in (OVERLAYS[0] / "child",
                     OLD / "zig-out/unknown/port/resources"):
            with self.subTest(path=path), self.assertRaises(RuntimeError):
                self.route("-I" + str(path))
        with self.assertRaises(RuntimeError):
            self.route("-include", OVERLAYS[0])

    def test_macro_map_routes_only_input_side_and_keeps_output_bytes(self):
        baseline = self.dependency("baseline")
        rhs = str(OLD / "zig-out/recorded-output") + "=unchanged"
        original = OLD / ".deps/native-current/baseline"
        routed, _ = self.route(
            "-fmacro-prefix-map=" + str(original) + "=" + rhs)
        self.assertEqual(
            routed[1], "-fmacro-prefix-map=" + str(baseline) + "=" + rhs)
        with self.assertRaises(RuntimeError):
            self.route("-fmacro-prefix-map=/foreign/input=" + rhs)

    def test_exact_empty_sysroot_requires_empty_owned_directory(self):
        sdk = OLD / ".deps/native-current/sdk"
        requested = "--sysroot=" + str(sdk / "empty-root")
        routed, omitted = self.route(
            requested, empty_sysroot=self.empty, work=self.work)
        self.assertEqual(routed[1], "--sysroot=" + str(self.empty))
        self.assertEqual(omitted, [])
        for candidate in (self.base, self.work / "other"):
            with self.subTest(candidate=candidate):
                with self.assertRaises(RuntimeError):
                    self.route(requested, empty_sysroot=candidate,
                               work=self.work)
        (self.empty / "unexpected.h").write_text("not empty")
        with self.assertRaises(RuntimeError):
            self.route(requested, empty_sysroot=self.empty, work=self.work)
        with self.assertRaises(RuntimeError):
            self.route("--sysroot=" + str(sdk / "other"),
                       empty_sysroot=self.empty, work=self.work)
        (self.empty / "unexpected.h").unlink()
        self.empty.rmdir()
        foreign = self.base / "foreign-empty"
        foreign.mkdir()
        self.empty.symlink_to(foreign, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            self.route(requested, empty_sysroot=self.empty, work=self.work)

    def test_unknown_missing_foreign_and_parent_paths_are_rejected(self):
        foreign = self.base / "foreign"
        foreign.mkdir()
        escape = self.public / (".deps/native-current/sdk/../../../"
                                "user/storage/openzfs-volume")
        for value in (foreign, self.volume / "missing",
                      OLD / "user/storage/other", OLD / ".deps/unknown/include",
                      OLD / ".deps/native-current/missing", escape):
            with self.subTest(value=value), self.assertRaises(RuntimeError):
                self.route("-I", value)

    def test_foreign_source_and_dependency_aliases_are_rejected(self):
        foreign = self.base / "foreign"
        foreign.mkdir()
        (self.volume / "alias").symlink_to(foreign, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            self.route("-I", self.volume / "alias")
        selected = self.public / ".deps/native-current"
        selected.parent.mkdir()
        selected.symlink_to(foreign, target_is_directory=True)
        self.dependency("baseline")
        with self.assertRaises((RuntimeError, ValueError)):
            self.route("-I", selected / "baseline")

    def test_malformed_or_unclassified_path_flags_are_rejected(self):
        for args in (("-I",), ("-isystem", "-O2"), ("-include", "relative.h"),
                     ("--sysroot=",), ("-fmacro-prefix-map=no-delimiter",),
                     ("-iquote", self.volume),
                     ("-include" + str(self.volume),),
                     (str(self.volume),), ("@response",)):
            with self.subTest(args=args), self.assertRaises(RuntimeError):
                self.route(*args)

    def test_unclassified_driver_and_preprocessor_options_are_rejected(self):
        for arg in ("-Wp,-I,/foreign", "-resource-dir=/foreign",
                    "-fmodule-map-file=/foreign", "--config=/foreign",
                    "-fplugin=/foreign", "-Xclang", "-mllvm"):
            with self.subTest(arg=arg), self.assertRaises(RuntimeError):
                self.route(arg)
        literal = "-DOPTION=-Wp,-I,/foreign"
        routed, omitted = self.route(literal)
        self.assertEqual(routed, [str(self.tool), literal])
        self.assertEqual(omitted, [])

    def test_compiler_path_and_bytes_are_not_substituted(self):
        with self.assertRaises(RuntimeError):
            checks.native_header_prefix(["/foreign/clang"], self.compiler)
        self.tool.write_bytes(b"changed synthetic tool")
        with self.assertRaises(RuntimeError):
            self.route("-I", self.volume)


class ActualCheckPrefix(unittest.TestCase):
    def test_standalone_component_import_finds_routing_modules(self):
        scripts = str(ROOT / "scripts")
        search = [str(SOURCE.parent),
                  *[name for name in sys.path if name != scripts]]
        pins = json.loads(checks.PINS.read_text())
        receipt = ROOT / ".deps/fs-launch-af07-2026-10-23-v13/build.json"
        original = json.loads(receipt.read_text())
        argv = next(row["argv"] for row in original["commands"]
                    if "-c" in row["argv"] and any(
                        arg.endswith("/metadata-provider.o")
                        for arg in row["argv"]))
        with tempfile.TemporaryDirectory(prefix="home-c-import-") as directory:
            work = Path(directory).resolve()
            empty = work / "home-c/empty-root"
            empty.mkdir(parents=True)
            with patch.object(sys, "path", search), patch.dict(sys.modules):
                for name in ("source_paths", "fs_host_dependencies"):
                    sys.modules.pop(name, None)
                spec = importlib.util.spec_from_file_location(
                    "home_c_standalone", SOURCE)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                routed, omitted = module.native_header_prefix(
                    argv[:argv.index("-c")], pins["tools"]["clang"],
                    empty_sysroot=empty, work=work)
                self.assertEqual(sys.path[0], scripts)
                self.assertIn("-I" + str(ROOT / "user/storage/openzfs-volume"),
                              routed)
                self.assertEqual(len(omitted), 2)

    def test_actual_check_routes_before_original_header_command(self):
        """Execute check's prefix stage with every process modeled."""
        class PrefixReached(Exception):
            pass

        captured = []
        generated = set()

        def replace_once(text, old, new):
            if text.count(old) != 1:
                raise ValueError("modeled generator anchor")
            return text.replace(old, new)

        def generate(folder):
            if folder == checks.S or folder in generated:
                raise ValueError("modeled generator output guard")
            generated.add(folder)
            (folder / "home-filesystem-engine.c").write_text(
                "modeled C input\n")
            (folder / "home-filesystem-import.c").write_text(
                "unsigned order_error = ordered_required ? "
                "aether_pool_hooks_check_ordered() : 0;")
            return []

        def deny_render(*args):
            raise ValueError("modeled original source guard")

        generator = {"generate": generate, "replace_once": replace_once,
                     "render": deny_render,
                     "ORIGINALS": {
                         "user/storage/service-runtime/filesystem-engine.c":
                         "modeled"}}

        def run(argv, **kwargs):
            label = kwargs["label"]
            if label == "home-c-original-headers-importer":
                captured.extend(map(str, argv))
                raise PrefixReached()
            expected = 0
            stdout = b""
            stderr = b""
            if (label.startswith("home-c-lifecycle-") and
                    label != "home-c-lifecycle-build"):
                case = label.rsplit("-", 1)[1]
                stdout = ("case " + case + " passed").encode()
            if label == "home-c-skipped-order-control":
                expected, stderr = 1, b"HOME_ORDER_ORACLE"
            if label == "home-c-reject-packed-layout":
                expected, stderr = 1, b"static assertion failed"
            if label == "home-c-reject-legacy-launch-pointer":
                expected = 1
                stderr = (b"incompatible pointer types aether_fs_launch_state "
                          b"aether_fs_home_launch_state")
            return SimpleNamespace(
                returncode=expected, stdout=stdout, stderr=stderr,
                record={"complete": True, "cleanup": "complete"})

        pins = json.loads(checks.PINS.read_text())
        proc = SimpleNamespace(clean_env=lambda work: {}, run=run)
        record = {"rows": []}
        temporary = tempfile.TemporaryDirectory(prefix="home-c-check-prefix-")
        with temporary as directory:
            with patch.object(checks.runpy, "run_path",
                              return_value=generator):
                with self.assertRaises(PrefixReached):
                    checks.check(record, Path(directory).resolve(), proc,
                                 pins["tools"], time.monotonic() + 60)
            volume = "user/storage/openzfs-volume"
            self.assertIn("-I" + str(ROOT / volume), captured)
            self.assertNotIn("-I" + str(OLD / volume), captured)
            self.assertNotIn("-I" + str(DELIVERY), captured)
            self.assertIn("-I" + str(checks.S), captured)
            recipe = record["home_c_original_header_recipe"]
            routed = recipe["routed_argv"]
            self.assertEqual(routed, captured[:len(routed)])
            self.assertIn("-I" + str(OLD / "user/storage/openzfs-volume"),
                          recipe["requested_argv"])
            self.assertEqual(recipe["omitted_missing_old_overlay_dirs"],
                             [{"flag": "-I", "path": str(path)}
                              for path in OVERLAYS])


if __name__ == "__main__":
    unittest.main()
