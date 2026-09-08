# Target scope

Active testing is allowlist-only. The default package ships **zero** live
external targets.

## Files

| File | Purpose |
|---|---|
| `configs/scope.example.yaml` | Template. Copy to `configs/scope.yaml` on the lab. |
| `engagement/scope.txt` | Runtime allowlist: one hostname, URL prefix, or CIDR per line |
| `engagement/authorization.md` | Written acknowledgement |
| `lib/scope_check.py` | Mechanical check used by install/verify and operators |

## What may be listed

- `127.0.0.1`, `localhost`, `::1`
- RFC1918 / lab CIDRs the operator controls
- Staging hostnames the operator owns
- Explicit URLs / API prefixes
- Explicit IP ranges

Wildcards like `*` or `0.0.0.0/0` are **rejected** by `scope_check.py`.

## What is never in default scope

- Production customer systems
- Third-party SaaS
- Cloud metadata (`169.254.169.254`, `metadata.google.internal`, …)
- Random internet hosts discovered during recon

## LLM endpoints

A model endpoint is in scope only if:

1. It is listed under `authorized_llm_endpoints` in `configs/scope.yaml`, **or**
2. It is loopback (`127.0.0.1` / `localhost`) **and** the operator named it as target.

OpenRouter / Nous public model IDs are **not** automatic authorization to
attack someone else's production app. They are model-as-SUT for **your**
eval account.

## AI Recon / web pentest

`web-pentest` already requires `engagement/scope.txt`. This package adds the
same file at lab root so red-team, recon, and web tools share one list.
