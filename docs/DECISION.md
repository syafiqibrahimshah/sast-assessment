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