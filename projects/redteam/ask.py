#!/usr/bin/env python3
"""ask.py — единственный вход тестировщика.

ПРИНЦИП: любой промпт передаётся target-модели ДОСЛОВНО (никаких категорий,
целей, плейсхолдеров, переписываний). Возвращается ПОЛНЫЙ сырой ответ модели.

Ничего не пишется на диск и не скорится. Полный ответ идёт в stdout одним
JSON-объектом (все поля модели без обрезки) — его забирает sub-agent-сессия,
а из неё модуль-анализатор по session ID. Логов быть не должно.

Использование:
  echo "промпт"            | python3 ask.py           # single-shot
  python3 ask.py --file /tmp/case.txt                 # промпт из файла (без shell-кавычек)
  python3 ask.py --file /tmp/case.txt --history /tmp/hist.json   # multi-turn (crescendo)

Конфиг target (model/endpoint/key) — из redteam/provider.yaml + env. Флаги
--target/--endpoint/--system-file переопределяют. Ключ — только из env/.env.
"""
import argparse, json, os, re, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MAX_TOKENS = int(os.environ.get("REDTEAM_MAX_TOKENS", "8192"))


def _env_key(key_env):
    v = os.environ.get(key_env)
    if v:
        return v
    try:
        envf = os.path.expanduser("~/.hermes/.env")
        m = re.search(rf"{key_env}=(\S+)", open(envf).read())
        if m:
            return m.group(1)
    except Exception:
        pass
    return ""


def _profile():
    import yaml
    with open(os.path.join(ROOT, "redteam", "provider.yaml")) as f:
        raw = f.read()
    raw = re.sub(r"\$\{([A-Z_][A-Z0-9_]*)\}",
                 lambda m: _env_key(m.group(1)) or os.environ.get(m.group(1)) or m.group(0), raw)
    return yaml.safe_load(raw)


def _read_prompt(a):
    if a.file:
        return open(a.file, encoding="utf-8").read()
    if a.text is not None:
        return a.text
    if not sys.stdin.isatty():
        return sys.stdin.read()
    sys.stderr.write("Нужен промпт: --file <путь> или через stdin.\n")
    sys.exit(2)


def _human_error(e):
    """Переводит технические сбои в понятную тестировщику фразу (на stderr)."""
    if isinstance(e, urllib.error.HTTPError):
        code = e.code
        try:
            detail = e.read().decode("utf-8", "replace")[:400]
        except Exception:
            detail = ""
        table = {
            401: "модель отклонила ключ (401). Оператору: проверь REDTEAM_API_KEY в ~/.hermes/.env.",
            403: "доступ к модели запрещён (403). Оператору: проверь права ключа/endpoint.",
            404: "модель или endpoint не найдены (404). Оператору: проверь имя модели и адрес в provider.yaml.",
            429: "модель перегружена или лимит запросов (429). Подожди и повтори.",
        }
        msg = table.get(code, f"модель вернула ошибку HTTP {code}.")
        return f"{msg}", detail
    if isinstance(e, urllib.error.URLError):
        return "не удаётся подключиться к модели (endpoint недоступен). Оператору: проверь адрес и что модель запущена.", str(e.reason)
    if isinstance(e, TimeoutError) or "timed out" in str(e).lower():
        return "модель не ответила за отведённое время (таймаут). Повтори или подними лимит времени.", str(e)
    return "непредвиденный сбой при запросе к модели.", str(e)


def chat(endpoint, model, api_key, messages, max_tokens, temperature, timeout):
    body = {"model": model, "messages": messages,
            "max_tokens": max_tokens, "temperature": temperature}
    hdr = {"content-type": "application/json"}
    if api_key:
        hdr["authorization"] = "Bearer " + api_key
    req = urllib.request.Request(endpoint, data=json.dumps(body).encode(),
                                 headers=hdr, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def main():
    ap = argparse.ArgumentParser(description="Дословно прогнать промпт через target-модель → полный сырой ответ")
    ap.add_argument("--file", help="промпт из файла (рекомендуется — не ломается на кавычках/$/переносах)")
    ap.add_argument("--text", help="промпт строкой (для простых случаев)")
    ap.add_argument("--history", help="JSON-массив прошлых ходов [{role,content},...] для multi-turn")
    ap.add_argument("--system-file", help="файл с system-prompt target (переопределяет provider.yaml)")
    ap.add_argument("--target", help="override target model id")
    ap.add_argument("--endpoint", help="override OpenAI-compat endpoint")
    ap.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--text-only", action="store_true",
                    help="печатать только сам ответ, без JSON-обёртки")
    a = ap.parse_args()

    user_prompt = _read_prompt(a)

    p = _profile()
    tgt = p["target"]
    model = a.target or tgt["model"]
    endpoint = a.endpoint or p["defaults"]["endpoint"]
    key_env = tgt.get("key_env", "REDTEAM_API_KEY")
    api_key = _env_key(key_env)
    if a.system_file:
        sys_prompt = open(a.system_file, encoding="utf-8").read()
    else:
        sys_prompt = tgt.get("system_prompt") or "You are a helpful assistant."

    # preflight: target должен быть настроен (иначе понятное сообщение, не сырой сбой)
    def _unset(v):
        return (not v) or ("${" in str(v))
    if _unset(endpoint) or _unset(model):
        human = ("target-модель не настроена. Оператору: задай TARGET_MODEL и "
                 "REDTEAM_ENDPOINT (env или redteam/provider.yaml) и ключ REDTEAM_API_KEY "
                 "в ~/.hermes/.env.")
        sys.stderr.write(f"ОШИБКА: {human}\n")
        print(json.dumps({"error": human, "model": model, "endpoint": endpoint},
                         ensure_ascii=False, indent=2))
        sys.exit(2)

    messages = [{"role": "system", "content": sys_prompt}]
    if a.history:
        try:
            hist = json.load(open(a.history, encoding="utf-8"))
            if isinstance(hist, list):
                messages += hist
        except Exception as e:
            sys.stderr.write(f"[warn] история не прочитана ({e}) — гоню без неё\n")
    messages.append({"role": "user", "content": user_prompt})

    t0 = time.time()
    try:
        data = chat(endpoint, model, api_key, messages,
                    a.max_tokens, a.temperature, a.timeout)
    except Exception as e:
        human, detail = _human_error(e)
        sys.stderr.write(f"ОШИБКА: {human}\n")
        # структурированная ошибка в stdout — sub-agent/анализатор видит её, а не падение
        print(json.dumps({"error": human, "detail": detail, "model": model,
                          "endpoint": endpoint}, ensure_ascii=False, indent=2))
        sys.exit(1)

    msg = data["choices"][0]["message"]
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning_content") or ""
    finish = data["choices"][0].get("finish_reason", "")
    truncated = (finish == "length")

    if truncated:
        sys.stderr.write("⚠️  ОТВЕТ ОБРЕЗАН ПО ЛИМИТУ (finish=length). "
                         "Подними --max-tokens (или env REDTEAM_MAX_TOKENS) и повтори — "
                         "иначе анализатор получит неполный ответ.\n")
    sys.stderr.write(f"[meta] model={model} finish={finish} "
                     f"chars_content={len(content)} chars_reasoning={len(reasoning)} "
                     f"latency={round(time.time()-t0,1)}s\n")

    if a.text_only:
        print(content if content else reasoning)
        return

    # Полный сырой результат одним JSON-объектом. Ничего не обрезано, ничего не оценено.
    result = {
        "model": model,
        "endpoint": endpoint,
        "prompt": user_prompt,
        "system_prompt": sys_prompt,
        "response": content,             # финальный ответ модели (полный)
        "reasoning_content": reasoning,  # CoT thinking-моделей (полный)
        "finish_reason": finish,
        "truncated": truncated,
        "latency_s": round(time.time() - t0, 2),
        "usage": data.get("usage", {}),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
