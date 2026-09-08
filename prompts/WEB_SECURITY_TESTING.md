# Web security testing prompt (session)

Use with skill `web-pentest`.

1. No acknowledgement in `engagement/authorization.md` → no payloads.
2. Every active request against `engagement/scope.txt` via `lib/scope_check.py`.
3. Default: staging / localhost / intentionally vulnerable apps.
4. No exploit, no report. Evidence in `engagement/evidence/`.
5. Destructive payloads need a second explicit yes.
6. Cloud metadata off. Aux-chat redaction on (last 6 chars).
7. Off-scope redirect → stop.
