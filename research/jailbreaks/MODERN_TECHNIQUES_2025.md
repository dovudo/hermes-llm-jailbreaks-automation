# Modern jailbreak / injection techniques (2024–2026)

> Superseded/expanded by the deep-dive [`TECHNIQUES_CATALOG.md`](TECHNIQUES_CATALOG.md) and [`DISCOVERY_METHODOLOGY.md`](DISCOVERY_METHODOLOGY.md). Kept for provenance of the first 29-case batch.

Survey feeding the abstract test cases added to `projects/redteam/static/corpus.json`
(ids `NM*`, `CR1`, `SK1`, `PP*`, `DD1`, `BLJ1`, `SM*`, `ART1`, `OB*`, `TB1`, `BON1`,
`RS1`, `IW1`, `EC1`, `CO1`, `AG*`, `MCP*`, `MP1`, `LK*`). All corpus payloads are
**abstract scaffolds with placeholders only** — no operational content.

> ⚠️ **Source caveat.** Verify the URLs below before citing them publicly. The
> load-bearing citations are the vendor blogs, CVEs, and ACL/NeurIPS/ICML/USENIX
> papers. A few arXiv identifiers surfaced by search could not be individually
> opened to confirm — treat bare arXiv IDs as leads, not verified references,
> until link-checked.

| Technique (first seen) | Mechanism | Why it bypasses defenses | Layer | Corpus id | Primary source |
|---|---|---|---|---|---|
| Many-shot jailbreaking (Apr 2024, Anthropic) | Flood long context with 128–256 faux compliant Q/A before the real ask | In-context learning overrides safety training; scales with context window | input+alignment | NM1, NM2 | anthropic.com/research/many-shot-jailbreaking; NeurIPS 2024 |
| Crescendo (Apr 2024, Microsoft) | Gradual multi-turn escalation citing the model's own prior replies | No single turn looks harmful | alignment | CR1 | arxiv 2404.01833; USENIX Sec '25 |
| Skeleton Key (Jun 2024, Microsoft) | "Augment, don't refuse" — agree to a warning-label rule, then answer | Reframes refusal as behavior to update | alignment | SK1 | microsoft.com (Skeleton Key, 2024-06-26) |
| Policy Puppetry (Apr 2025, HiddenLayer) | Wrap ask in XML/JSON/INI mimicking a system "policy" + roleplay | Structured config treated as trusted system directive | input+alignment | PP1, PP2 | securityweek.com (policy-puppetry) |
| Deceptive Delight (Oct 2024, Unit 42) | Link 2 benign topics + 1 harmful in one narrative, then deepen the harmful | Harm camouflaged; distraction defeats intent detection | alignment | DD1 | unit42.paloaltonetworks.com |
| Bad Likert Judge (Dec 2024, Unit 42) | Make model a harmfulness "judge," then ask for a score-5 example | Turns the model's eval capability into the elicitation vector | alignment | BLJ1 | unit42.paloaltonetworks.com |
| Unicode-tag / ASCII smuggling (2024, Embrace The Red) | Hide instructions in invisible U+E00xx tag chars | Invisible to human review; still tokenized | input, agent/rag | SM1, SM2 | embracethered.com |
| ArtPrompt / ASCII-art masking (Feb 2024, ACL) | Render trigger word as ASCII art | Safety is semantic-only; misses visual encoding | input | ART1 | arxiv 2402.11753 |
| Low-resource language (2023→) | Translate the request into an under-covered language | Alignment coverage thin outside high-resource languages | input+alignment | OB1 | arxiv 2310.02446 |
| Encoding obfuscation (Base64/ROT13/Morse/hex/leet) | Encode request; model decodes and complies | Long-tail encodings evade classifiers | input | OB2 | arxiv 2411.01084 |
| FlipAttack (ICML 2025) | Reverse/flip chars; model unflips and answers | 1-query; keyword guards see scrambled text | input | OB3 | github.com/yueliu1999/FlipAttack; arxiv 2410.02832 |
| TokenBreak (Jun 2025, HiddenLayer/Pillar) | Stray chars break the *classifier's* tokenizer | Moderation mislabels safe; target still infers meaning | input | TB1 | pillar.security |
| Best-of-N (Dec 2024, Anthropic et al.) | Resubmit with random augmentations until one slips | Black-box search over stochastic decoding | input | BON1 | arxiv 2412.03556 |
| Refusal suppression / prefix injection (2024) | Ban refusal tokens; force "Sure, here is" prefix | Removes tokens a refusal begins with | alignment | RS1 | arxiv 2404.16369 |
| Immersive World (Mar 2025, Cato) | Fictional world where the harm is normal; stay in character | Roleplay frame detaches output from policy | alignment | IW1 | securityweek.com |
| Echo Chamber (Jun 2025, NeuralTrust) | Multi-turn context poisoning via indirect references | Exploits cross-turn reference resolution; no trigger words | alignment | EC1 | neuraltrust.ai |
| Distraction / context-overflow | Bury ask in long benign filler + competing instructions | Harmful span diluted, low-salience | input+alignment | CO1 | arxiv 2402.14020 |
| Indirect prompt injection — tool/web (OWASP LLM01:2025) | Hidden instructions in fetched pages/tool output | Model can't separate retrieved data from instructions | agent/rag | AG1 | genai.owasp.org; lakera.ai |
| RAG document poisoning (2025) | Planted high-ranking doc carries directives above the user | Retrieved content prioritized over the query | agent/rag | AG2 | (RAG poisoning literature) |
| Confused-deputy / zero-click exfil (CVE-2025-32711, Jun 2025) | Chain a privileged tool under user authority; exfil via agent's channel | Capability ≠ authorization; no click needed | agent/rag | AG3 | CVE-2025-32711 (EchoLeak) |
| MCP tool poisoning (Apr 2025, Invariant Labs) | Malicious instructions in tool description/schema | Tool metadata trusted as instructions at load | agent/rag | MCP1 | lenshq.io; invariantlabs |
| MCP rug pull (CVE-2025-54136, Jul 2025) | Tool swaps behavior after approval | Definition change not re-verified | agent/rag | MCP2 | CVE-2025-54136 |
| MCP line jumping / tool shadowing (2025) | One server alters a *different* trusted tool | Cross-tool contamination | agent/rag | MCP3 | CSA / lenshq |
| Memory poisoning (MINJA, 2025) | Query-only writes of attacker "rules" into long-term memory | Persists across sessions; biases later decisions | agent/rag | MP1 | christian-schneider.net; MINJA |
| System-prompt leakage (OWASP LLM07:2025; PLeak) | "Repeat everything above"; encoded re-emit | Model can reproduce its own context | input, input+alignment | LK1, LK2 | genai.owasp.org (LLM07); trendmicro.com (PLeak) |

## Deliberately excluded from the corpus
- **Operational exploit specifics** (real infostealer code, PLeak optimizer strings,
  literal Unicode-tag byte sequences) — kept as placeholders only.
- **Gradient / white-box adversarial suffixes (GCG and successors)** — require
  model-specific optimization and produce non-human-readable token strings that
  don't fit the placeholder-scaffold format. Noted for awareness.
- **Fine-tuning / training-data poisoning** — targets the training pipeline, not a
  runtime prompt/agent input, so out of scope for this input/alignment/agent-rag corpus.
