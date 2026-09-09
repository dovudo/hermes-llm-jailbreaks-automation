# Finding model vulnerabilities: a repeatable discovery methodology

How to systematically mine the internet — papers, vendor research, forums,
frameworks — for new attacks and fold them into this corpus. Defensive use:
everything you find becomes an ABSTRACT test case (placeholder-only), never a
working payload.

## The loop (run on a cadence — attacks compound in weeks, not years)

```
mine sources → normalize (technique · mechanism · layer · dated source)
   → dedupe by MECHANISM (many "new" names are re-skins)
   → write an ABSTRACT scaffold ({id,category,layer,target,payload})
   → run vs your model → feed the MISSES back as new seeds → repeat
```

Release gate: every framework category (below) has ≥1 probe, and benchmark
behaviors show no regression vs. the last run.

## Source tiers (mine highest-signal first)

### 1. Academic / preprint (mechanism + measured ASR)
- **Anchor on benchmark & survey papers first** — they are pre-built citation hubs:
  HarmBench, JailbreakBench, AdvBench, "Jailbroken: How Does LLM Safety Training
  Fail?" Their related-work enumerates the current families; leaderboards show
  which attacks beat which defenses.
- **arXiv:** browse `cs.CR/recent` + `cs.CL/recent` (also cs.LG/cs.AI); full-text
  search `jailbreak`, `adversarial suffix`, `prompt injection`, `refusal`,
  `red team`. Watch `vN` revisions (camera-ready adds stronger results). Set
  arXiv + Google Scholar alerts on those terms and on prolific authors.
- **Citation-chase both ways:** from a seed (GCG, PAIR, "Jailbroken") walk
  backward through refs and forward via Semantic Scholar / Connected Papers.
- **Venue sweeps:** ACL/EMNLP/NAACL, NeurIPS/ICML/ICLR (+ OpenReview reviews
  reveal robustness gaps), USENIX Security, IEEE S&P, CCS, NDSS, and co-located
  workshops (AISec, SaTML, TrustNLP, SoLaR) where attacks appear first.

### 2. Vendor / lab research (named techniques, real disclosures)
- **Offensive-research labs (weekly, most have RSS):** HiddenLayer, Palo Alto
  Unit 42, NeuralTrust, Cato CTRL, Pillar, Zenity, Noma, Radware, Aim Labs,
  Lakera, Robust Intelligence / Cisco AI Defense, Trend Micro / ZDI, Protect AI
  (+ huntr.com), Invariant Labs, Embrace The Red (Rehberger), Simon Willison
  (`prompt-injection` / `exfiltration-attacks` tags).
- **Lab safety teams:** Anthropic, OpenAI, Microsoft MSRC + AI Red Team (+ PyRIT),
  Google Project Zero / DeepMind, NVIDIA AI Red Team (+ garak changelog).
- **Always follow news rewrites (Hacker News, SecurityWeek, Dark Reading) back to
  the vendor post / paper / CVE** — cite the primary, never the rewrite.

### 3. Community / in-the-wild (emerging shapes, fast + noisy)
- Practitioner blogs (highest signal, dated): Embrace The Red, Simon Willison,
  NVIDIA/Greshake writeups.
- Structured collectives: GitHub jailbreak collections and awesome-lists,
  HackAPrompt dataset — read the **taxonomy/README**, not raw payload files.
- Forums: r/ChatGPTJailbreak, r/LocalLLaMA, X (@elder_plinius, @simonw,
  @goodside, @wunderwuzzi23), Discord — sort by date; heavy dedup; verify a
  forum claim against a reproducible writeup before trusting it.
- Disclosures: HackerOne/Bugcrowd public reports, huntr.com.
- **Ethics:** extract the *shape* of a pattern, map to a placeholder scaffold;
  never clone a working prompt or ship a copy-pasteable exploit.

### 4. Disclosure / CVE trackers (productized LLM & agent vulns)
- NVD/MITRE keyword watches: `LLM`, `prompt injection`, `Copilot`, `agent`,
  `MCP`, `RAG`, plus product names (e.g. EchoLeak = CVE-2025-32711, Cursor
  rug-pull = CVE-2025-54136). GitHub Security Advisories for AI SDKs / MCP servers.

### 5. Conference talk calendars (mine slides/recordings 2–6 weeks after)
- DEF CON AI Village, Black Hat AI/ML track, USENIX Security, IEEE S&P, SANS AI.

## Frameworks as a coverage checklist (so no whole category is missed)

Treat these as **orthogonal axes** and union them — technique-only tagging hides
gaps (resource exhaustion, poisoning, misinformation, repudiation have no
"technique" flavor and get missed):

- **OWASP Top 10 for LLM Apps (2025)** — application-risk axis (LLM01…LLM10).
- **OWASP Top 10 for Agentic Applications (Dec 2025, ASI01–ASI10)** and the
  earlier **Agentic Threats & Mitigations (T1–T15)** — autonomy/tool/multi-agent.
- **MITRE ATLAS** — attacker-lifecycle axis (recon → access → execution →
  exfiltration → impact); check you test *stages*, not just techniques.
- **NIST AI 100-2e2025** — attacker-goal axis (integrity / availability / privacy
  / misuse).
- **Llama Guard / MLCommons hazard taxonomy (S1–S14) + AVID** — harm-content axis.

Build a matrix: framework category × your corpus IDs. A category with zero mapped
probes is a whole-category gap → add a scaffold before release.

## Turn open tooling into category generators (not payload sources)

Enumerate each tool's probe *families* and map each to a framework category; copy
the taxonomy, never the payloads: **garak** (encoding, dan, leakreplay,
packagehallucination…), **PyRIT** (crescendo/PAIR/TAP orchestrators + converters),
**promptfoo** red-team (plugins + strategies), **HarmBench / JailbreakBench**
(behavior classes for regression), **giskard**, **Meta Purple Llama / CyberSecEval**.

## Normalizing a finding into this repo

```json
{"id":"<PREFIX><n>","category":"<technique_snake_case>",
 "layer":"input|alignment|input+alignment|agent/rag","target":"generic|tool|secret",
 "payload":"<abstract scaffold: placeholders only>"}
```

Dedupe against existing IDs **by mechanism, not by name**. Corpus id prefixes:
`A–F` seed set · `AC` academic · `VN` vendor · `CM` community · `TA` agentic ·
`FW` framework-coverage · `EN` encoding · `MM` multimodal · plus the earlier
`NM/CR/SK/PP/DD/BLJ/SM/ART/OB/TB/BON/RS/IW/EC/CO/AG/MCP/MP/LK` set.
See `TECHNIQUES_CATALOG.md` for the technique→source map.
