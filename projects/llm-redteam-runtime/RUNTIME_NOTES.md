# LLM RED-TEAM СТЕНД — локальная среда для атак на СВОЮ модель

Готовый контур для систематического тестирования твоей LLM устойчивостью к
jailbreak и prompt-injection. **Все атаки нацелены на твою собственную модель**,
не на чужие сервисы. Анализ результатов ведёт отдельный серверный модуль (отдельно
обученная LLM) — здесь только прогон атак + сырой вывод.

---

## Что уже собрано и ПРОВЕРЕНО локально ✓

| Контур | Статус | Как запустить |
|--------|--------|---------------|
| **Hermes-профиль `llm-redteam`** | ✅ smoke `REDTEAM_OK` | `llm-redteam chat` или `hermes -p llm-redteam chat -q "..."` |
| **Jailbreaker (SpecterOps) UI** | ✅ 3 контейнера healthy | `http://localhost:3000` (API :8000, DB :5432) |
| **Promptfoo eval — ручной корпус jailbreak** | ✅ 10/10 атак прогнано, 100% refuse | `cd promptfoo/jailbreak-eval && ../node_modules/.bin/promptfoo eval -o ../../results/out.jsonl` |
| **Наблюдатель** | ✅ `observe.sh` | `bash observe.sh [results/*.jsonl]` |

**Верифицировано:** на текущем провайдере (`your provider` → DeepSeek-V4-Flash)
модель устояла в 10/10 jailbreak-атак (отказ на DAN-режим, root-эскалацию, взлом
чужой БД, system-prompt leak, base64-smuggling, эксплоит CVE).

---

## Быстрый старт для «хакера» (оператора стенда)

```bash
# 1. Стенд: статус всего
bash /opt/projects/llm-redteam/start.sh

# 2. Прогнать базовый jailbreak-корпус против модели
cd /opt/projects/llm-redteam/promptfoo/jailbreak-eval
../node_modules/.bin/promptfoo eval -o /opt/projects/llm-redteam/results/run1.jsonl

# 3. Посмотреть сводку (наблюдатель)
bash /opt/projects/llm-redteam/observe.sh /opt/projects/llm-redteam/results/run1.jsonl

# 4. Отдельный модуль-аналитик
#    → подать run1.jsonl на свой аналитический модуль для глубокого разбора.
```

## Провайдер/модель

Временно — тот же, что и текущий Hermes: `your provider`
(`${REDTEAM_ENDPOINT}`, модель `deepseek-ai/DeepSeek-V4-Flash-0731-TEE`).
Ключ берётся из `REDTEAM_API_KEY`. Когда понадобится своя модель — поменяйте
`providers[].id` и модельный ID в `promptfoo/jailbreak-eval/promptfooconfig.yaml`.
Позже подтянете OpenRouter → своя модель — та же точка правки.

## Jailbreaker (UI-платформа)

- Панель: http://localhost:3000
- Создайте vault (passphrase) → профили **target / attacker / judge**
- Нацельте TARGET на свою модель (Ollama/OpenRouter), запустите технику или полный eval
- Результаты сохраняются в платформе, scoring 1–10 (7+ = успешная атака)

## Структура

```
/opt/projects/llm-redteam/
├── start.sh                  # статус всего стенда
├── observe.sh                # наблюдатель (сводка по результатам)
├── README.md                 # этот файл
├── jailbreaker/              # SpecterOps Jailbreaker-CE (docker compose up)
├── promptfoo/
│   ├── jailbreak-eval/promptfooconfig.yaml    # ручной корпус jailbreak-атак
│   ├── redteam-provider/promptfooconfig.yaml    # promptfoo redteam (cloud-гейт)
│   └── redteam-ollama/promptfooconfig.yaml    # конфиг под свою Ollama
└── results/                  # JSONL-вывод прогонов (для модуля-аналитика)
```

## Scope

**Только собственная модель.** Неавторизованное отсекается. Стенд не предназначен
и не настроен для атак на чужие публичные LLM-сервисы. Ключи/токены в конфигах не
хранятся открыто (ключ из REDTEAM_API_KEY/.env).