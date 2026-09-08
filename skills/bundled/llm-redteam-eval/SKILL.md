---
name: llm-redteam-eval
description: 'Eval safety of YOUR model: static ASR corpus + injection.'
version: 1.1.0
author: hermes
license: proprietary
metadata:
  related_skills: [hermes-redteam-suite]
  tags: redteam, llm-security, prompt-injection, jailbreak, ASR, deprecated
---

# LLM Red-Team Eval → перенесён в `hermes-redteam-suite`

> **DEPRECATION NOTICE:** этот скилл — redirect-заглушка. Вся функциональность
> (статический corpus-скан) консолидирована в единый скилл **`hermes-redteam-suite`**
> в `/opt/projects/redteam/` (подкоманда `rt static`). Движок `harness.py` вендорен
> туда. Оригинал кода по-прежнему лежит в `/opt/projects/hermes-redteam/harness.py`.

## What this was
Статический red-team харнесс: прогнать корпус prompt-injection атак (25 кейсов × 8
категорий) против СВОЕГО OpenAI-совместимого эндпоинта и измерить ASR по (category,
layer). DEFENSIVE — только модели, которыми владеешь/имеешь право тестировать.

## Where it moved
- Команда: `cd /opt/projects/redteam && bash run.sh static`
- Единый provider-профиль: `redteam/provider.yaml`
- Единый отчёт: `bash run.sh report`
- См. полный runbook в `skill_view(name='hermes-redteam-suite')`.

## Pitfalls (перенесены)
- Heuristic judge завышает ASR — всегда judge-LLM (профиль ставит gpt-5.6-luna).
- GCG требует вайт-бокс/прокси; в black-box основной вектор — TAP, дешёвый baseline — PAIR.
