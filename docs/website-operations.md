# PQS website operations

Status: **implementation draft, not an operational deployment system**. Production
is not authorized by this document. The existing live site is ahead of the source
repository; a full build of current source must not replace it.

## Current owner workflow

1. Describe the requested edit in Work/Codex. The agent reads current source,
   applicable `AGENTS.md`, open PRs and the accepted baseline before changing a
   feature branch. New scientific or commercial claims require evidence and Jon's
   acceptance; layout tests do not approve claims.
2. Inspect the PR and its tests. Infrastructure changes in this draft require
   Jon's explicit review. A PR is not publication approval.
3. Stop before merging until the legacy FTP workflow has been **administratively
   disabled** and verified. A feature-branch edit to its YAML does not disable
   the version on `main`. Do not rely on secrets being absent.
4. Complete the setup and acceptance gates below. The disabled workflow jobs and
   receiver activation block are deliberate; flipping configuration flags is
   insufficient to complete this implementation.

Connected GitHub branch creation has been exercised. Commit/PR results are
recorded in the implementation report. Native tools expose merge, but it has not
been invoked. Workflow disable/dispatch, protected environment configuration and
deployment review are not exposed by the current connector. The Namecheap plugin
supports domain availability, not hosting administration. No custom identity or
`approved_by` field may substitute for GitHub's authenticated reviewer.

## One-time secure setup, in order

### Freeze and recover

An authorized repository administrator disables `.github/workflows/deploy.yml`
using the GitHub Actions workflow menu. Verify its state is `disabled_manually`,
inspect queued/running jobs and any cPanel hooks, and record the result privately.
Do this **before any merge to main**, even a documentation-only merge. Do not
delete recovery credentials until the replacement recovery path works.

Use an authenticated cPanel interface to identify the real document root, host,
SSH port and enabled shell. Preserve the actual root directory. Capture a fresh
read-only snapshot including dotfiles, file modes and active routing. Keep it
outside every served directory and retain an encrypted off-host backup. Never
commit raw host backups, private configuration or secrets to this public repo.
Record inventory hashes and verify a restore in private staging. A public crawl
cannot reveal hidden files or prove host ownership and is not this snapshot.

### Reconcile the baseline

Compare every current application route, download, form, gallery asset, redirect
and visible claim with a locked source build. Port newer live material into
editable Astro source; record intentional differences for Jon's review. Keep
Media + Architecture separate from the research pages. Do not incorporate draft
PRs #4 or #7 without checking their overlap with the current live snapshot.

Maintain two inventories: the private complete hosting inventory and the
sanitized application baseline allowed in source control. Recheck live hashes
immediately before cutover to detect manual edits since capture. Acceptance binds
to the baseline's exact digest; a newer snapshot requires renewed review.

### Establish the trusted host boundary

Use an authenticated test hostname with HTTPS, server-side authentication and
noindex headers. Test unauthenticated denial for HTML, assets and alternate paths.
Do not change artifact bytes between preview and production. Keep mail/DNS
routing unchanged except an explicitly authorized staging hostname.

Install reviewed receiver code and its private configuration outside the web root.
Use distinct keys and storage for staging and production. A forced command fixes
the receiver path, config and role; those values never come from the SSH request.
Disable forwarding, PTY and user rc where supported and test denial of arbitrary
shell/SFTP/SCP. A shared cPanel Unix account does not become isolated merely
because it has two keys. Configuration/code/authorized_keys must not be writable
through the receiver protocol. Record Python compatibility, free bytes/inodes,
filesystem identity and independent recovery scheduling.

Pin the server host key obtained through an authenticated provider channel.
Never accept a changed key automatically or disable strict host-key checking.
Keep the production private key only in GitHub's protected production environment;
never give it to the coding agent or paste it into chat.

The stable router and retained fingerprinted-asset serving mechanism still need
implementation against the actual host. They must preserve `.well-known` and all
inventoried host-managed paths, prevent direct internal-path access, preserve
redirects/query strings/404 status and route application URLs even when obsolete
physical root files remain. Test same-filesystem atomic pointer replacement.
Do not substitute in-place destructive synchronization if this fails.

### Establish approval and wire promotion

Configure `production` with Jon (`MrOweItAll`) as required reviewer, explicit
`main`-only deployment eligibility and no administrator bypass. Keep deployment
Prevent self-review off if Jon starts his own runs. PR review and deployment
review are different: do not impose a PR self-approval rule that locks out the
sole maintainer. CODEOWNERS is a review signal until enforceable settings are
verified; it does not create those settings.

After host tests pass, separately review the code that connects the artifact
download to the forced-command receiver. The privileged job must use trusted
infrastructure, never execute scripts from the website artifact, and never
rebuild. Use one production concurrency group with cancellation disabled, plus
the host lock and expected-current comparison. Configure recovery independently
of the SSH client and execute the kill-after-activation test on staging.

## Intended publish runbook after setup

This section describes the target operation; these steps are not enabled yet.

1. Merge the reviewed content change only after the baseline and legacy freeze
   gates pass. A trusted post-merge main run builds once without hosting secrets.
2. Record `{release ID, full source SHA, artifact SHA-256, workflow run, baseline
   identity}`. Stage exactly that artifact. Show the authenticated preview and
   test results, including changed routes and the available recovery target.
3. Jon reviews that candidate and approves its protected GitHub deployment.
   Currently the GitHub UI approval is required; fully conversational deployment
   approval is not available. New bytes or a changed baseline require new review.
4. The production job transfers those same bytes, validates them, locks, compares
   the expected current release, journals activation, switches the pointer and
   performs bounded live identity/content/asset checks.
5. Report published only when the actual live release matches and checks pass.
   On failure, report the failed candidate and verified restored release. A timed
   out SSH connection is an unknown outcome: read status and journal before retry.

## Intended rollback and emergency recovery

Rollback is a protected operation with an exact retained target ID/digest and the
expected current ID. It uses the same lock, journal, live checks and approval
boundary as publish; it does not rebuild or modify older releases. Retain current,
previous and pinned recovery releases and ensure cached fingerprinted assets work
in both directions. No automatic pruning is implemented in this draft.

Before enabling production, document the actual private backup location and an
owner-operated restoration procedure that works without AI or GitHub. Preserve
the original root/router configuration. Test restoration from the encrypted
backup and verify critical routes, assets, forms and host-managed paths. A full
host outage cannot be fixed by an on-host recovery process; use provider recovery
and the off-host backup. Never invent a server path or delete the current site to
make room for deployment.

## Required evidence

Use the stable test IDs in [ACCEPTANCE_TESTS.md](automation/ACCEPTANCE_TESTS.md).
Local fixture results prove only those code paths; they do not prove real SSH
restrictions, authenticated previews, owner approval or safe hosting cutover.
Keep all unexecuted tests marked blocked or not run. The system is complete only
after the real request → preview → exact approval → publish → live status →
rollback sequence has been demonstrated with Jon's authorization.
