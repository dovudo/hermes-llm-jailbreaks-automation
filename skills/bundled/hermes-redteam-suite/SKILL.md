---
name: hermes-redteam-suite
description: 'Autonomous red-team of YOUR model. Agent orchestrates everything and returns only a SESSION_ID. You resume that session from any agent chat — no scripts to run. Verbatim prompts, full raw responses, no scoring.'
version: 4.2.0
author: hermes-llm-jailbreaks-automation
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [llm-safety, red-team, jailbreak, autonomous, resumable-session, verbatim, defensive]
    related_skills: []
---

# hermes-redteam-suite (v4.2 — autonomous, resume by SESSION_ID)

The **agent** drives the whole module. The **operator** never runs a script — they
paste prompts and receive, at the end, a **SESSION_ID**. Handing that ID to any
fresh agent chat re-enters the exact conversation with the target model.

DEFENSIVE ONLY: own model / written authorization. Prompts pass through verbatim;
the agent never invents working harmful payloads and never scores results.

## Autonomy contract (how the agent behaves)

- **Decide, don't ask.** Do not ask the operator procedural questions (session
  names, flags, files). Infer everything. Ask only if the target model is
  unconfigured and cannot be resolved.
- **Never expose scripts to the operator.** `chat.py` / `ask.py` are yours to call
  via Bash. The operator's entire interface is: paste a prompt, get a response +
  SESSION_ID; later, give a SESSION_ID, keep talking.
- **Never distort the result.** Return the model's full raw output. A short
  human-readable summary is fine, but the untouched response must remain in the
  session (the operator's analyzer reads it by SESSION_ID).
- **Never score or judge.** That is the operator's separate analyzer's job.

## Core loop — new case

On the operator's first prompt (no SESSION_ID in play):

```bash
cd ${LAB_ROOT}/projects/redteam
# write the prompt to a temp file so quotes/$/newlines can't break the shell
python3 chat.py start --file /tmp/case.txt
```

`chat.py` prints `SESSION_ID: rt-…` (stderr) and the full raw JSON response
(stdout). **Report the full response AND the SESSION_ID to the operator.**

Each subsequent prompt in the same chat continues that session (multi-turn /
crescendo):

```bash
python3 chat.py say --session <SESSION_ID> --file /tmp/case.txt
```

## Resume protocol — operator returns by SESSION_ID (the key feature)

When the operator gives you a `SESSION_ID` (in this or any later chat) and asks to
continue / investigate — e.g. *"resume rt-20260909-011632-326d and ask the model
why it complied"* — you become a thin relay to that persisted session:

1. For each operator message, run:
   ```bash
   python3 chat.py say --session <SESSION_ID> --file /tmp/turn.txt
   ```
   The full prior conversation is replayed to the target model automatically — the
   operator resumes exactly where the bypass happened.
2. Return the model's full raw response. Repeat for every follow-up.
3. `python3 chat.py show --session <SESSION_ID>` dumps the whole transcript if the
   operator (or their analyzer) wants it.

This works from a **fresh** agent session because the state lives in the session
**file**, not in agent memory — no sub-agent resume needed.

## Optional — orchestrate the whole corpus

If the operator says "run the corpus" / "run everything", iterate
`static/corpus.json`, one session per case, and return a manifest of SESSION_IDs:

```bash
# for each entry: write payload to /tmp/case.txt, then
python3 chat.py start --file /tmp/case.txt
# collect each SESSION_ID -> present the list for the analyzer
```

Do not summarize or score; just deliver the SESSION_ID list + each full response.

## Optional — adaptive attacker & mutation engine (creative / high-volume)

For deeper load-testing beyond the static corpus:

- **Adaptive attacker** — a SEPARATE attacker model creatively composes/mutates
  techniques against the target across turns, adapting when refused:
  ```bash
  python3 adaptive/adaptive_attack.py --target-api openai --target-endpoint <ep> \
    --target-model <your-model> --attacker-model <SEPARATE uncensored model> \
    --objectives adaptive/objectives.json --out out/adaptive_report.json
  ```
  The attacker's arsenal auto-loads from the live corpus. `target ≠ attacker` — and
  strongly-aligned attacker models often REFUSE to generate attacks even for
  authorized testing, so pick a less-restricted model for that role and tell the
  operator if it is refusing.
- **Mutation engine** — deterministic, no refusal risk, unlimited abstract volume:
  ```bash
  python3 mutators.py --out /tmp/load.json --objectives adaptive/objectives.json
  ```
  Then run each generated case via chat.py and collect SESSION_IDs.

Corpus is 272 abstract cases; see research/jailbreaks/TECHNIQUES_CATALOG.md and
DISCOVERY_METHODOLOGY.md.

## Optional — direct operator access (power users)

An operator who prefers a terminal can reattach without the agent:
`python3 chat.py repl --session <SESSION_ID>`. Not required; the agent path above
needs no scripts from the operator.

## Fidelity notes

- `response` may be empty for thinking models — the full answer is then in
  `reasoning_content`. Both are always returned in full.
- If `truncated=true` (hit `max_tokens`), warn and rerun with higher
  `--max-tokens` (or env `REDTEAM_MAX_TOKENS`, default 8192).

## Safety

- `target` ≠ `attacker` ≠ `judge`; the tested model is only ever `target`.
- Scope empty by default; active tests only against own / authorized models.
- Prompts pass verbatim, but never author working weapons/CBRN/malware payloads.
- Keys only via env / `~/.hermes/.env`, never in the repo.

## Integrity

```bash
python3 -m py_compile ask.py chat.py rt.py static/harness.py
bash deployment/verify.sh   # exit 0
```
