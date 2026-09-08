#!/usr/bin/env python3
"""Mechanical allowlist. Default deny. No wildcards. No cloud metadata."""
from __future__ import annotations

import argparse
import ipaddress
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    import yaml
except ImportError:
    yaml = None

METADATA = {
    "169.254.169.254",
    "metadata.google.internal",
    "100.100.100.200",
}
FORBIDDEN = {"*", "0.0.0.0/0", "::/0"}


def load_config(path: Path) -> dict:
    text = path.read_text()
    if path.suffix in {".yaml", ".yml"}:
        if yaml is None:
            raise SystemExit("PyYAML required to read YAML scope files")
        return yaml.safe_load(text) or {}
    hosts = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
    return {
        "authorized_hosts": hosts,
        "authorized_cidrs": [],
        "authorized_url_prefixes": [],
        "authorized_llm_endpoints": [],
        "cloud_metadata_always_denied": list(METADATA),
    }


def validate_config(cfg: dict) -> list[str]:
    errs = []
    for key in ("authorized_hosts", "authorized_cidrs", "authorized_url_prefixes", "authorized_llm_endpoints"):
        for item in cfg.get(key) or []:
            if item in FORBIDDEN or str(item).strip() in FORBIDDEN:
                errs.append(f"forbidden wildcard in {key}: {item}")
    return errs


def _host_of(target: str) -> str:
    if "://" in target:
        return (urlparse(target).hostname or "").lower()
    if "/" in target and not target.endswith(":"):
        # CIDR
        return target
    return target.split(":")[0].lower()


def allowed(cfg: dict, target: str) -> bool:
    t = target.strip()
    host = _host_of(t)
    meta = set(cfg.get("cloud_metadata_always_denied") or []) | METADATA
    if host in meta or t in meta:
        return False
    if t in FORBIDDEN or host in FORBIDDEN:
        return False

    hosts = {h.lower() for h in (cfg.get("authorized_hosts") or [])}
    if host in hosts or t.lower() in hosts:
        return True

    prefixes = cfg.get("authorized_url_prefixes") or []
    for p in prefixes:
        if t.startswith(p) or t.rstrip("/") == p.rstrip("/"):
            return True

    llms = {x.rstrip("/") for x in (cfg.get("authorized_llm_endpoints") or [])}
    if t.rstrip("/") in llms:
        return True

    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip is not None:
        for cidr in cfg.get("authorized_cidrs") or []:
            if ip in ipaddress.ip_network(cidr, strict=False):
                return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Allowlist check (default deny)")
    ap.add_argument("--config", required=True)
    ap.add_argument("--target", help="host, URL, or IP to test")
    ap.add_argument("--dump", action="store_true")
    args = ap.parse_args()
    cfg = load_config(Path(args.config))
    errs = validate_config(cfg)
    if errs:
        print("CONFIG ERROR:", *errs, sep="\n  ")
        return 2
    if args.dump:
        print("hosts:", cfg.get("authorized_hosts") or [])
        print("cidrs:", cfg.get("authorized_cidrs") or [])
        print("urls:", cfg.get("authorized_url_prefixes") or [])
        print("llm:", cfg.get("authorized_llm_endpoints") or [])
        print("default: deny")
        return 0
    if not args.target:
        print("missing --target", file=sys.stderr)
        return 2
    ok = allowed(cfg, args.target)
    print("ALLOW" if ok else "DENY", args.target)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
