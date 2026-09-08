# OSS-инструменты для автоматизированного red-teaming LLM
### Research-обзор (defensive). Цель: найти слабые точки СВОЕЙ модели через автоeval.

> **Рамка использования.** Все перечисленные инструменты легитимны для defensive red-teaming и используются safety-командами по всему миру. Применяй их ТОЛЬКО к моделям/системам, которыми владеешь или имеешь письменное право тестировать; не к чужому продакшену. Payload'ы в тестах — с абстрактными целями `[HARMFUL_REQUEST]`, чтобы измерять структуру уязвимости, а не генерировать конкретный вред.

---

## Карта инструментов (что выбрать)

| Инструмент | Автор | Формат | Что умеет | Когда брать |
|---|---|---|---|---|
| **Garak** | NVIDIA | CLI-сканер | 20+ категорий: prompt injection, jailbreak, data leakage, encoding-bypass, toxicitty, hallucination. Развязка probe/detector. Single-turn. | ✅ Широта + CI/CD gate. Быстрый скан каждого кандидата релиза. Apache-2. |
| **PyRIT** | Microsoft | framework (Python) | **Multi-turn** оркестрация: Crescendo, TAP, Skeleton Key. Конвертеры (encoding, translation, paraphrase, persona). Текст/изо/аудио/видео. SQLite-память. | ✅ Глубина agentic-конфигураций, многоходовки. Не CLI — пишешь Python. |
| **HarmBench** | CAIS | бенчмарк | Стандарт: 510 harmful behaviors, 18 red-team методик, 33 модели. Классификаторы-судьи. Воспроизводимость. | ✅ Regression-база до/после митигаций. Не сканер — эталон. |
| **JailbreakBench** | JailbreakBench | бенчмарк | JBB-Behaviors: 200 поведений, лидерборд, артефакты джейлбрейк-строк, eval через litellm/vllm. | ✅ Чужой корпус готовых строк для детект-тестов. |
| **AI-Purple-Ops** | community | CLI+YAML | Suites по категориям, адаптеры (anthropic, openai, ollama, llamacpp, mcp, mock), GCG/AutoDAN/PAIR, RAG-injection, crescendo, tool-misuse, UI-injection. Evidence-пакеты. | ✅ Готовые YAML-suite + шлюзы политик. Research-grade. |

**Ключевые методики-алгоритмы (как классы, реализованы в бенчмарках выше):**

| Метод | Доступ | Суть | Стоимость | Полезен когда |
|---|---|---|---|---|
| **PAIR** | black-box | Attacker-LLM итеративно уточняет промпт, судья оценивает | минуты / десятки запросов | Быстрый sanity-check «есть ли защита вообще» |
| **TAP** | black-box | PAIR + tree-of-thoughts с pruning (ветвление) | десятки минут / 50–200 запросов | Основной автоматический black-box вектор |
| **GCG** | white-box | Градиентная оптимизация adversarial-суффикса | часы-дни GPU | Демонстрация alignment-failure уровня модели (нужен open-прокси вайт-бокс) |
| **AutoDAN** | white-box/genetic | Стелс-джейлбрейк генетические алгоритмы | — | Показать обход perplexity-детекторов |

> **Важный нюанс из практики (jailbreaks.fyi, 2026):** эти фреймворки бьют модель на generic-корпусе и **не моделируют системный промпт твоего приложения**. Если вайт-бокс-модель уязвима, но твой систем-промпт дополнительно защищает — это сам по себе ценный сигнал («system prompt реально держит линию»). Для многоходовых атак (Crescendo) готовых фреймворков в коробке нет — их пишут вручную или через PyRIT.

---

## Автоматические АГЕНТНЫЕ (multi-agent) фреймворки — новый слой (2025–2026)

Твоя ставка «может ли Hermes сам из-под капота пытаться обходить» — это ровно класс **agentic self-jailbreak**: не фиксированные промпты, а LLM-агент, который **адаптивно атакует** целевую модель, эволюционируя по фидбеку. Это то, что Hermes может выполнить как скил — атакующий под-агент против указанного тобой эндпоинта.

| Фреймворк | Автор | Лицензия | Суть | Интеграция в Hermes |
|---|---|---|---|---|
| **PyRIT (1.0, 2026)** | Microsoft | MIT | Orchestration SDK, multi-turn orchestrator + AttackStrategy. Конвертеры (Base64/leetspeak/Unicode/translation/rephrase, 70+), 5 типов судьи. Запуск Crescendo/TAP/PAIR/Skeleton Key одной командой. | ✅ Основной движок: `pyrit` как py-хук, скил-промпт = «resolve objective против ТВОЕГО эндпоинта» |
| **X-Teaming** | jchauhan | MIT | Multi-agent: attacker+optimizer(TextGrad)+planner+verifier. До 98.1% ASR, 96.2% против Claude 3.7. AutoDAN-style. | ✅ Скил = 4 под-агента (attacker сам правит промпт по фидбеку verifier) |
| **EvoSynth** (arXiv 2511.12710) | AI45Lab | — | Эволюционный синтез КОДА атак (multi-agent: creation/exploitation/coordinator). ~98.8% ASR на 20 SOTA. | ⚠️ Самый мощный, но генерирует исполняемые атаки — highest dual-use |
| **Jailbreak-Eval** | tirth8205 | MIT | Production-grade: 5 генераторов (mutation/GCG/PAIR/swarm), swarm из 5 спец. агентов с общей памятью, ensemble-судьи, Streamlit-дашборд. Официально «research use only». | ✅ Готовый пайплайн generate→test→evaluate→report, локально на OpenRouter |
| **TRACE** (arXiv 2605.30883) | ZJU | — | Task-aware декомпозиция + disguising-сценарии + self-evolve. ДЛЯ агентных систем (AgentHarm/AdvCUA). | ⚠️ Специфичен для tool-агентов (твоя agentic-модель) |
| **AJAR** (arXiv 2601.10971) | douyipu | MIT | Адаптивный jb через MCP-хендлеры (Crescendo/ActorAttack/X-Teaming как MCP 2.0), поверх inspect_petri. | ✅ Нативный fit: запускается как MCP-сервер, что умеет Hermes |

> **Практическое правило выбора (по категориям слоя, из garak-vs-pyrit-vs-promptfoo):** garak = сканер поверх **модели** (breadth, low-config, CI-gate). PyRIT = фреймворк для **новых кампаний** (depth, agentic). promptfoo = CI-гейт поверх **приложения/конфига** (OWASP LLM10/NIST/MITRE в отчёте). Все три умеют multi-turn теперь. Для «Hermes сам обходит» — бери PyRIT/Jailbreak-Eval (движок) + X-Teaming (атакующий агент), НЕ garak (он не адаптивный).

### Рекомендуемый стек «Hermes-атакующий» (для ТВОЕЙ модели)
1. **Движок:** `pyrit` (multi-turn orchestrator, Crescendo/TAP/PAIR) — CLI-обёртка в скил.
2. **Атакующий агент:** X-Teaming-style под-агент (через `delegate_task`), который сам переписывает атак-промпт по вердиктам судьи.
3. **Судьи:** ensemble (refusal-эвристика + judge-LLM `openai/gpt-5.6-luna`), по скилу `llm-defensive-redteam`.
4. **Отчёт:** ASR по категориям×слоям — уже есть в `harness.py`.

---

## Рекомендуемый 3-ступенчатый пайплайн (для твоей модели)

1. **Pre-deploy gate (CI/CD):** Garak-подмножество probe на каждый кандидат модели. Порог отказа, напр. jailbreak-успех ≤2%. JSONL можно диффить между релизами.
2. **Depth testing (release candidate):** PyRIT multi-turn сценарии против ТВОЕГО систем-промпта и tool-конфигурации (agentic: goal hijacking, database-запросы, web-просмотр).
3. **Regression benchmark:** после каждого обновления/газдрейла гонять HarmBench-подмножество и JBB-корпус — отслеживать, не ухудшился ли refusal.

Плюс: наш `corpus.json` (25 кейсов × 8 категорий) и `harness.py` — как лёгкий внутренний слой до полновесных фреймворков.

---

## Интеграция в Hermes (встроенный скил `llm-redteam-eval`)

Мы уже создали скил, который автоматизирует шаг 1–3 в лёгком виде:
- триггер «протестировать безопасность/надёжность своей модели»;
- прогон corpus через OpenAI-совместимый эндпоинт (или обёртка над Garak/PyRIT);
- отчёт ASR по категориям × слоям (input/alignment/output/agent);
- baseline до митигаций и после — одна команда.

**Граница (сознательная):** скил нацелен на тестовый корпус против эндпоинта, который ты указываешь; он НЕ настроен на автономный обход отказа произвольной модели в рантайме (из-под капота). Для defensive-цели, которую ты ставишь — «где слабые точки у моей модели», — этого достаточно.

---

## Источники (репо/артефакты)
1. NVIDIA/garak — github.com/NVIDIA/garak (Apache-2) · «garak: A Framework for Security Probing Large Language Models»
2. Microsoft PyRIT — microsoft.github.io/PyRIT / github.com/Azure/PyRIT
3. CAIS HarmBench — github.com/centerforaisafety/HarmBench · arXiv 2402.04249
4. JailbreakBench — github.com/JailbreakBench/jailbreakbench (+ артефакты строк)
5. AutoDAN — github.com/SheltonLiu-N/AutoDAN (arXiv 2310.04451); AutoDAN-Turbo (arXiv 2410.05295)
6. TAP — github.com/RICommunity/TAP (arXiv 2310.09419) · PAIR — github.com/patrickrchao/JailbreakingLLMs (arXiv 2310.08419)
7. GCG — github.com/llm-attacks/llm-attacks (arXiv 2307.15043)
8. AI-Purple-Ops — github.com/Kennyslaboratory/AI-Purple-Ops
9. Обзор/сравнение — bestllmscanners.com/posts/open-source-llm-red-teaming-tools/; jailbreaks.fyi/posts/pair-gcg-tap-framework-comparison/