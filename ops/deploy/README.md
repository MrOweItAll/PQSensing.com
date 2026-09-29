# Receiver scaffold — disabled, not installed

This directory implements an artifact contract and local filesystem transaction
component. It is **not an operational Namecheap deployment system**. There are no
credentials, remote writes, installed keys, router changes, cron tasks, or live
health checks here. Public `promote`, `rollback`, and `recover` commands are
unconditionally rejected in code, including with an enabled configuration.

The block is deliberate: retained assets across promotion **and rollback**,
stable host routing, bounded live HTTP health checks, initial baseline cutover,
and account capability proof remain unfinished. Removing the block alone is not
an implementation of those requirements. No flag enables the unfinished path.

## Artifact contract

Requires Python 3.10+ and the standard library. Build once with no hosting
credentials. The pipeline wrapper is `scripts/make-release.py`; the underlying
packager is usable independently:

```sh
python3 ops/deploy/artifact.py create \
  --site dist --output /private-work/candidate.tar \
  --release-id PQS-WEB-example \
  --source-commit FULL_40_CHARACTER_LOWERCASE_COMMIT \
  --baseline-id APPROVED_BASELINE_ID \
  --request-id REQUEST_ID --workflow-run RUN_ID \
  --test-reference CHECK_RESULT_REFERENCE
python3 ops/deploy/artifact.py verify \
  --archive /private-work/candidate.tar --sha256 FULL_64_CHARACTER_SHA256
```

The archive is uncompressed USTAR. It contains `manifest.json` and regular
`site/<path>` files only. Ordering, timestamps, ownership, and modes are
deterministic. `site/release.json` is generated inside the archive, leaving
`dist/` unchanged. The archive digest is external; no self-referential digest
appears in the manifest. Both environments must consume the exact same archive
bytes. `release-manifest.schema.json` documents the fields; executable validation
in `artifact.py` additionally checks paths, inventory, markers, counts, and hashes.

The manifest binds release ID, full source SHA, baseline ID, request, workflow,
test references, routes, and every file's SHA-256 and size. These are identity
and integrity checks, **not proof that a claimed source SHA was actually built or
that a test reference passed**; the trusted workflow must establish that.

Only reviewed static extensions are allowed. Paths are canonical ASCII with no
dotfiles, parent traversal, absolute names, URL-encoded ambiguity, case aliases,
or file/ancestor collisions. Host/internal namespaces `cgi-bin` and `_pqs_*`
are rejected. Archives cannot contain links, devices, executable mode bits,
PAX/GNU extension headers, duplicates, or hidden nonzero trailing data.
Server-code extensions are denied even in names such as `code.php.html`.

The sole source omission is the existing repository placeholder
`cgi-bin/.gitkeep`, **only** when its bytes are empty or exactly one newline.
The packager records this in `excludedPaths` in its JSON receipt. It is not
application content or a deployable form handler. Other dotfiles, files in
`cgi-bin`, and changed placeholder content fail the build. Manifest verification
does not permit this placeholder inside an artifact.

Textual static files are screened for PHP/ASP template markers. All files are
screened for PEM/OpenSSH private-key headers. These narrow checks do not detect
every API key, password, private document, or customer datum. Baseline inventory
and human content/privacy review remain required. Binary media is not rejected
for coincidental PHP/ASP byte sequences.

## Trusted host receiver interface

`host-config.example.json` is disabled and contains unresolved paths. A reviewed
host installation would keep configuration and receiver code outside **all**
web roots and outside artifact-writable paths. Configuration must be owned by
the receiver user and not group/world writable. Deployment base is private,
already exists, and is disjoint from the real document root. No path, URL, shell
command, role, or approval identity is taken from artifact metadata.

The host installer, key restrictions, and staging/production isolation are not
implemented. A future forced-command entry must fix `--config`, `--role`, and
`--ssh` on the host; the client's command cannot supply these trusted arguments.
`SSH_ORIGINAL_COMMAND` is parsed as a fixed grammar, never evaluated by a shell.
The only currently usable public verbs are:

```text
pqs-receiver receive --release-id ID --sha256 DIGEST --source-commit COMMIT --bytes COUNT
pqs-receiver verify --release-id ID --sha256 DIGEST --source-commit COMMIT
pqs-receiver status
```

`receive` reads the bounded archive from standard input under a deadline. It
checks configuration gates, disk/inodes, lock, byte count, digest, manifest,
release/source/baseline identity, and all contents before publishing a private
release directory. Interrupted or rejected input never changes a public pointer.
Same ID and identical digest/source is idempotent after full verification;
conflicting content under an existing ID is rejected. Files are synced and made
read-only. This is operational immutability, not a security boundary against
another process running as the same cPanel account user.

Disk checks reserve the maximum configured extraction size plus the archive and
free-space/inode margin. The receiver does not prune releases. Crash remnants in
`incoming/` need an administrator's reviewed cleanup; a later receive does not
reuse or trust them. Configurable limits cannot exceed the reviewed parser's
256 MiB archive / 200 MiB extracted / 10,000 file ceilings.

## Offline transaction component

`TransactionEngine.transition()` and `.recover()` are directly exercised by
tests, but **are not public CLI capabilities**. They require a trusted health
callback, which production has not yet implemented. The local fixture begins
with an already installed, verified baseline pointer; there is no initial
cutover function.

The component uses `flock`, immutable release identities, expected-current
comparison, a durable journal before pointer change, and same-directory atomic
symlink replacement. It leaves the real document-root directory and host-managed
files in place. Successful retries use the recorded transaction. Bad health
restores and verifies the previous release; failed restoration remains unresolved.
Recovery of a prepared/activated transaction conservatively restores the verified
previous release. It refuses to overwrite a pointer that no longer belongs to
that transaction. Pending transactions block further receive/transition work.

This demonstrates filesystem behavior on the local Linux workspace, not cPanel
HTTP routing, whole-host power-loss durability, same-account access isolation,
or availability during hosting outages. `status` reports on-disk state and
identifies the activation block; it is not a live HTTP success claim.

## Required before any operational enablement

1. Accept the fresh private production snapshot, source reconciliation, baseline,
   backup restoration, and preserved host-managed path inventory.
2. Implement and review stable routing and immutable retained-asset access in both
   promotion directions. Simply retaining old release directories is insufficient
   for cached HTML when the current pointer changes.
3. Implement bounded trusted live health checks, receipt/live-marker comparison,
   initial cutover, recovery scheduling, and emergency restoration.
4. Install and test separate forced-command credentials, permissions, server host
   key pinning, staging authentication/noindex, and environment approval identity.
5. Run the remaining handoff acceptance tests on the actual account; only then
   submit a separately reviewed change exposing activation.

## Local verification

```sh
python3 -m unittest discover -s tests/deploy -p 'test_*.py' -v
```

See `tests/deploy/RESULTS.md` for executed scope. No test authorizes production.
