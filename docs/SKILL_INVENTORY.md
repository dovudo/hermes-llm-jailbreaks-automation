# Skill inventory (origin → lab)

Do not silently delete skills. Dangerous ones are documented, not default-installed.

`P` = portable (bundled). `D` = documented only. `R` = redirect stub.

## Bundled (`skills/bundled/`)

| Skill | Origin | Portable? | Secrets? | Machine paths? | Notes |
|---|---|---|---|---|---|
| hermes-redteam-suite | security/ | P | no | rewritten to `${LAB_ROOT}` | Canonical LLM eval |
| llm-defensive-redteam | security/ | P | no | still mentions origin `/opt/projects/hermes-redteam` | Methodology; engines moved |
| llm-redteam-eval | devops/ | R | no | origin paths | Redirect → suite |
| hermes-adaptive-redteam | security/ | R | no | origin paths | Redirect → suite |
| agent-aggression-test | security/ | R | no | origin paths | Redirect → suite |
| web-pentest | security/ | P | no | uses `engagement/scope.txt` | Allowlist already in skill |
| ai-pentest-agents | security/ | P | no | none | Catalog; deadend-cli install broken |
| backend-security-audit | software-development/ | P | no | none | Code audit, not live exploit |
| oss-forensics | security/ | P | no | none | Supply chain |
| sherlock | security/ | P | no | network | Username OSINT — still needs scope for *active* use |
| domain-intel | research/ | P | no | network | Passive |
| osint-investigation | research/ | P | no | public records | Passive |

## Documented, NOT bundled (dual-use / off-policy by default)

| Skill | Risk | Lab policy |
|---|---|---|
| operational-jailbreak tooling | Operational jailbreaks vs arbitrary APIs | Origin only unless operator copies |
| weight-ablation tooling | Weight ablation | GPU + own weights |
| captcha-analysis-and-bypass | Off-scope automation | Scope gate |
| ecommerce-pentest | Live shop IDOR | Own staging |
| pentest-toolkit-generator | Generates attack scripts | RoE first |
| scrapling | Stealth scrape / CF bypass | Scope gate |
| blocked-page-recovery | WAF/paywall | Scope gate |

## Gaps / related but out of security-lab default

No standalone frontend-security skill was recovered. Frontend testing is covered
partly by `web-pentest` (HTTP/app layer) plus stock Playwright/UI QA skills;
add a dedicated frontend-security skill only when the receiving operator
supplies one. Do not invent a duplicate.

Playwright, agent-browser, linux-server-ops, hermes-config-ops (deploy notes),
hermes-agent (self-config) remain stock Hermes capabilities; install from stock
Hermes, do not duplicate.

## Overlaps (merged conceptually)

- `llm-redteam-eval` + `hermes-adaptive-redteam` + `agent-aggression-test` → **hermes-redteam-suite**
- `llm-defensive-redteam` kept as **eval methodology** (judges, mitigations)
- Human corpus markdown vs `corpus.json` — JSON is runtime; markdown is research

## Environment / network (bundled skills)

| Need | Who |
|---|---|
| Docker | agency canary |
| PyYAML + python3 | rt.py, scope_check |
| Outbound LLM API or local proxy | live red-team only |
| Browser / nmap / whatweb | web-pentest (not auto-installed) |
