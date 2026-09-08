# Jailbreak research — consolidated corpus

Authoritative reconstruction of previous work on the origin host.
Payloads remain **abstract**. This is defensive evaluation material.

## Files

| File | Contents |
|---|---|
| `TAXONOMY.md` | Layers, categories, OWASP/ATLAS mapping |
| `TECHNIQUES.md` | PAIR/TAP/GCG/Crescendo/agency cascade — classes, not recipes |
| `TEST_CASES.md` | 25 static + 8 adaptive + 5 agency IDs |
| `MUTATION_STRATEGIES.md` | How the adaptive layer rewrites |
| `EVALUATION.md` | ASR, judges, matrix, triage |
| `SOURCES.md` | Papers, tools, origin paths |
| `sources/` | Verbatim recovered documents |

## What was recovered

1. **Safety-layer model** (`llm_safety_deepseek_research.md`): input / training-time alignment / inference-time guarding. RLHF = alignment-by-example. Role-confusion in ~78% of evaluated jailbreaks.
2. **Prompt-injection corpus** (`prompt_injection_test_corpus.md` + `corpus.json`): 8 categories A–H, placeholders only.
3. **OSS tooling map** (`oss_redteam_research.md`): Garak (breadth), PyRIT (depth), HarmBench/JBB (regression), TAP/PAIR/GCG classes.
4. **Live sweep ASR** (summary only): DeepSeek-chat 25%, Qwen3.8-27b 12.5%, Hunyuan-A13B 50% under adaptive `max_turns=5`, judge `gpt-5.6-luna`. Full transcripts stay on origin (`/opt/projects/hermes-redteam/sweep_report.md`) — dual-use, not migrated.
5. **Unified automation**: `/opt/projects/redteam` → vendored here as `projects/redteam/`.

## What this lab should actually run

Not a paper recreation of GCG/AutoDAN. Run:

```
projects/redteam : static → adaptive → agency → UNIFIED_REPORT.md
```

against a **named target model** with attacker ≠ target.

## Explicitly not in this folder

- operational jailbreak templates (operational-jailbreak tooling skill exists on origin; not default-installed).
- Concrete harmful behaviors from HarmBench (use official benchmark under its license if needed).
- Weight ablation (weight-ablation tooling).
