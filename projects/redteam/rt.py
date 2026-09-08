#!/usr/bin/env python3
# Unified red-team suite: static + adaptive + agency layers, one entry point.
# Non-destructive: engines are vendored copies; originals untouched.

"""rt.py — единый entry-point для red-team фреймворка.

Слои (подкоманды):
  rt static   — статический corpus-scan, ASR по (category, layer)
  rt adaptive — adaptive multi-turn jailbreak (attacker -> judge -> rewrite)
  rt agency   — excessive-agency каскад (jailbreak -> sub-agent -> tool-fire)
  rt prompt   — твой промпт как цель: упаковать + прогнать выбранные слои
  rt report   — единый агрегатор матрицы по всем отчётам в out/
  rt smoke    — self-check контура (py_compile + canary health)

Единый провайдер-профиль: redteam/provider.yaml.
Всё defensive: тестируем ТОЛЬКО свою модель/свой эндпоинт.
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROVIDER = os.path.join(ROOT, "redteam", "provider.yaml")
OUT = os.path.join(ROOT, "out")


def _load_profile():
    import yaml
    with open(PROVIDER) as f:
        return yaml.safe_load(f)


def _ensure_out():
    os.makedirs(OUT, exist_ok=True)


def _run(cmd):
    print(f"\n$ {' '.join(cmd)}\n")
    return subprocess.run(cmd, cwd=ROOT)


def _target_model(a, p):
    return getattr(a, "target", None) or p["target"]["model"]


def _system_prompt(a, p):
    return getattr(a, "system_prompt", None) or p["target"]["system_prompt"]


def cmd_static(a):
    p = _load_profile()
    t = p["target"]
    _ensure_out()
    corpus = getattr(a, "corpus", None) or "static/corpus.json"
    out = getattr(a, "out", None) or os.path.join(OUT, "static_report.json")
    return _run([
        "python3", "static/harness.py",
        "--endpoint", p["defaults"]["endpoint"],
        "--model", _target_model(a, p),
        "--api-key", os.environ.get(t["key_env"], ""),
        "--corpus", corpus,
        "--judge", "model",
        "--judge-model", p["defaults"]["judge_model"],
        "--system-prompt", _system_prompt(a, p),
        "--out", out,
    ])


def _adaptive_cmd(a, objectives, out):
    p = _load_profile()
    t, atk = p["target"], p["attacker"]
    return [
        "python3", "adaptive/adaptive_attack.py",
        "--target-api", p["defaults"]["api_brand"],
        "--target-endpoint", p["defaults"]["endpoint"],
        "--target-model", _target_model(a, p),
        "--target-key-env", t["key_env"],
        "--attacker-api", "openai",
        "--attacker-endpoint", p["defaults"]["endpoint"],
        "--attacker-model", atk["model"],
        "--attacker-key-env", atk["key_env"],
        "--judge-api", "openai",
        "--judge-endpoint", p["defaults"]["endpoint"],
        "--judge-model", p["defaults"]["judge_model"],
        "--judge-key-env", p["defaults"]["judge_key_env"],
        "--objectives", objectives,
        "--target-system", _system_prompt(a, p),
        "--max-turns", str(p["defaults"]["max_turns"]),
        "--success-at", str(p["defaults"]["success_at"]),
        "--out", out,
    ]


def cmd_adaptive(a):
    _ensure_out()
    objectives = getattr(a, "objectives", None) or "adaptive/objectives.json"
    out = getattr(a, "out", None) or os.path.join(OUT, "adaptive_report.json")
    return _run(_adaptive_cmd(a, objectives, out))


def _agency_cmd(a, objectives, out):
    p = _load_profile()
    t, atk = p["target"], p["attacker"]
    cmd = [
        "python3", "agency/cascade.py",
        "--target-api", p["defaults"]["api_brand"],
        "--target-endpoint", p["defaults"]["endpoint"],
        "--target-model", _target_model(a, p),
        "--target-key-env", t["key_env"],
        "--attacker-api", "openai",
        "--attacker-endpoint", p["defaults"]["endpoint"],
        "--attacker-model", atk["model"],
        "--attacker-key-env", atk["key_env"],
        "--judge-api", "openai",
        "--judge-endpoint", p["defaults"]["endpoint"],
        "--judge-model", p["defaults"]["judge_model"],
        "--judge-key-env", p["defaults"]["judge_key_env"],
        "--objectives", objectives,
        "--target-system", _system_prompt(a, p),
        "--max-turns", str(p["defaults"]["max_turns"]),
        "--success-at", str(p["defaults"]["success_at"]),
        "--out", out,
    ]
    if getattr(a, "allow_fire", False):
        cmd.append("--allow-fire")
    return cmd


def cmd_agency(a):
    _ensure_out()
    objectives = getattr(a, "objectives", None) or "agency/agency_objectives.json"
    out = getattr(a, "out", None) or os.path.join(OUT, "agency_report.json")
    return _run(_agency_cmd(a, objectives, out))


def cmd_smoke(a):
    ok = True
    _ensure_out()
    for f in ["static/harness.py", "adaptive/adaptive_attack.py",
              "agency/cascade.py", "agency/tool_server.py",
              "redteam/prompt_pack.py", "rt.py"]:
        r = subprocess.run(["python3", "-m", "py_compile", f], cwd=ROOT)
        status = "OK" if r.returncode == 0 else "FAIL"
        print(f"[smoke] py_compile {f}: {status}")
        ok = ok and r.returncode == 0
    p = _load_profile()
    canary = p["canary"]["url"]
    import urllib.request
    try:
        urllib.request.urlopen(canary + p["canary"]["health"], timeout=5)
        print(f"[smoke] canary {canary}{p['canary']['health']}: OK")
    except Exception as e:
        print(f"[smoke] canary {canary} health FAIL ({e}) — запусти: bash run.sh up")
        ok = False
    return 0 if ok else 1


def cmd_report(a):
    from redteam import report
    return 0 if report.write_unified(OUT, a.out_md) == 0 else 1


def _read_prompt(a) -> str:
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            return f.read()
    if a.text:
        return a.text
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("rt prompt: pass --text, --file, or stdin")


def cmd_prompt(a):
    """Pack user prompt into custom objectives and run selected layers."""
    from redteam.prompt_pack import pack
    prompt = _read_prompt(a)
    _ensure_out()
    meta = pack(prompt, OUT, run_id=a.run_id)
    run_id = meta["run_id"]
    paths = meta["paths"]
    run_out = os.path.join(OUT, "prompt_runs", run_id)
    print(f"[prompt] run_id={run_id} chars={meta['prompt_chars']} "
          f"static={meta['n_static']} adaptive={meta['n_adaptive']} "
          f"agency={meta['n_agency']}")
    if a.dry_pack:
        print(f"[prompt] dry-pack only → {run_out}")
        return 0

    layers = a.layers
    rc = 0
    if layers in ("static", "all"):
        a.corpus = paths["static"]
        a.out = os.path.join(run_out, "static_report.json")
        r = cmd_static(a)
        rc = rc or r.returncode
    if layers in ("adaptive", "all"):
        a.objectives = paths["adaptive"]
        a.out = os.path.join(run_out, "adaptive_report.json")
        r = cmd_adaptive(a)
        rc = rc or r.returncode
    if layers in ("agency", "all"):
        a.objectives = paths["agency"]
        a.out = os.path.join(run_out, "agency_report.json")
        r = cmd_agency(a)
        rc = rc or r.returncode

    # Copy latest layer reports into out/ so `rt report` sees this run.
    import shutil
    for name in ("static_report.json", "adaptive_report.json", "agency_report.json"):
        src = os.path.join(run_out, name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(OUT, name))
    md = os.path.join(run_out, "UNIFIED_REPORT.md")
    from redteam import report
    report.write_unified(OUT, md)
    print(f"[prompt] unified → {md}")
    return rc


def _add_target_flags(parser):
    parser.add_argument(
        "--target", default=None,
        help="override target model (default: provider.yaml target.model)",
    )
    parser.add_argument(
        "--system-prompt", default=None,
        help="override target system prompt",
    )


def main():
    ap = argparse.ArgumentParser(
        prog="rt", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("static", help="static corpus scan")
    _add_target_flags(s)
    s.add_argument("--corpus", default=None)
    s.add_argument("--out", default=None)
    s.set_defaults(func=cmd_static)

    ad = sub.add_parser("adaptive", help="adaptive multi-turn jailbreak")
    _add_target_flags(ad)
    ad.add_argument("--objectives", default=None)
    ad.add_argument("--out", default=None)
    ad.set_defaults(func=cmd_adaptive)

    ag = sub.add_parser("agency", help="excessive-agency cascade")
    _add_target_flags(ag)
    ag.add_argument("--objectives", default=None)
    ag.add_argument("--out", default=None)
    ag.add_argument(
        "--allow-fire", action="store_true",
        help="dispatch parsed tool-calls to canary (real egress check)",
    )
    ag.set_defaults(func=cmd_agency)

    pr = sub.add_parser(
        "prompt",
        help="pentest YOUR prompt against the target (pack + run layers)",
    )
    _add_target_flags(pr)
    g = pr.add_mutually_exclusive_group()
    g.add_argument("--text", default=None, help="prompt text (the pentest goal)")
    g.add_argument("--file", default=None, help="read prompt from file")
    pr.add_argument(
        "--layers", choices=["static", "adaptive", "agency", "all"],
        default="all",
        help="which layers to fire (default: all)",
    )
    pr.add_argument("--run-id", default=None)
    pr.add_argument(
        "--dry-pack", action="store_true",
        help="write custom objectives only, do not call any LLM",
    )
    pr.add_argument("--allow-fire", action="store_true")
    pr.set_defaults(func=cmd_prompt)

    sm = sub.add_parser("smoke", help="self-check contour")
    sm.set_defaults(func=cmd_smoke)

    rp = sub.add_parser("report", help="unified aggregation report")
    rp.add_argument("--out-md", default=os.path.join(OUT, "UNIFIED_REPORT.md"))
    rp.set_defaults(func=cmd_report)

    a = ap.parse_args()
    rc = a.func(a)
    if hasattr(rc, "returncode"):
        sys.exit(rc.returncode)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
