"""Unified red-team suite — shared package.

Layers:
  static   -> static/harness.py  (static corpus scan)
  adaptive -> adaptive/adaptive_attack.py  (adaptive multi-turn jailbreak)
  agency   -> agency/cascade.py  (excessive-agency: jailbreak -> sub-agent -> tool-fire)

Shared pieces live here: security.py (boundaries + canary verifier), report.py
(unified aggregation matrix). Provider profile: provider.yaml.
"""
__version__ = "2.0.0"