# Techniques catalog (deep-dive 2026)

Consolidated, mechanism-deduped catalog behind the 272-case corpus in
`projects/redteam/static/corpus.json`. Every corpus payload is an ABSTRACT
scaffold (placeholders only). Prefix legend: `A–F` seed · `AC` academic ·
`VN` vendor · `CM` community · `TA` agentic · `FW` framework-coverage ·
`EN` encoding · `MM` multimodal · plus `NM/CR/SK/PP/DD/BLJ/SM/ART/OB/TB/BON/RS/
IW/EC/CO/AG/MCP/MP/LK`.

> ⚠️ **Source caveat.** Verify each URL before citing publicly. Load-bearing
> sources are the vendor posts, CVEs, and ACL/USENIX/NeurIPS/ICML/IEEE papers.
> Some arXiv IDs were surfaced from model knowledge (cutoff ~Jan 2026) and were
> not individually re-opened — treat bare arXiv IDs as leads until link-checked.

## 1. Input-surface: encoding & obfuscation
| Technique | Mechanism | Source (dated) |
|---|---|---|
| Base64/base32/hex/binary/percent | Encode the ask; model decodes & complies | Wei et al., "Jailbroken", arXiv:2307.02483 (Jul 2023) |
| CipherChat | Whole conversation in a cipher channel | Yuan et al., arXiv:2308.06463 (Aug 2023) |
| Bijection learning | Teach an in-context bijection, converse mapped | Haize Labs, arXiv:2410.01294 (Oct 2024) |
| ArtPrompt (ASCII art) | Trigger word as ASCII art | Jiang et al., arXiv:2402.11753 (Feb 2024) |
| FlipAttack | Reverse chars/words as a "noise gate" | Liu et al., arXiv:2410.02832 (Oct 2024) |
| Payload splitting / variable assembly | Concatenate benign fragments at gen-time | Kang et al., arXiv:2302.05733 (Feb 2023) |
| TokenBreak | Perturb trigger so guardrail tokenizes differently | HiddenLayer (2025) |
| Zero-width / homoglyph / reorder | Imperceptible/look-alike Unicode | Boucher et al., "Bad Characters", IEEE S&P 2022 |
| Unicode Tag (U+E00xx) smuggling | Instructions in invisible Tag block | Rehberger, Embrace The Red (2024); MS blog (2026) |
| Leetspeak / emoji / whitespace | Substitution/segmentation of keywords | Wei et al. 2023 |
| Nested / multi-layer encodings | Stack transforms (Base64∘ROT13) | Wei et al. 2023 |
| Low-resource language | Translate into thin-coverage language | Yong et al., arXiv:2310.02446 (Oct 2023) |

## 2. Alignment-surface: framing, persona, multi-turn
| Technique | Mechanism | Source (dated) |
|---|---|---|
| DAN / persona / anti-persona (Waluigi) | Unrestricted alter-ego w/ exemption claim | Shen et al., arXiv:2308.03825 (2023) |
| Persona modulation | Auto-generate tailored personas | Shah et al., arXiv:2311.03348 (2023) |
| DeepInception / nested fiction | Deeply nested fictional framing | Li et al., arXiv:2311.03191 (2023) |
| Immersive World | Persistent fictional universe rewards restricted output | Cato Networks (Mar 2025) |
| Skeleton Key | "Augment, don't refuse" + warning label | Microsoft (Jun 26 2024) |
| Deceptive Delight | Weave restricted topic among benign, then deepen | Unit 42 (Oct 2024) |
| Bad Likert Judge | Model scores harmfulness, then emits the score-5 example | Unit 42 (Dec 2024) |
| Crescendo | Gradual multi-turn escalation citing prior replies | Russinovich et al., arXiv:2404.01833 (Apr 2024) |
| Echo Chamber (+Crescendo) | Context poisoning via indirect references | NeuralTrust (Jun–Jul 2025) |
| Many-shot | Long context of faux compliant demos | Anthropic (Apr 2024) |
| Context Compliance Attack | Forge a prior assistant "agreement" in client history | Microsoft, arXiv:2503.05264 (Mar 2025) |
| Policy Puppetry | Disguise ask as system "policy" config + roleplay | HiddenLayer (Apr 2025) |
| Refusal suppression + prefix injection | Ban refusal tokens; force "Sure, here is" | Wei et al. 2023 |
| Tense/hypothetical reframing | Past-tense/historical framing | Andriushchenko & Flammarion, arXiv:2407.11969 (2024) |
| Cognitive overload / distraction | Bury ask in dense filler + competing instructions | Xu et al., arXiv:2311.09827 (2023) |
| Decoding/sampling exploitation | Sweep temperature/top-k/top-p, sample many | Huang et al., arXiv:2310.06987 (2023) |
| CodeAttack | Embed request as data in a code task | Ren et al., arXiv:2403.07865 (2024) |

## 3. Automated / optimization / attacker-LLM
| Technique | Mechanism | Source (dated) |
|---|---|---|
| GCG (gradient suffix) + transfer | Optimize an adversarial suffix; transfers black-box | Zou et al., arXiv:2307.15043 (Jul 2023) |
| AmpleGCG | Generative model amortizes suffix production | Liao & Sun, arXiv:2404.07921 (2024) |
| AutoDAN (genetic) | Fluency-preserving genetic evolution | Liu et al., arXiv:2310.04451 (2023) |
| PAIR | Attacker-LLM refines from refusal feedback | Chao et al., arXiv:2310.08419 (2023) |
| TAP (tree-of-attacks) | Branch-and-prune search over attacker prompts | Mehrotra et al., arXiv:2312.02119 (2023) |
| GPTFuzzer / MasterKey | LLM-mutation fuzzing; fine-tuned attacker | Yu et al. 2309.10253; Deng et al. NDSS 2307.08715 |
| Best-of-N | N stochastic augmentations until one passes | Hughes et al., arXiv:2412.03556 (Dec 2024) |
| Adaptive random search (logprobs) | Per-target random-search suffix | Andriushchenko et al., arXiv:2404.02151 (2024) |
| AutoDAN-Turbo / h4rm3l | Lifelong strategy discovery; composable DSL | arXiv:2410.05295; arXiv:2408.04811 (2024) |
| PAP (persuasion) | Wrap ask in social-science persuasion | Zeng et al., arXiv:2401.06373 (2024) |
| Refusal-direction ablation | Ablate the latent refusal direction | Arditi et al., arXiv:2406.11717 (2024) |
| Imprompter | Auto-computed obfuscated string drives tool misuse | Fu et al., arXiv:2410.14923 (2024) |

## 4. Multimodal
| Technique | Mechanism | Source (dated) |
|---|---|---|
| FigStep (typographic list) | Harmful steps rendered as an image list | Gong et al., arXiv:2311.05608 (Nov 2023) |
| Typographic / handwritten instruction | Rendered text in an image | OpenAI GPT-4V System Card (Sep 2023) |
| Cross-modal payload split | Sensitive token in image, verb in text | Willison (Oct 2023) |
| Visual adversarial / image hijack | Optimized perturbation forces affirmation | Qi et al. 2306.13213; Bailey et al. 2309.00236 (2023) |
| Steganographic instruction | Instruction in LSB/hidden channel | Qi et al. 2023 lineage |
| Audio jailbreak | Harmful request as speech (or reversed/spelled) | arXiv:2405.19103 (May 2024) |
| QR / barcode-encoded prompt | Instruction the agent decodes | Willison/Rehberger (2023–2024) |
| Document injection (PDF/DOCX/SVG/EXIF) | Injected instruction in body/metadata | Rehberger (2023–2024) |

## 5. Agentic / tool / RAG / MCP / memory
| Technique | Mechanism | Source (dated) |
|---|---|---|
| Indirect prompt injection | Directive in fetched web/tool/RAG content | Greshake et al., arXiv:2302.12173 (2023); OWASP LLM01:2025 |
| InjecAgent (tool hijack) | Injected tool output redirects tool calls | Zhan et al., arXiv:2403.02691 (2024) |
| PoisonedRAG | Poison retrieval corpus to control generation | Zou et al., arXiv:2402.07867 (2024) |
| Confused-deputy / privilege escalation | Untrusted content drives a privileged tool | OWASP LLM06:2025 |
| EchoLeak (zero-click exfil) | Untrusted input pulls scoped data cross-boundary | CVE-2025-32711, Aim Labs (Jun 2025) |
| ShadowLeak / AgentFlayer / ForcedLeak | Hidden-content → connector/egress exfil | Radware / Zenity / Noma (Aug–Sep 2025) |
| Markdown-image exfiltration | Auto-rendered `![](url?d=DATA)` beacon | Rehberger (2024) |
| MCP tool poisoning / line-jumping / shadowing | Directives in tool description/schema | Invariant Labs (Apr 2025); Trail of Bits (2025) |
| MCP rug pull | Approved tool mutates behavior post-consent | CVE-2025-54136, Check Point (Aug 2025) |
| Memory poisoning (MINJA / AgentPoison) | Query-only writes persist across sessions | arXiv:2503.03704 (NeurIPS 2025); arXiv:2407.12784 |
| Multi-agent injection / Morris-II worm | Self-propagating prompt across agents | arXiv:2410.07283; arXiv:2403.02817 (2024) |
| Rules-file backdoor | Hidden bidi/zero-width directive in shared config | Pillar Security (Mar 2025) |
| Tool-output/error spoofing | Fake "authorized"/error strings carry instructions | OWASP Agentic Threats (2025) |
| HITL approval fatigue | Flood benign approvals, slip in a sensitive action | OWASP Agentic T10/T15 (2025) |

## 6. Extraction / leakage
| Technique | Mechanism | Source (dated) |
|---|---|---|
| System-prompt leak (PLeak) | "Repeat everything above"; encoded re-emit | OWASP LLM07:2025; Zhang et al. 2307.06865 |
| Training-data extraction / membership inference | Elicit memorized PII/docs | NIST AI 100-2e2025 (privacy) |
| Vector/embedding weakness | Cross-tenant retrieval / embedding inversion | OWASP LLM08:2025 |

## 7. Framework-coverage categories (no "technique" flavor — easy to miss)
Unbounded consumption / denial-of-wallet (OWASP LLM10), data/model poisoning &
supply chain (LLM03/04), misinformation / cascading hallucination (LLM09,
Agentic T5), harmful-content taxonomy sweep (Llama Guard S1–S14), toxicity/bias
(AVID), insecure-code / package hallucination (Meta CyberSecEval), repudiation /
identity spoofing (Agentic T8/T9), benchmark-behavior regression (HarmBench /
JailbreakBench). Covered by the `FW` prefix.

## Deliberately excluded from the corpus (tracked, not scaffolded)
- All operational content (real suffixes, encoded-harmful strings, stego bytes,
  harmful images) — placeholders only.
- Fine-tuning / weight-poisoning safety removal (Qi et al. arXiv:2310.03693) —
  training-time, not an inference-time prompt; guard the fine-tune API separately.
- GCG raw suffix strings — represented only as `[ADV_SUFFIX]`.
