# Recommendation
Recommend **Semgrep** for the 120-repository SAST rollout.

The biggest practical win is how low-friction it is to run locally and in CI
across Python, JavaScript, Java, and Go — custom rules live right next to the
application code, so they're easy to review (though they also need an owner
to maintain them as the codebase evolves). This supports a gradual rollout:
full scans for baseline inventory, diff-aware enforcement on pull requests,
and a dashboard for triage. That simplicity is what drives faster, better
adoption across teams.

Cost and portability matter too. Semgrep is cheaper, and — unlike CodeQL,
which is tightly coupled to GitHub Advanced Security — it isn't tied to a
single CI provider, so we're not locked in if we ever move off GitHub.

The main tradeoff is weaker cross-file, semantic analysis than CodeQL offers
for dataflow that crosses service or layer boundaries. We can offset that
with targeted taint rules where needed (though these carry their own
maintenance cost), plus a recurring full scan. Human review of reachability
on every blocking finding also helps, and stays sustainable because
diff-aware scanning keeps the finding volume manageable in the first place.

In 6 months, I'd change my mind if: 

- **CodeQL ships buildless analysis for Go.** Java already got this in 2024(~90% working);
  Go's build requirement is now the main remaining gap keeping it from being
  a closer contest.

- **CodeQL decouples from GHAS licensing.** The portability argument above
  rests on CodeQL being tied to GitHub Advanced Security — if that changes,
  Semgrep's cost/portability edge mostly goes with it.

## Where AI/LLM tooling fits (optional section)

I'd use it for:
- First-pass triage, e.g.: is this reachable, is this the same root cause as another finding? Walk me through the source to sink. The output and AI reasonings are then verified by a human reviewer.
- Handling large amounts of low severity backlog findings.

I would **not** let it make the block/don't-block decision unsupervised. Human in the loop is needed to verify evidence — a traced, reproducible path from source to sink for accountability.
