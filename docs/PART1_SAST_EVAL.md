# Part 1 — SAST Tools Evaluation

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

### Local Runs
##### `--config auto`. Output json.

```bash
%  semgrep scan \
  --time \
  --config auto \
  --error \
  --json-output=./artifacts/semgrep-auto.json \
  --sarif-output=./artifacts/semgrep-auto.sarif \
  --text-output=./artifacts/semgrep-auto.txt \
  .
```
##### `--config semgrep/rules.yml`. Rules customization exploration. 
```bash
% semgrep scan \
  --time \
  --config semgrep/rules.yml \
  --json-output=./artifacts/semgrep-custom.json \
  --sarif-output=./artifacts/semgrep-custom.sarif \
  --text-output=./artifacts/semgrep-custom.txt \
  .
```

##### Create CodeQL Python DB
```bash
% codeql database create artifacts/codeql-python --language=python --source-root=.
```
##### Create CodeQL Javascript DB
```bash
 % codeql database create artifacts/codeql-javascript --language=javascript --source-root=.
```
##### Create CodeQL Java DB
```bash 
% cd services/settlement
% codeql database create ../../artifacts/codeql-java \
  --language=java \
  --source-root=. \
  --command='mvn clean package'
```

##### Create CodeQL Go
```bash
% cd services/ledger
% codeql database create ../../artifacts/codeql-go \
  --language=go \
  --source-root=. \
  --command='go build ./...'
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

## Duration measurement
Caveat: AI agent assisted (copilot) as I was getting inconsistent results multiple times.

Both tools were measured on the same macOS machine against the application
source under `services/`. Semgrep was measured as one scan. CodeQL was measured
in two phases: database creation, which includes extraction and any required
build, followed by query analysis. The `real` value from `/usr/bin/time -p` is
the wall-clock time used for comparison. CodeQL runs used a workspace temporary
directory to avoid a macOS temporary-path permission issue.

| Tool and scope | Phase | Wall clock (`real`) | Findings |
|---|---|---:|---:|
| Semgrep custom rules on `services/` | Scan | 1.23s | 5 |
| Semgrep `p/security-audit` on `services/` | Scan | 2.30s | 11 |
| Semgrep `auto` on `services/` | Scan | 8.17s | 33 |
| CodeQL Python | Database creation | 1.97s | n/a |
| CodeQL Python | Query analysis | 5.26s | 8 |
| CodeQL JavaScript | Database creation | 3.07s | n/a |
| CodeQL JavaScript | Query analysis | 9.10s | 5 |
| CodeQL Java | Database creation, including `mvn clean package` | 13.23s | n/a |
| CodeQL Java | Query analysis | 8.39s | 0 |
| CodeQL Go | Database creation | 8.02s | n/a |
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

