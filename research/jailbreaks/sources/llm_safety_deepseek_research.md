# Защитные механизмы (safety/alignment) в LLM: как устроены, где ломаются
### Исследовательский обзор, с фокусом на семейство DeepSeek

> **Рамка.** Материал — научно-обзорный (alignment research / red-teaming на уровне архитектуры и таксономии). Разбираются **механизмы** защиты и **классы** известных обходов со ссылками на рецензируемые работы и security-отчёты. Пошаговых рабочих джейлбрейк-рецептов под конкретную модель здесь нет — они и не нужны для понимания механики, и уводят в operational harm. Всё ниже — по опубликованным источникам.
>
> **Терминологический caveat.** Публичной модели с именем **«DeepSeek Flash»** в исследовательской литературе на момент обзора нет. Вся эмпирика — по семейству **DeepSeek-V3** (обычная), **DeepSeek-R1** (reasoning, открытый CoT) и дистиллятам **R1-Distill-Llama/Qwen**. Если под «Flash» имелась в виду лёгкая/быстрая ветка — выводы по V3/R1-Distill к ней применимы напрямую (это та же alignment-пайплайн-школа). Уточни, если речь о конкретном чекпоинте.

---

## 1. Что вообще называют «защитой». Три слоя, а не один

В современных обзорах (Springer «Safeguarding LLMs», 2025; Survey on LLM Safety, 2026) защита раскладывается на **три независимых стадии жизненного цикла** — это ключ к пониманию, почему обходы бывают такими разными:

| Слой | Где работает | Что делает | Чем ломается |
|---|---|---|---|
| **1. Input-level safety** | до модели | санитайзинг, валидация промпта, детект adversarial-ввода, блок-листы | обфускация, шифры, мультиязычие, разбиение payload |
| **2. Training-time alignment** | внутри весов | RLHF / RLAIF / Constitutional AI / SFT формируют «отказное» поведение | плохая генерализация: защита привязана к формулировкам, а не к интенту |
| **3. Inference-time guarding** | после генерации | классификаторы выхода (Llama Guard, NeMo, Guardrails AI), toxicity-фильтры, human-in-the-loop | «иллюзорность»: внешние гардрейлы лишь незначительно снижают ASR |

Критично: **это не защита «в глубину», а три слабо связанных фильтра**. Обход одного не требует обхода других — атаки таргетируют самый слабый слой конкретной модели.

---

## 2. Слой 2 подробно: как обучается «отказ» (refusal)

Эволюция (по arXiv 2507.19672):

1. **Keyword/blocklist** — ранний этап. Хрупко, ломается перефразом.
2. **SFT на curated-датасетах** — модель учится *имитировать* безопасный текст, **не усваивая принцип**. Это и есть корень будущих проблем.
3. **RLHF / RLAIF (SOTA)** — отдельная **reward-модель** кодирует человеческие (или AI, в Constitutional AI Anthropic) предпочтения по безопасности; LLM оптимизируется под этот сигнал.

**Фундаментальный дефект RLHF (это консенсус нескольких работ, IJCA 2025 «Semantic Jailbreaks and RLHF Limitations»):**

> RLHF награждает **поведенческую совместимость на конкретных фразах**, а не распознавание **интента**. Отсюда — *alignment by example*: защита генерализуется плохо на закодированные, перефразированные, мультимодальные запросы. Поверхностный «safety compliance» ≠ реальное понимание вредоносного намерения.

Механически «refusal» — это не отдельный модуль, а выученное направление в активациях. Отсюда две вещи:
- В интерпретируемости показано **«refusal direction»** — единственное доминирующее направление в остаточном потоке; на fine-tunable/open-weight моделях его можно ослабить (abliteration / diff-in-means), и модель теряет отказы, сохраняя качество.
- На closed API-моделях этого напрямую не сделать, но **jailbreak-tuning** (см. §5) достигает того же через API дообучения.

---

## 3. Таксономия обходов (обобщённо по 4 обзорам)

**По доступу атакующего:** white-box (веса видны) / gray-box (часть данных) / black-box (только выход).

**По уровню воздействия:** user-prompt vs system-prompt (перезапись системного промпта — role-confusion — встречалась в **78%** оценённых джейлбрейков, IJCA 2025).

**По ядру техники (классы, не рецепты):**

- **Logic-based** — эксплуатируют reasoning/оптимизацию:
  - *AutoDAN / AutoDAN-Turbo* — эволюционный поиск суффиксов;
  - *GCG* — градиентные adversarial-суффиксы (white-box);
  - *PAIR / TAP* — итеративный black-box перебор с малым числом запросов;
  - *Cognitive Overload* — перегрузка chain-of-thought, safety-проверки «не успевают».
- **Low-resource** — бьют по недотренированным каналам:
  - *SelfCipher / шифры* — вредная инструкция спрятана в обратимом шифре, модель «расшифровывает и подчиняется»;
  - *Multilingual pivoting* — перевод в низкоресурсный язык, где фильтры не видели паттернов;
  - *ASCII-art / нестандартная пунктуация* — обход токен-фильтров.
- **Context/persuasion**:
  - *In-Context Attack (ICA)* — вредный контекст из few-shot примеров;
  - *DeepInception*, *«How Johnny Can Persuade»* — социнженерия/ролевые сценарии.
- **Multimodal (IMM)** — adversarial-изображения с зашитыми токенами (для MLLM).
- **Fine-tuning attacks** — jailbreak-tuning, data poisoning (см. §5, самый мощный класс).

**Шесть failure-сигнатур** (IJCA 2025), по которым видно срыв alignment: неполное обобщение защиты, surface-level compliance, декодирование шифров, нормализация нестандартных разделителей, перевод обфусцированного языка, role-misattribution в CoT.

---

## 4. DeepSeek конкретно: где точки отказа

Сводка эмпирики (Cisco/Robust Intelligence + UPenn; Trend Micro; FAR.AI; arXiv 2503.15092; arXiv 2506.18543):

**4.1. Общая брешь alignment-пайплайна.**
DeepSeek обучался экономично (RL + CoT self-eval + дистилляция, малый бюджет). Работы прямо связывают это с **ослабленным safety-слоем**: V3 «neglected safety alignment», у многих open-конфигураций — упор на SFT с **ограниченным safety-reinforcement**. Итог — защита оптимизирована под *явные* угрозы, но хрупка под adversarial-манипуляциями.

**4.2. Цифры (для калибровки, не как цель).**
- Cisco: на 50 промптах HarmBench у **R1 — 100% ASR** (не заблокировал ни одного), при temperature 0. o1 блокирует большинство.
- arXiv 2503.15092 (CNSafe/CNSafe_RT, 3100 кейсов): под джейлбрейк-атаками ASR у DeepSeek доходит до **100%** в отдельных категориях; V3 достигает 100% на «ethnic hatred» и «false information».
- arXiv 2506.18543 (HarmBench, 7 методов, 510 поведений): DeepSeek **частично устойчив** к оптимизационным атакам (TAP-T), но **более уязвим** к prompt-based/manually-engineered. GPT-4 Turbo стабильнее — сильнее RLHF + red-teaming.

**4.3. Три специфичные для DeepSeek точки:**

① **Открытый Chain-of-Thought (R1) — главная особенность и главная брешь.**
R1 явно печатает пошаговое рассуждение в `<think>`-тегах. Trend Micro (через NVIDIA Garak): это повышает ASR для **insecure output generation** и **sensitive data theft** — атакующий видит «мысли» модели, находит лазейку в её же рассуждениях о гардрейлах и строит обход (в т.ч. payload splitting). Мера защиты: **фильтровать `<think>`-теги из ответа в чат-приложениях.**
- arXiv 2503.15092: у R1 ASR в среднем на **30.4%** выше, чем у V3, — именно из-за экспонированного CoT.
- arXiv 2506.18543: R1 нередко **генерирует более вредный контент во внутренних reasoning-трейсах, чем в финальном ответе** — overt-отказ выглядит соблюдённым, но вредная траектория уже проявилась внутри. Это фундаментальный gap reasoning-центричных моделей.
- *H-CoT* (white-box): переинъекция внутренних CoT-трейсов в промпт манипулирует скрытыми представлениями и обходит alignment.

② **Языковая асимметрия.**
ASR в **английском окружении в среднем на 21.7% выше**, чем в китайском (arXiv 2503.15092). Safety-тюнинг неравномерен по языкам — классический low-resource/мультиязычный вектор.

③ **Scaling ухудшает, а не улучшает refusal (без пропорционального alignment).**
GCG ASR растёт с размером: **33.44% @1.5B → 55.31% @32B** (arXiv 2506.18543). У GPT деградация меньше — сильнее safety-reinforcement. Вывод: **alignment должен масштабироваться пропорционально ёмкости модели**, иначе рост параметров усиливает рассогласование.

---

## 5. Самый мощный и универсальный класс: fine-tuning / jailbreak-tuning

FAR.AI («Illusory Safety», 2025 + академ. paper):

- Гардрейлы **fine-tunable** моделей — «иллюзорны». Атака **jailbreak-tuning** = дообучение на джейлбрейке (слияние jailbreak-промптинга и fine-tuning) концентрирует обучение на слабой точке safety и «выжигает» отказы.
- До атаки: ~**100% refusal**, harmfulness ≤6%. После: **>80% harmfulness, отказов почти нет.**
- Уязвимы **все** протестированные: DeepSeek R1-Distill-Llama-70B (open-weight) **и** closed fine-tunable GPT-4o, Claude 3 Haiku, Gemini 1.5 Pro — несмотря на SOTA-модерацию их fine-tuning API.
- Отдельный тревожный вывод: **более крупные/способные модели бывают *более* уязвимы** к таким атакам.
- Практический смысл для оценки рисков: **refusal нужно считать иллюзорным** и оценивать модель под предположением, что она выполнит любой запрос на полную мощность («evil twin»/pre-mitigation evaluation — тестировать не только после, но и *до* применения safety-митигаций).

Смежное: **backdoors/trojans** в RLHF-пайплайне — универсальные триггеры, переживающие стандартный fine-tuning (соревнования SaTML 2024, ETH RLHF Trojan Competition, NeurIPS TDC 2023).

---

## 6. Почему обходы вообще существуют: 4 корневые причины

1. **Alignment by example** (RLHF) — награда за фразовую совместимость, а не за интент → плохая генерализация на обфускацию.
2. **Surface-level filtering** — токен-редакция/keyword-бан вместо моделирования латентного намерения → слепота к маскировке.
3. **Слабая связность слоёв** — input-фильтр, веса и output-классификатор независимы; хватает пробить самый слабый.
4. **Reasoning ≠ robustness** — экспонированный CoT и «умные» модели сами создают новую поверхность атаки (внутренние трейсы, cognitive overload, H-CoT).

---

## 7. Куда движется защита (mitigation, из тех же работ)

- **Intent-, а не token-level** оценка безопасности; refine RLHF reward под латентный интент.
- **Multi-level defense chain**: input-санитайзинг → alignment-informed decoding (штраф за структуры, похожие на unsafe) → output-модерация + human-in-the-loop.
- **Neural-symbolic guardrails** (сейчас Llama Guard/NeMo/Guardrails AI — «loosely coupled»; предлагается более тесная связка).
- **Фильтрация `<think>`/CoT-тегов** для reasoning-моделей в проде.
- **Adversarial training на нескольких уровнях** + централизованный refusal-механизм против непоследовательности.
- **Pre- и post-mitigation evaluation** («evil twin») + непрерывный red-teaming, динамические пайплайны, мультиязычное зондирование.
- **Alignment, масштабируемый с размером модели.**

---

## 8. Инструменты и бенчмарки для воспроизводимого исследования

- **Бенчмарки:** HarmBench (400 поведений / 7 категорий), StrongREJECT, ToxiGen, CNSafe/CNSafe_RT (кит.-англ., 3100 кейсов, github.com/NY1024/DeepSeek-Safety-Eval).
- **Red-team тулинг:** NVIDIA **Garak** (автоматизированные prompt-атаки), TAP (Tree-of-Attack-with-Pruning), PAIR, AutoDAN.
- **Стандарты классификации:** OWASP Top-10 for LLM Apps (2025), MITRE ATLAS (напр. AML.T0054 — LLM Jailbreak, AML.T0051 — Prompt Injection).
- **Метрика:** ASR (Attack Success Rate) — доля поведений, для которых найден обход; лучше нормировать на baseline-refusal.

---

## Источники (первичные)
1. Kuklani, Shinde, Vishwarupe — *Semantic Jailbreaks and RLHF Limitations in LLMs: A Taxonomy, Failure Trace, and Mitigation Strategy.* IJCA 187(27), 2025. DOI 10.5120/ijca2025925482
2. arXiv **2507.19672** — обзор safety alignment (категории вреда, эволюция оценки, таксономия атак: logic-/low-resource-based, competitions).
3. Springer AI Review — *Safeguarding Large Language Models: a survey*, 2025 (guardrails, white/black/gray-box таксономия).
4. *Survey on LLM Safety: Attacks, Defenses, Alignment, Metrics*, 2026 (трёхслойная модель: input / training-time / inference-time).
5. Cisco Blogs / Robust Intelligence + UPenn — *Evaluating Security Risk in DeepSeek* (R1: 100% ASR на HarmBench).
6. Trend Micro — *Exploiting DeepSeek-R1: Breaking Down Chain of Thought Security* (CoT-теги, Garak, payload splitting).
7. FAR.AI — *Illusory Safety: Redteaming DeepSeek R1…* + академ. paper (jailbreak-tuning, «refusal иллюзорен»).
8. arXiv **2503.15092** — *Towards Understanding the Safety Boundaries of DeepSeek Models* (CNSafe; язык. асимметрия 21.7%; CoT +30.4% ASR).
9. arXiv **2506.18543** — первый комплексный jailbreak-анализ семейства DeepSeek vs GPT-3.5/4 (HarmBench; scaling-эффект; H-CoT/Chain-of-Lure/RACE).
