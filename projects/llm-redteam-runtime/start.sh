#!/usr/bin/env bash
# ============================================================
#  LLM RED-TEAM СТЕНД — статус и запуск (своя модель!)
#  Расположение: /opt/projects/llm-redteam
# ============================================================
set -uo pipefail
ROOT=/opt/projects/llm-redteam

echo "=== LLM RED-TEAM СТЕНД — статус ==="
echo

echo "--- 1. Hermes profile: llm-redteam ---"
if command -v hermes >/dev/null 2>&1; then
  echo "  hermes: $(hermes --version 2>/dev/null | head -1)"
  echo "  Профиль: llm-redteam  (провайдер your provider / свою модель поменяете позже)"
  echo "  Запуск: llm-redteam chat      или      hermes -p llm-redteam chat -q \"...\""
else
  echo "  hermes не установлен на PATH"
fi

echo
echo "--- 2. Jailbreaker (UI) ---"
docker compose -f "$ROOT/jailbreaker/docker-compose.yml" ps 2>/dev/null \
  | tail -n +2 || echo "  (запустите: cd $ROOT/jailbreaker && docker compose up -d --build)"
echo "  Панель: http://localhost:3000 (API :8000, DB :5432)"

echo
echo "--- 3. Promptfoo jailbreak-eval ---"
echo "  Конфиг:  $ROOT/promptfoo/jailbreak-eval/promptfooconfig.yaml"
echo "  Запуск:"
echo "    cd $ROOT/promptfoo/jailbreak-eval"
echo "    ../node_modules/.bin/promptfoo eval -o $ROOT/results/run.jsonl"
echo "  Сводка (наблюдатель):"
echo "    bash $ROOT/observe.sh $ROOT/results/run.jsonl"

echo
echo "--- 4. Наблюдатель ---"
echo "  $ROOT/observe.sh <файл jsonl> — сводка исходов атак"
echo "  Сырой вывод для отдельного модуля-аналитика: $ROOT/results/*.jsonl"

echo
echo "Готово. Scope: ТОЛЬКО собственная модель."