#!/usr/bin/env python3
"""Fail-closed receiver scaffold. Public activation intentionally unavailable.

Receive/verify can be installed only after host setup. TransactionEngine is an
offline-tested component, NOT an installed or complete production deployer.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import signal
import stat
import sys
import tempfile
import time
import uuid

import artifact

ACTIVATION_BLOCK = (
    "activation unavailable: retained-asset routing, trusted live health checks, "
    "initial baseline cutover, and host capability proof are not implemented/installed; "
    "no configuration flag can enable this scaffold"
)
REQUIRED_GATES = ("baselineAccepted", "legacyDeploymentDisabled", "hostCapabilityTestsPassed",
                  "routerAccepted", "keyRestrictionsVerified", "privateBackupVerified")


class ReceiverError(ValueError):
    pass


def fsync_dir(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def atomic_json(path, value):
    """Write+sync+rename on the same filesystem; no delete/recreate interval."""
    path = Path(path)
    descriptor, temporary = tempfile.mkstemp(prefix=".state-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(artifact.canonical_json(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        fsync_dir(path.parent)
    finally:
        Path(temporary).unlink(missing_ok=True)


def read_json(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 8 * 1024 * 1024:
        raise ReceiverError("invalid state file")
    return artifact.strict_json(path.read_bytes())


def trusted_directory(value, private=False):
    if not isinstance(value, str) or not value or not Path(value).is_absolute():
        raise ReceiverError("absolute trusted host path required")
    path = Path(value)
    if path.resolve() != path or not path.is_dir() or path.is_symlink():
        raise ReceiverError("host path must exist without symlink components")
    info = path.stat()
    if info.st_uid != os.geteuid() or info.st_mode & 0o022 or (private and info.st_mode & 0o077):
        raise ReceiverError("untrusted host directory ownership/permissions")
    return path


def load_config(path, role):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ReceiverError("trusted host config file required")
    info = path.stat()
    if info.st_uid != os.geteuid() or info.st_mode & 0o022:
        raise ReceiverError("host config must be owned by receiver user and not group/world writable")
    config = read_json(path)
    if config.get("schemaVersion") != 1 or config.get("environment") != role:
        raise ReceiverError("configuration version/environment mismatch")
    if config.get("enabled") is not True:
        raise ReceiverError("receiver disabled in trusted host config")
    for gate in REQUIRED_GATES:
        if config.get("gates", {}).get(gate) is not True:
            raise ReceiverError("unverified host gate: " + gate)
    if role == "production" and config.get("gates", {}).get("approvalCapabilityVerified") is not True:
        raise ReceiverError("production approval capability not verified")
    artifact.identifier(config.get("acceptedBaseline"), "accepted baseline")
    base = trusted_directory(config.get("deploymentBase"), private=True)
    root = trusted_directory(config.get("documentRoot"))
    if base == root or base.is_relative_to(root) or root.is_relative_to(base):
        raise ReceiverError("private deployment base and real document root must be disjoint")
    limits = config.get("limits", {})
    for key in (*artifact.DEFAULT_LIMITS, "minimumFreeDiskBytes", "minimumFreeInodes", "receiveTimeoutSeconds"):
        if type(limits.get(key)) is not int or limits[key] <= 0:
            raise ReceiverError("positive host limit required: " + key)
    if limits["receiveTimeoutSeconds"] > 1800:
        raise ReceiverError("receive timeout cannot exceed 1800 seconds")
    # Never let a host config silently relax the reviewed parser memory ceiling.
    for key, ceiling in artifact.DEFAULT_LIMITS.items():
        if limits[key] > ceiling:
            raise ReceiverError("host limit exceeds receiver ceiling: " + key)
    return config


class TransactionEngine:
    """Filesystem transaction component; callers supply a trusted health checker.

    The CLI deliberately does not expose this component's transition/recover
    methods until routing, asset retention, and live checks are implemented.
    """

    def __init__(self, config, health_check=None):
        self.config = config
        self.base = trusted_directory(config["deploymentBase"], private=True)
        self.root = trusted_directory(config["documentRoot"])
        self.limits = config["limits"]
        self.health_check = health_check
        self.releases = self.base / "releases"
        self.incoming = self.base / "incoming"
        self.state = self.base / "state"
        for directory in (self.releases, self.incoming, self.state):
            directory.mkdir(mode=0o700, exist_ok=True)
            trusted_directory(str(directory), private=True)
        self.pointer = self.root / "_pqs_current"
        self.journal_path = self.state / "journal.json"

    @contextmanager
    def locked(self):
        descriptor = os.open(self.state / "deployment.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise ReceiverError("invalid deployment lock")
            try:
                fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise ReceiverError("deployment busy; read status before retrying") from error
            yield
        finally:
            os.close(descriptor)

    def space_check(self, archive_bytes=0):
        available = os.statvfs(self.base)
        needed = self.limits["minimumFreeDiskBytes"] + archive_bytes + self.limits["maxExtractedBytes"]
        if available.f_bavail * available.f_frsize < needed:
            raise ReceiverError("insufficient free disk; no releases were removed")
        if available.f_favail < self.limits["minimumFreeInodes"] + self.limits["maxFileCount"] + 10:
            raise ReceiverError("insufficient free inodes; no releases were removed")

    def journal(self):
        return read_json(self.journal_path) if self.journal_path.exists() else None

    def unresolved(self):
        journal = self.journal()
        return journal if journal and journal.get("status") in {"prepared", "activated", "rollback_failed"} else None

    def current(self):
        if not self.pointer.is_symlink():
            if self.pointer.exists():
                raise ReceiverError("current pointer is not a symlink; refusing to replace a real file/directory")
            return None
        target = Path(os.readlink(self.pointer))
        try:
            relative = target.relative_to(self.releases)
        except ValueError as error:
            raise ReceiverError("current pointer escapes releases") from error
        if len(relative.parts) != 2 or relative.parts[1] != "site":
            raise ReceiverError("invalid current pointer target")
        release_id = artifact.identifier(relative.parts[0])
        if target != self.releases / release_id / "site" or target.resolve() != target or not target.is_dir():
            raise ReceiverError("dangling/indirect current pointer")
        return release_id

    def identity(self, release_id, sha, commit):
        artifact.identifier(release_id)
        artifact.digest(sha)
        artifact.source_commit(commit)
        directory = self.releases / release_id
        if directory.is_symlink() or not directory.is_dir():
            raise ReceiverError("unknown release")
        stored = read_json(directory / "receipt.json")
        if (stored.get("releaseId"), stored.get("artifactSha256"), stored.get("sourceCommit")) != (release_id, sha, commit):
            raise ReceiverError("release ID/digest/source conflict")
        if stored.get("baselineId") != self.config["acceptedBaseline"]:
            raise ReceiverError("release baseline is not accepted")
        return stored

    def verify_release(self, release_id, sha, commit):
        stored = self.identity(release_id, sha, commit)
        directory = self.releases / release_id
        checked = artifact.verify(directory / "artifact.tar", sha, self.limits)
        if stored != {k: v for k, v in checked.items() if k != "manifest"}:
            raise ReceiverError("stored receipt mismatch")
        if read_json(directory / "manifest.json") != checked["manifest"]:
            raise ReceiverError("stored manifest mismatch")
        expected = {f["path"]: f for f in checked["manifest"]["files"]}
        observed = {}
        for root, directories, files in os.walk(directory / "site", followlinks=False):
            for name in directories + files:
                if (Path(root) / name).is_symlink():
                    raise ReceiverError("installed symlink")
            for name in files:
                file = Path(root) / name
                relative = file.relative_to(directory / "site").as_posix()
                if not file.is_file():
                    raise ReceiverError("installed special file")
                observed[relative] = {"path": relative, "size": file.stat().st_size, "sha256": artifact.file_sha(file)}
        if observed != expected:
            raise ReceiverError("installed file inventory/hash mismatch")
        return stored

    def receive(self, stream, release_id, sha, commit, byte_count):
        artifact.identifier(release_id)
        artifact.digest(sha)
        artifact.source_commit(commit)
        if type(byte_count) is not int or not 1024 <= byte_count <= self.limits["maxArchiveBytes"]:
            raise ReceiverError("invalid receive byte count")
        with self.locked():
            if self.unresolved():
                raise ReceiverError("unresolved transaction; administrative recovery required")
            self.space_check(byte_count)
            descriptor, temporary = tempfile.mkstemp(prefix="upload-", suffix=".tar", dir=self.incoming)
            unpacked = self.incoming / ("unpacked-" + uuid.uuid4().hex)
            try:
                running_hash = hashlib.sha256()
                remaining = byte_count
                with os.fdopen(descriptor, "wb") as output:
                    while remaining:
                        block = stream.read(min(1024 * 1024, remaining))
                        if not block:
                            raise ReceiverError("interrupted/truncated upload")
                        remaining -= len(block)
                        running_hash.update(block)
                        output.write(block)
                    if stream.read(1):
                        raise ReceiverError("upload exceeds declared byte count")
                    output.flush()
                    os.fsync(output.fileno())
                if running_hash.hexdigest() != sha:
                    raise ReceiverError("upload SHA-256 mismatch")
                checked = artifact.verify(temporary, sha, self.limits)
                if (checked["releaseId"], checked["sourceCommit"], checked["baselineId"]) != (release_id, commit, self.config["acceptedBaseline"]):
                    raise ReceiverError("artifact release/source/baseline identity mismatch")
                destination = self.releases / release_id
                if destination.exists() or destination.is_symlink():
                    result = self.verify_release(release_id, sha, commit)
                    return {"status": "already_received", **result}
                artifact.verify(temporary, sha, self.limits, unpacked)
                os.replace(temporary, unpacked / "artifact.tar")
                result = {k: v for k, v in checked.items() if k != "manifest"}
                atomic_json(unpacked / "receipt.json", result)
                # Read-only contents are operational immutability, not isolation
                # from other processes running as the same hosting account.
                for root, directories, files in os.walk(unpacked, topdown=False):
                    for name in files:
                        file = Path(root) / name
                        file.chmod(0o444 if file.is_relative_to(unpacked / "site") else 0o400)
                        with file.open("rb") as source:
                            os.fsync(source.fileno())
                    fsync_dir(root)
                os.rename(unpacked, destination)
                fsync_dir(self.releases)
                return {"status": "received", **result}
            finally:
                Path(temporary).unlink(missing_ok=True)
                if unpacked.exists():
                    shutil.rmtree(unpacked)

    def status(self, release_id=None, sha=None, commit=None):
        with self.locked():
            result = {"environment": self.config["environment"], "current": self.current(),
                      "journal": self.journal(), "activationAvailable": False,
                      "activationBlock": ACTIVATION_BLOCK}
            if release_id is not None:
                result["release"] = self.verify_release(release_id, sha, commit)
            return result

    def _point(self, release_id):
        """Transaction primitive. Never replace the real document root."""
        artifact.identifier(release_id)
        target = self.releases / release_id / "site"
        if target.resolve() != target or not target.is_dir():
            raise ReceiverError("invalid release pointer target")
        self.current()  # Refuse unexpected existing pointers/real files.
        temporary = self.root / ("_pqs_next_" + uuid.uuid4().hex)
        try:
            os.symlink(str(target), temporary)
            os.replace(temporary, self.pointer)
            fsync_dir(self.root)
        finally:
            temporary.unlink(missing_ok=True)

    def _healthy(self, stored):
        if self.health_check is None:
            raise ReceiverError("no trusted health checker installed")
        try:
            return self.health_check(stored) is True
        except Exception:
            return False

    def _restore(self, journal, success_status):
        previous = journal["previous"]
        current = self.current()
        if current not in {journal["releaseId"], previous["releaseId"]}:
            raise ReceiverError("transaction no longer owns current pointer; manual recovery required")
        self.verify_release(previous["releaseId"], previous["artifactSha256"], previous["sourceCommit"])
        if current != previous["releaseId"]:
            self._point(previous["releaseId"])
        healthy = self._healthy(previous)
        journal.update(status=success_status if healthy else "rollback_failed", restored=previous["releaseId"], completedAt=int(time.time()))
        atomic_json(self.journal_path, journal)
        return journal

    def transition(self, release_id, sha, commit, expected_current, operation="promote"):
        """Offline-testable transition; deliberately NOT wired to public CLI."""
        if operation not in {"promote", "rollback"} or self.health_check is None:
            raise ReceiverError("trusted transition operation/health checker required")
        artifact.identifier(expected_current, "expected current")
        with self.locked():
            if self.unresolved():
                raise ReceiverError("unresolved transaction; recover before retrying")
            target = self.verify_release(release_id, sha, commit)
            current = self.current()
            prior = self.journal()
            if current == release_id and prior and prior.get("status") == "succeeded" and all(prior.get(k) == v for k, v in (("releaseId", release_id), ("artifactSha256", sha), ("sourceCommit", commit), ("operation", operation))) and expected_current in {current, prior["expectedCurrent"]}:
                return prior
            if current != expected_current:
                raise ReceiverError("expected-current conflict")
            if current == release_id:
                raise ReceiverError("already current without matching transaction receipt")
            # Initial router/baseline cutover is a separate unimplemented task.
            if current is None:
                raise ReceiverError("initial cutover is not implemented")
            previous = read_json(self.releases / current / "receipt.json")
            self.verify_release(current, previous["artifactSha256"], previous["sourceCommit"])
            self.space_check()
            journal = {"transactionId": uuid.uuid4().hex, "operation": operation,
                       "releaseId": release_id, "artifactSha256": sha, "sourceCommit": commit,
                       "expectedCurrent": expected_current, "previous": previous,
                       "status": "prepared", "startedAt": int(time.time())}
            atomic_json(self.journal_path, journal)
            self._point(release_id)
            journal["status"] = "activated"
            atomic_json(self.journal_path, journal)
            if not self._healthy(target):
                return self._restore(journal, "rolled_back")
            journal.update(status="succeeded", completedAt=int(time.time()))
            atomic_json(self.journal_path, journal)
            return journal

    def recover(self):
        """Resolve uncertain outcome conservatively to previous verified release."""
        if self.health_check is None:
            raise ReceiverError("trusted recovery health checker required")
        with self.locked():
            journal = self.unresolved()
            if journal is None:
                return {"status": "no_pending_transaction", "current": self.current()}
            return self._restore(journal, "interrupted_rolled_back")


def operation_parser():
    parser = argparse.ArgumentParser(prog="pqs-receiver", allow_abbrev=False)
    verbs = parser.add_subparsers(dest="verb", required=True)
    for name in ("receive", "verify", "promote", "rollback"):
        verb = verbs.add_parser(name, allow_abbrev=False)
        verb.add_argument("--release-id", required=True)
        verb.add_argument("--sha256", required=True)
        verb.add_argument("--source-commit", required=True)
        if name == "receive":
            verb.add_argument("--bytes", type=int, required=True)
        if name in {"promote", "rollback"}:
            verb.add_argument("--expected-current", required=True)
    verbs.add_parser("status", allow_abbrev=False)
    verbs.add_parser("recover", allow_abbrev=False)
    return parser


def main():
    trusted = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    trusted.add_argument("--config", required=True)
    trusted.add_argument("--role", choices=("staging", "production"), required=True)
    trusted.add_argument("--ssh", action="store_true", help="parse fixed pqs-receiver command from SSH_ORIGINAL_COMMAND")
    args, remaining = trusted.parse_known_args()
    try:
        if args.ssh:
            if remaining:
                raise ReceiverError("SSH wrapper cannot accept extra trusted arguments")
            original = os.environ.get("SSH_ORIGINAL_COMMAND", "")
            if len(original) > 4096 or any(ord(c) < 32 or ord(c) > 126 for c in original):
                raise ReceiverError("invalid SSH command")
            remaining = shlex.split(original)
            if not remaining or remaining.pop(0) != "pqs-receiver":
                raise ReceiverError("only pqs-receiver fixed verbs accepted")
        operation = operation_parser().parse_args(remaining)
        # A hard block, before filesystem changes, regardless of config flags.
        if operation.verb in {"promote", "rollback", "recover"}:
            raise ReceiverError(ACTIVATION_BLOCK)
        config = load_config(args.config, args.role)
        engine = TransactionEngine(config)
        if operation.verb == "receive":
            def timeout(_signum, _frame):
                raise ReceiverError("receive deadline exceeded")
            signal.signal(signal.SIGALRM, timeout)
            signal.alarm(config["limits"]["receiveTimeoutSeconds"])
            try:
                result = engine.receive(sys.stdin.buffer, operation.release_id, operation.sha256, operation.source_commit, operation.bytes)
            finally:
                signal.alarm(0)
        elif operation.verb == "verify":
            result = engine.status(operation.release_id, operation.sha256, operation.source_commit)
        else:
            result = engine.status()
        print(json.dumps(result, sort_keys=True))
    except (ReceiverError, artifact.ContractError, OSError, ValueError) as error:
        print(json.dumps({"status": "rejected", "reason": str(error)}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
