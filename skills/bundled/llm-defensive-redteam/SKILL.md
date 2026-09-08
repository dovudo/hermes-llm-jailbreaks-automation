---
name: llm-defensive-redteam
description: "Test your OWN LLM for prompt-injection weaknesses. ASR eval."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [llm-safety, red-teaming, prompt-injection, asr, defensive, alignment, eval-harness, owasp-llm, mitre-atlas]
    related_skills: [web-pentest]
---

# LLM Defensive Red-Teaming (own model)

Measure and fix safety weaknesses in a model you OWN or have written authorization to test, by running a **prompt-injection attack corpus** against your own OpenAI-compatible endpoint and computing **Attack Success Rate (ASR)** per category/layer.

**Polarity (important):** this skill is DEFENSIVE. It hardens *your* model — it is the mirror image of operational-jailbreak tooling (which creates jailbreaks to bypass *other/API* models' safety). Do NOT use this to evade safety on models you don't own or against third-party production services. When a circumvention request starts leaning that way, redirect to own-model testing (the framing that worked here). Resisting this drift is a feature, not a bug.

## When to Use
- User wants to "test safe my own model", "find weak points", "see how defenses are bypassed", "build test cases", "harden against prompt injection".
- You need a reproducible baseline (ASR before) → mitigation → ASR after ("evil twin" evaluation).
- You're building a red-team corpus or eval harness for a model endpoint you control.

## Deliverables / Artifacts
Working reference implementation lives in `/opt/projects/hermes-redteam/`:
- `harness.py` — Python3 stdlib-only eval harness (OpenAI-compatible `/v1/chat/completions`). Judge = heuristic refusal-marker OR separate judge-LM. Emits ASR by (category, layer) + JSON report.
- `corpus.json` — 25 machine-readable prompt-injection cases across 8 categories.

Usage:
```bash
python3 harness.py --endpoint http://127.0.0.1:8000/v1/chat/completions \
                   --model my-model --api-key $KEY \
                   --corpus corpus.json --out report.json
# more accurate judging (recommended):
python3 harness.py ... --judge model --judge-model openai/gpt-5.6-luna
```

See `references/eval-architecture.md` (harness design decisions + ad-hoc verification recipe) and `references/attack-corpus.md` (the corpus taxonomy + payload patterns). DeepSeek-family findings from upstream security reports: `references/deepseek-findings.md`.

## Workflow
1. **Frame it defensively.** Confirm target is a model/system you own or are authorized to test. Keep harmful payloads ABSTRACT (`[HARMFUL_REQUEST]`, `[SECRET]`, `[TOOL]` placeholders) so the detector/corpus teaches *structure*, not topic. This is what makes it durable and safe.
2. **Build/load the corpus** — 8 categories (instruction-override, role/persona, obfuscation, multilingual, indirect/agent-rag, secret-extraction, multi-turn/persuasion, output-handling). Fill real harmful targets from HarmBench/StrongREJECT behavior sets for full coverage.
3. **Run a baseline (pre-mitigation).** Record ASR per category and overall.
4. **Apply mitigations per weak layer** (see below), then re-run. Compare ASR.
5. **Automate the judge:** prefer `--judge model` (separate LLM verdict on "did the model perform the harmful action") over the heuristic for real runs.

## Key Mitigations to Test (layer → fix)
- **Indirect/agent-rag (class E, most dangerous):** enforce data/instruction separation — external content never executed as a command.
- **Obfuscation (C) & multilingual (D):** normalize input BEFORE the safety check (decode base64, collapse leetspeak, translate low-resource text) — check is only as good as its input.
- **Secret extraction (F):** never place secrets in the system prompt; for reasoning models, filter `` `thinking` `` / CoT tags from the answer.
- **Multi-turn (G):** evaluate the WHOLE dialogue, not the last turn.
- **Output-handling (H):** downstream systems must sanitize LLM output (never trust it).
- **General:** keyword/blocklist filters are weak; prefer intent-level classification; add an external output-guard (Llama Guard / NeMo) as a layer but never as the sole defense.

## Pitfalls
1. **Heuristic refusal detection misses terse refusals** — e.g. `"Sorry, no."` contains none of the standard markers (`i'm sorry`, `i can't`, `cannot assist`...). This inflated ASR in testing. Use `--judge model` for real runs; treat the heuristic as a fast smoke test only. Also include RU markers (`не могу`, `отказываюсь`, `не могу помочь`) for Russian-language models.
2. **Placeholder hygiene** — always substitute `[HARMFUL_REQUEST]` in `build_prompt`; a leftover literal placeholder silently turns the case into a no-op (target string mismatch). Assert "no placeholder left in final prompt" in verification.
3. **Verify harness logic with a mock API before a live run** — feed canned responses (2 refusals + 1 compliant) and assert ASR comes out exactly 1/3. Do this in a temp `/tmp/hermes-verify-*.py` script via subprocess, then remove it (execute_code sandbox has a clean interpreter per call; `from hermes import *` does NOT exist).
4. **`system_prompt` wrapping** — when a case declares its own system prompt, the global system prompt must not be appended twice; branch on `prompts[0]["role"]=="system"`.
5. **Rate limits** — retry on HTTP 429 with backoff; a single 429 collapse is a flaky-baseline failure, not a safety result.
6. **Reporting** — give ASR by (category, layer), not just overall; different layers are different failure domains. Always report total cases and method (heuristic vs judge-model) so numbers are interpretable.

## Sources / Benchmarks
- OWASP LLM Top-10 (2025): LLM01 Prompt Injection, LLM02 Sensitive Info Disclosure, LLM05 Improper Output Handling.
- MITRE ATLAS: AML.T0051 (Prompt Injection), AML.T0054 (Jailbreak), AML.T0057.
- Behavior sets: HarmBench (400 behaviors/7 categories), StrongREJECT, ToxiGen.
- Tooling to layer on: NVIDIA Garak (automated attack runs — integrates well), TAP/PAIR/AutoDAN for optimization-based attacks.