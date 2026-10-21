"""Focused source/publication gates; temporary Git objects, no scientific jobs."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

UNIT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("c21k_runner_contract_test_subject", UNIT / "epoch_pilot_contract.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n")


class PublishedTree:
    """Synthetic authority fixture. Only its commit constants are test-local."""
    def __init__(self, parent):
        self.root = parent / "checkout"
        self.control = parent / "external_controls"
        self.root.mkdir()
        self.control.mkdir()
        self.research = self.root / "research"
        self.h, self.i, self.k = (self.research / name for name in (C.H_NAME, C.I_NAME, Path(C.UNIT).name))
        self.git("init", "-q")
        self.git("config", "user.name", "C21K focused fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.h_own = self.source(self.h, {"h.py": b"h-source\n"})
        groups = {}
        for prefix, key, count in ((C.F_NAME, "c21f_runtime_files", 10),
                                   (C.G_NAME, "c21g_runtime_files", 4),
                                   (C.F_NAME + "/evidence/C21F_NATIVE_NCP_20261018T1358Z", "baseline_files", 6)):
            entries = {}
            for n in range(count):
                name = "fixture_%02d.txt" % n
                data = (key + str(n)).encode()
                path = self.research / prefix / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                entries[name] = C.record(data)
            groups[key] = entries
        self.g_manifest = self.research / C.G_NAME / "EXECUTION_MANIFEST.json"
        dump(self.g_manifest, groups)
        self.h_commit = self.commit("H fixture")
        self.i_own = self.source(self.i, {"i.py": b"i-source\n"})
        self.i_commit = self.commit("I fixture")
        self.k_own = self.source(self.k, {name: (name + "\n").encode() for name in C.RUNTIME_FILES})
        self.k_commit = self.commit("K fixture")
        self.git("checkout", "--detach", "-q", self.k_commit)
        self.receipts = {}
        for label, unit, own, commit in (("h", self.h, self.h_own, self.h_commit),
                                         ("i", self.i, self.i_own, self.i_commit),
                                         ("k", self.k, self.k_own, self.k_commit)):
            p = self.control / (label + ".json")
            dump(p, {"status": "PUBLISHED", "repository": C.REPOSITORY,
                     "unit": unit.relative_to(self.root).as_posix(),
                     "branch": "fixture/" + label, "content_commit": commit,
                     "execution_manifest_sha256": own["manifest"]["sha256"]})
            self.receipts[label] = p

    def git(self, *args):
        p = subprocess.run(["git", "-C", str(self.root), *args],
                           capture_output=True, check=True, timeout=10)
        return p.stdout.decode().strip()

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def source(self, unit, files):
        unit.mkdir(parents=True, exist_ok=True)
        records = {}
        for name, data in files.items():
            (unit / name).write_bytes(data)
            records[name] = C.record(data)
        dump(unit / "EXECUTION_MANIFEST.json", {"runtime_files": records})
        return {"manifest": C.record((unit / "EXECUTION_MANIFEST.json").read_bytes()),
                "runtime_files": records}

    def repoint_k(self, commit):
        value = json.loads(self.receipts["k"].read_text())
        value["content_commit"] = commit
        dump(self.receipts["k"], value)

    def verify(self):
        with patch.multiple(C, H_CONTENT=self.h_commit, I_CONTENT=self.i_commit,
                            G_MANIFEST_SHA256=C.record(self.g_manifest.read_bytes())["sha256"]):
            return C.verify_publications(self.receipts["k"], self.receipts["i"], self.receipts["h"],
                self.k_own, self.i_own, self.h_own, k_unit=self.k, i_unit=self.i)


class PublicationAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="c21k-pub-gate-")
        self.addCleanup(self.temp.cleanup)
        self.tree = PublishedTree(Path(self.temp.name))

    def test_published_detached_descendant_admits_all_three_actual_contents(self):
        t = self.tree
        p = t.verify()
        self.assertEqual(p["c21h"]["content_commit"], t.h_commit)
        self.assertEqual(p["c21i"]["content_commit"], t.i_commit)
        self.assertEqual(p["c21k"]["content_commit"], t.k_commit)
        self.assertTrue(p["inherited_execution_bytes_unchanged"])

    def test_attached_and_later_document_heads_are_rejected(self):
        t = self.tree
        t.git("checkout", "-q", "-b", "fixture-attached")
        with self.assertRaisesRegex(C.EpochPilotError, "DETACHED_PUBLISHED_C21K"):
            t.verify()
        t.git("checkout", "--detach", "-q", t.k_commit)
        (t.root / "metadata.txt").write_text("later document\n")
        t.commit("later metadata fixture")
        with self.assertRaisesRegex(C.EpochPilotError, "DETACHED_PUBLISHED_C21K"):
            t.verify()

    def test_old_i_receipt_cannot_be_relabelled_with_k_head(self):
        t = self.tree
        value = json.loads(t.receipts["i"].read_text())
        value["content_commit"] = t.k_commit
        dump(t.receipts["i"], value)
        with self.assertRaisesRegex(C.EpochPilotError, "MATCHING_PUBLISHED_CONTENT"):
            t.verify()

    def test_controls_must_be_external_and_published(self):
        t = self.tree
        original = t.receipts["k"]
        internal = t.root / "publication.json"
        internal.write_bytes(original.read_bytes())
        t.receipts["k"] = internal
        with self.assertRaisesRegex(C.EpochPilotError, "OUTSIDE_CHECKOUT"):
            t.verify()
        t.receipts["k"] = original
        value = json.loads(original.read_text())
        value["status"] = "PENDING_ROOT_PUBLICATION"
        dump(original, value)
        with self.assertRaisesRegex(C.EpochPilotError, "MATCHING_PUBLISHED_CONTENT"):
            t.verify()

    def test_committed_inherited_h_drift_rejected_even_with_restored_working_bytes(self):
        t = self.tree
        path = t.h / "h.py"
        original = path.read_bytes()
        path.write_bytes(b"changed only in K commit\n")
        changed = t.commit("bad inherited H")
        path.write_bytes(original)
        t.repoint_k(changed)
        with self.assertRaisesRegex(C.EpochPilotError, "PUBLISHED_RUNTIME_CONTENT_MISMATCH"):
            t.verify()

    def test_committed_f_dependency_drift_rejected(self):
        t = self.tree
        path = t.research / C.F_NAME / "fixture_00.txt"
        original = path.read_bytes()
        path.write_bytes(b"changed F dependency\n")
        changed = t.commit("bad inherited F")
        path.write_bytes(original)
        t.repoint_k(changed)
        with self.assertRaisesRegex(C.EpochPilotError, "PUBLISHED_RUNTIME_CONTENT_MISMATCH"):
            t.verify()

    def test_wrong_ancestry_does_not_reach_blob_admission(self):
        real = C._git
        def checked(root, *args, **kwargs):
            if args[:2] == ("merge-base", "--is-ancestor") and args[2] == self.tree.i_commit:
                raise C.EpochPilotError("PUBLICATION_GIT_CHECK_FAILED ancestry")
            return real(root, *args, **kwargs)
        with patch.object(C, "_git", side_effect=checked), patch.object(C, "_committed_records") as blobs:
            with self.assertRaisesRegex(C.EpochPilotError, "ancestry"):
                self.tree.verify()
            blobs.assert_not_called()

    def test_duplicate_or_nonfinite_receipt_json_is_rejected(self):
        t = self.tree
        original = t.receipts["k"].read_bytes()
        for suffix in (b',"status":"PUBLISHED"}', b',"extra":NaN}'):
            with self.subTest(suffix=suffix):
                t.receipts["k"].write_bytes(original.rstrip()[:-1] + suffix)
                with self.assertRaises(C.EpochPilotError):
                    t.verify()


class RuntimeSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="c21k-source-gate-")
        self.addCleanup(self.temp.cleanup)
        self.unit = Path(self.temp.name) / "unit"
        self.unit.mkdir()
        for name in C.RUNTIME_FILES:
            (self.unit / name).write_text("# isolated source fixture: " + name + "\n")
        self.manifest = {"schema": "C21K_EXECUTION_MANIFEST_V1", "unit": C.UNIT,
                         "c21h_manifest_sha256": C.H_MANIFEST_SHA256,
                         "c21i_manifest_sha256": C.I_MANIFEST_SHA256,
                         "runtime_files": {name: C.record((self.unit / name).read_bytes())
                                           for name in C.RUNTIME_FILES}}
        self.save()

    def save(self):
        dump(self.unit / "EXECUTION_MANIFEST.json", self.manifest)

    def test_exact_three_runtime_files_and_supported_modes(self):
        for mode in C.OPTIMIZATIONS:
            identity, _ = C.verify_k_source(mode, self.unit)
            self.assertEqual(identity["optimization"], mode)
        with self.assertRaisesRegex(C.EpochPilotError, "UNKNOWN_C21K_OPTIMIZATION"):
            C.verify_k_source("baseline", self.unit)
        (self.unit / "extra.py").write_text("# extra\n")
        self.manifest["runtime_files"]["extra.py"] = C.record((self.unit / "extra.py").read_bytes())
        self.save()
        with self.assertRaisesRegex(C.EpochPilotError, "THREE_SOURCE_MANIFEST"):
            C.verify_k_source("vectorized_exact", self.unit)

    def test_runtime_drift_and_symlink_are_rejected(self):
        path = self.unit / "epoch_adapter.py"
        original = path.read_bytes()
        path.write_bytes(original + b"# drift\n")
        with self.assertRaisesRegex(C.EpochPilotError, "RUNTIME_SOURCE_MISMATCH"):
            C.verify_k_source("vectorized_exact", self.unit)
        path.unlink()
        target = self.unit.parent / "same-bytes.py"
        target.write_bytes(original)
        path.symlink_to(target)
        with self.assertRaisesRegex(C.EpochPilotError, "SYMLINK"):
            C.verify_k_source("vectorized_exact", self.unit)

    def test_boolean_size_is_not_an_integer_file_record(self):
        self.manifest["runtime_files"]["epoch_adapter.py"]["bytes"] = True
        self.save()
        with self.assertRaisesRegex(C.EpochPilotError, "EXACT_FILE_RECORD_REQUIRED"):
            C.verify_k_source("vectorized_exact", self.unit)

    def test_inherited_i_authority_cannot_be_rewritten_with_an_edited_manifest(self):
        research = Path(self.temp.name) / "research"
        for name in (C.H_NAME, C.I_NAME):
            shutil.copytree(UNIT.parent / name, research / name,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        i = research / C.I_NAME
        C.verify_inherited_sources(i)
        adapter = i / "optimized_adapter.py"
        adapter.write_bytes(adapter.read_bytes() + b"\n")
        with self.assertRaisesRegex(C.EpochPilotError, "RUNTIME_SOURCE_MISMATCH"):
            C.verify_inherited_sources(i)
        manifest = json.loads((i / "EXECUTION_MANIFEST.json").read_bytes())
        manifest["runtime_files"]["optimized_adapter.py"] = C.record(adapter.read_bytes())
        dump(i / "EXECUTION_MANIFEST.json", manifest)
        with self.assertRaisesRegex(C.EpochPilotError, "PINNED_EXECUTION_MANIFEST"):
            C.verify_inherited_sources(i)


if __name__ == "__main__":
    unittest.main()
