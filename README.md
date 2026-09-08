# Hermes Security Lab

Authoritative, portable migration package for an **authorized** security-testing
laboratory on a **fresh Hermes install**.

This is a reconstruction and synchronization of previous work on this host
(jailbreak research, unified red-team suite, web/backend pentest skills,
Nous Portal / subscription proxy docs). It is **not** a new research program.

## What this laboratory is for

- Adversarial LLM testing (jailbreak, prompt injection, agent/tool-use safety)
- Authorized web / backend / frontend security testing
- Passive recon and AI-surface reconnaissance
- Report generation with evidence files (not chat-only)

Default posture: **no active external targets**. Active tests require an
explicit allowlist plus written authorization recorded in the engagement dir.

## Architecture

```
                SECURITY TESTING
                       │
                       ↓
                HERMES AGENT
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    RED-TEAM LLM   SECURITY TOOLS   AI RECON
         │             │             │
         └─────────────┼─────────────┘
                       ↓
                  TARGET MODEL
                       ↓
                EVALUATION ENGINE
                       ↓
                    REPORT
```

Hard rule: **attacker / judge / reasoning models are never the target**.
Configure roles in `configs/models.example.yaml` and
`projects/redteam/redteam/provider.yaml`.

## Layout

| Path | Role |
|---|---|
| `BOOTSTRAP_PROMPT.md` | Paste into the **new** Hermes after unpacking this package |
| `SYNC_REPORT.md` | What was preserved / merged / missing |
| `MANIFEST.md` | File inventory + provenance |
| `SECURITY_MODEL.md` | Authorization, roles, dual-use limits |
| `TARGET_SCOPE.md` | Allowlist semantics |
| `OPERATIONS.md` | Day-2 runbook |
| `research/jailbreaks/` | Consolidated jailbreak corpus (abstract payloads) |
| `projects/redteam/` | Unified 3-layer red-team CLI (`rt.py` / `run.sh`) |
| `projects/llm-redteam-runtime/` | Jailbreaker UI + promptfoo eval + observer (verified on build host) |
| `projects/ai-recon/` | Integration notes — public `pikpikcu/airecon`; private unconfirmed |
| `skills/bundled/` | Portable copies of relevant Hermes skills |
| `configs/` | Provider / model / scope **examples** (no secrets) |
| `deployment/` | inspect / install / verify / uninstall |
| `docs/` | Credentials, Nous Portal, inventory |

## Transfer to a new server

1. Install a clean Hermes (`hermes setup --portal` if using Nous subscription).
2. Copy this directory. Do **not** copy `~/.hermes/.env`, `auth.json`, or API keys.
3. Paste `BOOTSTRAP_PROMPT.md` into the new agent.
4. The new agent **inspects** the package first. It must not blindly run scripts.
5. Operator fills credentials interactively (`docs/CREDENTIALS.md`).
6. Run `deployment/verify.sh` (harmless smoke only). Do **not** start live attacks.

## Non-goals

- Not a general-purpose exploit framework.
- Does not include live jailbreak transcripts from previous sweeps.
- Does not include operational jailbreak / weight-ablation payloads in the default install.
- Does not vendor AI Recon source (it was not found on the origin host).

## Origin host notes (do not treat as portable paths)

On the machine that built this package:

- Unified suite: `/opt/projects/redteam/`
- Original static/adaptive: `/opt/projects/hermes-redteam/` (untouched)
- Original agency: `/opt/projects/agent-aggression-test/` (untouched)
- Skills live under `~/.hermes/skills/`
