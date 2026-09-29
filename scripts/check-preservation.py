#!/usr/bin/env python3
"""Check the reviewed infrastructure change did not rewrite source/public content.

This manifest is repository evidence only. Passing does not accept or reconcile
the live website. A future intentional content change needs a reviewed baseline
update, not a bypass of this check.
"""
import argparse
import hashlib
import json
from pathlib import Path


def protected_files(root):
    paths = []
    for directory in ("src", "public"):
        paths.extend(p for p in (root / directory).rglob("*") if p.is_file())
    paths.extend(root / p for p in ("astro.config.mjs", "package.json", "package-lock.json"))
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--baseline", default="tests/site/repository-baseline.json")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    baseline_path = Path(args.baseline)
    if not baseline_path.is_absolute():
        baseline_path = root / baseline_path
    baseline = json.loads(baseline_path.read_text())
    expected = baseline["protectedFileSha256"]
    actual = protected_files(root)
    changed = sorted(p for p in expected.keys() & actual.keys() if expected[p] != actual[p])
    missing = sorted(expected.keys() - actual.keys())
    added = sorted(actual.keys() - expected.keys())
    result = {"status": "failed" if changed or missing or added else "passed",
              "scope": "repository source/public preservation only; live baseline unaccepted",
              "sourceSha": baseline["sourceSha"], "protectedFiles": len(expected),
              "changed": changed, "missing": missing, "added": added}
    print(json.dumps(result, indent=2))
    return int(result["status"] == "failed")


if __name__ == "__main__":
    raise SystemExit(main())
