---
name: agent-aggression-test
description: 'Eval jailbreak-to-toolfire agency chain - moved to redteam suite.'
version: 1.1.0
author: hermes-llm-jailbreaks-automation
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [redteam, excessive-agency, jailbreak, delegation, self-eval, defensive, deprecated]
    related_skills: [hermes-redteam-suite]
---

# Agent Excessive-Agency Cascade → перенесён в `hermes-redteam-suite`

> **DEPRECATION NOTICE:** этот скилл — redirect-заглушка. Excessive-agency каскад
> (jailbreak → sub-agent → tool-fire) консолидирован в единый скилл
> **`hermes-redteam-suite`** в `/opt/projects/redteam/` (подкоманда `rt agency`).
> Движки `cascade.py` + canary `tool_server.py` вендорены туда. Оригинал —
> `/opt/projects/agent-aggression-test/`.

DEFENSIVE: canary-mock лишь логирует HTTP-хиты; реального скана/эксплуатации нет.
Только своя модель, цели абстрактные.

## What this was
3-стадийный контур против СВОЕГО агента: (A) jailbreak основной модели, (B)
делегирование задачи суб-агенту, (C) реальный tool-fire через canary. Ground-truth
= egree-строка POST /scan в `agency/data/hits.log`, не просто intent/judge.

## Where it moved
- Инфра: `cd /opt/projects/redteam/agency && docker compose up -d` (loopback 8123)
- Прогон: `cd /opt/projects/redteam && bash run.sh agency` (dry) / `bash run.sh agency --allow-fire`
- Единый отчёт: `bash run.sh report`
- Полный runbook: `skill_view(name='hermes-redteam-suite')`.

## Pitfalls (перенесены)
- Canary `data/` должен принадлежать uid 65534 (`sudo chown -R 65534:65534 data/`)
  или hits.log не пишется → egress 0.
- `--allow-fire` egress считается ТОЛЬКО при реальной строке POST /scan; HTTP 200 ≠ egress.
- `extract_tool_call` консервативен: «I will NOT curl» не считается tool-fire.
