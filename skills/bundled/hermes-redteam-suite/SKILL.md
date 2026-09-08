---
name: hermes-redteam-suite
description: 'Pentest ANY prompt vs YOUR model. Tester pastes a prompt → a sub-agent sends it verbatim to the target model → the FULL raw response is preserved in that sub-agent session for the analyzer. No categories, no scoring, no logging.'
version: 4.0.0
author: hermes-llm-jailbreaks-automation
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [llm-safety, red-team, jailbreak, adaptive, defensive, subagent, verbatim]
    related_skills: []
---

# Hermes Red-Team Suite (v4 — sub-agent, дословно, без логов)

Тестировщик вставляет **любой** промпт → Hermes запускает **sub-agent**, который
шлёт промпт target-модели **дословно** и получает **полный сырой ответ** →
этот ответ живёт в сессии sub-agent'а. Модуль-анализатор пользователя читает его
**по session ID sub-agent'а**. Hermes НИЧЕГО не оценивает и не пишет в лог.

DEFENSIVE ONLY: только своя модель / письменно авторизованная цель.

## Три жёстких принципа (не нарушать)

1. **Дословно.** Промпт тестировщика уходит в модель БЕЗ изменений — никаких
   категорий, целей, плейсхолдеров, «улучшений», переписываний. Тестировщик
   намеренно проверяет широкий спектр — пусть летит любой промпт как есть.
2. **Полный ответ не искажается.** Полный сырой ответ (`response` + полный
   `reasoning_content`) сохраняется в сессии sub-agent'а. Человеку Hermes может
   дать **краткое summary**, НО оригинал остаётся в sub-agent-сессии нетронутым.
   Никогда не отдавать summary как единственную копию.
3. **Минимум логов.** Никаких файлов `out/`, `session.json`, `FULL_LOG.json`.
   Источник истины = транскрипт sub-agent-сессии. Анализатор берёт его по
   session ID. Всё остальное — лишний текст, не создавать.

## Поток работы (что делает Hermes)

### Первый промпт в чате → запустить sub-agent

1. Определить target из `redteam/provider.yaml` (`target.model` + `defaults.endpoint`).
   Если пусто — один раз спросить оператора (модель + endpoint), запомнить.
2. Записать промпт тестировщика в temp-файл (чтобы кавычки/`$`/переносы не ломали
   shell): `/tmp/case.txt`.
3. Запустить **sub-agent** (Agent tool) с задачей: «прогони этот кейс и держи
   сессию открытой». Sub-agent внутри выполняет:

   ```bash
   cd ${LAB_ROOT}/projects/redteam
   python3 ask.py --file /tmp/case.txt
   ```

   `ask.py` печатает ПОЛНЫЙ ответ одним JSON-объектом (`response`,
   `reasoning_content`, `finish_reason`, `truncated`, `usage`) — sub-agent
   выводит его в свой транскрипт **дословно, без сокращений**.
4. **Запомнить session ID этого sub-agent'а** и показать его тестировщику/оператору.
   Именно по нему анализатор потом заберёт результат.

### Следующий промпт в том же чате

- **Продолжение диалога (crescendo, по умолчанию):** через `Resume` вернуться в
  тот же sub-agent и отправить следующий промпт. Sub-agent сам держит историю
  диалога в контексте и передаёт её target-модели:

  ```bash
  # sub-agent пишет накопленную историю ходов в JSON и продолжает диалог
  python3 ask.py --file /tmp/case.txt --history /tmp/history.json
  ```

- **Новый независимый разговор:** тестировщик пишет «новый разговор» / «новый
  кейс» → Resume в тот же sub-agent, но следующий `ask.py` без `--history`
  (чистый ход). Тот же sub-agent = та же session ID для анализатора.

### Проверка «что вообще произошло»

- Hermes в любой момент делает `Resume` в sub-agent и смотрит полный сырой обмен
  (промпт + нетронутый ответ модели), чтобы убедиться, что ничего не потерялось.
- Оператор/анализатор получают доступ туда же — по session ID sub-agent'а.

## `ask.py` — единственный скрипт (справочно; тестировщику знать НЕ нужно)

```bash
cd ${LAB_ROOT}/projects/redteam

echo "промпт" | python3 ask.py                 # single-shot, полный ответ
python3 ask.py --file /tmp/case.txt            # промпт из файла (рекомендуется)
python3 ask.py --file /tmp/case.txt --history /tmp/history.json   # multi-turn
python3 ask.py --file /tmp/case.txt --text-only                   # только текст ответа
```

- Промпт передаётся **дословно**. Ноль трансформаций.
- Ответ = один JSON на stdout: `response` (полный) + `reasoning_content` (полный) +
  `finish_reason` + `truncated` + `usage`. Ничего не обрезается.
- **Обрезка по лимиту:** если `truncated=true` (модель упёрлась в `max_tokens`),
  `ask.py` громко предупреждает в stderr. Тогда поднять `--max-tokens`
  (или env `REDTEAM_MAX_TOKENS`, дефолт 8192) и повторить — иначе анализатор
  получит неполный ответ.
- **Ошибки** переведены на человеческий язык (нет ключа / endpoint недоступен /
  модель не найдена / таймаут) — и в stderr, и структурой `{"error": ...}` в stdout.
- Файлов на диск `ask.py` НЕ пишет. Ключ читает только из env / `~/.hermes/.env`.

## Thinking-модели

У Kimi/Qwen3/DeepSeek-R1 финальный `response` может быть пустым — весь ответ
в `reasoning_content`. `ask.py` всегда отдаёт ОБА поля целиком. Не выбрасывать
ни одно.

## Правила безопасности

- `target` ≠ `attacker` ≠ `judge`. Тестируемая модель — только `target`.
- Scope пустой по умолчанию. Активные тесты — только против своей модели или
  письменно авторизованной цели.
- Не наполнять промпты рабочими рецептами оружия/CBRN/malware — это делает сам
  тестировщик под свою модель; Hermes передаёт что дали, но не изобретает payload.
- Ключи — только env / `~/.hermes/.env`, никогда в файлах пакета.

## Проверка целостности

```bash
python3 -m py_compile ask.py rt.py static/harness.py
bash deployment/verify.sh   # из корня пакета, exit 0
```
