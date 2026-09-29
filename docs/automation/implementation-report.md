# PQS automation implementation report

Date: 2026-09-29. Status: **draft implementation; not ready for cutover**.

## What is established

The current main commit inspected is
`44d5cf4d9934ca86f1ef650056cf5164e1888917`. A feature branch,
`automation/reviewable-release-pipeline`, was created through the connected
GitHub integration. Main and production have not been modified. Existing draft
PRs #4 and #7 remain independent and unmerged.

The repository still contains a push-to-main FTP workflow. Its branch version is
made inert by this proposal, but the actual workflow must be disabled through
GitHub administration before this PR is merged. That administrative capability
is not exposed by the current connection; no disabled state is claimed.
The current branch metadata reports `main` as unprotected. This proposal does
not create branch rules or configure required deployment reviewers.

The September 18 `MediaArchitecture_Deployment_Guide.txt` was read from its current
saved file. It records a one-file production-derived patch, not a reconciled
whole-site source tree. A fresh public inspection also shows the homepage differs
from the repository. Public observations are not an authenticated hosting backup.
See [reconciliation](../reconciliation.md).

## Deliverables in this proposal

- Project authoring rules and infrastructure ownership guidance.
- Unprivileged CI for the existing locked dependency install, tests/build,
  source preservation, browser checks and release validation.
- A deterministic static release archive and digest receipt, with production
  eligibility explicitly false.
- A bounded archive verifier, restricted receiver protocol and locally tested
  activation/recovery engine. Real activation remains blocked pending the actual
  stable router, asset retention and host tests.
- Inert production/rollback workflow boundaries, host capability report,
  reconciliation report, acceptance inventory and secure setup/publish/recovery
  runbook. These documents do not configure GitHub environments or hosting.

No page copy, prices, patents, scientific claims, downloads or gallery content
are changed. No framework or lockfile upgrade is included.

## Execution evidence

Commands run from the unchanged baseline:

| Check | Result |
|---|---|
| Runtime | Node 24.19.0; npm 11.9.0; Python 3.12.14 |
| `npm ci` | Passed from existing `package-lock.json` |
| `npm test` | 14 tests passed |
| `npm run build` | Passed; 256 internal links across 10 HTML files |
| Source/public/config preservation | 285 file hashes retained; no approved content edits |
| Gallery inventory | 17 projects; 99 full-size images in repository baseline |
| Preservation negative tests | 5 passed: changed/missing/added content rejected |
| Local HTTP/download checks | 23 assertions passed; browser execution still blocked |
| Browser installation/execution | Chromium download failed; no viewport or screenshot pass claimed |
| Release-wrapper fixture checks | 7 passed: exact HEAD/clean-tree checks, deterministic bytes, ineligible receipt, source/dirty-tree rejection and no overwrite |
| Workflow structure | 4 YAML workflows checked; 5 action pins resolved and metadata inspected |
| Full current build artifact verification | Passed locally: 331 files in a 76,421,120-byte tar |
| `python3 -m unittest discover -s tests/deploy -v` | 22 passed: archive rejection, interrupted uploads, conflicts, rollback and real process-exit recovery |

The one excluded build path is `cgi-bin/.gitkeep`, an empty repository placeholder
(zero bytes or one newline); actual host-managed CGI content is not packaged.
Unknown files in that namespace are rejected. A generated `release.json` marker
is included in the immutable artifact. No file in `dist` is edited by packaging.

An independent review exercised identical receive retries, failed-health recovery,
interrupted pointer activation and unconditional public activation rejection. The
committed receiver tests provide the reproducible fixture coverage. Neither that
review nor the results above establishes live
site parity, protected staging, SSH confinement or production approval.

## Acceptance status by supplied test ID

| IDs | Status and scope |
|---|---|
| B01 | Blocked: administrative legacy freeze not available; no main mutation performed. |
| B02–B05 | Blocked: no fresh authenticated host snapshot, encrypted restore proof or owner-accepted reconciled baseline. |
| C01 | Workflow design has read-only permissions and no hosting secrets; a real untrusted/fork execution remains unverified. |
| C02 | Existing locked install/tests/build passed locally; hosted CI result reported separately. |
| C03–C04 | Local artifact identity checks only; identical bytes through staging/production and renewed real approval not demonstrated. |
| C05 | Repository build links and content hashes checked; live/accepted-baseline and browser coverage remain separate gates. |
| C06–C07 | Actual browser/form validation status is recorded in reconciliation report; no messages submitted. |
| C08 | No claim changes. Preservation is verified, not scientific acceptance of old content. |
| S01–S05 | Blocked: no authenticated staging or actual host/SSH/key/router tests. |
| S06–S07 | Local artifact path/type/hash/secret-pattern tests only; not proof all private content is automatically detectable. |
| D01–D05 | Local receiver fixtures only; real SSH/disk/concurrency behavior must be exercised on staging. |
| D06–D07 | Blocked: host router, cached assets and host-managed paths not implemented/verified. |
| D08–D09 | Local transaction engine fault tests only; no independent host recovery scheduler installed. |
| D10 | Blocked: real retained-asset serving mechanism pending. Public activation is hard-disabled. |
| D11–D12 | Production paths disabled; real GitHub approval eligibility, fake-identity denial and plan/rule transitions untested. |
| O01 | Blocked: full conversational publish/status/rollback sequence not demonstrated. |
| O02 | Limitation documented: authenticated GitHub owner approval is required when enabled. |
| O03–O04 | Blocked: private emergency restoration and retirement of old publishing require host/admin setup. |

## Exact candidate and preview status

There is **no production-eligible release and no authenticated preview URL**.
A local verification bundle may be generated from the final branch SHA; its
receipt is explicitly marked `BLOCKED_SETUP_INCOMPLETE`. Its digest demonstrates
the archive format, not permission to publish stale repository content.

The PR identifies the exact implementation commit. No hosting keys, provider
passwords, API tokens, raw backups or new private user material are included.
Production credentials have not been installed or inspected.

## Remaining work needed for completion

Follow [website-operations.md](../website-operations.md) in order: administratively
freeze FTP; obtain a private snapshot and restore proof; reconcile and accept the
baseline; implement and test stable host routing and cached-asset retention;
install separate restricted keys and verified host identity; establish protected
GitHub environments; connect reviewed artifact transfer/promotion code; run
staging security/fault tests; review the real preview; perform an owner-authorized
cutover and rollback demonstration.

The implementation agent must not approve its own infrastructure work. Host and
GitHub setup require secure account interfaces; do not paste credentials into
chat. The missing account access and implementation gates are concrete blockers,
not tests that can be waived by marking the configuration enabled.
