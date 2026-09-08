# Techniques (classes)

Operational recipes against third-party production systems are out of scope.
Below are **classes** implemented or referenced by previous work.

## Black-box iterative (lab default)

| Class | Idea | In this lab |
|---|---|---|
| PAIR | Attacker-LLM rewrites a prompt from judge feedback | `adaptive/adaptive_attack.py` |
| TAP | PAIR + tree-of-thoughts / pruning | documented; not a separate binary |
| Crescendo | Multi-turn gradual escalation | adaptive O7, agency X5 |
| Wrapper pack | Fixed transformations of the operator prompt | `redteam/prompt_pack.py` |

## Input-filter evasion (structure only)

Encoding (Base64/hex/ROT13), payload splitting, leetspeak, ASCII-art, low-resource language pivot. Corpus C/D. Adaptive O3/O4.

## Alignment / persona

DAN-style persona, nested fiction (DeepInception-class), dual-channel “safe vs unrestricted”, false authority + urgency. Corpus B/G.

## Indirect / tool

Hidden HTML, poisoned tool JSON, RAG document instructions. Corpus E. Agency X3.

## Agency cascade (Hermes-specific)

Recovered from `agent-aggression-test`:

1. Attacker jailbreaks the **target agent**.
2. Target delegates to a sub-agent.
3. Sub-agent emits a tool call.
4. Optional `--allow-fire` sends it to a **mock** scanner on loopback.

This tests OWASP LLM06/LLM08, not network exploitation.

## White-box (documented, not shipped as runners)

| Class | Access | Note |
|---|---|---|
| GCG | gradients | hours–days GPU; not in `rt.py` |
| AutoDAN | genetic / stealth suffixes | perplexity-detector bypass class |
| Abliteration | refusal direction in activations | weight-ablation tooling skill — not bundled |

## Frameworks to layer later (not vendored)

Garak (CI breadth), PyRIT (campaign depth), HarmBench / JailbreakBench (regression), AI-Purple-Ops, X-Teaming, Jailbreak-Eval, TRACE, AJAR. See `sources/oss_redteam_research.md`.

## Practice note (jailbreaks.fyi, recovered)

Generic frameworks do **not** model your application system prompt. Always set `target.system_prompt` to the real app prompt when evaluating a product, not bare weights.
