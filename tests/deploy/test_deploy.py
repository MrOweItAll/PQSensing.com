"""Local fixtures only. No hosting/network/approval/asset-retention claims."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

DEPLOY = Path(__file__).resolve().parents[2] / "ops" / "deploy"
sys.path.insert(0, str(DEPLOY))
import artifact
import receiver

COMMIT = "a" * 40


class DeployFixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.base = self.root / "private"
        self.docroot = self.root / "document-root"
        self.base.mkdir(mode=0o700)
        self.docroot.mkdir()
        (self.docroot / "host-managed.txt").write_text("host file must survive")
        self.config = {
            "schemaVersion": 1, "enabled": True, "environment": "staging",
            "deploymentBase": str(self.base), "documentRoot": str(self.docroot),
            "acceptedBaseline": "baseline-fixture",
            "gates": {gate: True for gate in receiver.REQUIRED_GATES},
            "limits": {**artifact.DEFAULT_LIMITS, "minimumFreeDiskBytes": 1,
                       "minimumFreeInodes": 1, "receiveTimeoutSeconds": 10},
        }
        self.config_path = self.root / "trusted.json"
        self.save_config()
        self.engine = receiver.TransactionEngine(self.config, lambda _: True)
        self.counter = 0

    def save_config(self):
        self.config_path.write_bytes(artifact.canonical_json(self.config))
        self.config_path.chmod(0o600)

    def build(self, release_id="release-one", text="original", extra=None):
        self.counter += 1
        site = self.root / ("site-" + str(self.counter))
        site.mkdir()
        (site / "index.html").write_text("<html>" + text + "</html>")
        (site / "style.css").write_text("body { color: black }")
        for name, content in (extra or {}).items():
            file = site / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(content)
        archive_path = self.root / ("candidate-" + str(self.counter) + ".tar")
        result = artifact.create(site, archive_path, release_id, COMMIT, "baseline-fixture", "request-1", "workflow-1", ["unit-fixture"])
        return archive_path, result

    def receive(self, archive_path, result):
        with archive_path.open("rb") as stream:
            return self.engine.receive(stream, result["releaseId"], result["artifactSha256"], result["sourceCommit"], result["artifactBytes"])

    def installed_pair(self):
        old_path, old = self.build("old")
        new_path, new = self.build("new", "new candidate")
        self.receive(old_path, old)
        self.receive(new_path, new)
        self.engine._point("old")  # A local fixture, not a production bootstrap path.
        return old, new

    def raw_tar(self, entries, name="malformed.tar", format=tarfile.USTAR_FORMAT):
        path = self.root / name
        with tarfile.open(path, "w", format=format) as archive:
            for entry in entries:
                filename, data, kind, mode = entry
                member = tarfile.TarInfo(filename)
                member.type, member.mode = kind, mode
                member.size = len(data)
                if kind == tarfile.SYMTYPE:
                    member.linkname = "../../outside"
                archive.addfile(member, io.BytesIO(data))
        return path

    def repack(self, original, transform):
        with tarfile.open(original, "r:") as archive:
            entries = [(member.name, archive.extractfile(member).read(), tarfile.REGTYPE, 0o644) for member in archive]
        return self.raw_tar(transform(entries), "mutated.tar")


class ArtifactTests(DeployFixture):
    def test_deterministic_bytes_and_virtual_marker(self):
        first, result = self.build()
        second, second_result = self.build()
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(result, second_result)
        self.assertFalse((self.root / "site-1" / "release.json").exists())
        verified = artifact.verify(first, result["artifactSha256"])
        self.assertEqual(verified["sourceCommit"], COMMIT)
        self.assertEqual(verified["routes"], ["/"])

    def test_digest_and_manifest_hash_binding(self):
        original, result = self.build()
        with self.assertRaisesRegex(artifact.ContractError, "SHA-256 mismatch"):
            artifact.verify(original, "b" * 64)
        changed = self.repack(original, lambda entries: [(name, b"changed" if name == "site/index.html" else data, kind, mode) for name, data, kind, mode in entries])
        with self.assertRaisesRegex(artifact.ContractError, "hash/size mismatch"):
            artifact.verify(changed, artifact.file_sha(changed))

    def test_paths_links_special_files_extensions_and_duplicates(self):
        cases = [
            ("/index.html", tarfile.REGTYPE), ("site/../index.html", tarfile.REGTYPE),
            ("site/.htaccess", tarfile.REGTYPE), ("site/a\\b.html", tarfile.REGTYPE),
            ("site/a.php.html", tarfile.REGTYPE), ("site/a.html", tarfile.SYMTYPE),
            ("site/a.html", tarfile.LNKTYPE), ("site/a.html", tarfile.FIFOTYPE),
            ("site/a.html", tarfile.CHRTYPE), ("site/%2e%2e/x.html", tarfile.REGTYPE),
            ("site/cgi-bin/form.html", tarfile.REGTYPE), ("site/_pqs_current/x.html", tarfile.REGTYPE),
            ("site/_pqs_next_abc/x.html", tarfile.REGTYPE), ("site/a.sh", tarfile.REGTYPE),
            ("site/space .html.", tarfile.REGTYPE),
        ]
        for number, (name, kind) in enumerate(cases):
            with self.subTest(name=name, kind=kind):
                path = self.raw_tar([(name, b"x" if kind == tarfile.REGTYPE else b"", kind, 0o644)], "bad-" + str(number) + ".tar")
                destination = self.root / ("output-" + str(number))
                with self.assertRaises(artifact.ContractError):
                    artifact.verify(path, artifact.file_sha(path), destination=destination)
                self.assertFalse(destination.exists())
        for names in (("site/a.html", "site/a.html"), ("site/a.html", "site/A.html")):
            path = self.raw_tar([(name, b"x", tarfile.REGTYPE, 0o644) for name in names])
            with self.assertRaisesRegex(artifact.ContractError, "duplicate"):
                artifact.verify(path, artifact.file_sha(path))

    def test_executable_modes_extended_headers_and_hidden_tail(self):
        path = self.raw_tar([("site/index.html", b"x", tarfile.REGTYPE, 0o755)])
        with self.assertRaisesRegex(artifact.ContractError, "executable"):
            artifact.verify(path, artifact.file_sha(path))
        long_name = "site/" + "/".join(["a" * 50] * 3) + "/x.html"
        path = self.raw_tar([(long_name, b"x", tarfile.REGTYPE, 0o644)], "gnu.tar", tarfile.GNU_FORMAT)
        with self.assertRaisesRegex(artifact.ContractError, "extension"):
            artifact.verify(path, artifact.file_sha(path))
        path, _ = self.build()
        with path.open("ab") as stream:
            stream.write(b"x" * 512)
        with self.assertRaisesRegex(artifact.ContractError, "trailing data"):
            artifact.verify(path, artifact.file_sha(path))

    def test_count_expansion_and_manifest_limits(self):
        path, result = self.build()
        for limits in ({"maxArchiveBytes": 1024}, {"maxExtractedBytes": 3}, {"maxFileCount": 1}, {"maxManifestBytes": 20}):
            with self.subTest(limits=limits), self.assertRaises(artifact.ContractError):
                artifact.verify(path, result["artifactSha256"], limits)

    def test_no_partial_extraction_when_inventory_wrong(self):
        path, _ = self.build()
        changed = self.repack(path, lambda entries: entries + [("site/extra.html", b"extra", tarfile.REGTYPE, 0o644)])
        destination = self.root / "extracted"
        with self.assertRaisesRegex(artifact.ContractError, "inventory mismatch"):
            artifact.verify(changed, artifact.file_sha(changed), destination=destination)
        self.assertFalse(destination.exists())

    def test_file_ancestor_collision(self):
        path, _ = self.build(extra={"a.js": b"x"})
        def collision(entries):
            result = []
            for name, data, kind, mode in entries:
                if name == "manifest.json":
                    manifest = json.loads(data)
                    manifest["files"].append({"path": "a.js/child.html", "size": 1, "sha256": hashlib.sha256(b"x").hexdigest()})
                    manifest["routes"] = artifact.route_inventory(f["path"] for f in manifest["files"])
                    data = artifact.canonical_json(manifest)
                result.append((name, data, kind, mode))
            return result + [("site/a.js/child.html", b"x", tarfile.REGTYPE, 0o644)]
        changed = self.repack(path, collision)
        with self.assertRaisesRegex(artifact.ContractError, "path collision"):
            artifact.verify(changed, artifact.file_sha(changed))

    def test_text_key_scan_and_binary_template_bytes(self):
        for name, data in (("a.html", b"<?php echo 1 ?>"), ("a.html", b"<%= dangerous %>"), ("a.txt", b"-----BEGIN OPENSSH PRIVATE KEY-----\nxxx")):
            with self.subTest(name=name), self.assertRaises(artifact.ContractError):
                self.build(extra={name: data})
        self.build(extra={"a.jpg": b"\xff\x00<%<?php<?=\x80"})

    def test_only_exact_known_placeholder_omitted(self):
        _, result = self.build(extra={"cgi-bin/.gitkeep": b"\n"})
        self.assertEqual(result["excludedPaths"], ["cgi-bin/.gitkeep"])
        for payload in (b"private info", b"\n\n"):
            with self.assertRaises(artifact.ContractError):
                self.build(extra={"cgi-bin/.gitkeep": payload})
        with self.assertRaises(artifact.ContractError):
            self.build(extra={".env": b"password=secret"})

    def test_source_symlink_and_duplicate_json_rejected(self):
        with self.assertRaisesRegex(artifact.ContractError, "duplicate JSON"):
            artifact.strict_json(b'{"x": 1, "x": 2}')
        site = self.root / "symlink-site"
        site.mkdir()
        (site / "index.html").symlink_to(self.docroot / "host-managed.txt")
        with self.assertRaisesRegex(artifact.ContractError, "symlinks"):
            artifact.create(site, self.root / "symlink.tar", "r", COMMIT, "b", "q", "w")


class ReceiverTests(DeployFixture):
    def test_receive_idempotence_conflict_and_identity(self):
        path, result = self.build()
        self.assertEqual(self.receive(path, result)["status"], "received")
        self.assertEqual(self.receive(path, result)["status"], "already_received")
        changed, changed_result = self.build(text="changed same ID")
        with self.assertRaisesRegex(receiver.ReceiverError, "conflict"):
            self.receive(changed, changed_result)
        with path.open("rb") as stream, self.assertRaisesRegex(receiver.ReceiverError, "identity mismatch"):
            self.engine.receive(stream, "different", result["artifactSha256"], COMMIT, result["artifactBytes"])
        with self.assertRaisesRegex(receiver.ReceiverError, "conflict"):
            self.engine.verify_release(result["releaseId"], result["artifactSha256"], "b" * 40)

    def test_interrupted_and_corrupt_upload_never_publish(self):
        path, result = self.build()
        for content in (path.read_bytes()[:500], path.read_bytes() + b"x"):
            with self.assertRaises(receiver.ReceiverError):
                self.engine.receive(io.BytesIO(content), result["releaseId"], result["artifactSha256"], COMMIT, result["artifactBytes"])
        self.assertEqual(list(self.engine.incoming.iterdir()), [])
        self.assertEqual(list(self.engine.releases.iterdir()), [])
        self.assertIsNone(self.engine.current())

    def test_baseline_mismatch_and_disk_shortage(self):
        path, result = self.build()
        self.engine.config["acceptedBaseline"] = "other-baseline"
        with self.assertRaisesRegex(receiver.ReceiverError, "baseline identity"):
            self.receive(path, result)
        self.engine.config["acceptedBaseline"] = "baseline-fixture"
        with patch.object(self.engine, "space_check", side_effect=receiver.ReceiverError("insufficient free disk")):
            with self.assertRaisesRegex(receiver.ReceiverError, "free disk"):
                self.receive(path, result)
        self.assertEqual(list(self.engine.releases.iterdir()), [])

    def test_installed_tamper_and_pointer_escape(self):
        path, result = self.build()
        self.receive(path, result)
        file = self.engine.releases / result["releaseId"] / "site" / "index.html"
        file.chmod(0o644)
        file.write_text("tampered")
        with self.assertRaisesRegex(receiver.ReceiverError, "hash mismatch"):
            self.engine.verify_release(result["releaseId"], result["artifactSha256"], COMMIT)
        self.engine.pointer.symlink_to(self.root)
        with self.assertRaisesRegex(receiver.ReceiverError, "escapes"):
            self.engine.current()

    def test_lock_and_stale_expected_current(self):
        old, new = self.installed_pair()
        with self.engine.locked():
            another = receiver.TransactionEngine(self.config)
            with self.assertRaisesRegex(receiver.ReceiverError, "busy"):
                another.status()
        with self.assertRaisesRegex(receiver.ReceiverError, "expected-current conflict"):
            self.engine.transition("new", new["artifactSha256"], COMMIT, "stale")
        self.assertEqual(self.engine.current(), "old")
        self.assertIsNone(self.engine.journal())

    def test_success_idempotence_explicit_rollback_and_root_preservation(self):
        old, new = self.installed_pair()
        root_inode = self.docroot.stat().st_ino
        first = self.engine.transition("new", new["artifactSha256"], COMMIT, "old")
        self.assertEqual(first["status"], "succeeded")
        second = self.engine.transition("new", new["artifactSha256"], COMMIT, "old")
        self.assertEqual(first["transactionId"], second["transactionId"])
        rollback = self.engine.transition("old", old["artifactSha256"], COMMIT, "new", operation="rollback")
        self.assertEqual(rollback["status"], "succeeded")
        self.assertEqual(self.engine.current(), "old")
        self.assertEqual(root_inode, self.docroot.stat().st_ino)
        self.assertEqual((self.docroot / "host-managed.txt").read_text(), "host file must survive")
        self.assertEqual(list(self.docroot.glob("_pqs_next_*")), [])

    def test_failed_health_restores_previous_and_verifies_it(self):
        old, new = self.installed_pair()
        checks = []
        def health(result):
            checks.append(result["releaseId"])
            return result["releaseId"] == "old"
        self.engine.health_check = health
        result = self.engine.transition("new", new["artifactSha256"], COMMIT, "old")
        self.assertEqual(result["status"], "rolled_back")
        self.assertEqual(checks, ["new", "old"])
        self.assertEqual(self.engine.current(), "old")

    def test_failed_restoration_stays_unresolved(self):
        old, new = self.installed_pair()
        self.engine.health_check = lambda _: False
        result = self.engine.transition("new", new["artifactSha256"], COMMIT, "old")
        self.assertEqual(result["status"], "rollback_failed")
        with self.assertRaisesRegex(receiver.ReceiverError, "unresolved"):
            self.engine.transition("new", new["artifactSha256"], COMMIT, "old")
        self.engine.health_check = lambda _: True
        self.assertEqual(self.engine.recover()["status"], "interrupted_rolled_back")

    def test_real_process_exit_after_pointer_switch_recovers_from_disk(self):
        old, new = self.installed_pair()
        child = """
import json, os, sys
sys.path.insert(0, sys.argv[1])
import receiver
engine = receiver.TransactionEngine(json.load(open(sys.argv[2])), lambda _: True)
original = engine._point
def exit_after_pointer(release_id):
    original(release_id)
    os._exit(93)
engine._point = exit_after_pointer
engine.transition('new', sys.argv[3], 'a' * 40, 'old')
"""
        result = subprocess.run([sys.executable, "-c", child, str(DEPLOY), str(self.config_path), new["artifactSha256"]], capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 93, result.stderr)
        fresh = receiver.TransactionEngine(self.config, lambda _: True)
        self.assertEqual(fresh.current(), "new")
        self.assertEqual(fresh.journal()["status"], "prepared")
        restored = fresh.recover()
        self.assertEqual(restored["status"], "interrupted_rolled_back")
        self.assertEqual(fresh.current(), "old")
        self.assertEqual(fresh.recover()["status"], "no_pending_transaction")

    def test_recovery_does_not_overwrite_an_unrelated_pointer(self):
        old, new = self.installed_pair()
        third_path, third = self.build("third")
        self.receive(third_path, third)
        original_point = self.engine._point
        def stop_after_pointer(release_id):
            original_point(release_id)
            raise SystemExit(93)
        with patch.object(self.engine, "_point", side_effect=stop_after_pointer), self.assertRaises(SystemExit):
            self.engine.transition("new", new["artifactSha256"], COMMIT, "old")
        original_point("third")
        with self.assertRaisesRegex(receiver.ReceiverError, "no longer owns"):
            self.engine.recover()
        self.assertEqual(self.engine.current(), "third")

    def test_public_activation_unconditionally_blocked_and_forced_command_not_shell(self):
        for verb in ("promote", "rollback", "recover"):
            command = [sys.executable, str(DEPLOY / "receiver.py"), "--config", str(self.config_path), "--role", "staging", verb]
            if verb != "recover":
                command.extend(["--release-id", "r", "--sha256", "a" * 64, "--source-commit", COMMIT, "--expected-current", "old"])
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("activation unavailable", result.stderr)
        touched = self.root / "must-not-exist"
        result = subprocess.run([sys.executable, str(DEPLOY / "receiver.py"), "--config", str(self.config_path), "--role", "staging", "--ssh"], env={**os.environ, "SSH_ORIGINAL_COMMAND": "pqs-receiver status; touch " + str(touched)}, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(touched.exists())

    def test_disabled_config_permissions_and_root_protection(self):
        self.config["enabled"] = False
        self.save_config()
        with self.assertRaisesRegex(receiver.ReceiverError, "disabled"):
            receiver.load_config(self.config_path, "staging")
        self.config["enabled"] = True
        self.save_config()
        self.assertEqual(receiver.load_config(self.config_path, "staging"), self.config)
        self.config_path.chmod(0o666)
        with self.assertRaisesRegex(receiver.ReceiverError, "not group/world writable"):
            receiver.load_config(self.config_path, "staging")
        self.config_path.chmod(0o600)
        self.config["deploymentBase"] = str(self.docroot)
        self.docroot.chmod(0o700)
        self.save_config()
        with self.assertRaisesRegex(receiver.ReceiverError, "disjoint"):
            receiver.load_config(self.config_path, "staging")


if __name__ == "__main__":
    unittest.main()
