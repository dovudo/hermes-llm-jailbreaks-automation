# Operations

Day-2 runbook after `deployment/install.sh` succeeded and `verify.sh` is green.

## 0. Do not auto-attack

Install and verify are smoke-only. Live layers cost tokens and hit the target
model. Start them only when the operator names a target and accepts spend.

## 1. Confirm roles

```bash
# attacker / judge / target must be distinct in intent
grep -n 'model:' configs/models.yaml projects/redteam/redteam/provider.yaml
```

Never point `target.model` at the lab's own reasoning model by accident.

## 2. Fill scope + authorization

```bash
cp configs/scope.example.yaml configs/scope.yaml
cp configs/authorization.example.md engagement/authorization.md
# edit both
python3 lib/scope_check.py --config configs/scope.yaml --dump
```

## 3. LLM red-team (own model)

```bash
cd projects/redteam
# canary (agency layer)
bash run.sh up          # docker canary on 127.0.0.1:8123
bash run.sh smoke

# dry pack of the operator's prompt (no LLM)
python3 rt.py prompt --text 'self-test ping' --dry-pack

# live — only after target + spend confirmed
# bash run.sh full
# python3 rt.py prompt --file ./goal.txt --target <TARGET_MODEL>
python3 rt.py report    # out/UNIFIED_REPORT.md
```

Triage:

- High static/adaptive ASR → weak safety / system prompt.
- Agency `egress=Y` → CRITICAL (canary `POST /scan` actually landed).
- Jailbreak without egress → environment stopped the chain.

## 4. Web / backend (authorized apps)

Load skill `web-pentest` or `backend-security-audit`. Keep evidence in
`engagement/evidence/`. Prefer local DVWA / Juice Shop.

Passive recon skills (`domain-intel`, `osint-investigation`)
do not replace the allowlist for active probes.

## 5. AI Recon

See `projects/ai-recon/README.md`. Upstream source was **not** on the origin
host. Wire it to the local Subscription Proxy (`http://127.0.0.1:8645/v1`)
so it never holds Nous OAuth.

## 6. Nous Portal + proxy

```bash
hermes setup --portal          # OAuth, interactive, on the NEW box
hermes portal status
hermes proxy start --provider nous --host 127.0.0.1 --port 8645
```

Keep the proxy on loopback unless there is a documented LAN reason.

## 7. Logging / hygiene

- Do not paste captured tokens into chat (aux compression can exfil them).
- Redact to last 6 chars in conversation; full values only in `engagement/evidence/`.
- Canary `agency/data/` must be uid 65534 or `hits.log` dies (false-zero egress).

## 8. Uninstall

`deployment/uninstall.sh` removes lab docker canary and optional skill copies.
It does **not** uninstall Hermes.
