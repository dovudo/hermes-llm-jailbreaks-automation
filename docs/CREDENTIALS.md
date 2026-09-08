# Credential setup (interactive, on the NEW server)

Do **not** copy `~/.hermes/.env`, `auth.json`, SSH keys, or cookies from the
origin host. This package contains none of them.

## 1. Nous Portal (preferred)

```bash
hermes setup --portal
hermes portal status
```

OAuth lands in `~/.hermes/auth.json` (mode 600). Never put it in the lab git tree.

## 2. Subscription proxy (for AI Recon / Garak / any OpenAI client)

```bash
hermes proxy start --provider nous --host 127.0.0.1 --port 8645
hermes proxy status
```

Clients:

```
OPENAI_BASE_URL=http://127.0.0.1:8645/v1
OPENAI_API_KEY=not-used-but-required
```

## 3. Optional OpenRouter

```bash
# ~/.hermes/.env
OPENROUTER_API_KEY=...
# origin also had REDTEAM_API_KEY for a second account — recreate if needed
```

Only if Nous is insufficient. Keep it optional.

## 4. Red-team engines

`projects/redteam/redteam/provider.yaml` reads env names, not key values.

Suggested:

```bash
export REDTEAM_API_KEY="${OPENROUTER_API_KEY:-dummy}"
export REDTEAM_ENDPOINT="http://127.0.0.1:8645/v1/chat/completions"
export TARGET_MODEL="..."
export ATTACKER_MODEL="..."
export JUDGE_MODEL="..."
```

Or point `REDTEAM_ENDPOINT` at a local vLLM for the **target only**.

## 5. Never in the package / never in chat

API keys, OAuth refresh tokens, cookies, session tokens, cloud creds, PATs,
SSH private keys.

If `deployment/verify.sh` reports a secret-scan hit, stop transfer and purge.
