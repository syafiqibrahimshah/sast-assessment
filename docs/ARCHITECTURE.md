# paylink architecture

```
merchant ──► CDN ──► api (python)
                      │
                      ├──► ledger (go)  ──► ledger-prod.internal
                      └──► settlement (java, batch)

partner  ──► webhooks (node) ──► api
```

## Trust boundaries

- `api` is internet-facing. Every route under `/v1` is merchant-authenticated
  via the `paylink_session` cookie.
- Routes under `/internal` are reachable only through the internal load
  balancer. There is no additional authorisation inside the application.
- `webhooks` is internet-facing for `/events/*`. `/admin/*` is restricted at
  the load balancer by source range.
- `settlement` runs as a batch job and consumes files uploaded by the acquirer
  to an S3 prefix.
- `ledger` is internal only.
