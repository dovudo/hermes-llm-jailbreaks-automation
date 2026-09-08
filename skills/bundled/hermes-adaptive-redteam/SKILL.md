---
name: hermes-adaptive-redteam
description: 'Adaptive multi-turn jailbreak eval - moved to redteam suite.'
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [llm-safety, red-team, jailbreak, adaptive, asr, defensive, deprecated]
    related_skills: [hermes-redteam-suite]
---

# Hermes Adaptive Red-Team → перенесён в `hermes-redteam-suite`

> **DEPRECATION NOTICE:** этот скилл — redirect-заглушка. Adaptive multi-turn
> jailbreak консолидирован в единый скилл **`hermes-redteam-suite`**
> в `/opt/projects/redteam/` (подкоманда `rt adaptive`). Движок `adaptive_attack.py`
> вендорен туда. Оригинал — `/opt/projects/hermes-redteam/adaptive_attack.py`.

DEFENSIVE: тестировать ТОЛЬКО свою/авторизованную модель. Цели абстрактные.

## What this was
Adaptive multi-turn jailbreak-campaign против СВОЕЙ модели: attacker iteratively
переписывает атаку по feedback judge-модели, пока target не выполнит (абстрактную)
цель. Меряет Adaptive ASR по (category, layer). Статик-ASR ≈ 0 ≠ безопасно —
adaptive role-persona пробивал qwen/deepseek/hunyuan при статик 0%.

## Where it moved
- Команда: `cd /opt/projects/redteam && bash run.sh adaptive`
- Единый provider-профиль: `redteam/provider.yaml` (attacker/judge/target модели, key-env)
- Единый отчёт: `bash run.sh report`
- Полный runbook: `skill_view(name='hermes-redteam-suite')`.

## Pitfalls (перенесены)
- `temperature` deprecated на некоторых anthropic-прокси → HTTP 400 (тихий отказ attacker,
  ASR ложно 0); `RT_NO_TEMP=1` если режут.
- Суб-агент ≠ модель: delegate_task не гарантирует модель аттакера — для конкретной
  (DeepSeek/Qwen) прямой API-вызов через профиль.
- Timeout mid-run → отчёт не пишется; проверяй `[ -f out.json ]`.
