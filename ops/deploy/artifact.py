#!/usr/bin/env python3
"""Deterministic static-site artifact contract. No third-party dependencies."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import tarfile
import tempfile

SCHEMA_VERSION = 1
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
ALLOWED_EXTENSIONS = {
    ".html", ".css", ".js", ".mjs", ".json", ".txt", ".xml", ".svg",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".ico", ".pdf",
    ".woff", ".woff2", ".ttf", ".otf", ".eot", ".mp3", ".mp4", ".webm",
    ".ogg", ".wav", ".webmanifest", ".m4a", ".m4v", ".pptx",
}
TEXT_EXTENSIONS = {".html", ".css", ".js", ".mjs", ".json", ".txt", ".xml", ".svg", ".webmanifest"}
SERVER_EXTENSIONS = {"php", "php3", "php4", "php5", "php7", "php8", "phtml", "pht", "phar", "cgi", "pl", "py", "rb", "sh", "shtml", "shtm", "asp", "aspx", "jsp", "htaccess", "htpasswd"}
DEFAULT_LIMITS = {"maxArchiveBytes": 256 * 1024 * 1024,
                  "maxExtractedBytes": 200 * 1024 * 1024,
                  "maxFileCount": 10000,
                  "maxManifestBytes": 4 * 1024 * 1024}


class ContractError(ValueError):
    pass


def canonical_json(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ContractError("duplicate JSON key")
            result[key] = value
        return result
    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ContractError("nonfinite JSON")))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ContractError("invalid JSON") from error


def identifier(value, label="release ID"):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ContractError("invalid " + label)
    return value


def digest(value):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise ContractError("invalid SHA-256")
    return value


def source_commit(value):
    if not isinstance(value, str) or not COMMIT.fullmatch(value):
        raise ContractError("source commit must be full lowercase 40-character SHA")
    return value


def safe_path(value):
    if not isinstance(value, str) or not value or len(value) > 220:
        raise ContractError("invalid path length")
    if value.startswith("/") or "\\" in value or any(ord(c) < 32 or ord(c) > 126 for c in value):
        raise ContractError("unsafe path")
    if any(c in value for c in ":%?#<>|\"*;"):
        raise ContractError("ambiguous path")
    top = value.split("/", 1)[0].lower()
    if top == "cgi-bin" or top.startswith("_pqs_"):
        raise ContractError("reserved host/internal namespace")
    for part in value.split("/"):
        if not part or part.startswith(".") or part.endswith((".", " ")) or len(part) > 100:
            raise ContractError("dotfile, traversal, or ambiguous path")
        if any(ext.lower() in SERVER_EXTENSIONS for ext in part.split(".")[1:]):
            raise ContractError("server-executable/configuration filename")
    if str(PurePosixPath(value)) != value:
        raise ContractError("noncanonical path")
    if PurePosixPath(value).suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ContractError("unapproved static file type: " + value)
    return value


def validate_payload(path, data):
    safe_path(path)
    if PurePosixPath(path).suffix.lower() in TEXT_EXTENSIONS:
        lower = data.lower()
        if b"<?php" in lower or b"<?=" in lower or b"<%" in lower:
            raise ContractError("server template content")
    if re.search(rb"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----", data):
        raise ContractError("private-key material")


def file_sha(path):
    result = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def route_inventory(paths):
    return sorted({"/" if p == "index.html" else "/" + p for p in paths if p.endswith(".html")})


def validate_manifest(manifest, limits):
    expected = {"schemaVersion", "releaseId", "sourceCommit", "baselineId", "requestId", "workflowRun", "tests", "files", "routes"}
    if not isinstance(manifest, dict) or set(manifest) != expected or type(manifest["schemaVersion"]) is not int or manifest["schemaVersion"] != 1:
        raise ContractError("invalid manifest fields/version")
    identifier(manifest["releaseId"])
    source_commit(manifest["sourceCommit"])
    identifier(manifest["baselineId"], "baseline ID")
    for key in ("requestId", "workflowRun"):
        value = manifest[key]
        if not isinstance(value, str) or not value or len(value) > 200 or any(ord(c) < 32 or ord(c) > 126 for c in value):
            raise ContractError("invalid manifest " + key)
    if not isinstance(manifest["tests"], list) or len(manifest["tests"]) > 100 or any(not isinstance(v, str) or not v or len(v) > 300 or any(ord(c) < 32 or ord(c) > 126 for c in v) for v in manifest["tests"]):
        raise ContractError("invalid test references")
    files = manifest["files"]
    if not isinstance(files, list) or not 1 <= len(files) <= limits["maxFileCount"]:
        raise ContractError("invalid file count")
    seen, folded, total = set(), set(), 0
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"path", "size", "sha256"}:
            raise ContractError("invalid manifest file entry")
        name = safe_path(entry["path"])
        if name in seen or name.casefold() in folded:
            raise ContractError("duplicate/case-ambiguous manifest path")
        seen.add(name)
        folded.add(name.casefold())
        if type(entry["size"]) is not int or not 0 <= entry["size"] <= limits["maxExtractedBytes"]:
            raise ContractError("invalid file size")
        total += entry["size"]
        digest(entry["sha256"])
    if total > limits["maxExtractedBytes"]:
        raise ContractError("extracted size limit exceeded")
    for name in seen:
        if any(str(parent).casefold() in folded for parent in PurePosixPath(name).parents if str(parent) != "."):
            raise ContractError("file/directory path collision")
    if "index.html" not in seen or "release.json" not in seen:
        raise ContractError("index.html and release.json are required")
    if manifest["routes"] != route_inventory(seen):
        raise ContractError("route inventory mismatch")
    return manifest


def receipt(manifest, archive_sha, archive_bytes):
    result = {k: manifest[k] for k in ("releaseId", "sourceCommit", "baselineId", "requestId", "workflowRun", "routes")}
    result.update(artifactSha256=archive_sha, artifactBytes=archive_bytes, fileCount=len(manifest["files"]))
    return result


def create(site, output, release_id, source_sha, baseline_id, request_id, workflow_run, tests=()):
    site, output = Path(site), Path(output)
    identifier(release_id)
    source_commit(source_sha)
    identifier(baseline_id, "baseline ID")
    if site.is_symlink() or not site.is_dir():
        raise ContractError("site must be a real directory")
    payloads, total, excluded = {}, 0, []
    for root, directories, files in os.walk(site, followlinks=False):
        for item in directories + files:
            item_path = Path(root) / item
            if item_path.is_symlink():
                raise ContractError("source symlinks forbidden")
        for item in files:
            path = Path(root) / item
            name = path.relative_to(site).as_posix()
            if name == "cgi-bin/.gitkeep" and path.is_file() and path.stat().st_size <= 1 and path.read_bytes() in (b"", b"\n"):
                excluded.append(name)  # Repository placeholder; never an executable host directory.
                continue
            if name == "release.json":
                raise ContractError("release.json is generated by the packager")
            if not path.is_file():
                raise ContractError("nonregular source file")
            total += path.stat().st_size
            if total > DEFAULT_LIMITS["maxExtractedBytes"] or len(payloads) >= DEFAULT_LIMITS["maxFileCount"] - 1:
                raise ContractError("source byte/count limit exceeded")
            data = path.read_bytes()
            validate_payload(name, data)
            payloads[name] = data
    payloads["release.json"] = canonical_json({"releaseId": release_id, "sourceCommit": source_sha, "baselineId": baseline_id})
    manifest = {"schemaVersion": 1, "releaseId": release_id, "sourceCommit": source_sha,
                "baselineId": baseline_id, "requestId": request_id, "workflowRun": workflow_run,
                "tests": list(tests), "routes": route_inventory(payloads),
                "files": [{"path": p, "size": len(payloads[p]), "sha256": hashlib.sha256(payloads[p]).hexdigest()} for p in sorted(payloads)]}
    validate_manifest(manifest, DEFAULT_LIMITS)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() or output.is_symlink():
        raise ContractError("output already exists")
    descriptor, temporary = tempfile.mkstemp(prefix=".pqs-artifact-", dir=output.parent)
    os.close(descriptor)
    try:
        with tarfile.open(temporary, "w", format=tarfile.USTAR_FORMAT) as archive:
            entries = {"manifest.json": canonical_json(manifest), **{"site/" + p: b for p, b in payloads.items()}}
            for name in sorted(entries):
                data = entries[name]
                member = tarfile.TarInfo(name)
                member.size = len(data)
                member.mode = 0o644
                member.uid = member.gid = member.mtime = 0
                member.uname = member.gname = ""
                archive.addfile(member, io.BytesIO(data))
        verified = verify(temporary, file_sha(temporary))
        os.link(temporary, output)  # Exclusive publication; never overwrite another candidate.
        return {**verified, "excludedPaths": excluded}
    finally:
        Path(temporary).unlink(missing_ok=True)


def verify(archive_path, expected_sha, limits=None, destination=None):
    """Fully validate before extraction; destination must be a new private directory."""
    limits = dict(DEFAULT_LIMITS, **(limits or {}))
    digest(expected_sha)
    archive_path = Path(archive_path)
    if archive_path.is_symlink() or not archive_path.is_file():
        raise ContractError("archive must be a regular file")
    size = archive_path.stat().st_size
    if not 1024 <= size <= limits["maxArchiveBytes"] or size % 512:
        raise ContractError("archive byte limit or framing invalid")
    if file_sha(archive_path) != expected_sha:
        raise ContractError("archive SHA-256 mismatch")
    payloads, folded, total, end = {}, set(), 0, 0
    try:
        with tarfile.open(archive_path, "r:") as archive:
            for member in archive:
                name = member.name
                # Reject hidden PAX/GNU extension headers as well as public links/types.
                if member.offset != end or member.offset_data != member.offset + 512 or member.type != tarfile.REGTYPE or member.pax_headers or member.linkname or member.mode & 0o7111:
                    raise ContractError("archive link, special file, extension header, or executable mode")
                if name != "manifest.json":
                    if not name.startswith("site/"):
                        raise ContractError("unexpected archive root")
                    safe_path(name[5:])
                if name in payloads or name.casefold() in folded:
                    raise ContractError("duplicate/case-ambiguous archive path")
                if len(payloads) >= limits["maxFileCount"] + 1 or member.size < 0:
                    raise ContractError("archive count/size invalid")
                allowed = limits["maxManifestBytes"] if name == "manifest.json" else limits["maxExtractedBytes"]
                if member.size > allowed:
                    raise ContractError("member too large")
                total += member.size
                if total > limits["maxExtractedBytes"] + limits["maxManifestBytes"]:
                    raise ContractError("archive extracted-byte limit exceeded")
                stream = archive.extractfile(member)
                data = stream.read(member.size + 1)
                if len(data) != member.size:
                    raise ContractError("truncated member")
                if name != "manifest.json":
                    validate_payload(name[5:], data)
                payloads[name] = data
                folded.add(name.casefold())
                end = member.offset_data + ((member.size + 511) // 512) * 512
        with archive_path.open("rb") as stream:
            stream.seek(end)
            trailer = stream.read()
            if len(trailer) < 1024 or any(trailer):
                raise ContractError("missing zero trailer or hidden trailing data")
    except (tarfile.TarError, OSError, EOFError) as error:
        raise ContractError("invalid archive") from error
    if "manifest.json" not in payloads:
        raise ContractError("missing manifest")
    manifest = validate_manifest(strict_json(payloads["manifest.json"]), limits)
    expected_names = {"manifest.json"} | {"site/" + f["path"] for f in manifest["files"]}
    if set(payloads) != expected_names:
        raise ContractError("manifest/archive inventory mismatch")
    for entry in manifest["files"]:
        data = payloads["site/" + entry["path"]]
        if len(data) != entry["size"] or hashlib.sha256(data).hexdigest() != entry["sha256"]:
            raise ContractError("file hash/size mismatch")
    marker = strict_json(payloads["site/release.json"])
    if marker != {k: manifest[k] for k in ("releaseId", "sourceCommit", "baselineId")}:
        raise ContractError("release marker identity mismatch")
    if destination is not None:
        destination = Path(destination)
        destination.mkdir(mode=0o700, parents=False, exist_ok=False)
        for name, data in payloads.items():
            target = destination / name
            target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(data)
            target.chmod(0o644 if name.startswith("site/") else 0o600)
        # Host must independently demonstrate its web server can traverse this tree.
    return {**receipt(manifest, expected_sha, size), "manifest": manifest}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    verbs = parser.add_subparsers(dest="verb", required=True)
    pack = verbs.add_parser("create")
    for name in ("site", "output", "release-id", "source-commit", "baseline-id", "request-id", "workflow-run"):
        pack.add_argument("--" + name, required=True)
    pack.add_argument("--test-reference", action="append", default=[])
    check = verbs.add_parser("verify")
    check.add_argument("--archive", required=True)
    check.add_argument("--sha256", required=True)
    args = parser.parse_args()
    try:
        if args.verb == "create":
            result = create(args.site, args.output, args.release_id, args.source_commit, args.baseline_id, args.request_id, args.workflow_run, args.test_reference)
        else:
            result = verify(args.archive, args.sha256)
        print(json.dumps(result, sort_keys=True))
    except (ContractError, OSError) as error:
        parser.exit(1, "artifact rejected: " + str(error) + "\n")


if __name__ == "__main__":
    main()
