# Local deployment component results

Executed 2026-09-29 with Python standard-library unittest in the local Linux
workspace. Command: `python3 -m unittest discover -s tests/deploy -v`.

**22 tests passed.** All filesystem mutations used temporary fixtures. No
Namecheap/GitHub credentials, network deployment, mail, or production writes.

| Local evidence | Covered cases |
| --- | --- |
| Deterministic artifact | Identical source/metadata produces identical archive; virtual release marker; routes and full source identity. |
| Archive rejection | Traversal/absolute/encoded/dotfile/server paths, reserved namespaces, links, special types, executable bits, GNU extensions, duplicates/case aliases, trailing data, file/ancestor collision, byte/count/manifest limits. |
| Integrity and privacy-check scope | Archive digest, per-file hash/size, exact inventory, private-key marker, textual server-template markers; binary false-positive regression. |
| Source omission | Only the known empty or one-newline `cgi-bin/.gitkeep` placeholder is omitted and reported. |
| Receive safety | Interrupted/oversized input leaves no installed release; repeat receive idempotent; conflicting digest/source and unaccepted baseline rejected. |
| State safety | Lock contention, stale expected-current, installed-file tampering, escaped pointers, insufficient-space branch, config disabled/permission checks. |
| Local transitions | Success, repeat transaction, explicit rollback, preservation of real document-root inode and host-managed fixture. |
| Local health/restore | Candidate failure restores previous; both health results are checked; failed restore remains unresolved. |
| Real process interruption | A subprocess exits with `os._exit(93)` immediately after durable pointer switch. Fresh engine reads prepared journal, restores verified previous release, and clears pending state. |
| Recovery ownership | Recovery refuses to overwrite an unrelated intervening pointer. |
| Public safety block | Promote/rollback/recover always reject; crafted SSH command is parsed/rejected and does not run a shell. |

These are local components of handoff S07 and D01–D05/D08–D09, not full passing
results for those account-level acceptance tests. Disk shortage is an injected
branch fixture, not an actual full-disk or inode-exhaustion experiment. Health is
a trusted test callback, not HTTP. The public CLI remains unable to activate or
recover a release. Asset retention, host routing/authentication, actual approval,
baseline reproduction, responsive browser checks, and live end-to-end publishing
remain unverified or unimplemented.
