# Part 2 — Pipeline integration and enforcement policy

The runnable artifact is `.github/workflows/semgrepci.yml`. This document is the policy and reasoning behind it, the two required demonstration runs, and other considerations for the assessment.

## The two required runs

**Run 1 — clean commit, passes.**
- PR: https://github.com/syafiqibrahimshah/coda-sast-assessment/pull/6
- Rerun jobs: https://github.com/syafiqibrahimshah/coda-sast-assessment/actions/runs/33035161295/job/98396183834?pr=6

**Run 2 — vulnerable diff, fails.**
- PR:
- Rerun jobs:

## Enforcement policy

Reuse Semgrep Scoring System.

| Finding type | Action | Threshold |
|---|---|---|
| `ERROR` severity | **Blocks merge** | Confirmed sink + untrusted source per rule's own dataflow. |
| `WARNING` severity | **Annotates only** — PR comment | Non-blocking |
| Anything found only in the nightly/main full-repo scan | **Triaged asynchronously** — files into the backlog | Non-blocking |

## Diff scope

**PR / push: changed-files only** via `semgrep ci`, which has diff-aware capability. Scan on changed files only for speed. Full scan job will provide full coverage on a scheduled basis.

**main / nightly: full-repo scan, non-blocking.** We don't want to block devs' PRs on legacy code that they did not introduce.

## Day-one findings

- Roll out via monitor/comment mode first, not block. Set new rules/policies to non-blocking on rollout so the existing backlog surfaces on the dashboard without failing every open PR — only block for newly introduced findings going forward.
- Bulk-triage the backlog using triage statuses. Semgrep AppSec Platform findings get one of: `Open`, `Reviewing`, `To fix`, `Fixed`, `Ignored`, `Provisionally ignored`. Use bulk triage actions to mark clearly irrelevant findings `Ignored` (with a reason: `False positive`, `Acceptable risk`, `No time`, `Duplicate`) so the dashboard reflects real signal.
- Use Semgrep Multimodal's Autotriage if licensed — it automatically flags likely false positives as `Provisionally ignored`, which the docs note reduces backlogs by roughly 60% on first use, so a human only reviews the smaller remainder rather than triaging everything manually.
- Route remaining `To fix` findings to owning teams via PR/MR comments, Slack, email, or Jira ticket creation — Semgrep AppSec Platform supports pushing findings into developers' native tools instead of requiring them to check a separate dashboard.

## Developer experience

- **Where they see it:** Inline PR annotations (familiar working environment for devs). Semgrep AppSec Dashboard (single source of truth for triage, fix/no fix). No SARIF uploads to GitHub Security.
- **Who owns remediation:** The dev/team that owns the PR/file/service/app, same as any other code review finding.
- **Appeal path for a false positive:** Via Semgrep AppSec Dashboard.
- **Remediation SLA:** Follow PCI DSS remediation timeline.
  - High Risk: Within 30 days (1 month) (mandated under Requirement 6.3.3 for newly released patches).
  - Medium Risk: Within 60 to 90 days (defined by internal policy and auditor discretion).
  - Low Risk: Within 180 days (defined by internal policy).

## Secrets and dependency vulnerabilities: in scope or separate?

- **Secrets:** For this assessment, out of scope. It's a paid service in Semgrep.
- **Dependency:** In scope via `semgrep ci` (Supply Chain). It's free, so why not. In this specific context, more security is good. SCA/dependency scanning serves a different function and does not overlap SAST.

## Failure behaviour

**Fail-open (`semgrep ci`, the default):**
- If Semgrep hits an internal scanner error/crash, the CI job passes (`exit 0`) anyway.
- An anonymous crash report is sent, but the PR is allowed to merge.
- Only genuine blocking findings (not scanner errors) fail the job.

**Fail-closed (`semgrep ci --no-suppress-errors`):**
- A scanner crash/internal error also fails the job, exactly like a blocking finding would.
- The PR cannot merge until someone fixes the scanner issue or otherwise resolves it.

For PCI-scope repos, use fail-closed. The security gate is a compliance control — fail-closed forces a human to notice and intervene (fix the scanner, retry, etc.) before code with cardholder-adjacent exposure merges without a completed scan.

For non-PCI repos, occasional CI friction from scanner infra isn't worth blocking merges over, so fail-open is more practical.

## Testing scope — what I tested, what I couldn't

**Tested:**
- Both tools run hands-on against the real repo (not just documentation).
- The diff-aware pass/fail gate.
- The full-scan run job via GitHub.

**NOT tested:**
- Managed scans; could be useful for 120++ repos. See: https://docs.semgrep.dev/deployment/managed-scanning/overview

## Where AI/LLM tooling fits (optional section)

I'd use it for:
- First-pass triage, e.g.: is this reachable, is this the same root cause as another finding? Walk me through the source to sink. Reasoning is then verified by a human reviewer.
- Handling large amounts of low severity backlog findings.

I would **not** let it make the block/don't-block decision unsupervised. Human in the loop is needed to verify evidence — a traced, reproducible path from source to sink for accountability.