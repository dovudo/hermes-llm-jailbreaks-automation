# Auditing headless / agent write paths against the UI path

Applies whenever a product grows a second way to write the same tables: an AI
copilot, an agent adapter, a background job, a batch importer, an admin script,
or an MCP/RPC surface. The UI path accumulated its guards over months. The new
path is written in one wave and silently inherits none of them.

The governing invariant:

> Anything the UI enforces before a write, the machine path enforces too.
> Same rows, no weaker path, idempotent.

Everything below was CONFIRMED on a real Next.js + Drizzle codebase where an AI
copilot ("SPHERIK") gained the ability to create projects, hire crew, and seed a
pre/production/post workspace without `auth()`.

## Architecture that makes the audit tractable

Do not let the machine path re-implement the writes, and do not try to reuse the
framework-bound server actions (they call `auth()` and `revalidatePath`).

Extract a **session-agnostic core**:

```
UI "use server" action            headless adapter
  auth() + ownership                explicit actorUserId + ownership
  revalidatePath                    no framework calls
        └────────────┬───────────────┘
                     ▼
        core: pure fn(tx, { actorUserId, ... })
        no auth(), no next/cache, writes + audit log in the caller's tx
                     ▼
              the same tables
```

Then the audit question collapses from "are these two paths equivalent?" to
"does every caller of the core apply the policy the core deliberately omits?"

Deliberate omission is fine and is good SRP (the core should not know about
sessions), but it MUST be written down, because it converts into an IDOR the
moment someone adds a caller.

## The five hypotheses worth testing every time

Give these to a read-only subagent verbatim; they map to real findings.

**H-A IDOR / ownership.** Can any exported function write to a resource the
actor does not own? If the core omits ownership by design, verify EVERY caller
checks. Specifically check whether a caller-supplied *template / batch payload*
can carry a foreign resource id (if the template type has no `projectId` field
and the code always uses `input.projectId`, this is refuted — say so).

**H-B moderation / privilege bypass.** The UI calls something like
`assertNotSuspended`. Does the headless path? Compare semantics exactly, not by
name: which suspension kinds block, do lifted/expired ones block, is a
warning-level record allowed through.

**H-C input validation.** Unvalidated enum values reaching Postgres (a hard
error, so this is a build/DoS vector plus a driver-message leak), unbounded
strings, uncapped arrays that seed unbounded rows inside one transaction,
negative/NaN positions and amounts, raw `sql` interpolation, prototype-pollution
keys in jsonb merges.

**H-D transaction integrity.** Any write + audit-log pair outside one
transaction; any check-then-act.

**H-E audit trail.** Every mutation appends an event with the REAL actor.

## Finding class 1: consent forgery via a schema default

The highest-severity finding of the session, and the one most likely to recur.

Shape:

- A join table records that a person is attached to a resource
  (`project_credits`: talent on a film).
- Its `status` column defaults to `accepted` at the **schema** level.
- A **public** surface renders rows filtered on `status = 'accepted'`
  (`/resume/[slug]` — the person's public filmography).
- The UI only ever writes `accepted` at the end of a real consent flow
  (offer approved), and records `invitedByUserId` + `respondedAt`.
- The new machine path inserts with the schema default.

Result: the agent can publish any person as crew on any project they never
agreed to. It is a consent/integrity bug that reads as a harmless insert.

Fix shape:

```ts
// Consent state. Defaults to "pending".
// SECURITY: "accepted" is rendered publicly. Only a flow carrying real consent
// may pass it. Machine callers leave the default.
status?: ProjectCreditStatus;

const status = input.status ?? "pending";
await tx.insert(credits).values({
  ...,
  status,
  invitedByUserId: input.invitedByUserId ?? input.actorUserId,
  respondedAt: status === "pending" ? null : new Date(),
});
```

Self-consent (the creator crediting their own profile) legitimately stays
`accepted` — pass it explicitly so the intent is visible in the code.

**Then audit every OTHER writer of that table.** In this codebase the *main UI
project-creation path* also wrote `accepted` with a NULL inviter and NULL
`respondedAt`, and three more sites set `accepted` without `respondedAt`. The
agent path was the loudest instance of a bug the product already had. Grep:

```
grep -rn "insert(<table>)" src/lib | grep -v test
```

and diff each site's status/inviter/timestamp columns against each other.

Generalized rule: **a permissive schema default plus a public read filter is a
latent authorization bug.** Anywhere a column's default value is also the value
that grants visibility or capability, every insert site must set it explicitly.

## Finding class 2: the guard that exists on one path only

`assertNotSuspended` was called by the UI and simply absent from the adapter, so
a banned account kept working through the agent.

Two-step fix, and the second step is the one that lasts:

1. Enforce it at every headless entry point.
2. **Extract one shared predicate so the two can never drift.** A copy-paste of
   the rule into the adapter is a finding in its own right ("behaviorally
   equivalent today"), because a future change to the blocking rule leaves a
   headless bypass behind.

```ts
// lib/mod/suspension.ts — single source of truth, db injected
export async function isSuspendedWith(db: Selectable, userId: string) { ... }

// UI guard throws, adapter returns {ok:false}; both call the predicate.
```

Inject the db handle rather than importing the real pool, so a background job,
cron, or in-memory test DB can call it.

## Finding class 3: check-then-act idempotency

"Skip if the workspace already has stages" executed **outside** the transaction,
and the table had only a plain index on `(project_id, phase)`, no unique key. Two
concurrent calls both observe an empty workspace and both seed it.

No-migration fix: move the existence check inside the transaction behind a row
lock on the parent.

```ts
await db.transaction(async (tx) => {
  await tx.select({ id: projects.id })
    .from(projects).where(eq(projects.id, projectId)).for("update");
  const existing = await tx.select(...).limit(1);
  if (existing.length) return { skipped: true };
  ...
});
```

Prefer a unique constraint when a migration is acceptable; the lock is the
no-migration option.

## Validating a caller-supplied template

When the machine path accepts a structured payload that becomes many rows, hold
it to the UI's standard and cap it:

- validate every enum field with the SAME type guard the UI uses
  (`isPhase`, `isBlockType`) — an out-of-enum value is a hard Postgres error
  that aborts the build and returns the driver message to the caller;
- require non-empty titles, but distinguish "absent" (fall back to a default)
  from "supplied but blank" (reject);
- cap array lengths so one call cannot seed unbounded rows in one transaction.

## Do not persist display copy from a machine path

An i18n gate caught the seeded stage titles ("Pre-production", ...) being written
into the DB as English strings. The UI already rendered phase labels via `t()`
from the phase key, so the stored title was redundant copy. Default such fields
to the **technical key** and let the UI translate. Fixing the gate honestly beat
updating the baseline.

## Reporting

Report REFUTED hypotheses with file:line evidence too. "IDOR refuted: the
template type has no projectId field, all four writes call `actorOwnsProject`"
is as valuable as a finding, because it stops the next reviewer re-deriving it.
