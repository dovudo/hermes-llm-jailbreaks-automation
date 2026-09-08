# Nous Portal / Hermes subscription

Source: Hermes docs (`hermes portal`, `hermes setup --portal`, `hermes proxy`),
cached from hermes-agent.nousresearch.com on the origin host.

## Intended lab path

```
Nous Portal subscription
    → Hermes (lab agent)
    → hermes proxy (127.0.0.1:8645)
    → OpenAI-compatible local endpoint
    → AI Recon / Garak / other clients
```

Proxy stays **loopback-only** unless the operator documents a LAN reason.
`--host 0.0.0.0` would expose the subscription to the network — do not.

## Commands (run on the NEW box, interactively)

| Command | Why |
|---|---|
| `hermes setup --portal` | OAuth, set Nous as inference, optional Tool Gateway |
| `hermes auth add nous` | If Hermes already installed |
| `hermes portal status` | Auth + Tool Gateway routing |
| `hermes proxy start --provider nous --host 127.0.0.1 --port 8645` | Local OpenAI-compat |
| `hermes proxy status` | Creds present / OAuth valid |
| `hermes proxy providers` | Upstream list |

External apps send any bearer token; the proxy attaches real OAuth upstream.
That is why AI Recon should talk to the proxy, not to Portal directly.

## Coexistence

Nous, optional OpenRouter, local vLLM, and other OpenAI-compat providers
can coexist. Assign them to **roles** (`configs/models.example.yaml`), not
as a single global model.

Origin Hermes was **not** on Nous as the live chat model (it used a custom
Claude proxy + OpenRouter fallback). The lab should not copy that topology
unless the operator wants it. The purchased Portal plan is the lab default.
