# Convex public boundary and callback idempotency

Use this reference when a Convex application intends HTTP actions/BFF handlers to be its authenticated product boundary.

## Exposure model

An exported `query(...)` or `mutation(...)` is a public Convex function even when the frontend normally calls an authenticated HTTP route. A signature check in `http.ts` does not protect a separate public query.

A query that accepts caller-provided identity such as `telegram_user_id`, then checks that identity's membership, is still bypassable if it never verifies the signed identity at the same boundary. Knowing or guessing a valid identity and tenant can become an IDOR.

Preferred split:

- Product implementation: `internalQuery` / `internalMutation`.
- Authenticated HTTP action: verify Telegram/session/API credentials, derive actor and tenant, then call the internal function.
- Public test wrapper: only if needed, reject every non-`smoke_` tenant or identity before invoking the shared handler.
- Do not retain a caller-supplied production identity override in the public wrapper.

Share one handler function between internal and smoke wrappers; do not duplicate a large dashboard implementation.

### Shared-handler typing pitfall

When extracting an inline Convex handler, do not type its context as `any`. That removes the query builder's contextual typing from database results and can produce a cascade of unrelated-looking `TS7006` callback errors plus `Map<unknown, unknown>` failures across a large handler. Import and use generated `QueryCtx` (or `MutationCtx` for mutations) on the shared function instead of annotating dozens of callbacks.

```ts
import type { QueryCtx } from "./_generated/server";

async function dashboardHandler(ctx: QueryCtx, args: DashboardArgs) {
  // shared implementation
}
```

## Default-deny contract

Add a static contract that inventories every exported `query(...)` using the TypeScript AST. The test should fail unless the initializer explicitly contains a smoke guard. Production functions disappear from this inventory because they use `internalQuery(...)`.

Discover source modules dynamically from the Convex directory instead of maintaining a hand-written filename array. Exclude generated/config/schema files deliberately. A static module list turns every newly added file into a potential default-deny bypass.

Keep focused assertions for high-risk paths:

- the production implementation is internal;
- the public wrapper has no production identity argument;
- HTTP handlers reference only internal function names;
- direct tenant/user/document/audit/report reads reject non-smoke data.

AST inspection is preferable to slicing source with regex: a helper definition after the export can otherwise create a false GREEN. If the repository already has a regex/source-slicing contract, keep the public wrapper deliberately auditable: destructure `tenant_id` and call `assertSmokeTenant(ctx, tenant_id)` directly in the export block rather than hiding the guard behind a generic `args` object. Treat that explicit source shape as part of the security contract; do not weaken the test merely to accommodate an equivalent but opaque implementation.

When handlers are split out of a monolith, update static contracts to load all authoritative handler modules dynamically. Scope each assertion to its target export or initializer. Do not concatenate files and then assert textual ordering across them: that order is artificial. Assert dispatcher-call order in the dispatcher and feature behavior inside the feature module.

## Callback idempotency

For external worker callbacks, dedupe before every side effect:

1. Producer sends an optional stable idempotency key derived from the durable job ID and event type, e.g. `ocr:<job_id>:extraction.recorded`.
2. Store the key on the event row and index `(tenant, idempotency_key)`.
3. At mutation start, look up the existing event. If found, return its ID with `deduplicated: true`.
4. Only after the miss should code insert the event, materialize extraction/domain rows, append audit events, and schedule notifications.

Do not dedupe OCR only by `document_id`: a legitimate reprocessing of the same document must create a new extraction. A synchronous path without a stable request/job ID should retain non-deduped semantics unless the caller explicitly supplies a key.

Convex indexes accelerate lookup but are not SQL-style uniqueness constraints. Keep lookup and insert in one serializable mutation, and load-test concurrent duplicate delivery.

## Verification sequence

1. Capture baseline `git status` before editing, especially in a shared worktree.
2. Run the contract before implementation and retain RED evidence.
3. Implement internal/shared/smoke wrappers.
4. Run the focused contract to GREEN.
5. Run the exact deployment-qualified Convex typecheck/codegen command required by the project. If a codegen run reports transient intermediate binding errors but leaves regenerated files, run plain `tsc --noEmit` as a diagnostic and then repeat the exact required command for authoritative evidence; only the final exit code supports a success claim.
6. Run focused worker tests and the frontend/miniapp production build.
7. Re-run the focused contract plus `git diff --check`, and inventory HTTP references to prove zero production references to public queries.
8. Inspect actual `git diff` after delegated or interrupted implementation. In a concurrently modified worktree, do not revert unrelated changes; distinguish authorized manual edits from generated-file changes caused by required codegen.
9. Do not deploy until an independent reviewer verifies callers and boundary coverage.
