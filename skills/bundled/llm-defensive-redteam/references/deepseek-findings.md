# DeepSeek-family safety findings (upstream security reports)

Context caveat: no public model named "DeepSeek Flash" exists in research literature as of this writing; findings below are for **DeepSeek-V3/R1/R1-Distill**. A fast/lightweight variant of the same alignment school inherits these properties.

## Layer model of LLM safety (not defense-in-depth)
Three weakly-coupled filters, not real depth:
1. **Input-level** sanitization/blocklists → beaten by obfuscation, ciphers, multilingual.
2. **Training-time alignment** (RLHF / RLAIF / Constitutional AI / SFT) → the core defector.
3. **Inference-time guarding** (Llama Guard, NeMo, output classifiers) → only marginally lowers ASR.

Core training defect (works consensus): RLHF rewards *behavioral compliance on specific phrasings*, not *intent recognition* → "alignment by example" generalizes poorly to encoded/rephrased/multimodal input.

## DeepSeek specifics
- **Weak alignment layer** correlated with cheap training (RL + CoT self-eval + distillation, low budget). V3 "neglected safety alignment"; safety optimized for *explicit* threats, fragile under adversarial manipulation.
- **Cisco/Robust Intelligence + UPenn:** R1 = **100% ASR** on a 50-prompt HarmBench subset (temperature 0).
- **arXiv 2503.15092 (CNSafe, 3100 cases):** under jailbreak attacks ASR reaches **100%** in some categories (ethnic hatred, false info); V3 hits 100% on those.
- **arXiv 2506.18543 (HarmBench, 7 methods, 510 behaviors):** DeepSeek *partially* robust to optimization attacks (TAP-T) but *more* vulnerable to prompt-based/manually-engineered. GPT-4 Turbo more stable (stronger RLHF + red-teaming).

## Three DeepSeek-specific failure points
1. **Open Chain-of-Thought (R1) — main feature = main breach.** Exposed `thinking` tags raise ASR for insecure-output generation and sensitive-data theft (Trend Micro via NVIDIA Garak). R1 ASR ~**+30.4%** vs V3 (arXiv 2503.15092). R1 sometimes generates MORE harmful content in internal reasoning traces than in the final answer (2506.18543) — overt refusal looks fine while the harmful trajectory already ran. `H-CoT` (white-box): re-injecting internal CoT traces back into the prompt manipulates hidden representations. Fix: filter `thinking` tags from chat answers.
2. **Language asymmetry:** English ASR ~**+21.7%** higher than Chinese (2503.15092).
3. **Scaling hurts refusal without proportional alignment:** GCG ASR grows with size — **33.44% @1.5B → 55.31% @32B** (2506.18543). GPT degrades less due to stronger safety-reinforcement.

## Most powerful universal class: fine-tuning / jailbreak-tuning
FAR.AI "Illusory Safety": guardrails are **illusory** on fine-tunable models. Jailbreak-tuning (fine-tune on a jailbreak) concentrates learning on the safety weak spot and burns out refusals. Before: ~100% refusal, harmfulness ≤6%. After: >80% harmfulness, refusals nearly gone. Vulnerable: ALL tested — DeepSeek R1-Distill-Llama-70B AND closed fine-tunable GPT-4o, Claude 3 Haiku, Gemini 1.5 Pro. Larger/more capable models can be MORE vulnerable.

Practical implication: **treat refusal as illusory**; evaluate your model under the assumption it will comply at full capability ("evil twin" / pre-mitigation evaluation — test before AND after mitigations).

## Root causes (4)
1. Alignment by example (RLHF) — phrasing, not intent.
2. Surface-level filtering — token edits, blind to masking.
3. Weak layer coupling — beat the weakest filter only.
4. Reasoning ≠ robustness — exposed CoT/multimodal create new attack surface.

## Benchmarks / tooling
HarmBench (400 behaviors/7 categories), StrongREJECT, ToxiGen, CNSafe/CNSafe_RT (zh-en, github.com/NY1024/DeepSeek-Safety-Eval), NVIDIA Garak, TAP, PAIR, AutoDAN. Standards: OWASP LLM Top-10 (2025), MITRE ATLAS.

Primary sources (arXiv / reports): 2507.19672 (safety-align survey), 2503.15092 (DeepSeek safety boundaries), 2506.18543 (DeepSeek jailbreak analysis vs GPT); Cisco/Robust Intelligence "Evaluating Security Risk in DeepSeek"; Trend Micro "Exploiting DeepSeek-R1: Breaking Down CoT Security"; FAR.AI "Illusory Safety"; IJCA 187(27) 2025 "Semantic Jailbreaks and RLHF Limitations".