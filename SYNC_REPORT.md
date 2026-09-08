# SYNC_REPORT

Synchronization of origin-host work into **one** package:
`/opt/projects/hermes-security-lab/` (this tree).

Built for handoff to another agent running the same master prompt.
Not a live deploy onto a second server.

## PRESERVED

- Unified red-team suite logic: `rt.py`, `run.sh`, static/adaptive/agency engines,
  `redteam/security.py`, `redteam/report.py`, `redteam/prompt_pack.py`,
  `corpus.json`, `objectives.json`, `agency_objectives.json`, canary Dockerfile.
- Jailbreak research documents:
  - `/opt/projects/llm_safety_deepseek_research.md`
  - `/opt/projects/prompt_injection_test_corpus.md`
  - `/opt/projects/hermes-redteam/oss_redteam_research.md`
- Skill **hermes-redteam-suite** v2.1.0 (paths rewritten to `${LAB_ROOT}`).
- Redirect stubs: llm-redteam-eval, hermes-adaptive-redteam, agent-aggression-test.
- Methodology skill llm-defensive-redteam.
- web-pentest, ai-pentest-agents, backend-security-audit, oss-forensics,
  sherlock, domain-intel, osint-investigation.
- Origin originals **untouched**:
  `/opt/projects/redteam/`, `/opt/projects/hermes-redteam/`,
  `/opt/projects/agent-aggression-test/`.
- Nous/proxy CLI knowledge from Hermes docs (`hermes setup --portal`,
  `hermes proxy` on 127.0.0.1:8645).
- Adaptive sweep **ASR table** (DeepSeek 25% / Qwen 12.5% / Hunyuan 50%).

## UPDATED

- `projects/redteam/redteam/provider.yaml` — secrets/model ids replaced with
  `${…}` / `REDTEAM_API_KEY`. Origin values kept as comments only.
- Bundled `hermes-redteam-suite` paths: `/opt/projects/redteam` → `${LAB_ROOT}/projects/redteam`.
- Jailbreak corpus re-homed under `research/jailbreaks/` with required filenames
  (README, TAXONOMY, TECHNIQUES, TEST_CASES, MUTATION_STRATEGIES, EVALUATION, SOURCES).
- Explicit mechanical allowlist: `lib/scope_check.py` + empty `scope.example.yaml`.
- Role-separated model/provider templates (attacker ≠ target).

## MERGED

- Three LLM red-team skills → one suite (already done on origin 2026-09-07; package keeps stubs).
- Human markdown corpus + JSON corpus → research + runtime copies (not duplicated as a third format).
- Agency HERMES_PROMPT.md ideas → `prompts/JAILBREAK_TESTING.md` + OPERATIONS (not a second cascade repo).

## REMOVED (from the package only; origin still has them)

- Live adaptive **attack transcripts** (`sweep_report.md` ~96k chars) — dual-use.
  ASR summary kept. Full file remains on origin.
- operational-jailbreak tooling skill payloads — documented in inventory, not bundled.
- weight-ablation tooling — documented, not bundled.
- Runtime `out/` JSON, canary `hits.log`, `__pycache__`.
- Origin Hermes `config.yaml` / `auth.json` / `.env` — must not migrate.

## MISSING (do not invent)

- **AI Recon** as a local repo/skill/binary: not found in sessions, `/opt/projects`,
  or `~/.hermes/skills`. Integration is a stub (`projects/ai-recon/README.md`).
- Written RoE / customer authorization files (none in origin lab dirs).
- A previous `hermes-security-lab` tree (this is the first).
- Portable copy of origin Claude-max-proxy (not required; lab should use Nous).
- Garak/PyRIT/HarmBench installs (documented, not vendored).
- Standalone frontend-security skill (none was found; web-pentest + stock UI
  tooling are the nearest coverage).
- Session transcripts of all historical jailbreak chats (compaction; recovered
  via artifacts above rather than full logs).

## CONFLICTS

1. **Origin live Hermes ≠ intended lab topology.** Origin chat model is
   `custom:claude-max-proxy` with OpenRouter fallback. The master prompt wants
   Nous Portal + local subscription proxy. Package follows the **prompt**, not
   the origin `config.yaml`.
2. **operational-jailbreak tooling vs defensive suite.** operational-jailbreak tooling is for bypassing arbitrary API models.
   Lab default is own-model eval via hermes-redteam-suite. Both exist on origin;
   only the latter is bundled.
3. **Hardcoded OpenRouter in engines.** Vendored `harness.py` / `cascade.py`
   still default `--*-key-env REDTEAM_API_KEY`. Override via provider.yaml /
   env. Not rewritten in every argparse default to avoid drifting from origin
   engines; profile is the source of truth.
4. **llm-defensive-redteam** still points at `/opt/projects/hermes-redteam/` —
   origin path. Runtime engines in the package are `projects/redteam/`.

## SECURITY CONCERNS

- Empty allowlist still requires operators to fill it; a future agent might
  skip `scope_check.py`. Bootstrap forbids that.
- Agency `--allow-fire` talks to loopback canary only — still a tool-fire path.
- Bundled `web-pentest` / `ai-pentest-agents` / `sherlock` can hit the network
  if the receiving agent ignores scope.
- Aux compression in Hermes can leak evidence from chat — reporting prompt
  says files + last-6 redaction.
- Wildcard scope is rejected by `scope_check.py`.

## MIGRATION RISKS

- Fresh Hermes may lack Docker → agency canary skippable; static/adaptive still work.
- PyYAML required for `rt.py` and YAML scope.
- The receiving agent does not need `${LAB_ROOT}` pre-set; it must locate the
  tree and substitute the path when installing the skill / running commands.
- Provider.yaml placeholders (`${JUDGE_MODEL}`) are **not** auto-expanded by
  Python yaml — operator/agent must edit real strings before a live run.
- UID 65534 on `agency/data` needed for canary writes (origin lesson).
- Transfer tarball must exclude origin `.env` if someone packs the wrong parent.

## Handoff note

If the operator later drops extra files (“докину полезное”), merge into this
same directory. Do not fork `hermes-security-lab-2/`.


---

# APPENDIX A — Reconciliation on the RECEIVING host (2026-09-08)

This appendix was added by the second pass (the agent that received the
tarball). It records how the origin-host package maps onto THIS machine's
actual state and what was merged in. Prior sections above are the origin
agent's findings and are kept verbatim.

## Host differences

| Aspect | Origin agent's host | THIS receiving host | Resolution |
|---|---|---|---|
| `/opt/projects/redteam` | present (vendored from here) | **absent** | suite lives *in this package* under `projects/redteam/`; verified runnable locally |
| `/opt/projects/hermes-redteam` | present | **absent** | only referenced in SKILL_INVENTORY; no engine dependency at runtime |
| `/opt/projects/agent-aggression-test` | present | **absent** | same — vendored under `projects/redteam/agency/` |
| Live chat model | `custom:claude-max-proxy` + OpenRouter fallback | `your provider` (DeepSeek-V4-Flash / Kimi-K3) | **package follows the master prompt, not either host's live chat** |
| Hermes install | that host's instance | this host has **working Hermes v0.20.5**, profile `llm-redteam` | existing profile kept; package does NOT overwrite live config |
| LLM runtime stack | **did not exist on origin lab** | **this host HAS one** (`/opt/projects/llm-redteam`: Jailbreaker UI + promptfoo + observer) | **imported** as `projects/llm-redteam-runtime/` — verified 10/10 refuse on 10-attack eval |
| AI Recon | MISSING on origin | public `pikpikcu/airecon` identified | `projects/ai-recon/README.md` updated with integration + does-it-cover analysis |

## What this host VERIFIED after unpacking

- `bash deployment/verify.sh` → **exit 0** (py_compile all engines, scope deny
  8.8.8.8 + localhost-by-default, secret scan clean).
- `cd projects/redteam && python3 rt.py prompt --text 'integration self-test'
  --dry-pack` → produced valid run dir with `[AUTHORIZED TEST]`-tagged
  objectives (8 static / 5 adaptive / 3 agency). Run deleted after check.
- No leaked `sk-…`, `cpk_…`, or `OPENROUTER*_API_KEY=` values anywhere in the tree.
- `pyyaml` present on the receiving host (rt.py + scope_check dependency).

## ADDED by this host

| Path | What / status |
|---|---|
| `projects/llm-redteam-runtime/` | NEW project dir imported from this host's verified stack — **Jailbreaker compose, promptfoo eval config, `observe.sh`, `start.sh`**. Complements `projects/redteam/` (interactive UI + promptfoo plugin corpus + JSONL triage). |
| `projects/ai-recon/README.md` | REPLACED stub with researched `pikpikcu/airecon` integration notes. Private instance still unconfirmed (operator confirm). |

## NEW conflict found on THIS host

1. **Two LLM-eval paths now coexist.** `projects/redteam/` (unified CLI,
   attacker != target, dry-pack) **vs** `projects/llm-redteam-runtime/`
   (Jailbreaker UI + promptfoo). They are *complementary*, not duplicates —
   but the receiving operator should pick ONE default to avoid drift.
   **Recommendation:** keep `projects/redteam/` as canonical for role-separated
   CI-style evals; use the runtime for interactive UI / promptfoo exploration.

2. **`hermes-redteam-suite` skill vs `llm-redteam` Hermes profile.** The
   bundled skill expects `${LAB_ROOT}/projects/redteam/`; this host's live
   profile `llm-redteam` points at `your provider`. They are different roles
   (skill = eval logic; profile = chat routing). Not a real conflict — but do
   NOT copy profile's `config.yaml` into the package; it carries provider
   secrets. Package keeps placeholders only.

## DECISIONS (this host)

- Base = origin agent's package **kept wholesale**; no rewrite of his research.
- My additions go **alongside**, marked with this appendix.
- Nothing on this host's live `~/.hermes` config was shipped into the package;
  the package remains origin-agnostic for reusable transfer.
- `deployment/install.sh` **not run** during this reconciliation (per its own
  first-run semantics); verify.sh green is the on-host gate.
