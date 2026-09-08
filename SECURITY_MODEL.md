# Security model

This laboratory exists for **authorized defensive testing**. Natural-language
policy is not enough. Scope is enforced by files + scripts.

## Two classes of targets

| Class | Meaning | Default |
|---|---|---|
| AUTHORIZED | Explicitly listed in `configs/scope.yaml` (copied to `engagement/scope.txt`) | empty |
| UNAUTHORIZED / UNKNOWN | Everything else | refuse active tests |

Passive public lookup (WHOIS, published docs) is allowed. Payload-bearing
requests, scans, jailbreak evals against a live endpoint, and tool-fire are
**active** and require an allowlist hit.

## Authorization gate (web / infra)

Before the first active request in a session:

1. Operator records written authorization in `engagement/authorization.md`.
2. Operator fills `engagement/scope.txt` from `configs/scope.example.yaml`.
3. Tools that can send traffic MUST call `lib/scope_check.py` (or equivalent)
   with the destination host/URL/CIDR.
4. No match → refuse. Redirects off-scope → stop and ask.

Default `scope.example.yaml` contains **no external hosts**. Localhost and
RFC1918 lab ranges are commented examples only.

## LLM red-team gate

- Test only models you own or have written permission to test.
- Objectives stay abstract: `[AUTHORIZED TEST]`, `[HARMFUL_REQUEST]`, `[SECRET]`, `[TOOL]`.
- Attacker and judge models are **not** the target.
- Agency layer's scanner is a **canary mock** (`127.0.0.1:8123`). Real exploit
  payloads are out of scope of the packaged suite.
- `--allow-fire` is the only path that dispatches parsed tool-calls to the canary.

## Role isolation

| Role | May be | Must not be |
|---|---|---|
| attacker | strong reasoning model | the system under test |
| judge | separate strong model | the system under test |
| target | the SUT (local, OpenAI-compat, Hermes) | used as attacker/judge |
| aux (summarize/vision) | cheap model | mixed into attacker prompts |

If a config would set `target.model == attacker.model`, treat it as a
misconfiguration and refuse a live run until the operator confirms they
intentionally want a self-play eval.

## Dual-use / dangerous skills (not auto-installed)

These exist on the origin Hermes and are **documented, not bundled as default
runtime**:

| Skill | Risk | Lab policy |
|---|---|---|
| operational-jailbreak tooling | Operational jailbreak templates against arbitrary APIs | Do not install on the lab unless operator explicitly copies it. Prefer `hermes-redteam-suite` (own-model, abstract corpus). |
| weight-ablation tooling | Weight-level refusal ablation | Open-weight + GPU only; out of default lab. |
| `captcha-analysis-and-bypass` | Can be used off-scope | Install only with scope_check. |
| `pentest-toolkit-generator` | Generates attack scripts | Phase 1 analysis only until RoE exists. |
| `ecommerce-pentest` | Price/IDOR against live shops | Own staging only. |

## Secrets

Never store in this package:

- API keys, OAuth tokens, cookies, SSH private keys, PATs

Use `${ENVIRONMENT_VARIABLE}` placeholders. Operator setup: `docs/CREDENTIALS.md`.

## Logging

- Engagement evidence → `engagement/evidence/` (redact secrets to last 6 chars in chat).
- Red-team JSON transcripts → `projects/redteam/out/` (may contain attack text; do not ship to untrusted aux models).
- Canary hits → `projects/redteam/agency/data/hits.log` (uid 65534).

## Destructive operations

DROP/DELETE SQL, `rm`/`mkfs`/`shutdown`, filesystem-write SSTI, production
mutators: **ask first**. Default lab prefers Juice Shop / DVWA / local canary.
