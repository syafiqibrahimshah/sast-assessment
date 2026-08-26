# Recommendation
Recommend **Semgrep** for the 120-repository SAST rollout.

The decisive practical advantage is the low-friction local and CI workflow for
Python, JavaScript, Java, and Go, with custom rules that can be reviewed beside
the application. It supports a gradual policy: full scans for inventory,
diff-aware pull-request enforcement, SARIF artifacts, and optional dashboard
triage.

The most significant tradeoff is accepting less semantic, cross-file analysis
than CodeQL can provide for some dataflow questions. Reduce that risk with
targeted taint rules, a recurring full scan, representative CodeQL spot checks
for high-risk services, and human review of reachability for every blocking
finding.

This recommendation changes in six months if Semgrep misses confirmed reachable
vulnerabilities in the supported services, produces an unmanageable false-
positive rate, cannot meet the required PR latency, or its private-code and
commercial terms do not fit the 120-repository rollout. A CodeQL pilot should
replace the recommendation if its measured recall and developer workflow are
materially better at an acceptable licensing and build-maintenance cost.

Success criteria are at least 95% of repositories scanning weekly, PR median
runtime under ten minutes, 100% ownership for blocking findings within one
business day, and a reviewed false-positive rate below 15% after the first
month.

AI may suggest rule variants, remediation text, or candidate reachability paths.
It may not decide exploitability, approve a suppression, or close a PCI finding.
Those decisions require a human reviewer and source-level evidence.

## Pipeline enforcement

The merge gate has two layers:

1. `.github/workflows/semgrep.yml` runs `semgrep ci` and submits the result to
	the Semgrep project using `SEMGREP_APP_TOKEN`.
2. The Semgrep policy evaluates the submitted finding and applies the blocking
	action. The current policy is configured for `Critical` or `High` severity
	**and** `High` confidence, with the action `Block merge and comment on
	PR/MR`.

GitHub branch protection must also require the workflow check reported as
`semgrep/ci`. The platform policy creates the security decision; the required
GitHub check makes that decision enforceable at the merge boundary. The
Semgrep dashboard remains the system for centralized ownership, triage, and
history, but is not the only merge control.

The `High confidence` condition is an automated proxy for the stronger human
criterion of confirmed reachability. AppSec reviews reachability, exploitability,
false-positive appeals, suppressions, and PCI findings. Findings below the
policy threshold remain visible for asynchronous triage and do not block a PR.

## Scope and failure behavior

Pull requests use Semgrep CI's diff-aware behavior for fast feedback. Pushes to
`main` and the weekly scheduled run provide full-repository inventory. This
means an unchanged vulnerable file can remain undiscovered by a particular PR
until the full scan; the tradeoff is a short PR feedback loop and recurring
coverage of legacy code.

The PR check fails closed when the scanner errors, cannot authenticate, or
times out. A security check that reports success while unavailable is not a
meaningful gate. Scheduled inventory failures are treated as operational alerts
and must not be interpreted as a clean scan.

The scanner image is pinned to the evaluated Semgrep version and the checkout
action is pinned to an immutable commit. Before rollout, AppSec should verify
the container digest and image signature in the release process and record that
verification alongside the organization policy. The workflow has read-only
repository permissions. The Semgrep token is supplied only by GitHub Actions
secrets and must not be exposed to untrusted fork code.

Secrets scanning and dependency vulnerabilities are separate controls. Secret
scanning is source-control and credential-rotation work; dependency findings
require lockfile/SCA data and package-owner remediation. Keeping these controls
separate avoids treating a SAST pattern as evidence that secrets or vulnerable
dependencies are safe.

## Rollout and developer workflow

For the first full scan across 120 repositories, AppSec creates an inventory,
groups findings by repository and owning service, assigns blocking findings
within one business day, and opens tracked remediation work. Teams first fix
reachable Critical/High findings, then address recurring rule families. A
finding owner may appeal with source-level reachability or sanitizer evidence;
an AppSec reviewer approves or rejects the appeal. Suppressions require an
owner, reason, expiry/review date, and a link to the tracking issue.

Proposed remediation SLAs are 24 hours for ownership of a blocking finding, 7
days for Critical, 30 days for High, and 90 days for lower-severity findings.
An emergency exception requires an accountable security approver and an
explicit expiry. Developers see blocking comments on the PR and broader
inventory findings in the Semgrep dashboard. Adoption is encouraged with a
starter rule pack, local reproduction commands, office hours, and metrics that
reward reduced time-to-fix rather than raw alert counts.

## Validation plan

`tools/test_semgrep_gate.sh` creates a temporary Python file containing the
repository's `paylink.python-shell-true` pattern and a safe comparison fixture.
It expects the vulnerable scan to return non-zero and the safe scan to return
zero, then removes both files. This validates rule behavior without adding a
permanent vulnerable file to the application. The repository currently contains
known baseline findings, so a whole-repository zero-finding assertion would not
be a valid clean-commit test; PR evidence must instead demonstrate that a new
finding is blocked and disappears after the fix.

Required GitHub evidence is two real runs: an intentionally vulnerable PR whose
Semgrep policy comments and blocks the merge, followed by a fixed commit whose
required `semgrep/ci` check passes. Record both commit SHAs, run URLs, rule IDs,
and the policy result in `docs/SAST_EVAL.md`. The local harness cannot prove
Semgrep-to-GitHub policy connectivity, branch protection, fork secret behavior,
SARIF visibility, or unavailable-scanner behavior; those require GitHub and
Semgrep project access.