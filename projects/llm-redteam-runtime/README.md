# projects/llm-redteam-runtime — additional eval harness (this host)

**Status: VERIFIED WORKING on the build host (2026-09-08).**

This project bundles an *alternative* LLM evaluation path that runs **alongside**
`projects/redteam/` (the unified `rt.py` suite). Use whichever fits the task:

| Path | Tool | Best for |
|---|---|---|
| `projects/redteam/` (`rt.py`) | Unified static+adaptive+agency suite | own-OpenAI-compat target, dry-pack, cascades |
| `projects/llm-redteam-runtime/` | **Jailbreaker UI + promptfoo eval + observer** | interactive UI runs, promptfoo plugin corpus, quick JSONL triage |

Both are abstract/placeholder corpora. Neither carries live harmful payloads.

## Contents

| Component | What it is | Status |
|---|---|---|
| `docker-compose.jailbreaker.yml` | SpecterOps Jailbreaker-CE (frontend:3000, backend:8000, db:5432) | healthy on build host |
| `promptfoo/jailbreak-eval/promptfooconfig.yaml` | hand-built jailbreak corpus (10 attacks) + provider | ✅ ran on build host |
| `observe.sh` | JSONL triage: refuse / leak / neutral per attack | ✅ 10/10 refuse on DeepSeek-V4-Flash |
| `results/` | JSONL output dir (feed to analysis module) | dir |
| `start.sh` | status of the whole runtime | ✅ |
| `README.md` (this file) | overview | — |

## Quick start (build host already has Docker)

```bash
cd projects/llm-redteam-runtime

# 1. Jailbreaker UI
docker compose -f docker-compose.jailbreaker.yml up -d --build
# panel: http://localhost:3000

# 2. promptfoo eval vs your model (edit config provider first)
cd promptfoo/jailbreak-eval
export REDTEAM_API_KEY=...   # or your provider key + apiBaseUrl
../node_modules/.bin/promptfoo eval -o ../../results/run.jsonl

# 3. triage
bash observe.sh ../../results/run.jsonl
```

## Provenance (this host)

Built and verified on the SAME build host as this package:
- Hermes profile `llm-redteam` → provider `your provider` (DeepSeek-V4-Flash) smoke OK
- 10-attack promptfoo eval → 10/10 correct refusals
- Jailbreaker 3 containers healthy

## Relationship to the unified suite

- `rt.py` is the **canonical** path for role-separated (attacker/judge/target)
  OpenAI-compatible evaluation with dry-pack and cascades.
- This runtime is the **complementary** path when you want the Jailbreaker UI
  (analyst-friendly) or promptfoo's plugin ecosystem (harmbench, cyberseceval).
- Keep BOTH out of the default live posture. No external targets; fill
  `configs/scope.yaml` + `engagement/authorization.md` first.

## Secrets

Provider keys are NOT included. Set them via env (`REDTEAM_API_KEY`,
`OPENROUTER_API_KEY`, `REDTEAM_API_KEY`) or `~/.hermes/.env` on the target host.
