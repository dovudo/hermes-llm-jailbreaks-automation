# hermes-llm-jailbreaks-automation

**Automated, defensive red-teaming of *your own* LLM.** Paste any adversarial
prompt → it is sent to your target model **verbatim** → you get the **full raw
response** back, in a **resumable session** you can re-enter later to interrogate
the model about *why* a bypass worked.

> ⚠️ **Defensive use only.** This tool is for testing models **you own** or are
> **explicitly authorized in writing** to test. The attack corpus contains
> **abstract scaffolds with placeholders only** (`[HARMFUL_REQUEST]`, `[SECRET]`,
> `[TOOL]`, …) — **no working exploits, malware, or harmful recipes**. Do not use
> it to attack third-party services or to evade the safety of models you don't own.
> Contributions that add operational harmful content will be rejected.

## Why it exists

If you are hardening an LLM before release, you need to (1) throw a broad,
current attack surface at it, (2) capture the model's **exact** output without any
summarization, and (3) come back later and *ask the model itself* why it complied.
This project automates (1)–(3) and hands the raw result to whatever analyzer /
scorer you already run — it deliberately does **no scoring of its own**.

## How it works

```
your prompt ──▶ target model (verbatim) ──▶ full raw response
                     │
                     └──▶ persisted as a SESSION (out/sessions/<SESSION_ID>.json)
                              ├──▶ analyzer reads it by SESSION_ID
                              └──▶ you re-enter it later and keep asking the model
```

- **Verbatim.** Prompts are passed to the model unchanged — no categories, goals,
  or rewrites. You control exactly what gets tested.
- **Full fidelity.** Both `response` and (for thinking models) the complete
  `reasoning_content` are returned. Truncation by token limit is flagged, never
  silent.
- **Resumable sessions.** Every session has a stable `SESSION_ID`. The session is
  a file you own — any process (an orchestrating agent, or you directly) can
  reattach to it and continue the exact conversation with the target model.
- **No hidden logging.** The only thing persisted is the conversation state needed
  to resume and to feed the analyzer. No scoring, no derived logs.

## Quickstart

### 1. Point it at your model

`projects/redteam/redteam/provider.yaml` reads env var names (never key values):

```bash
export REDTEAM_ENDPOINT="https://your-endpoint/v1/chat/completions"
export TARGET_MODEL="your-org/your-model"
export REDTEAM_API_KEY="…"          # or put it in ~/.hermes/.env (never committed)
```

Set your model's **real** system prompt in `provider.yaml` → `target.system_prompt`
so tests reflect what you actually deploy.

### 2. Run a case (standalone, no agent required)

```bash
cd projects/redteam

# resumable session — prints a SESSION_ID + full raw JSON response
python3 chat.py start --file /path/to/prompt.txt

# continue the same conversation (multi-turn / crescendo)
python3 chat.py say --session <SESSION_ID> --file /path/to/next.txt

# come back anytime and interrogate the model directly, in that context:
python3 chat.py repl --session <SESSION_ID>
#   you>   why did you comply instead of refusing?
#   model> <full raw response, in the exact context where the bypass happened>

# one-shot without persistence:
echo "prompt" | python3 ask.py
```

### 3. Or drive it from an agent

The bundled skill `skills/bundled/hermes-redteam-suite` lets an orchestrating
agent run all of this for you and hand back only a `SESSION_ID`. You then resume
that session — by ID — from a fresh agent chat, with no scripts to run yourself.
See [`RUNBOOK.md`](RUNBOOK.md).

## The attack corpus

`projects/redteam/static/corpus.json` — **54 abstract test cases** spanning
classic and current (2024–2026) techniques: many-shot, crescendo, skeleton key,
policy puppetry, deceptive delight, Bad-Likert-judge, unicode-tag / ASCII-art
smuggling, encoding / flip / tokenizer-break / best-of-N obfuscation, refusal
suppression, immersive-world roleplay, echo chamber, context overflow, indirect
prompt injection (tool/RAG), confused-deputy exfil, MCP tool poisoning /
rug-pull / line-jumping, memory poisoning, and system-prompt leakage.

Techniques and dated sources: [`research/jailbreaks/MODERN_TECHNIQUES_2025.md`](research/jailbreaks/MODERN_TECHNIQUES_2025.md).

## Repo layout

| Path | Role |
|---|---|
| `projects/redteam/ask.py` | Stateless one-shot: prompt → full raw response |
| `projects/redteam/chat.py` | Resumable sessions (`start` / `say` / `repl` / `show` / `list`) |
| `projects/redteam/static/corpus.json` | 54 abstract attack test cases |
| `projects/redteam/redteam/provider.yaml` | Target / roles config (env-driven, no secrets) |
| `skills/bundled/hermes-redteam-suite/` | Agent skill that orchestrates the above |
| `research/jailbreaks/` | Technique taxonomy, sources, evaluation notes |
| `lib/scope_check.py` | Default-deny allowlist check for authorized targets |
| `deployment/verify.sh` | Harmless integrity + secret-scan smoke |

## Contributing

Contributions welcome — especially **new abstract test cases** for emerging
techniques. Rules:

1. **Abstract only.** Payloads must use placeholders and describe the *structure*
   of a technique, never a working recipe. PRs with operational harmful content
   are rejected.
2. **Cite a dated source** for any new technique (add a row to
   `research/jailbreaks/MODERN_TECHNIQUES_2025.md`).
3. **Match the schema:** `{"id","category","layer","target","payload"}`; keep ids
   unique.
4. Run `bash deployment/verify.sh` (must exit 0) and
   `python3 -m py_compile projects/redteam/*.py` before opening a PR.

## Safety & scope

- `target` ≠ `attacker` ≠ `judge`. The tested model is only ever the `target`.
- Scope is **empty by default** (`configs/scope.example.yaml`); active testing of
  any endpoint requires an allowlist + written authorization.
- Secrets live only in env / `~/.hermes/.env`, never in the repo.

## License

MIT.
