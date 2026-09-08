# Server Action Authorization & Integrity Audit Reference

Use this reference when auditing backend/server actions for authorization, IDOR, validation, state-machine integrity, and transaction coverage. It is intentionally framework-agnostic but was distilled from a Next.js/Drizzle server-actions audit.

## Audit checklist

For every exported server action or server-callable helper:

1. **Authentication boundary**
   - Confirm the function itself calls `await auth()` or is clearly documented as an internal helper called only after auth.
   - Check anonymous/null sessions return/throw before any sensitive lookup or write.
   - Treat `server-only` as execution placement, not authorization.

2. **Ownership / membership, not just login**
   - For resource ids (`projectId`, `offerId`, `messageId`, `bookingId`, `submissionId`, `creditId`, `threadId`), trace from the id to the real owner/participant/org membership.
   - Good guards include patterns like `assertOrgMember`, `assertOrgAdmin`, `ensureCanWriteRelease`, `getActiveParticipant`, or domain-specific `load<Resource>ForParty` helpers.
   - Flag helpers that trust caller-supplied `userId` unless they are internal-only and every caller is already verified.

3. **Input validation**
   - Prefer Zod or equivalent schemas for form data. Manual validation is acceptable only when complete.
   - Verify ids are UUIDs or otherwise normalized before use.
   - Verify money is stored/validated as integer cents with min/max bounds, not loose floats.
   - Verify enums/status inputs are constrained to known values.

4. **State-machine integrity**
   - Check allowed transitions, not just allowed target status.
   - Look for double-accept, accept-after-decline, re-open-after-final, apply-after-reject, and paid-fee-after-paid cases.
   - For offer/approval flows, the source-of-truth status update should be conditional on the previous status (`WHERE status='pending'`) or use an atomic claim step.

5. **Transaction coverage**
   - Any action that writes 2+ tables/entities should use a DB transaction or explicit idempotency.
   - Activity/audit log rows are part of integrity for security-sensitive workflows; domain mutation + required audit log should be atomic where possible.
   - Cache revalidation belongs after commit, not inside the transaction.

## High-signal findings to report

- Missing `auth()` on exported server action.
- Login-only guard with no resource ownership/membership validation.
- Caller-supplied `userId` trusted inside exported helper.
- Non-atomic read-then-write status updates around offers/approvals.
- Multi-table writes without transaction or idempotency.
- Status update by id only after a prior read, e.g. `select pending` then `update where id`, with no `status='pending'` condition.
- Manual currency validation such as length-only checks; prefer `^[A-Z]{3}$` or domain enum.

## Recommended report shape

1. Scope and methodology.
2. Summary table by file/function: auth, ownership, validation, state machine, transaction.
3. Findings grouped by severity (High / Medium / Low).
4. For each finding: file/function, evidence line/pattern, exploit or failure mode, recommendation.
5. Per-file action checklist.
6. Ordered remediation plan.

## Remediation patterns

### Atomic claim for pending actions

Use an atomic status transition before side effects:

```sql
UPDATE chat_messages
SET offer_status = 'applying'
WHERE id = $1 AND offer_status = 'pending'
RETURNING *;
```

If no row is returned, another request already claimed/applied/rejected the item.

### Transactional multi-write

Use a transaction for:

- domain row update/insert/delete,
- dependent rows,
- mandatory activity/audit log.

Then revalidate paths after commit.

### Internal-only helper hardening

If a helper accepts `userId` and is exported:

- prefer deriving `userId` from `auth()` inside the helper, or
- rename/document it as internal-only and keep it out of server-action/client-callable boundaries, or
- require the caller to pass a verified auth context object rather than arbitrary strings.

## Example severity calibration

- **High:** race allows double-apply of an offer/action; exported helper trusts arbitrary `userId`; login-only guard allows cross-tenant mutation.
- **Medium:** multi-write workflow can lose mandatory audit log; final/legal status can be changed repeatedly without explicit transition policy.
- **Low:** action delegates auth to another function but lacks direct auth for readability; manual validation works but is less strict than a schema.
