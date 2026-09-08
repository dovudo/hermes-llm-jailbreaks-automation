# Operator cheat-sheet

## First hour on a new box

1. Unpack this package. Read `README.md`, `SECURITY_MODEL.md`, `BOOTSTRAP_PROMPT.md`.
2. `hermes setup --portal` if using Nous subscription (interactive OAuth).
3. Fill `docs/CREDENTIALS.md` env vars in `~/.hermes/.env` — never into git.
4. Copy `configs/*.example.*` → live files. Keep attacker ≠ target.
5. `deployment/inspect.sh` then `deployment/install.sh` then `deployment/verify.sh`.
6. Do not run `bash run.sh full` yet.

## Role map

| Job | Typical provider |
|---|---|
| Lab reasoning (Hermes itself) | Nous Portal (subscription) |
| Attacker / judge | Strong model via Nous proxy or optional OpenRouter |
| Target | Named SUT — local vLLM, OpenAI-compat, or a model ID you are allowed to eval |
| Cheap aux | Flash / Haiku-class |
| Vision | Vision-capable aux |
| AI Recon | OpenAI-compat → `http://127.0.0.1:8645/v1` (subscription proxy) |

## Stop conditions

- Scope miss
- Redirect off-scope
- Production mentioned without paper
- Script you have not read
- Request to jailbreak a third-party consumer product
