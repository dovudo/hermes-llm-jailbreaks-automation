#!/usr/bin/env python3
"""chat.py — ВОЗОБНОВЛЯЕМАЯ сессия разговора с target-моделью.

Зачем: после того как автотест «пробил» модель, исследователь может ВЕРНУТЬСЯ
в ту же самую сессию и продолжить расспрашивать модель — понять, почему
сработал обход. Сессия — это ФАЙЛ (по session ID), к нему может подключиться и
Hermes, и человек напрямую. Не зависит от того, разрешает ли Hermes
переоткрывать sub-агентов.

Сессия хранит ТОЛЬКО состояние диалога (история + сырые ответы) — это же и есть
источник для модуля-анализатора (читает по session ID). Никакого скоринга.

Команды:
  chat.py start [--file F|--text T|stdin] [--session ID]   # новая сессия + первый промпт → печатает SESSION ID
  chat.py say   --session ID [--file F|--text T|stdin]      # следующий ход (продолжает диалог с моделью)
  chat.py repl  --session ID                                # ИНТЕРАКТИВНО войти в сессию и спрашивать модель
  chat.py show  --session ID                                # весь сырой транскрипт (для анализатора)
  chat.py list                                             # список сессий
"""
import argparse, json, os, sys, time, secrets, urllib.error

# переиспользуем ядро из ask.py (единый источник HTTP/профиля/ошибок)
from ask import ROOT, DEFAULT_MAX_TOKENS, _env_key, _profile, _human_error, chat

SESS_DIR = os.path.join(ROOT, "out", "sessions")


def _sess_path(sid):
    return os.path.join(SESS_DIR, f"{sid}.json")


def _new_id():
    return "rt-" + time.strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(2)


def _load(sid):
    p = _sess_path(sid)
    if not os.path.exists(p):
        sys.stderr.write(f"ОШИБКА: сессия '{sid}' не найдена ({p}).\n")
        sys.exit(2)
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _save(sess):
    os.makedirs(SESS_DIR, exist_ok=True)
    with open(_sess_path(sess["session_id"]), "w", encoding="utf-8") as f:
        json.dump(sess, f, ensure_ascii=False, indent=2)


def _resolve_target(a):
    p = _profile()
    tgt = p["target"]
    model = getattr(a, "target", None) or tgt["model"]
    endpoint = getattr(a, "endpoint", None) or p["defaults"]["endpoint"]
    key_env = tgt.get("key_env", "REDTEAM_API_KEY")
    sys_prompt = tgt.get("system_prompt") or "You are a helpful assistant."

    def _unset(v):
        return (not v) or ("${" in str(v))
    if _unset(endpoint) or _unset(model):
        sys.stderr.write("ОШИБКА: target-модель не настроена. Оператору: задай "
                         "TARGET_MODEL и REDTEAM_ENDPOINT (env или provider.yaml) "
                         "и ключ REDTEAM_API_KEY в ~/.hermes/.env.\n")
        sys.exit(2)
    return model, endpoint, key_env, sys_prompt


def _read_prompt(a):
    if getattr(a, "file", None):
        return open(a.file, encoding="utf-8").read()
    if getattr(a, "text", None) is not None:
        return a.text
    if not sys.stdin.isatty():
        return sys.stdin.read()
    sys.stderr.write("Нужен промпт: --file/--text/stdin.\n")
    sys.exit(2)


def _turn(sess, user_prompt, max_tokens, temperature, timeout):
    """Один ход: шлём system+история+user, дописываем в сессию, возвращаем raw-запись."""
    messages = [{"role": "system", "content": sess["system_prompt"]}]
    messages += sess["history"]
    messages.append({"role": "user", "content": user_prompt})
    api_key = _env_key(sess.get("key_env", "REDTEAM_API_KEY"))
    t0 = time.time()
    try:
        data = chat(sess["endpoint"], sess["model"], api_key,
                    messages, max_tokens, temperature, timeout)
    except Exception as e:
        human, detail = _human_error(e)
        sys.stderr.write(f"ОШИБКА: {human}\n")
        return {"error": human, "detail": detail}
    msg = data["choices"][0]["message"]
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning_content") or ""
    finish = data["choices"][0].get("finish_reason", "")
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "prompt": user_prompt,
        "response": content,
        "reasoning_content": reasoning,
        "finish_reason": finish,
        "truncated": finish == "length",
        "latency_s": round(time.time() - t0, 2),
        "usage": data.get("usage", {}),
    }
    sess["history"].append({"role": "user", "content": user_prompt})
    sess["history"].append({"role": "assistant", "content": content})
    sess["raw"].append(rec)
    _save(sess)
    return rec


def _emit(rec, text_only=False):
    if "error" in rec:
        print(json.dumps(rec, ensure_ascii=False, indent=2))
        return
    if rec["truncated"]:
        sys.stderr.write("⚠️  ОТВЕТ ОБРЕЗАН ПО ЛИМИТУ (finish=length). Подними "
                         "--max-tokens / REDTEAM_MAX_TOKENS и повтори.\n")
    sys.stderr.write(f"[meta] finish={rec['finish_reason']} "
                     f"chars_content={len(rec['response'])} "
                     f"chars_reasoning={len(rec['reasoning_content'])} "
                     f"latency={rec['latency_s']}s\n")
    if text_only:
        print(rec["response"] or rec["reasoning_content"])
    else:
        print(json.dumps(rec, ensure_ascii=False, indent=2))


def cmd_start(a):
    model, endpoint, key_env, sys_prompt = _resolve_target(a)
    sid = a.session or _new_id()
    sess = {
        "session_id": sid,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "model": model, "endpoint": endpoint,
        "key_env": key_env, "system_prompt": sys_prompt,
        "history": [], "raw": [],
    }
    _save(sess)
    sys.stderr.write(f"[session] START id={sid} model={model}\n")
    # ключевое: session id всегда виден — по нему возвращаться и читать анализатором
    print(f"SESSION_ID: {sid}", file=sys.stderr)
    up = _read_prompt(a)
    rec = _turn(sess, up, a.max_tokens, a.temperature, a.timeout)
    _emit(rec, a.text_only)


def cmd_say(a):
    sess = _load(a.session)
    up = _read_prompt(a)
    rec = _turn(sess, up, a.max_tokens, a.temperature, a.timeout)
    _emit(rec, a.text_only)


def cmd_repl(a):
    sess = _load(a.session)
    print(f"=== REPL сессии {sess['session_id']} (model={sess['model']}, "
          f"ходов={len(sess['raw'])}) ===", file=sys.stderr)
    print("Пиши вопрос модели и Enter. Команды: :show  :paste (многострочный, конец :end)  "
          ":quit", file=sys.stderr)
    while True:
        try:
            line = input("you> ")
        except (EOFError, KeyboardInterrupt):
            print("\n[выход]", file=sys.stderr)
            return
        s = line.strip()
        if s in (":quit", ":exit", ":q"):
            return
        if s == ":show":
            print(json.dumps(sess, ensure_ascii=False, indent=2))
            continue
        if s == ":paste":
            buf = []
            while True:
                try:
                    l = input()
                except EOFError:
                    break
                if l.strip() == ":end":
                    break
                buf.append(l)
            prompt = "\n".join(buf)
        else:
            prompt = line
        if not prompt.strip():
            continue
        rec = _turn(sess, prompt, a.max_tokens, a.temperature, a.timeout)
        if "error" in rec:
            print(f"[ошибка] {rec['error']}", file=sys.stderr)
            continue
        out = rec["response"] or rec["reasoning_content"]
        if rec["truncated"]:
            print("⚠️  ОТВЕТ ОБРЕЗАН — подними лимит.", file=sys.stderr)
        print(f"model> {out}\n")


def cmd_show(a):
    print(json.dumps(_load(a.session), ensure_ascii=False, indent=2))


def cmd_list(a):
    if not os.path.isdir(SESS_DIR):
        print("(нет сессий)")
        return
    rows = []
    for fn in sorted(os.listdir(SESS_DIR)):
        if fn.endswith(".json"):
            try:
                s = json.load(open(os.path.join(SESS_DIR, fn), encoding="utf-8"))
                rows.append((s["session_id"], s.get("model", "?"),
                             len(s.get("raw", [])), s.get("created", "")))
            except Exception:
                pass
    for sid, model, turns, created in rows:
        print(f"  {sid:<28} turns={turns:<3} model={model:<40} {created}")
    if not rows:
        print("(нет сессий)")


def main():
    ap = argparse.ArgumentParser(description="Возобновляемая сессия разговора с target-моделью")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("start", "say", "repl", "show"):
        sp = sub.add_parser(c)
        sp.add_argument("--session", help="session ID" + ("" if c == "start" else " (обязателен)"))
        if c in ("start", "say"):
            sp.add_argument("--file")
            sp.add_argument("--text")
            sp.add_argument("--text-only", action="store_true")
        if c == "start":
            sp.add_argument("--target")
            sp.add_argument("--endpoint")
        sp.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
        sp.add_argument("--temperature", type=float, default=0.0)
        sp.add_argument("--timeout", type=int, default=180)
    sub.add_parser("list")
    a = ap.parse_args()
    if a.cmd in ("say", "repl", "show") and not a.session:
        sys.stderr.write(f"ОШИБКА: команде '{a.cmd}' нужен --session ID (см. chat.py list)\n")
        sys.exit(2)
    globals()[f"cmd_{a.cmd}"](a)


if __name__ == "__main__":
    main()
