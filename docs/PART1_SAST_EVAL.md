# SAST Evaluation

## Local environment and Reproducibility

### Tools Version
```markdown
% semgrep --version
1.174.0
```

```markdown
% codeql --version 
CodeQL command-line toolchain release 2.26.3.
Copyright (C) 2019-2026 GitHub, Inc.
..SNIP..
```

### Local Run
##### `--config auto`. Output json.

```markdown
%  semgrep scan --time --config auto --error --json-output=./artifacts/semgrep-auto.json .


..SNIP..
  ============================[ summary ]============================
  Total time: 40.3134s Config time: 3.5687s Core time: 36.7354s
                    
  Semgrep-core time:
  Total CPU time: 46.3111s  File parse time: 0.2855s  Rule parse time: 0.9786s  Match time: 2.2257s
  Slowest 5/6679 files
  ...l-java/results/run-info-20260826.033313.473.yml (478KB): 0.401s (0.073s to parse)
  ...eql-go/results/run-info-20260826.033418.747.yml (166KB): 0.151s (0.032s to parse)
  ...script/results/run-info-20260826.033238.771.yml (297KB): 0.169s (0.029s to parse)
  ...python/results/run-info-20260826.033157.332.yml (138KB): 0.065s (0.018s to parse)
  services/ledger/client.go                          (  1KB): 0.020s (0.008s to parse)
  Slowest 5 rules to match
  ...t.allow-privilege-escalation-no-securitycontext:         0.095s
  ...sqli-uri-params.django-aiomysql-sqli-uri-params:         0.054s
  ...lambda-websocket-ssrf.aws-lambda-websocket-ssrf:         0.053s
  ...n-ssrf-uri-params.fastapi-gdown-ssrf-uri-params:         0.051s
  ...pulation.serverless-hypercorn-path-manipulation:         0.048s
  Analyzed: 13281 generic files ( 46MB in 48.213 seconds)
            6 go files (  7KB in 0.061 seconds)          
            9 java files ( 12KB in 0.109 seconds)        
            12 js files ( 12KB in 0.219 seconds)         
            27 json files ( 17KB in 0.046 seconds)       
            27 python files ( 28KB in 1.709 seconds)     
            2 xml files (  1KB in 0.002 seconds)         
            33 yaml files (  3MB in 1.003 seconds)       
  Errors:   8 files with errors, see output before the results for details or run with --strict
            ParseError (1 files)                                                               
            MatchingError (2 files)                                                            

                
                
┌──────────────┐
│ Scan Summary │
└──────────────┘
✅ Scan completed successfully.
 • Findings: 34 (34 blocking)
 • Rules run: 2002
 • Targets scanned: 6679
 • Parsed lines: ~100.0%
 • Scan skipped: 
   ◦ Files larger than  files 1.0 MB: 20
   ◦ Files matching .semgrepignore patterns: 2
 • Scan was limited to files tracked by git
 • For a detailed list of skipped files and lines, run semgrep with the --verbose flag
Ran 2002 rules on 6679 files: 34 findings.
```
##### `--config p/security-audit`. Output sarif.
```markdown
% semgrep scan --metrics off --time --config p/security-audit --sarif-output=artifacts/semgrep-security-audit.sarif .

..SNIP..
  ============================[ summary ]============================
  Total time: 4.0853s Config time: 0.5193s Core time: 3.5623s
                    
  Semgrep-core time:
  Total CPU time: 3.1715s  File parse time: 0.1483s  Rule parse time: 0.1087s  Match time: 0.1258s
  Slowest 5/6679 files
  ...l-java/results/run-info-20260826.033313.473.yml (478KB): 0.057s (0.036s to parse)
  ...script/results/run-info-20260826.033238.771.yml (297KB): 0.032s (0.018s to parse)
  ...eql-go/results/run-info-20260826.033418.747.yml (166KB): 0.017s (0.012s to parse)
  ...python/results/run-info-20260826.033157.332.yml (138KB): 0.011s (0.008s to parse)
  ...og/database-index-files-20260826.110928.660.log (113KB): 0.010s (0.008s to parse)
  Slowest 5 rules to match
  ...te-as-no-escape.template-translate-as-no-escape:         0.041s
  ...from-http-request.tainted-cmd-from-http-request:         0.022s
  ....boto3.security.hardcoded-token.hardcoded-token:         0.013s
  ...e-with-script-tag.unknown-value-with-script-tag:         0.012s
  ...urity.detect-child-process.detect-child-process:         0.008s
  Analyzed: 6641 generic files ( 23MB in 2.938 seconds)
            4 go files (  4KB in 0.015 seconds)        
            6 java files (  8KB in 0.052 seconds)      
            8 js files (  8KB in 0.058 seconds)        
            18 json files ( 11KB in 0.005 seconds)     
            18 python files ( 18KB in 0.049 seconds)   
            1 xml files (700B in 0.000 seconds)        
            11 yaml files (  1MB in 0.118 seconds)     
  Errors:   4 files with errors, see output before the results for details or run with --strict
            ParseError (4 files)                                                               

                
                
┌──────────────┐
│ Scan Summary │
└──────────────┘
✅ Scan completed successfully.
 • Findings: 12 (12 blocking)
 • Rules run: 181
 • Targets scanned: 6679
 • Parsed lines: ~100.0%
 • Scan skipped: 
   ◦ Files larger than  files 1.0 MB: 21
   ◦ Files matching .semgrepignore patterns: 2
 • Scan was limited to files tracked by git
 • For a detailed list of skipped files and lines, run semgrep with the --verbose flag
Ran 181 rules on 6679 files: 12 findings.
```
##### `--config semgrep/rules.yml`. Rules customization exploration. 

```
% semgrep scan --time --config semgrep/rules.yml
                
  ============================[ summary ]============================
  Total time: 0.8699s Config time: 0.1057s Core time: 0.7609s
                    
  Semgrep-core time:
  Total CPU time: 0.0489s  File parse time: 0.0398s  Rule parse time: 0.0005s  Match time: 0.0065s
  Slowest 5/18 files
  services/webhooks/server.js                        (  2KB): 0.008s (0.007s to parse)
  services/webhooks/lib/verify.js                    (785B):  0.008s (0.007s to parse)
  ...in/java/com/coda/settlement/IdempotencyKey.java (  1KB): 0.008s (0.007s to parse)
  .../java/com/coda/settlement/LedgerRepository.java (  1KB): 0.008s (0.007s to parse)
  services/ledger/main.go                            (  1KB): 0.008s (0.006s to parse)
  Slowest 5 rules to match
  semgrep.paylink.java-string-sql:                            0.002s
  semgrep.paylink.python-shell-true:                          0.002s
  semgrep.paylink.go-command-shell:                           0.001s
  semgrep.paylink.javascript-jwt-none:                        0.001s
  semgrep.paylink.javascript-child-process-exec:              0.000s
  Analyzed: 2 go files (  2KB in 0.008 seconds)    
            3 java files (  4KB in 0.015 seconds)  
            4 js files (  4KB in 0.016 seconds)    
            9 python files (  9KB in 0.009 seconds)
  Errors:   0 files with errors

                
                
┌──────────────┐
│ Scan Summary │
└──────────────┘
✅ Scan completed successfully.
 • Findings: 5 (5 blocking)
 • Rules run: 5
 • Targets scanned: 18
 • Parsed lines: ~100.0%
 • Scan skipped: 
   ◦ Files larger than  files 1.0 MB: 21
   ◦ Files matching .semgrepignore patterns: 2
 • Scan was limited to files tracked by git
 • For a detailed list of skipped files and lines, run semgrep with the --verbose flag
Ran 5 rules on 18 files: 5 findings.

```


##### Create CodeQL Python DB
```bash
% codeql database create artifacts/codeql-python --language=python --source-root=.
..SNIP..
% Successfully created database at /Users/syafiq/Coda3/target-app-semgrepci/artifacts/codeql-python.
```
##### Create CodeQL Javascript DB
```bash
 % codeql database create artifacts/codeql-javascript --language=javascript --source-root=.
..SNIP..
% Successfully created database at /Users/syafiq/Coda3/target-app-semgrepci/artifacts/codeql-javascript.
```

##### Create CodeQL Java DB
```bash 
% cd services/settlement
% codeql database create ../../artifacts/codeql-java \
  --language=java \
  --source-root=. \
  --command='mvn clean package'
..SNIP..
Successfully created database at /Users/syafiq/Coda3/target-app-semgrepci/artifacts/codeql-java.
```

##### Create CodeQL Go
```bash
% cd services/ledger
% codeql database create ../../artifacts/codeql-go \
  --language=go \
  --source-root=. \
  --command='go build ./...'
..SNIP..
Successfully created database at /Users/syafiq/Coda3/target-app-semgrepci/artifacts/codeql-go.
```

##### Analyze using CodeQL

```
## python

% codeql database analyze artifacts/codeql-python \
  codeql/python-queries:codeql-suites/python-code-scanning.qls \
  --format=sarif-latest \
  --output=artifacts/codeql-python.sarif

## js
codeql database analyze artifacts/codeql-javascript \
  codeql/javascript-queries:codeql-suites/javascript-code-scanning.qls \
  --format=sarif-latest \
  --output=artifacts/codeql-javascript.sarif

## java
codeql database analyze artifacts/codeql-java \
  codeql/java-queries:codeql-suites/java-code-scanning.qls \
  --format=sarif-latest \
  --output=artifacts/codeql-java.sarif    

## go
codeql database analyze artifacts/codeql-go \
  codeql/go-queries:codeql-suites/go-code-scanning.qls \
  --format=sarif-latest \
  --output=artifacts/codeql-go.sarif
```

##### Artifacts 
```
syafiq@Syafiqs-MacBook-Air target-app-semgrepci % ls artifacts 
codeql-go			codeql-java.sarif		codeql-python			semgrep-security-audit.sarif
codeql-go.sarif			codeql-javascript		codeql-python.sarif
codeql-java			codeql-javascript.sarif		semgrep-auto.json
```

## Duration measurement
Caveat: AI agent assisted (copilot) as I was getting inconsistent results multiple times.

Both tools were measured on the same macOS machine against the application
source under `services/`. Semgrep was measured as one scan. CodeQL was measured
in two phases: database creation, which includes extraction and any required
build, followed by query analysis. The `real` value from `/usr/bin/time -p` is
the wall-clock time used for comparison. CodeQL runs used a workspace temporary
directory to avoid a macOS temporary-path permission issue.

| Tool and scope | Phase | Wall clock (`real`) | Findings | 
|---|---|---:|---:|---:|
| Semgrep custom rules on `services/` | Scan | 1.23s | 5 | 
| Semgrep `p/security-audit` on `services/` | Scan | 2.30s | 11 | 
| Semgrep `auto` on `services/` | Scan | 8.17s | 33 | 
| CodeQL Python | Database creation | 1.97s | n/a | 
| CodeQL Python | Query analysis | 5.26s | 8 | 
| CodeQL JavaScript | Database creation | 3.07s | n/a | 
| CodeQL JavaScript | Query analysis | 9.10s | 5 | 
| CodeQL Java, `--build-mode=none` | Database creation | 13.23s | n/a | 
| CodeQL Java | Query analysis | 8.39s | 0 | 
| CodeQL Go, including `go build ./...` | Database creation | 8.02s | n/a | 
| CodeQL Go | Query analysis | 5.23s | 2 |

**Verified against target-app:** Semgrep analyzed 17 application files. CodeQL
analyzed 10 Python, 4 JavaScript, 3 Java, and 2 Go files. CodeQL end-to-end
totals were Python 7.23s, JavaScript 12.17s, Java 21.62s, and Go 13.25s.
These totals include database creation; Semgrep has no database phase.

## Comparison table

| **Criterion** | Semgrep | CodeQL | Notes |
|---|---|---|---|
| **Languages in this repository** | Supports Python, JavaScript, Java, and Go in the selected scans. Verified against target-app; registry scans analyzed all four service languages | Supports Python, JavaScript, Java, and Go. Verified against target-app; CodeQL databases build and analyzed for all four languages | **Vendor documentation:** both tools list these languages as supported |
| **Findings returned** | 3 custom-rule findings; 34 with `auto`; 12 with `p/security-audit` | 8 Python, 5 JavaScript, 2 Go, and 0 Java security results | **Verified against target-app:** counts came from the JSON/SARIF artifacts in `artifacts/` |
| **Findings assessed real** | TODO | TODO | **Verified against target-app:** *reachability* and exploitability are documented in the walkthrough below |
| **Scan duration** | See Duration measurement | See Duration measurement | **Verified against target-app:** Initially Semgrep durations came from `--time`; CodeQL duration uses /usr/bin/time but comparing with different tools in biased. Used AI agents to perform analysis that uses /usr/bin/time|
| **Setup friction** | Easy local installation and setup. One command run. | CLI available. Database build required. Source build for compiled languages. | **Verified against target-app:** documented in the reproducibility section above |
| **Rule customisability** | YAML patterns and taint rules | QL query packs and custom queries | **Vendor documentation:** both support custom detection logic.<br><br>**Verified against target-app:** `semgrep/rules.yml` validated and ran 5 rules; standard CodeQL packs ran, with no custom QL query authored. |
| **Licensing/cost** | Free edition available; paid Teams and Enterprise features | CodeQL CLI terms and GitHub Advanced Security requirements apply to private repositories | **Vendor documentation:** pricing and license terms were reviewed for both tools. Semgrep $30/committer/month. CodeQL $35/committer/month |
| **Output and CI fit** | Text, JSON, SARIF | SARIF and GitHub Code Scanning Action | **Vendor documentation:** both integrate with CI; SARIF is the interchange format |
| **Maintenance burden** | Repository-owned local rules plus registry/policy review | Query packs plus language-specific build configuration | **Vendor documentation:** rules, query packs, and integrations require ongoing updates |

## Three-findings evaluation 

| Finding and evidence | How it was determined to be real | Untrusted-input reachability | Tool result and conclusion |
|---|---|---|---|
| **Go command injection** at `services/ledger/main.go:20`; Semgrep `paylink.go-command-shell`; CodeQL `go/command-injection` | `syncHandler` decodes JSON into `syncRequest`, passes `req.Region` to `reconcile`, and `reconcile` concatenates it into `sh -c`. An input such as `sg; id` changes the executed command. | **Yes.** HTTP request body -> `req.Region` -> `reconcile` -> `exec.Command("sh", "-c", ...)`. | **True positive found by both tools.** High-confidence and reachable. Suitable for the blocking gate. |
| **Reflected XSS** at `services/webhooks/server.js:29`; CodeQL `js/reflected-xss` | `rows` is produced by `receiptRow()`. That function applies `escapeHtml()` to `partner` and `reference` before returning the HTML row. The final handler only wraps the escaped value in a table. | **No exploitable path identified.** The request values are passed through the custom HTML escaping function before reaching the response. | **False positive from CodeQL.** CodeQL did not recognize the custom sanitizer. This finding should be suppressed with a reviewed justification, not fixed as an XSS vulnerability. |
| **Java SQL injection** at `services/settlement/src/main/java/com/coda/settlement/LedgerRepository.java:24-26`; Semgrep `java.lang.security.audit.formatted-sql-string`; no CodeQL Java result | `merchantId` and `batchRef` are concatenated into SQL executed with `Statement`. Quotes or SQL operators in either value can alter the query. The separate `findByStatus()` method demonstrates the safe `PreparedStatement` approach. | **Not proven end-to-end.** The repository does not include a caller showing whether these values originate from an HTTP request or settlement file. If an external caller supplies them, the vulnerability is reachable. | **True positive found by Semgrep and missed by CodeQL.** The unsafe SQL pattern is real. CodeQL did not report it because it did not establish an untrusted source-to-sink path in the available Java code. |

### Conclusion from the three cases

1. The Go result demonstrates agreement between Semgrep and CodeQL on an obvious,
reachable vulnerability. 

2. The CodeQL XSS result demonstrates why scanner
findings require manual review: custom sanitization can produce a false
positive when it is not modeled by the analyzer. 

3. The Java SQL result demonstrates
a coverage difference: Semgrep identified an objectively unsafe SQL construction
that CodeQL did not report because source-to-sink reachability was not proven.

## Pipeline integration and enforcement evidence

### Enforcement path

The repository workflow runs `semgrep ci` using the `SEMGREP_APP_TOKEN` GitHub
Actions secret. The scan is submitted to the Semgrep project shown in the
policy configuration. That policy triggers `Block merge and comment on PR/MR`
when both conditions are true:

- Severity is `Critical` or `High`.
- Confidence is `High`.

GitHub branch protection must require the resulting `semgrep/ci` check. The
Semgrep policy supplies the security decision; GitHub's required check makes
that decision enforceable at merge time. Lower-severity or lower-confidence
findings remain available for dashboard triage.

Pull requests use Semgrep CI's diff-aware behavior. Pushes to `main` and the
weekly schedule provide full-repository inventory. This trades immediate
re-evaluation of unchanged files on every PR for faster feedback, with the
weekly scan recovering repository-wide coverage.

### Local gate reproduction

Run from the repository root:

```bash
bash tools/test_semgrep_gate.sh
```

The script creates and removes temporary fixtures. Expected behavior:

```text
vulnerable.py: paylink.python-shell-true -> non-zero exit
safe.py -> zero exit
Semgrep gate fixtures behaved as expected
```

This test does not assert that the whole repository has zero findings because
the assessment sample intentionally contains baseline findings. It verifies
the contract for a newly introduced finding and a safe replacement.

### Required GitHub runs

These records must be populated from real GitHub and Semgrep executions; no
run identifiers are inferred from local scans.

| Case | Commit SHA | GitHub Actions URL | Semgrep finding/policy result |
|---|---|---|---|
| Vulnerable PR: introduce `paylink.python-shell-true` | `PENDING` | `PENDING` | Must comment and block merge |
| Fixed PR: remove the introduced vulnerability | `PENDING` | `PENDING` | Must pass `semgrep/ci` and allow merge |

To reproduce the failing case, create a branch from a clean commit, add a
temporary request-controlled `subprocess.run(..., shell=True)` change, push it,
and open a PR into `main`. Confirm the Semgrep project receives the matching
commit SHA, the policy comments on the PR, and GitHub refuses the merge because
`semgrep/ci` is required. To reproduce the passing case, remove that change,
push the follow-up commit, and rerun the workflow from the PR or use
`Actions -> Semgrep -> Run workflow` for the branch.

The local environment could not verify the Semgrep container digest because the
Docker daemon was unavailable. Before production rollout, record the digest
and verify the signed Semgrep image through the organization's approved image
verification process. The Go build passed; Python tests were blocked by the
environment's Python 3.14 dependency build for `psycopg2-binary==2.9.5`, and
the Maven build was not completed in this validation pass.

