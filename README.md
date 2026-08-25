# paylink

Internal payment orchestration sample. Four services:

| Service      | Language | Purpose                                      |
|--------------|----------|----------------------------------------------|
| `api`        | Python   | Merchant-facing transaction and receipt API  |
| `webhooks`   | Node.js  | Partner webhook intake and replay            |
| `settlement` | Java     | Daily settlement file ingestion              |
| `ledger`     | Go       | Internal ledger sync client                  |

## Running locally

```bash
docker compose up --build
# api        -> http://localhost:8080
# webhooks   -> http://localhost:8081
```

Java and Go services are built from source:

```bash
cd services/settlement && mvn -q package
cd services/ledger && go build ./...
```

## Notes

This codebase is a reduced sample assembled for training and assessment
purposes. It is not production software and must not be deployed or exposed
to any network you care about.
