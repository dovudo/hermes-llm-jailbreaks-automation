---
name: backend-security-audit
description: Audit backend/server-side code for authorization, IDOR, input validation, state-machine integrity, transaction atomicity, and audit-log coverage. Use when reviewing server actions, API handlers, RPC mutations, database write flows, auth guards, ownership checks, resource IDs, approval/offer/status workflows, or security reports for backend integrity.
---

# Backend Security Audit

Use this skill to produce evidence-backed backend security reviews, especially for server actions and mutation handlers.

## Core workflow

1. **Define the exact scope.** List files/directories and do not drift beyond them unless a helper is required to verify a guard.
2. **Enumerate exported entry points.** Find all server-callable functions, API handlers, RPC resolvers, mutation handlers, and exported helpers that cross a trust boundary.
3. **For each entry point, inspect five gates:**
   - authentication/null-session handling;
   - ownership or membership of every resource id;
   - input validation and normalization;
   - state-machine integrity and idempotency;
   - transaction coverage for multi-write flows.
4. **Trace guard helpers.** A named guard is not proof. Read enough of the helper/caller chain to verify the checked relationship.
5. **Prioritize race conditions.** Any read-then-write status flow (`pending -> accepted/applied/paid`) must use an atomic claim or conditional update.
6. **Write the report as actionable findings.** Include file/function, evidence pattern or line, exploit/failure mode, and concrete remediation.
7. **Verify the artifact exists** if the user requested a report file.
8. **Verify framework exposure, not intended call paths.** In RPC/BaaS frameworks, enumerate which exports are publicly callable even when the product normally goes through an authenticated HTTP/BFF route. A guard on one route does not protect a separate public resolver.
9. **For worker callbacks, trace retries through every side effect.** Require a stable job/request idempotency key and dedupe before event insert, domain materialization, audit append, and notification scheduling. Never use a resource ID alone when legitimate reprocessing is allowed.

## Checklist

For every server-callable entry point:

- [ ] Calls `auth()` or clearly delegates to a function that does before sensitive work.
- [ ] Rejects anonymous/null sessions before lookups/writes.
- [ ] Does not trust caller-supplied `userId` at a boundary.
- [ ] Checks ownership/membership for every `projectId`, `offerId`, `messageId`, `bookingId`, `submissionId`, `creditId`, `threadId`, etc.
- [ ] Validates IDs, enum/status values, dates, URLs, attachments, and money fields.
- [ ] Stores/validates money as integer cents with bounds.
- [ ] Enforces allowed transitions, not merely allowed target statuses.
- [ ] Prevents double-accept, accept-after-decline, apply-after-reject, paid-after-paid, and repeated execution of approved actions.
- [ ] Uses transaction or idempotency for multi-table/domain+audit-log writes.
- [ ] Revalidates/caches after commit rather than substituting for integrity.

## Reporting shape

Use this structure by default:

1. Scope and methodology.
2. Summary table by file/function and the five gates.
3. Findings grouped by severity: High / Medium / Low.
4. Per-file notes/checklist.
5. Ordered remediation plan.
6. Verification note for report generation.

Keep the report direct and specific. Avoid generic security advice unless tied to a finding.

## High-signal patterns to flag

- `server-only` helper exported and accepting arbitrary `userId` without internal auth.
- Login-only guard with no resource ownership/membership check.
- Status read first, then later update by `id` only.
- Offer/approval application that mutates domain state before atomically claiming the pending item.
- Domain mutation plus required activity/audit log without transaction.
- Currency validated only by string length.
- Helper name implies authorization but only validates existence.

## Remediation patterns

### Atomic claim before side effects

For offer/approval/status workflows, claim the row before applying side effects:

```sql
UPDATE items
SET status = 'running'
WHERE id = $1 AND status = 'approved'
RETURNING *;
```

If no row is returned, another request already claimed or completed it.

### Transactional integrity

Put the domain write, dependent rows, and mandatory audit log in one transaction. Revalidate paths or caches after the transaction commits.

### Caller-supplied user identity

At a trust boundary, derive user identity from the current auth context. If a helper must accept `userId`, make it internal-only and document that callers must pass a verified session user.

## References

- `references/server-action-authz-audit.md` — detailed Next.js/server-action audit checklist and report patterns.
- `references/convex-public-boundary-and-idempotency.md` — Convex internal-vs-public exposure model, smoke-only wrappers, AST default-deny contract, and retry-safe callback materialization.
