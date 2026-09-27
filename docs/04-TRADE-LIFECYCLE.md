# 04 — Trade Lifecycle

**Work item:** WI-F (`WO-TRON-D1`)
**Owns:** this document, `docs/04-TRADE-LIFECYCLE.md`, only.
**Source of truth:** `PID.md` §7 (Canonical Trade Lifecycle) and §8 (Order and Action State). This document restates, sequences and designs state machines against those sections; the PID itself is authoritative if any conflict is ever perceived.

This document does not define contract shape (owned by WI-B, `05-CONTRACTS.md`), the check catalogue (owned by WI-C, `06-CHECKS-CATALOGUE.md`), the architecture/capability model (owned by WI-E, `03-ARCHITECTURE.md` / `10-CAPABILITIES.md`), or the event-type catalogue (owned by WI-G, `09-EVENTS-AND-GRAYLOG.md`). Where this document names an event-style word for consistency (§2.2), that word is illustrative cross-reference only, not a claim on WI-G's catalogue.

---

## 0. Authority and scope of this document

**Central Architecture ruling for this run (recorded here for traceability).** Unlike the other Wave 2 work items, WI-F is the work item authorised to design the actual action/order/position state machines, transitions, and the action/intent/broker-order/position-state distinctions required by PID §8. This is this document's job, not something deferred elsewhere.

**Vocabulary reuse (binding constraint on this document).** This document reuses, and does not redefine, vocabulary already committed by WI-B:

- The **broker order state** vocabulary used throughout §2.4 is copied verbatim, in full and with no additions, renames or omissions, from `schemas/tron.execution_report.v1.json`'s `order_state` enum: `New`, `PartiallyFilled`, `Filled`, `Canceled`, `Rejected`, `Expired`.
- The **FALCON action** vocabulary used as the input to §2.2 is copied verbatim, in full and with no additions, renames or omissions, from `schemas/falcon.trade_action.v1.json`'s `action` enum: `OPEN`, `CLOSE`, `MODIFY`, `CANCEL`.

Both schemas explicitly say they do not encode lifecycle semantics or transition rules and defer that to this document; this document is the corresponding fulfilment, not a reinterpretation.

**Scope: OPEN only.** PID §7 titles its 18-step sequence "the canonical **OPEN** lifecycle." This document designs that OPEN pipeline in full. `CLOSE`, `MODIFY` and `CANCEL` share the same ingestion handling as `OPEN` through step 4 (INGEST/VALIDATE/EXPIRE/DEDUPLICATE — see §2.2), but their downstream eligibility, selection, negotiation, execution and conflict semantics are listed as **BACKLOG** capabilities in PID §17 ("CLOSE", "MODIFY", "CANCEL", "supersession", "conflict handling") and are **not** designed by this document. Inventing that design here would be exactly the kind of silent scope expansion PID §25/§27 forbids an Engineer from doing.

**OPEN-decision discipline.** PID §19 items marked "Proposed" are not Product Authority. Several steps below directly invoke `DEC-OPEN-nn` items. In every such case, the *step's existence and position in the pipeline* is **DEFINED** (PID §7 itself is settled — the 18-step sequence and its ordering is not in question), while the *specific policy that step applies* is flagged **OPEN** exactly where PID §19 says so. This document never upgrades an OPEN proposal to a decided rule, and never silently picks one of the proposed policies and presents it as decided.

---

## 1. The 18-step canonical OPEN lifecycle (PID §7)

| # | Step | What it does | OPEN flag | Traces to |
|---|---|---|---|---|
| 1 | **INGEST** | Consume a candidate `falcon.trade_action.v1` from the board. | — | HR-07 (board is transport, not durable truth) |
| 2 | **VALIDATE** | Validate the action's contract against its canonical schema. An invalid action is rejected, not processed further. | — | HR-04, HR-05 |
| 3 | **EXPIRE** | Reject any action whose `valid_until_ms` has passed. | — | — |
| 4 | **DEDUPLICATE** | Reject an action that is a duplicate of one already processed for the same `action_id` (idempotency at the ingestion boundary). | — | HR-13 |
| 5 | **DETERMINE ELIGIBILITY** | Apply deterministic, configuration-driven eligibility rules to decide whether a candidate may be considered at all this cycle. | — | HR-02, HR-03 |
| 6 | **APPLY THRESHOLD** | Apply configured confidence/quality thresholds to eligible candidates. | — | HR-02 |
| 7 | **RESOLVE CONFLICT** | Resolve a conflict between qualifying candidates for the same instrument (e.g. simultaneous qualifying LONG and SHORT). The step's existence is DEFINED; its exact resolution policy is **DEC-OPEN-01** (proposed: skip the instrument for that selection cycle) — **OPEN**, not decided. | **OPEN (DEC-OPEN-01)** | — |
| 8 | **RANK** | Rank surviving candidates against each other using deterministic, configured criteria. The step's existence is DEFINED; it touches **DEC-OPEN-02** (existing-position policy — proposed MVP: one position per instrument) and **DEC-OPEN-08** (cross-strategy confidence calibration — exact contract not decided), both of which govern *how* ranking may use confidence and existing-position facts. Both are **OPEN**. | **OPEN (DEC-OPEN-02, DEC-OPEN-08)** | HR-02, HR-03 |
| 9 | **SELECT** | Choose the candidate(s) to carry forward from the ranked set. Same OPEN dependencies as RANK (step 8) apply, since selection consumes the same ranking. | **OPEN (DEC-OPEN-02, DEC-OPEN-08)** | HR-02, HR-03 |
| 10 | **NEGOTIATE** | Transform the selected canonical action into a broker-valid `tron.trade_intent.v1`: resolve broker instrument symbol, convert canonical quantity to a negotiated broker-valid quantity, and carry/negotiate requested protection. This is TRON's negotiation boundary. | — | HR-09 |
| 11 | **SNAPSHOT REQUIRED STATE** | Capture a single consistent execution snapshot of broker/account/instrument state that all pre-trade checks will run against. | — | HR-06, HR-14 |
| 12 | **RUN PRE-TRADE CHECKS** | Run the applicable ordered check stages (PID §12) over the snapshot from step 11. All checks in a stage run; a stage failure blocks later stages and the trade. | — | HR-01, HR-02, HR-11, HR-14 |
| 13 | **JOURNAL EXECUTION INTENT** | Durably journal the intent and the checks decision **before** any broker submission is attempted. This is a hard gate: step 14 must not begin until this step has durably completed. | — | HR-08, HR-15 |
| 14 | **EXECUTE** | Submit the permitted order to the broker via the Broker Adapter. Submission is idempotent with respect to the originating `action_id`/`intent_id`: a retry of this step for an intent that has already reached this step or beyond must not silently place a second order. | — | HR-08, HR-13 |
| 15 | **READ BACK BROKER STATE** | Read back the broker's own view of the resulting order (broker order id, `order_state`, fills) to populate a `tron.execution_report.v1`. | — | HR-06 |
| 16 | **VERIFY SL/TP PROTECTION** | Verify, from the read-back broker state, that the mandatory stop-loss and take-profit protection required by HR-01 actually exists at the broker for this OPEN. A failure here is a **critical execution condition** — see the failure-mode statement below — and may never be silently accepted. | — | HR-01 |
| 17 | **RECONCILE** | Reconcile TRON's local view against broker truth. Broker-ledger authority itself is **DECIDED** (PID §5 HR-06, PID §19 DEC-OPEN-09): the broker ledger wins on conflict unless the broker response is unavailable or demonstrably invalid. The background reconciliation **cadence** beyond an immediate post-execution reconciliation (e.g. a periodic full sweep) remains **OPEN** under DEC-OPEN-09 and is not decided by this document. | **OPEN (DEC-OPEN-09, cadence only — the ledger-authority clause is DECIDED)** | HR-06, HR-15 |
| 18 | **RECORD OUTCOME** | Durably record the final outcome of this action's lifecycle traversal (success, blocked-pre-execution, or a flagged post-execution condition), correlated end-to-end. | — | HR-15 |

### Failure-mode statement (PID §7, restated as binding design constraint)

- **Failure before execution (steps 1–13) produces no new broker risk.** No order has been submitted; the action/intent is recorded as blocked and the lifecycle for that candidate ends at step 18 without ever reaching the broker.
- **Failure after broker submission (from step 14 onward) enters an explicit recovery/reconciliation path.** It is never treated as equivalent to a pre-execution rejection, because broker-side state may now exist that TRON must account for.
- **A failed protection verification (step 16) is a critical execution condition and may never be silently accepted.** It does not resolve to a quiet "trade complete." It forces the recovery/reconciliation path described in §2.3 and §2.5, and the position affected is never represented as a normal steady-state open position (see §2.5, `OPEN_UNPROTECTED`) until protection is confirmed or the condition is explicitly and durably recorded as an unresolved critical discrepancy (HR-15).

---

## 2. The four state representations (PID §8)

PID §8 requires TRON to distinguish four separate state representations and forbids collapsing them into one ambiguous `status` field. Each is a genuinely different question:

| Representation | Question it answers |
|---|---|
| FALCON action state | "What has TRON done with this incoming candidate action, up to and including handing it to negotiation?" |
| TRON intent state | "Where is this negotiated intent in TRON's own execution pipeline?" |
| Broker order state | "What does the broker say about the order TRON submitted?" (WI-B vocabulary, exactly) |
| Resulting position state | "What does the instrument's position look like as a consequence of one or more orders?" |

They are correlated (§3) but never merged. A single `status` field cannot answer all four questions at once without losing information that HR-15 requires to be reconstructable.

### 2.1 FALCON action state

Tracks a `falcon.trade_action.v1` (keyed by `action_id`) from ingestion through the point TRON hands it to negotiation. Applies to all four `action` values at ingestion (steps 1–4); only `OPEN` continues past step 4 in this document's scope (see §0).

**States**

| State | Meaning | Terminal? |
|---|---|---|
| `RECEIVED` | Ingested (step 1), not yet validated. | No |
| `REJECTED` | Failed contract VALIDATE (step 2). | Yes |
| `PENDING` | Validated, not expired, not a duplicate; eligible for (re-)evaluation each selection cycle. | No |
| `EXPIRED` | EXPIRE (step 3) found `valid_until_ms` in the past. | Yes |
| `DUPLICATE` | DEDUPLICATE (step 4) found this `action_id` already processed. | Yes |
| `SKIPPED` | Considered this cycle at steps 5–9 but not carried forward — ineligible, under threshold, conflict-skipped (**DEC-OPEN-01**, OPEN), or out-ranked. Cycle-scoped, not permanent. | No (loops back to `PENDING`) |
| `SELECTED` | Chosen at SELECT (step 9). | No |
| `NEGOTIATING` | NEGOTIATE (step 10) in progress. | No |
| `NEGOTIATION_FAILED` | NEGOTIATE (step 10) could not produce a valid intent (e.g. no broker symbol mapping). No broker risk incurred — folds back to `SKIPPED`/`PENDING` for possible re-evaluation next cycle, until `EXPIRED`. | No |
| `NEGOTIATED` | NEGOTIATE (step 10) completed; a `tron.trade_intent.v1` now exists. FALCON-action-state tracking for this `action_id` ends here — see §2.2. | Yes (handoff) |

**Transitions**

```text
(ingest)      -> RECEIVED
RECEIVED      -> REJECTED            [VALIDATE fails]
RECEIVED      -> PENDING             [VALIDATE passes]
PENDING       -> EXPIRED             [EXPIRE: valid_until_ms passed]
PENDING       -> DUPLICATE           [DEDUPLICATE: already processed]
PENDING       -> SKIPPED             [ELIGIBILITY/THRESHOLD fail, or
                                       RESOLVE CONFLICT skips (DEC-OPEN-01, OPEN), or
                                       not chosen at RANK/SELECT]
SKIPPED       -> PENDING             [re-evaluated on a later cycle, still valid]
PENDING       -> SELECTED            [SELECT chooses this action]
SELECTED      -> NEGOTIATING         [NEGOTIATE begins]
NEGOTIATING   -> NEGOTIATED          [NEGOTIATE succeeds -> handoff to TRON intent state]
NEGOTIATING   -> NEGOTIATION_FAILED  [NEGOTIATE cannot produce a valid intent]
NEGOTIATION_FAILED -> SKIPPED        [eligible for re-evaluation next cycle]
```

`REJECTED`, `EXPIRED`, `DUPLICATE` and `NEGOTIATED` are the only terminal states for a given `action_id`; everything else in the `PENDING`/`SKIPPED` loop is a cycle-scoped, re-evaluable condition until one of those four is reached.

Consistency with PID §15's illustrative event names: `RECEIVED`≈`action.received`, `REJECTED`≈`action.rejected`, `EXPIRED`≈`action.expired`, `DUPLICATE`≈`action.duplicate`, `SELECTED`≈`action.selected`. Naming the actual event catalogue is WI-G's (`09-EVENTS-AND-GRAYLOG.md`).

### 2.2 TRON intent state

Tracks a `tron.trade_intent.v1` (keyed by `intent_id`) from creation (NEGOTIATE, step 10, completing) through RECORD OUTCOME (step 18).

**States**

| State | Meaning | Terminal? |
|---|---|---|
| `CREATED` | Intent produced at the end of NEGOTIATE (step 10). | No |
| `SNAPSHOT_TAKEN` | SNAPSHOT REQUIRED STATE (step 11) captured a consistent snapshot. | No |
| `CHECKS_RUNNING` | RUN PRE-TRADE CHECKS (step 12) in progress. | No |
| `CHECKS_FAILED` | A check stage failed or errored (fail-closed, HR-14). No broker risk incurred. | No (proceeds directly to `OUTCOME_RECORDED`) |
| `CHECKS_PASSED` | All applicable check stages passed. | No |
| `JOURNALED` | JOURNAL EXECUTION INTENT (step 13) durably completed. **Hard gate (HR-08): EXECUTE (step 14) must never be attempted from any state other than `JOURNALED`.** | No |
| `SUBMITTED` | EXECUTE (step 14) has been sent to the Broker Adapter. **Idempotency gate (HR-13): a repeat EXECUTE attempt for an `intent_id` already at `SUBMITTED` or beyond must be a no-op / replay, never a second submission.** | No |
| `SUBMIT_REJECTED` | Broker rejected the order pre-fill (`order_state = Rejected`, no `broker_order_id` ever went live). No new broker risk — the order never existed at the broker as a live risk position. | No (proceeds to `OUTCOME_RECORDED`) |
| `SUBMIT_UNCERTAIN` | EXECUTE returned an ambiguous or missing acknowledgement (timeout, no clear response). Broker-state uncertainty affecting execution safety: **fails closed for new risk (HR-14)** — TRON must not submit again or assume success; it must resolve this uncertainty via RECONCILE (step 17) before the intent can progress. | No |
| `READ_BACK` | READ BACK BROKER STATE (step 15) completed; broker order id and `order_state` are known (see §2.4). | No |
| `PROTECTION_VERIFIED` | VERIFY SL/TP PROTECTION (step 16) confirmed both legs exist at the broker (HR-01). | No |
| `PROTECTION_FAILED` | VERIFY SL/TP PROTECTION (step 16) could not confirm both legs. **Critical execution condition (PID §7); never silently accepted.** Forces the recovery/reconciliation path — it is not a normal terminal failure. | No |
| `RECONCILED` | RECONCILE (step 17) completed: local view matches broker truth, or a discrepancy has been explicitly surfaced per HR-06 (broker wins unless unavailable/demonstrably invalid). Reconciliation *cadence* beyond immediate post-execution reconciliation is **OPEN (DEC-OPEN-09)**. | No |
| `OUTCOME_RECORDED` | RECORD OUTCOME (step 18) durably recorded. | **Yes** |

**Transitions**

```text
CREATED         -> SNAPSHOT_TAKEN
SNAPSHOT_TAKEN  -> CHECKS_RUNNING
CHECKS_RUNNING  -> CHECKS_FAILED      [any stage FAIL/ERROR, fail-closed]
CHECKS_RUNNING  -> CHECKS_PASSED      [all stages PASS]
CHECKS_FAILED   -> OUTCOME_RECORDED   [no broker risk incurred]
CHECKS_PASSED   -> JOURNALED          [HR-08 gate satisfied]
JOURNALED       -> SUBMITTED          [EXECUTE; HR-13 idempotent per intent_id]
SUBMITTED       -> SUBMIT_REJECTED    [broker rejects pre-fill]
SUBMITTED       -> SUBMIT_UNCERTAIN   [ambiguous/no ack; fails closed, HR-14]
SUBMITTED       -> READ_BACK          [broker acknowledged; order_state known]
SUBMIT_UNCERTAIN -> READ_BACK         [subsequent RECONCILE resolves the ambiguity]
SUBMIT_UNCERTAIN -> RECONCILED        [ambiguity resolved directly via reconciliation,
                                        e.g. broker confirms no order was ever created]
SUBMIT_REJECTED -> OUTCOME_RECORDED   [no broker risk incurred]
READ_BACK       -> PROTECTION_VERIFIED [step 16 passes]
READ_BACK       -> PROTECTION_FAILED   [step 16 fails; critical, HR-01]
PROTECTION_VERIFIED -> RECONCILED     [step 17]
PROTECTION_FAILED   -> RECONCILED     [step 17, entered via the mandatory recovery path;
                                        any residual discrepancy is surfaced, not hidden]
RECONCILED      -> OUTCOME_RECORDED   [step 18]
```

Note on `CHECKS_FAILED`/`SUBMIT_REJECTED` reaching `OUTCOME_RECORDED` directly: RECORD OUTCOME (step 18) always runs, whether the outcome is "blocked pre-execution", "rejected by broker", or "executed and reconciled" — PID §7 does not make step 18 conditional on success, and HR-15 requires every material decision, including blocks and rejections, to be reconstructable.

### 2.3 Broker order state

This is exactly WI-B's `order_state` enum from `schemas/tron.execution_report.v1.json` — no additions, renames or omissions: `New`, `PartiallyFilled`, `Filled`, `Canceled`, `Rejected`, `Expired`. This document documents the realistic transition graph between them, using FIX-aligned semantics per PID §8's own framing (market-standard/FIX-aligned terminology, **without adopting the FIX wire protocol**).

**Transition graph**

```text
(order accepted by broker) -> New
New             -> PartiallyFilled   [one or more, but not all, of requested_quantity filled]
New             -> Filled            [entire requested_quantity filled in one or more fills]
PartiallyFilled -> Filled            [remaining leaves_quantity filled]
New             -> Rejected          [broker/adapter rejects pre-acceptance or on submission]
New             -> Canceled          [cancelled before any fill]
PartiallyFilled -> Canceled          [cancelled after partial fill; leaves_quantity is not filled]
New             -> Expired           [order's broker-side time-in-force lapses unfilled]
```

`Filled`, `Canceled`, `Rejected` and `Expired` are terminal: once reached, a given broker order id emits no further `order_state` transitions. Whether a broker/order-type combination also permits `PartiallyFilled -> Expired` (a partially-filled order whose remaining leaves expire under its time-in-force) is broker/order-type-dependent behaviour, not a TRON-invariant transition; where an adapter reports it, it is a legitimate observed instance of the same terminal-`Expired` rule above, not a new state.

`order_state` says nothing on its own about whether SL/TP protection exists (§1, step 16) or about TRON's own intent-level state (§2.2) — those are read from `tron.trade_intent.v1`/TRON's local state and cross-referenced by `intent_id`/`correlation_id`, never inferred from `order_state` alone.

### 2.4 Resulting position state

The layer above individual orders: what an instrument's position looks like as a consequence of one or more orders resolving against it. In scope here only for the OPEN path; full position lifecycle including closing/reduction is **BACKLOG** (PID §17: "CLOSE", position-adjacent items) and is not designed by this document beyond what is needed to make the OPEN pipeline's resulting state well-defined.

**States**

| State | Meaning |
|---|---|
| `NO_POSITION` | No open position exists for this instrument (initial/default). |
| `OPEN_PENDING` | An OPEN intent has reached `SUBMITTED`/`READ_BACK` (order state `New`) for this instrument; no confirmed fill yet. |
| `PARTIALLY_FILLED` | Broker order state `PartiallyFilled`: some quantity is now live for this instrument, more expected. |
| `OPEN_UNPROTECTED` | A fill exists (order state `PartiallyFilled` or `Filled`) but SL/TP protection verification (step 16) has not yet passed. **Not a steady state** — per PID §7, this condition may never be silently accepted; the system must actively drive it to `OPEN_PROTECTED` or surface it as an unresolved critical discrepancy (HR-15), never simply leave it representing "open" the way `OPEN_PROTECTED` does. |
| `OPEN_PROTECTED` | A fill exists and protection has been verified present at the broker (HR-01). This is the only state in which a position is considered a normal, safely-open resting position. |

**Transitions**

```text
NO_POSITION       -> OPEN_PENDING       [OPEN intent SUBMITTED for this instrument]
OPEN_PENDING      -> PARTIALLY_FILLED   [broker order_state -> PartiallyFilled]
OPEN_PENDING      -> OPEN_UNPROTECTED   [broker order_state -> Filled, protection not yet verified]
PARTIALLY_FILLED  -> PARTIALLY_FILLED   [additional partial fills, still not fully filled]
PARTIALLY_FILLED  -> OPEN_UNPROTECTED   [broker order_state -> Filled, protection not yet verified]
OPEN_UNPROTECTED  -> OPEN_PROTECTED     [step 16 verification passes]
OPEN_PENDING      -> NO_POSITION        [order Rejected/Canceled/Expired with zero fill]
```

**DEC-OPEN-02 flag (OPEN, not decided).** Whether TRON may add to an existing position — i.e. whether SELECT (step 9, §1) may choose a further OPEN candidate for an instrument already at `OPEN_PENDING`, `PARTIALLY_FILLED`, `OPEN_UNPROTECTED` or `OPEN_PROTECTED` — is exactly **DEC-OPEN-02**. The proposed MVP policy (one position per instrument) would mean SELECT must treat any of those four states as blocking a further OPEN for that instrument, but that is a proposal, not a decision; this document flags the boundary at which that policy would apply without deciding it.

Position reduction/closing states (e.g. `CLOSING`, partial-close quantities, return to `NO_POSITION` via a CLOSE rather than a zero-fill cancellation) are out of this document's scope per PID §17's BACKLOG listing and §0 above.

---

## 3. Cross-representation correlation

The four representations are distinct but must remain reconstructable as one continuous chain per HR-15. The chain is:

```text
action_id  →  intent_id  →  broker_order_id / execution_id(s)  →  instrument position state
```

- `tron.trade_intent.v1.source_action_id` links TRON intent state back to FALCON action state.
- `tron.execution_report.v1.intent_id` and `.action_id` link broker order state back to both prior representations.
- `correlation_id` is carried on `tron.trade_intent.v1`, `tron.execution_report.v1` and `tron.event.v1`, and is the field HR-15 relies on to reconstruct the full chain independent of which specific identities exist for a given record (per `tron.event.v1`'s "where those identities exist" design, `05-CONTRACTS.md` §8).
- Resulting position state (§2.4) is derived by TRON from the sequence of broker order states observed for a given instrument; it is not itself carried as a field on any one message in this contract set — it is TRON's own durable local operational state (PID §14.2).

No implementation may collapse these into a single `status` field on any one record (PID §8, restated as a hard constraint on this design).

---

## 4. Hard Rule traceability

| Hard Rule | Where enforced in this lifecycle |
|---|---|
| HR-01 (SL/TP mandatory, verified) | Step 16 VERIFY SL/TP PROTECTION (§1); TRON intent states `PROTECTION_VERIFIED`/`PROTECTION_FAILED` (§2.2); position state `OPEN_UNPROTECTED` is explicitly non-steady-state (§2.4). |
| HR-02 (no hard-coded operational config) | Steps 5, 6, 8, 9, 12 (§1) — eligibility, threshold, ranking, selection and checks are all configuration-driven, not hard-coded. |
| HR-03 (no AI/discretionary judgement) | Steps 5–9 (§1) — deterministic, configuration-driven only. |
| HR-04 / HR-05 (canonical timestamp/decimal representation) | Step 2 VALIDATE (§1) rejects any action failing these contract-level constraints before any lifecycle state is created. |
| HR-06 (broker ledger authoritative) | Step 15 READ BACK BROKER STATE and step 17 RECONCILE (§1); broker order state (§2.3) is read, never inferred or overridden locally. |
| HR-08 (durable journal before submission) | Step 13 JOURNAL EXECUTION INTENT is a hard gate before step 14 EXECUTE; TRON intent state `JOURNALED` must precede `SUBMITTED` (§2.2) — no transition skips this gate. |
| HR-09 (no broker lots upstream) | Step 10 NEGOTIATE (§1) is the sole point where canonical quantity becomes a negotiated broker-valid quantity. |
| HR-11 (instrument must be tradable) | Step 12 RUN PRE-TRADE CHECKS (§1), stage 3 per PID §12; a non-tradable instrument blocks before step 13/14 are ever reached. |
| HR-13 (idempotent execution) | Step 4 DEDUPLICATE (§1, action-level); the `SUBMITTED` gate in TRON intent state, explicitly stated as a no-op-on-retry boundary (§2.2). |
| HR-14 (fail closed on uncertainty) | TRON intent state `CHECKS_FAILED` and `SUBMIT_UNCERTAIN` (§2.2) both explicitly block new risk rather than assume success. |
| HR-15 (reconstructable decisions) | Step 18 RECORD OUTCOME (§1) always runs, on every path (§2.2 note); §3's correlation chain is the mechanism. |
| HR-16 (no external instruction to trade) | Not a lifecycle-step concern — no step in §1 accepts an external trigger other than the FALCON board at step 1 (INGEST); NEO has no place in this state machine at any step. |

---

## 5. OPEN decisions referenced in this document

None of the following are decided by this document. Each is carried exactly as PID §19 states it, flagged wherever it is touched above.

| ID | Status here | Touches |
|---|---|---|
| DEC-OPEN-01 | **OPEN** — proposed: skip the instrument for the selection cycle. | Step 7 RESOLVE CONFLICT (§1); FALCON action state `SKIPPED` (§2.1). |
| DEC-OPEN-02 | **OPEN** — proposed MVP: one position per instrument. | Steps 8–9 RANK/SELECT (§1); resulting position state boundary (§2.4). |
| DEC-OPEN-08 | **OPEN** — cross-strategy confidence calibration contract not decided. | Steps 8–9 RANK/SELECT (§1). |
| DEC-OPEN-09 | **SPLIT**: broker-ledger authority is **DECIDED** (HR-06); background reconciliation *cadence* beyond immediate post-execution reconciliation is **OPEN**. | Step 17 RECONCILE (§1); TRON intent state `RECONCILED` (§2.2). |

