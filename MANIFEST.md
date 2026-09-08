# MANIFEST

Package: hermes-security-lab
Origin build path: /opt/projects/hermes-security-lab
Date: 2026-09-08
Purpose: handoff bundle for another agent / fresh Hermes lab

## Top-level

| Path | Provenance |
|---|---|
| README.md | new (index) |
| BOOTSTRAP_PROMPT.md | new (paste into receiving agent) |
| SYNC_REPORT.md | new (diff vs origin) |
| MANIFEST.md | this file |
| SECURITY_MODEL.md | new (policy + mechanical scope) |
| TARGET_SCOPE.md | new |
| OPERATIONS.md | new |
| prompts/ | new, distilled from suite + web-pentest + HERMES_PROMPT.md |
| research/jailbreaks/ | consolidated from origin research files |
| research/jailbreaks/sources/ | verbatim copies |
| skills/bundled/ | copies of origin ~/.hermes/skills/… |
| projects/redteam/ | rsync of /opt/projects/redteam minus caches/logs; provider.yaml sanitized |
| projects/ai-recon/README.md | new (MISSING upstream) |
| projects/llm-redteam-runtime/ | new on RECEIVING host (verified Jailbreaker UI + promptfoo + observer harness) |
| configs/ | new examples, no secrets |
| lib/scope_check.py | new |
| deployment/ | new inspect/install/verify/uninstall |
| docs/ | credentials, Nous, skill inventory |

## Intentionally absent

- API keys, auth.json, SSH keys
- operational jailbreak / weight-ablation skill trees
- sweep_report.md full transcripts
- origin Hermes config.yaml

## How to pack for transfer

```bash
tar -C /opt/projects -czf hermes-security-lab.tar.gz hermes-security-lab
# verify no secrets:
tar -tzf hermes-security-lab.tar.gz | grep -Ei 'auth.json|\.env|id_rsa' || echo clean
```

Give the receiving agent: this tarball + BOOTSTRAP_PROMPT.md (+ any extra files
the operator adds).
