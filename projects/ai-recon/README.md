# AI Recon — integration notes

**Status: PARTIALLY RECOVERED (public tool identified; private instance unconfirmed).**

## What was found

The receiving agent marked AI Recon **MISSING upstream** on its origin host. On
this build host, the only matching entity is the **public** repository:

**`pikpikcu/airecon`** — MIT, Python 3.12+, ~984★, updated 2026-06-20.

> AIRecon is an autonomous cybersecurity agent combining a self-hosted LLM
> (Ollama) with a Kali Linux Docker sandbox and a Textual TUI. Automates security
> assessments, pentesting, and bug-bounty recon — 100% local, no API keys or
> cloud dependency.

- Pipeline: `RECON → ANALYSIS → EXPLOIT → REPORT`
- ~1.09M-record offline knowledge base (SQLite FTS5) via `airecon-dataset`
- 57 built-in skill files + `airecon-skills` community playbooks
- MCP integration via `~/.airecon/mcp.json`
- Memory: `~/.airecon/memory/airecon.db`
- Colab T4 tunnel option (Cloudflare) when local VRAM is short

**Important:** AIRecon is a **web/infra pentest agent**, not an LLM red-team
harness. It answers a different question than `projects/redteam/`.

## Does it cover this lab's needs?

Partly. Recommended division of labor:

| Need | AIRecon | This package |
|---|---|---|
| Web pentest / recon / bug bounty | ✅ its purpose | `web-pentest`, `domain-intel` skills |
| Agent executes Kali tooling sandboxed | ✅ TUI + Docker | — |
| LLM jailbreak / prompt-injection eval | ❌ | `projects/redteam` (rt.py), `projects/llm-redteam-runtime` |
| ASR scoring, judge/target roles | ❌ | redteam suite |
| Offline autonomy | ✅ | proxy is local-only |

## Wiring (OpenAI-compatible local endpoint)

```
Nous Portal (OAuth on the lab Hermes)
    → hermes proxy  (127.0.0.1:8645, loopback)
        → OpenAI-compatible /v1
            → AIRecon (or any OpenAI-compat client)
```

AIRecon must **not** receive Nous OAuth tokens directly. Point it at the proxy:

| Setting | Value |
|---|---|
| Base URL | `http://127.0.0.1:8645/v1` |
| API key | any non-empty string (proxy attaches OAuth) |
| Model | attacker/reasoning model, never the SUT |

Keep AIRecon's recon targets inside `configs/scope.yaml`. Default deny.

## Hermes interaction

- Lab Hermes plans, authorizes, and reports.
- AIRecon is an **external tool**, not the target model, not the attacker model.
- Do not let AIRecon use target credentials.

## Recovery options

If the operator's "AI Recon" is `pikpikcu/airecon`, install per its README:

```bash
# pipx (clean) — preferred
pipx install git+https://github.com/pikpikcu/airecon.git
# dataset (optional, downloads ~once)
airecon init
```

**Unresolved (operator confirm):**
- Private/commercial AI Recon? → supply separately; do not bundle.
- Original config env var names / license.
- Confirm OpenAI-compat support in the version you run.
