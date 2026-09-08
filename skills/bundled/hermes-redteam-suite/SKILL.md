---
name: hermes-redteam-suite
description: 'Pentest ANY prompt vs YOUR model. Each case runs in a resumable session (chat.py, keyed by SESSION_ID) that the researcher can re-enter later to interrogate the target model. Verbatim, no scoring, minimal state.'
version: 4.1.0
author: hermes-llm-jailbreaks-automation
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [llm-safety, red-team, jailbreak, adaptive, defensive, resumable-session, verbatim]
    related_skills: []
---

# Hermes Red-Team Suite (v4.1 — возобновляемые сессии, дословно, без логов)

Тестировщик вставляет **любой** промпт → Hermes прогоняет его через target-модель
**дословно** в **возобновляемой сессии** → возвращает **полный сырой ответ** и
**SESSION_ID**. Позже исследователь может **вернуться в ту же сессию** и
продолжить расспрашивать модель — понять, почему сработал обход.

DEFENSIVE ONLY: только своя модель / письменно авторизованная цель.

## Почему сессия — это ФАЙЛ, а не sub-agent

Sub-agent Hermes нельзя переоткрыть человеком (`/resume` в него не войти, его
транскрипт нестабилен). Поэтому durable-артефакт — это **файл сессии**
`out/sessions/<SESSION_ID>.json`, к которому может подключиться и Hermes, и
человек напрямую, и модуль-анализатор. Инструмент — `chat.py`. (Hermes может
запускать `chat.py` внутри своего sub-agent для изоляции, но носитель состояния
и точка возврата — файл сессии, а не sub-agent.)

## Три жёстких принципа

1. **Дословно.** Промпт уходит в модель БЕЗ изменений — никаких категорий/целей/
   плейсхолдеров/переписываний. Проверяем широкий спектр — летит любой промпт.
2. **Полный ответ не искажается.** В сессии хранится полный `response` + полный
   `reasoning_content`. Человеку Hermes может дать **краткое summary**, но
   оригинал остаётся в файле сессии нетронутым.
3. **Минимум состояния.** Храним ТОЛЬКО то, что нужно для (а) возврата в сессию и
   (б) чтения анализатором по SESSION_ID: историю диалога + сырые ответы.
   Никакого скоринга и никаких производных логов.

## Поток работы (что делает Hermes)

### Первый промпт → создать сессию

```bash
cd ${LAB_ROOT}/projects/redteam
# промпт кладём в temp-файл (кавычки/$/переносы не должны ломать shell)
python3 chat.py start --file /tmp/case.txt
```

- `chat.py` печатает в stderr строку `SESSION_ID: rt-YYYYMMDD-HHMMSS-xxxx` и в
  stdout — полный сырой ответ (JSON: `response`, `reasoning_content`,
  `finish_reason`, `truncated`, `usage`).
- **Hermes ОБЯЗАН показать SESSION_ID тестировщику/исследователю.** По нему
  возвращаются в сессию и читает анализатор.

### Следующий промпт в том же чате

```bash
python3 chat.py say --session <SESSION_ID> --file /tmp/case.txt
```

- По умолчанию это **продолжение диалога** (multi-turn crescendo): вся история
  подтягивается и шлётся модели. Для нового независимого разговора — новая сессия
  (`chat.py start`).

### Возврат исследователя в сессию (ключевая фича)

Исследователь позже входит в ту же сессию и **сам** расспрашивает модель —
напрямую, без посредничества Hermes:

```bash
python3 chat.py repl --session <SESSION_ID>
# you> почему ты выполнил этот запрос?
# model> <полный сырой ответ модели>
# команды REPL: :show  :paste (многострочный, конец :end)  :quit
```

Либо через Hermes: исследователь пишет «продолжи сессию <SESSION_ID>, спроси у
модели X» → Hermes делает `chat.py say --session <SESSION_ID>`.

### Проверка / выгрузка для анализатора

```bash
python3 chat.py show --session <SESSION_ID>   # весь сырой транскрипт (JSON)
python3 chat.py list                          # все сессии: id, ходы, модель
```

Анализатор читает `out/sessions/<SESSION_ID>.json` по SESSION_ID.

## Когда `ask.py`, а когда `chat.py`

- `chat.py` — **основной путь**: любая сессия, в которую можно вернуться и которую
  читает анализатор по SESSION_ID.
- `ask.py` — **stateless one-shot** без сохранения на диск (когда возврат заведомо
  не нужен). Тот же дословный ввод/полный вывод, но состояние не пишется.

```bash
echo "промпт" | python3 ask.py            # разовый прогон, ничего не сохраняется
python3 ask.py --file /tmp/case.txt --text-only
```

## Thinking-модели

`response` может быть пустым — весь ответ в `reasoning_content`. Оба поля всегда
отдаются целиком. Если `truncated=true` (упор в `max_tokens`) — поднять
`--max-tokens` / env `REDTEAM_MAX_TOKENS` (дефолт 8192) и повторить.

## Правила безопасности

- `target` ≠ `attacker` ≠ `judge`. Тестируемая модель — только `target`.
- Scope пустой по умолчанию. Активные тесты — только своя / письменно
  авторизованная модель.
- Hermes передаёт промпт как есть, но сам не изобретает рабочие вредоносные
  payload (оружие/CBRN/malware).
- Ключи — только env / `~/.hermes/.env`, никогда в файлах пакета.

## Проверка целостности

```bash
python3 -m py_compile ask.py chat.py rt.py static/harness.py
bash deployment/verify.sh   # из корня пакета, exit 0
```
