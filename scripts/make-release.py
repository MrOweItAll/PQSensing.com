#!/usr/bin/env python3
"""Assemble one deterministic, non-deployable candidate from an existing build.

This wrapper never invokes npm, accesses a host, or modifies dist. The reviewed
artifact implementation supplies path/secret checks and manifest validation.
The archive digest identifies the tar bytes, not GitHub's transport ZIP.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path("dist"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--baseline-id", required=True)
    parser.add_argument("--request-id", required=True)
    parser.add_argument("--workflow-run", required=True)
    parser.add_argument("--test-reference", action="append", default=[])
    args = parser.parse_args()
    checked_out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True,
                                 capture_output=True, text=True).stdout.strip()
    if args.source_commit != checked_out:
        parser.error("source commit must equal the complete checked-out git HEAD")
    status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                            cwd=ROOT, check=True, capture_output=True, text=True).stdout
    if status:
        parser.error("commit or remove source changes before packaging; worktree must be clean")
    destination = args.output_dir.absolute()
    if destination.exists() or destination.is_symlink():
        parser.error("output directory must not exist; candidates are immutable")
    destination.parent.mkdir(parents=True, exist_ok=True)
    site = args.site.resolve(strict=True)
    if site == destination or site in destination.parents:
        parser.error("output directory must be outside the site directory")
    artifact_tool = ROOT / "ops/deploy/artifact.py"
    with tempfile.TemporaryDirectory(prefix=".candidate-", dir=destination.parent) as temp:
        temporary = Path(temp)
        archive = temporary / "bundle.tar"
        command = [sys.executable, str(artifact_tool), "create", "--site", str(site),
                   "--output", str(archive), "--release-id", args.release_id,
                   "--source-commit", args.source_commit, "--baseline-id", args.baseline_id,
                   "--request-id", args.request_id, "--workflow-run", args.workflow_run]
        for reference in args.test_reference:
            command.extend(["--test-reference", reference])
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        receipt = json.loads(result.stdout)
        expected = {"releaseId": args.release_id, "sourceCommit": args.source_commit,
                    "baselineId": args.baseline_id, "requestId": args.request_id,
                    "workflowRun": args.workflow_run}
        if any(receipt.get(key) != value for key, value in expected.items()):
            raise ValueError("artifact tool returned inconsistent candidate identity")
        with archive.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if receipt["artifactSha256"] != digest or receipt["artifactBytes"] != archive.stat().st_size:
            raise ValueError("artifact tool returned an inconsistent digest or size")
        subprocess.run([sys.executable, str(artifact_tool), "verify", "--archive", str(archive),
                        "--sha256", digest], check=True, capture_output=True, text=True)
        receipt.pop("manifest", None)  # Full per-file manifest remains inside the tar.
        receipt.update({"archiveFile": "bundle.tar", "publicationStatus": "BLOCKED_SETUP_INCOMPLETE",
                        "promotionEligible": False})
        # The status above is deliberate: this version packages and tests only.
        # Host acceptance and authenticated approval are not asserted by a model.
        (temporary / "candidate.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        (temporary / "bundle.tar.sha256").write_text(f"{digest}  bundle.tar\n")
        # mkdir reserves the destination exclusively even with concurrent callers.
        # Link the receipt last: interruption leaves an incomplete, ineligible
        # directory, never a successful receipt or an overwritten old candidate.
        destination.mkdir()
        for name in ("bundle.tar", "bundle.tar.sha256", "candidate.json"):
            os.link(temporary / name, destination / name)
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(run())
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            print(error.stderr.strip(), file=sys.stderr)
        print(f"Candidate creation failed: {error}", file=sys.stderr)
        sys.exit(1)
