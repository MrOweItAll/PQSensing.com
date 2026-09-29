# Acceptance tests — PQS website automation

Status: proposed tests, not results. Work/Codex must record execution evidence and dates.

| ID | Test | Passing result |
|---|---|---|
| B01 | Freeze legacy deployment before a main change. | No old FTP job or cPanel hook can publish unexpectedly; disabling is recorded. |
| B02 | Fresh private hosting snapshot and restore check. | Hidden files and active server configuration are captured; backup cannot be downloaded publicly; off-host copy is recoverable. |
| B03 | Source/live reconciliation. | Every public route and relevant file is accounted for; all intentional differences have owner acceptance. |
| B04 | Concurrent manual edit after baseline capture. | Changed live hash blocks cutover; newer content is not overwritten. |
| B05 | Baseline-only first candidate. | Approved copy, routes, gallery, downloads, forms, navigation, and metadata are preserved. |
| C01 | PR from an untrusted branch/fork. | Tests can run without hosting keys; no credentialed job checks out or executes that code. |
| C02 | Locked build. | Existing tests and build pass from the committed lockfile; runtime/tool identities are recorded. |
| C03 | Artifact identity. | Staging and production consume identical artifact SHA-256 bytes; no production rebuild. |
| C04 | Changed candidate after preview. | Earlier approval is not reused; a fresh digest and review are required. |
| C05 | Site regression. | Critical routes, actual baseline inventory, internal links, downloads, images, console checks, and menus pass. |
| C06 | Viewports. | 320, 375, 390, 768, 1024, and 1440 px checks pass with no unintended overflow. |
| C07 | Contact form. | Correct target, fields, prefills, and validation are tested without unsolicited production submissions. |
| C08 | Scientific/commercial claim change. | New claim has evidence and explicit owner acceptance; no unsupported validation or patent language appears. |
| S01 | Staging privacy. | Unauthenticated request is denied; authenticated preview works; noindex is applied without modifying artifact bytes. |
| S02 | Staging separation. | Staging key cannot alter production pointer, receiver, .ssh, or host-managed files. |
| S03 | Host capability test. | Same-account symlink, stable router, ownership, atomic replacement, query strings, redirects, and 404 behavior are demonstrated. |
| S04 | Host-key mismatch. | SSH stops; workflow does not disable verification to continue. |
| S05 | Forced-command key. | Arbitrary shell, forwarding, TTY, unrestricted SFTP/SCP, and path escape fail. |
| S06 | Secret exposure scan. | Private keys, passwords, .env, raw backups, private data, and deployment credentials are absent from artifacts and logs. |
| S07 | Malformed archive. | Absolute/parent paths, links, devices, executable server files, unapproved .htaccess, duplicates, and oversized contents are rejected. |
| D01 | Interrupted upload. | Existing website is unchanged; incomplete release is never eligible for serving. |
| D02 | Incorrect archive or manifest hash. | Verification fails before activation. |
| D03 | Disk or inode shortage. | Deployment stops before activation; current/previous recovery data remains intact. |
| D04 | Concurrent/stale publication. | Lock and expected-current check prevent an older or simultaneous run from overwriting a newer release. |
| D05 | Retried receive/promote. | Same ID/hash behaves idempotently; same ID/different hash is rejected. |
| D06 | Activation under repeated requests. | No missing-pointer interval; stable URL routing works; cached old pages can still load their assets. |
| D07 | Host-managed paths. | Certificate validation, redirects, error codes, and any inventoried form handlers remain functional. |
| D08 | Known-bad candidate health check. | The previous release is restored; restoration is verified and reported as rollback, not successful publishing. |
| D09 | Kill connection/process after activation. | Journal records pending state; tested recovery resolves it; client reads status before retrying. |
| D10 | Old cached HTML after promotion and rollback. | Referenced fingerprinted assets remain accessible in both directions. |
| D11 | Unauthorized publish or fake approval identity. | Release fails; only an eligible authenticated reviewer can approve the correct environment/run. |
| D12 | Private/plan or reviewer configuration change. | Setup detects unavailable gates or solo-owner self-review deadlock and does not silently remove protections. |
| O01 | Chat end-to-end. | An authorized test creates a change, returns candidate/preview, publishes exact candidate, reports live evidence, and rolls back. |
| O02 | Missing native approval capability. | System clearly reports the GitHub approval step; it never claims fully conversational publication is enabled. |
| O03 | Emergency recovery. | Owner can restore a known release/router without AI access; credentials and backup location are documented privately. |
| O04 | Retire old publishing. | Obsolete FTP workflow is removed/disabled; old credentials are retired or rotated after recovery is verified. |

Attach logs or receipts with secrets redacted. Use stable test identifiers in the final implementation report. Failure of a publication-safety test blocks production enablement.
