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
##### Semgrep using `--config auto`.

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
##### Semgrep using `--config semgrep/rules.yml` (Rules customization exploration).
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
## Comparison table

| **Criterion** | Semgrep | CodeQL | Notes |
|---|---|---|---|
| **Languages in this repository** | Supports Python, JavaScript, Java, and Go in the selected scans. Verified against target-app; registry scans analyzed all four service languages | Supports Python, JavaScript, Java, and Go. Verified against target-app; CodeQL databases build and analyzed for all four languages | **Vendor documentation:** Both tools list these languages as supported |
| **Findings returned** | 34 with `auto` | 8 Python, 5 JavaScript, 2 Go, and 0 Java security results | **Verified against target-app:** counts came from the `JSON/SARIF` artifacts in `artifacts/` |
| **Findings assessed real** | AI Assisted | AI Assisted | **Verified against target-app:** See Triage table |
| **Scan duration** | AI Assisted | AI Assisted | **Verified against target-app:** See Duration measurement |
| **Setup friction** | Easy local installation and setup. One command run. | CLI available. Database build required. Source build for compiled languages. | **Verified against target-app:** Documented in the reproducibility section above |
| **Rule customisability** | YAML patterns and taint rules | QL query packs and custom queries | **Vendor documentation:** both support custom detection logic.<br><br>**Verified against target-app:** `semgrep/rules.yml` validated and ran 5 rules (AI assisted rule authoring); standard CodeQL packs ran, with no custom QL query authored. |
| **Licensing/cost** | Free edition available; paid Teams and Enterprise features | CodeQL CLI terms and GitHub Advanced Security requirements apply to private repositories | **Vendor documentation:** pricing and license terms were reviewed for both tools. Semgrep $30/committer/month. CodeQL $35/committer/month |
| **Output and CI fit** | Text, JSON, SARIF | SARIF and GitHub Code Scanning Action | **Vendor documentation:** both integrate with CI; SARIF is the interchange format. Semgrep supports multiple CI integration. |
| **Maintenance burden** | Repository-owned local rules plus registry/policy review | Query packs plus language-specific build configuration | **Vendor documentation:** rules, query packs, and integrations require ongoing updates |

## Triage
Caveat: AI agent assisted analysis. Further reasoned and judgemet by human in the Three-findings evaluation sections.

Legend: **TP** = real, verified by hand · **FP** = flagged but not actually exploitable ·
**Info/quality** = correctness or style, not a security finding. "Caught by" lists every
tool that raised it; a location caught by only one tool is called out.

### True Positives
| # | Location | Issue | Caught by | Notes |
|---|---|---|---|---|
| 1 | `services/api/auth.py:18` | `pickle.loads` on an attacker-controlled session cookie → RCE | Semgrep + CodeQL | **TP**. CodeQL flags `py/unsafe-deserialization`, and the cookie/session value flows directly into `pickle.loads`. This is a real deserialization exploit and reachable from attacker-controlled input. |
| 2 | `services/api/db.py:35` | SQL injection via `reference` / `status` query params, built with f-string SQL | Semgrep + CodeQL | **TP**. Semgrep flags the raw f-string SQL, and CodeQL reports `py/sql-injection`. The request parameters flow directly into the SQL sink. |
| 3 | `services/api/app.py:62` | `banner` query param concatenated into a rendered template string → server-side template injection | Semgrep + CodeQL | **TP**. Semgrep raises a raw HTML/template warning, and CodeQL flags `py/template-injection`. This is more severe than simple XSS because Jinja SSTI can lead to code execution. |
| 4 | `services/api/receipts.py:15-16` | `subprocess.run(f"wkhtmltopdf --quiet {src} {dst}", shell=True)` → command injection | Semgrep + CodeQL | **TP**. The receipt filename/path is attacker-controlled and flows into a shell command. This is directly reachable and chains with the path traversal issue below. |
| 5 | `services/api/app.py:86` and `services/api/receipts.py:7-8` | Unvalidated `filename` path param used to build filesystem paths → path traversal | CodeQL only | **TP**. CodeQL reports `py/path-injection` twice. The attacker-controlled filename reaches filesystem path construction. Semgrep missed this in the default configuration. |
| 6 | `services/api/webhooks_out.py:8` | Outbound GET to merchant-supplied URL → SSRF | CodeQL only | **TP**. CodeQL reports `py/full-ssrf`. A user-controlled URL is used in a server-side outbound request. |
| 7 | `services/api/auth.py:22-27` | `jwt.decode(token, verify=False)` → any bearer token is accepted at face value | Manual only | **TP**. The code accepts tokens without verification. This is a real authentication bypass and was not caught by either default ruleset in the SARIF results. |
| 8 | `services/api/util/crypto.py:31-32` | `==` comparison in webhook signature validation → timing side channel | Manual only | **TP**. The code compares signatures using `==` rather than `hmac.compare_digest`, leaking timing signal. This is a real crypto/auth flaw, but not a standard scanner pattern. |
| 9 | `services/settlement/src/main/java/com/coda/settlement/SettlementParser.java:12-17` | XXE on acquirer-uploaded file | Semgrep only | **TP**. Semgrep reports an XXE sink in the XML parser. The XML document builder is not hardened against entity expansion in this code path. |
| 10 | `services/settlement/src/main/java/com/coda/settlement/LedgerRepository.java:26` | SQL injection via concatenated `merchantId` / `batchRef` values | Semgrep + CodeQL | **TP**. Semgrep flags `formatted-sql-string`; CodeQL flags `java/concatenated-sql-query`. The unsafe SQL string concatenation is present and reachable from untrusted values. |
| 11 | `services/settlement/src/main/java/com/coda/settlement/LedgerRepository.java:12-14` | Hardcoded database credentials in source | Manual only | **TP**. The application stores DB credentials directly in source. This is a real secret-management issue and was not flagged by the default scanner rules in this run. |
| 12 | `services/webhooks/lib/verify.js:19-21` | `jwt.decode` without verification used to gate `/admin/config` | Semgrep only | **TP**. The route uses decoded claims without verification. This is an authentication bypass pattern and a real issue even though CodeQL did not flag it in the default suite. |
| 13 | `services/webhooks/lib/verify.js:23-25` | `jwt.verify(..., { algorithms: ['none', 'HS256'] })` accepts unsigned tokens | Semgrep only | **TP**. The code explicitly permits the `none` algorithm, which is insecure. This is a real JWT validation issue. |
| 14 | `services/webhooks/lib/config.js:18` | Prototype pollution via recursive deep-merge assignment | CodeQL only | **TP**. CodeQL reports `js/prototype-pollution-utility`. Attacker-controlled config keys can pollute object prototypes and change application behavior. |
| 15 | `services/webhooks/server.js:29` and `services/webhooks/lib/render.js:15-17` | Reflected XSS via unescaped `message`/rendered value | Semgrep + CodeQL | **TP**. The output is rendered into HTML from user-controlled input. One of the reported JS XSS findings is a valid sink; the surrounding logic confirms this is an actual output path. |
| 16 | `services/webhooks/server.js:60` | `/admin/export` executes shell command built from request data | Semgrep + CodeQL | **TP**. User-controlled `partner`/`day` values are interpolated into a shell command. The sink is reachable and exploitable. |
| 17 | `services/webhooks/lib/verify.js:6` | Hardcoded HMAC secret in source | Semgrep only | **TP**. A static secret is committed in source. This is a real secret exposure issue and matches the generic secret-pattern rule. |
| 18 | `services/ledger/main.go:18-21` | `reconcile()` executes `sh -c` with request-controlled region | Semgrep + CodeQL | **TP**. The request body flows directly into a shell command. This is the clearest confirmed command-injection issue and matches both tools. |
| 19 | `services/ledger/client.go:14-19` | `InsecureSkipVerify: true` on outbound ledger client and hardcoded bearer token | Manual only | **TP**. The client skips certificate validation and sends a bearer token to an internal service. This is a real trust-boundary weakness, though impact is somewhat reduced because the service is internal-only. |
| 20 | `services/ledger/client.go:11` | Hardcoded bearer token in source | Manual only | **TP**. A static bearer token is committed to source and is thus exposed to anyone with repo access. |
| 21 | `services/ledger/main.go:45-52` | `fetchBatch` interpolates `id` query param into a URL without validation | Manual only | **TP**. The app handles a similar input elsewhere with validation; here it does not. This is a real logic inconsistency and should be reviewed as a follow-up issue. |

### False positives / low-confidence findings

| # | Location | Issue | Caught by | Notes |
|---|---|---|---|---|
| FP-1 | `services/api/db.py:20-24` | String-built SQL, looks similar to SQL injection | Semgrep (low confidence) | **FP**. `column` is restricted by a hardcoded whitelist before reaching the query string. User input never reaches the SQL text directly. |
| FP-2 | `services/webhooks/lib/render.js:11-13` | HTML template literal | Semgrep | **FP**. The values are sanitized by `escapeHtml()` before rendering. Semgrep pattern matching lacked escaping awareness. |
| FP-3 | `services/ledger/main.go:23-29` | `exec.Command` same family as the real injection | Neither tool flagged it | **FP**. Input is validated against a regex and passed as a discrete argv value, not string-built into a shell. |
| FP-4 | `services/webhooks/server.js:47-56` | `execFile` with request data | Neither tool flagged it | **FP**. `region` is checked against `ALLOWED_REGIONS` and `execFile` prevents shell breakout. |
| FP-5 | `services/settlement/src/main/java/com/coda/settlement/SettlementParser.java:19-25` | Same `DocumentBuilderFactory` pattern as XXE | Neither tool flagged it | **FP**. Entity expansion is explicitly disabled. |
| FP-6 | `services/settlement/src/main/java/com/coda/settlement/IdempotencyKey.java:24-27` | `java.util.Random` pattern | Neither tool flagged it | **FP / quality note**. Used only for log correlation, not security-relevant input. |
| FP-7 | `services/api/util/crypto.py:21-24` | MD5 usage | Semgrep + CodeQL | **FP**. The value is a cache key, not an auth or integrity control. |
| FP-8 | `services/api/tests/test_auth.py:4-5` | Strings shaped like live API keys / webhook secrets | Semgrep secret rule | **FP / triage**. They are test fixtures with `_test_` names and placeholder entropy. |

### Quality / correctness findings (not counted as security vulnerabilities)

| Location | Issue | Why not a security TP |
|---|---|---|
| `services/webhooks/server.js:4-9` | Unused imports | Style issue only |
| `services/webhooks/lib/verify.js` | CSRF middleware warning | Not a direct security issue in the current route setup |
| `services/api/webhooks_out.py` | `raise-for-status` style warning | Not a vulnerability |
| `services/ledger/main.go:42,51` | “No direct write to ResponseWriter” | Best-practice warning, not a confirmed vulnerability |
| `services/api/app.py:5` | Unused import | Style issue only |

## Duration measurement
Caveat: AI agent assisted analysis.

Semgrep was measured as one scan. CodeQL was measured in two phases: database creation, which includes extraction and any required build, followed by query analysis. The `real` value from `/usr/bin/time -p` is the wall-clock time used for comparison. CodeQL runs used a workspace temporary directory to avoid a macOS temporary-path permission issue.

| Tool and scope | Phase | Wall clock (`real`) | 
|---|---|---:|---:|
| Semgrep `auto` on `services/` | Scan | 8.17s | 
| Semgrep custom rules on `services/` | Scan | 1.23s |
| CodeQL Python | Database creation | 1.97s | 
| CodeQL Python | Query analysis | 5.26s |
| CodeQL JavaScript | Database creation | 3.07s | 
| CodeQL JavaScript | Query analysis | 9.10s | 
| CodeQL Java | Database creation, including `mvn clean package` | 13.23s |
| CodeQL Java | Query analysis | 8.39s | 
| CodeQL Go | Database creation | 8.02s |
| CodeQL Go | Query analysis | 5.23s | 2 |

**Verified against target-app:** Semgrep analyzed 17 application files. CodeQL
analyzed 10 Python, 4 JavaScript, 3 Java, and 2 Go files. CodeQL end-to-end
totals were Python 7.23s, JavaScript 12.17s, Java 21.62s, and Go 13.25s.
These totals include database creation; Semgrep has no database phase.


## Three-findings evaluation 

### Case 1: Go command injection
This is a confirmed command injection in `services/ledger/main.go`.

The vulnerable flow is:

1. A JSON request is decoded into a struct.
2. The `region` value from the request is passed into `reconcile(...)`.
3. `reconcile(...)` concatenates the user-controlled string directly into a shell command.
4. The command is executed via `sh -c`, which interprets the text as shell input.

### Exact code path

#### 1) Incoming request is decoded
```go
var req syncRequest
if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
    http.Error(w, "bad request", http.StatusBadRequest)
    return
}```

#### 2) The request struct contains a user-controlled Region
```go
type syncRequest struct {
    BatchID string `json:"batch_id"`
    Region  string `json:"region"`
}
```

#### 3) The value is passed to the vulnerable function
```go
out, err := reconcile(req.Region)
```

#### 4) The vulnerable sink: string concatenation into a shell command
```go
func reconcile(region string) ([]byte, error) {
    return exec.Command("sh", "-c", "/opt/paylink/reconcile --region "+region).CombinedOutput()
}```

#### If the attacker sends:
```go
{"region":"us-east-1; id"}
```
then:
```go
sh -c "/opt/paylink/reconcile --region us-east-1; id"
go

## Case 2: Reflected XSS
The CodeQL finding is reported at `services/webhooks/server.js:29` and relates to HTML generated by `services/webhooks/lib/render.js:15-17`.

The relevant request flow is:

1. The request supplies `partner` and `reference` values.
2. These values are passed to `receiptRow(...)`.
3. `receiptRow(...)` applies `escapeHtml(...)` to both values.
4. The escaped HTML row is inserted into a table response.
5. The values therefore do not reach the browser as executable HTML or JavaScript.

### Exact code path

#### 1) Request values are passed to `receiptRow`

File: `services/webhooks/server.js:28-30`

```js
app.get('/events/:partner/table', (req, res) => {
  const rows = [receiptRow(req.params.partner, req.query.reference || '')].join('');
  res.type('html').send(`<table>${rows}</table>`);
});
```

The values come from:
```js
req.params.partner
req.query.reference
```

#### 2) The values reach the rendering function
```js
function receiptRow(partner, reference) {
  return `<tr><td>${escapeHtml(partner)}</td><td>${escapeHtml(reference)}</td></tr>`;
}
```
The values are inserted into an HTML row, but both values are passed through escapeHtml(...) first.

#### 3) The custom HTML escaping function
```js
function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}```

For example, an input such as:
```js
<script>alert(1)</script>
```

is rendered as:
```js
&lt;script&gt;alert(1)&lt;/script&gt;
```
The scanner observes that request-controlled values eventually appear in an HTML response. However, the values used by `receiptRow(...)` are sanitized before they are inserted into the HTML template. Because the custom sanitizer handles the relevant HTML characters, the CodeQL result should be classified as a false positive for this specific path.

## Case 3: Python Server-Side Request Forgery
The CodeQL finding is reported at:

`services/api/webhooks_out.py:8`

The vulnerability is a server-side request forgery (SSRF) in `probe_endpoint(...)`.

The request flow is:

1. A client sends a URL to the `/v1/webhooks/probe` endpoint.
2. The application reads the URL from the JSON request body.
3. The URL is passed to `probe_endpoint(...)`.
4. `probe_endpoint(...)` sends a server-side HTTP request to that URL.
5. The application returns part of the response to the client.

### Exact code path

#### 1) The application accepts a URL from the request body

File: `services/api/app.py:119-125`

```python
@app.post("/v1/webhooks/probe")
def webhook_probe():
    merchant = current_merchant(request)
    if not merchant:
        abort(401)
    body = request.get_json(force=True) or {}
    return jsonify(probe_endpoint(body.get("url", "")))
```

The URL comes from:
```python
body.get("url", "")
```
No hostname validation, allowlist, scheme restriction, or private-network blocking is applied.

#### 2) The URL is passed to probe_endpoint
```python
return jsonify(probe_endpoint(body.get("url", "")))
```

#### 3) The server makes the outbound request
```python
def probe_endpoint(url):
    resp = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
    return {"status": resp.status_code, "body": resp.text[:2048]}
```
The vulnerable sink is:
```python
requests.get(url, timeout=TIMEOUT, allow_redirects=True)
```
An authenticated attacker could submit:
```python
{
  "url": "http://127.0.0.1:8081/health"
}
```
Possible targets include internal services, localhost-only endpoints, private network resources, and cloud metadata endpoints.

### Conclusion from the three cases

1. The Go result demonstrates agreement between Semgrep and CodeQL on an obvious, reachable vulnerability. 

2. The CodeQL XSS result demonstrates why scanner findings require manual review: custom sanitization can produce a false
positive when it is not modeled by the analyzer. 

3. CodeQL identified a confirmed server-side request forgery vulnerability. An attacker could potentially reach against internal services, private network resources, or cloud metadata endpoints.


### Overall assessment

These cases show complementary strengths between Semgrep and CodeQL:

- **Semgrep** was effective at detecting explicit insecure code patterns, including shell execution, SQL concatenation, and HTML construction.
- **CodeQL** was effective at tracing data from request-controlled sources to security-sensitive sinks, including command execution and outbound network requests.
- **Custom sanitizers, authentication boundaries, input validation, and application context** materially affect whether a scanner result is exploitable.

Semgrep contributes fast pattern-based detection and straightforward rule customization, while CodeQL contributes deeper data-flow analysis and reachability reasoning.