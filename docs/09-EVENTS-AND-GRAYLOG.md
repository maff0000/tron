# 09 — Events & Trading Graylog

**Work item:** WI-G (`WO-TRON-D1`)
**Owns:** this document — the journal/spool-then-ship delivery model (PID §14.3) and the event-type catalogue (PID §15). It does not own the `tron.event.v1` envelope schema itself (owned by WI-B — `05-CONTRACTS.md` §8, `schemas/tron.event.v1.json`). That schema deliberately leaves its `event_type` field as a pattern-constrained, dot-namespaced free string rather than a closed enum, exactly so that this document — not the schema — owns and can extend the set of legitimate values. This document supplies that set; it does not redefine the envelope's shape, required fields, or field types.

This document does not define trade-lifecycle transition semantics (owned by WI-F, `04-TRADE-LIFECYCLE.md`), pre-trade check PASS/FAIL/ERROR semantics or the check-ID catalogue (owned by WI-C, `06-CHECKS-CATALOGUE.md`), or capability sequencing (owned by WI-E, `10-CAPABILITIES.md`). Where an event's firing occasion depends on a mechanism one of those documents owns, this document names the occasion only in the terms PID §7/§15 already use, without pre-empting the owning document's design.

Nothing in this document asserts a decided production Graylog placement or topology. Where Trading Graylog is deployed and how it is reached in production is **DEC-OPEN-07** (PID §19) — explicitly **not decided by D1**. This document describes the delivery model TRON's runtime must implement; it does not choose infrastructure.

---

## 1. Journal/spool-then-ship model (PID §14.3)

TRON has two operational persistence concepts relevant here (PID §14; the third, the broker ledger, is authoritative trading truth and is not TRON's own record — PID §14.1):

- **Local journal** (PID §14.2) — TRON's durable, append-oriented operational record. At minimum it records consumed action identity, decision, negotiated intent, check results, broker submission attempt, broker response, protection verification, reconciliation outcome, and **events awaiting shipment**.
- **Trading Graylog** (PID §14.3) — the operational audit and analysis record that NEO and other observers consume (PID §6.2).

The delivery model between them is **journal, then ship**:

1. TRON writes the durable local journal entry (and, for material lifecycle transitions, the corresponding event) first.
2. Events are spooled from the journal and shipped onward to Trading Graylog.

This ordering is load-bearing, not incidental:

- **A Graylog outage must not cause execution history to disappear.** Because the journal is written first and independently of Graylog's availability, an execution history exists durably on the local journal regardless of whether shipment to Graylog has yet succeeded. Events awaiting shipment remain in the journal until delivery succeeds.
- **A Graylog outage alone does not necessarily stop trading, provided the durable local journal remains healthy.** Graylog is a downstream consumer of the journal, not the mechanism that makes execution safe. TRON's execution safety is not conditioned on Graylog's reachability.
- **No execution may occur when the required local durable journal write cannot be made.** This is stated here as an **absolute** — it is load-bearing for everything above it. A healthy Trading Graylog is never a substitute for a journal write that cannot be made, and no fallback or degraded-mode path may permit execution to proceed past a failed or unavailable journal write. This restates PID §14.3 directly and is the same requirement HR-08 enforces structurally ("No execution may proceed unless the intent and decision are durably journalled before broker submission" — PID §5). A journal-write failure is a case where TRON must fail closed for new risk (HR-14).

Where and how Trading Graylog is deployed in production, and the transport by which shipped events reach it, is DEC-OPEN-07 and is not settled here. This document constrains only the *behaviour* TRON's runtime must exhibit around that boundary (journal-first, spool-then-ship, outage-tolerant, journal-write-failure-blocks-execution) — never a specific host, network path, or deployment topology.

---

## 2. The event-type catalogue

`schemas/tron.event.v1.json`'s `event_type` field states its own reasoning:

> "Dot-namespaced event type name (e.g. `action.received`, `execution.filled`). Deliberately not a closed enum in this envelope contract: PID section 15 lists event types 'at minimum', and the full catalogue is owned by WI-G. This contract only constrains the naming shape, not the permitted set of values."

The naming shape the schema enforces is: lowercase, dot-namespaced, at least two segments (pattern `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$`) — e.g. `action.received`, `execution.partial_fill`, `system.degraded`. Every name below conforms to that shape (verified — see §5 of this document's companion evidence, and the self-check recorded in the WI-G handback).

### 2.1 Catalogue

PID §15 states its list "at minimum." The table below restates every event PID §15 names, fixes when each one fires (in the vocabulary PID §7's canonical OPEN lifecycle and PID §12's check-stage model already use, without redefining either), and states what identities it correlates to. Identity field names match `tron.event.v1` exactly (`action_id`, `intent_id`, `order_id`, `execution_id`, `correlation_id`); "where that identity exists" language matches the schema's own conditional-field wording — an absent field means no such identity is applicable to that event, not that it was omitted in error.

| Event type | Fires when | Correlates to |
|---|---|---|
| `action.received` | A candidate action is ingested from the board (PID §7 step 1, INGEST), prior to contract validation. | `action_id`, `correlation_id` |
| `action.rejected` | A consumed action fails contract validation, or is otherwise determined not eligible to proceed (PID §7 step 2 VALIDATE; step 5 DETERMINE ELIGIBILITY where the outcome is rejection rather than simply not being ranked/selected). The exact validation and eligibility mechanics belong to WI-B (schema conformance) and WI-E/WI-F (selection/lifecycle semantics); this catalogue fixes only the event's firing occasion and correlation. | `action_id`, `correlation_id` |
| `action.expired` | A consumed action's validity window (`falcon.trade_action.v1.valid_until_ms`) has passed before the action could be selected or executed (PID §7 step 3, EXPIRE). | `action_id`, `correlation_id` |
| `action.duplicate` | A consumed action is identified as a duplicate of an action already processed (PID §7 step 4, DEDUPLICATE). Supports HR-13 idempotency. | `action_id`, `correlation_id` |
| `action.selected` | An action is chosen to proceed to negotiation by selection/threshold/conflict-resolution/ranking policy (PID §7 steps 5–9). | `action_id`, `correlation_id` |
| `intent.created` | A selected action has been negotiated into an executable `tron.trade_intent.v1` (PID §7 step 10, NEGOTIATE). | `action_id`, `intent_id`, `correlation_id` |
| `check.stage.completed` | All checks in one pre-trade check stage (PID §12) have executed to completion over a consistent snapshot, regardless of individual outcomes. | `action_id`, `intent_id`, `correlation_id` |
| `check.failed` | An individual check, or a check stage, returns a result that blocks the proposed trade (PID §7 step 12; PID §12 — a FAIL, or an ERROR treated as fail-closed under HR-14). Exact PASS/FAIL/ERROR semantics and check IDs are WI-C's territory (`06-CHECKS-CATALOGUE.md`). | `action_id`, `intent_id`, `correlation_id` |
| `execution.submitted` | TRON submits an order to the broker adapter, after the execution intent and decision have been durably journalled (PID §7 steps 13–14; HR-08). | `action_id`, `intent_id`, `order_id` (where the broker has assigned an order identity at submission time — absent otherwise), `correlation_id` |
| `execution.accepted` | The broker acknowledges/accepts the submitted order on read-back (PID §7 step 15, READ BACK BROKER STATE). | `action_id`, `intent_id`, `order_id`, `correlation_id` |
| `execution.rejected` | The broker rejects the submitted order on read-back. | `action_id`, `intent_id`, `order_id` (where an order identity was assigned before rejection — absent otherwise), `correlation_id` |
| `execution.partial_fill` | A broker execution/fill event is read back that partially fills the order (`tron.execution_report.v1` `order_state` = `PartiallyFilled`). | `action_id`, `intent_id`, `order_id`, `execution_id`, `correlation_id` |
| `execution.filled` | A broker execution/fill event is read back that completes the order's fill (`tron.execution_report.v1` `order_state` = `Filled`). | `action_id`, `intent_id`, `order_id`, `execution_id`, `correlation_id` |
| `protection.verified` | Post-execution read-back confirms the mandatory broker-side stop-loss and take-profit protection required by HR-01 is in place as intended (PID §7 step 16). | `action_id`, `intent_id`, `order_id`, `correlation_id` |
| `protection.failed` | Post-execution read-back cannot confirm required SL/TP protection is in place — a critical execution condition (PID §7's closing statement: "may never be silently accepted"). Entry into explicit recovery/reconciliation handling follows (PID §16, CAP-06). | `action_id`, `intent_id`, `order_id`, `correlation_id` |
| `reconciliation.completed` | TRON's view of state has been reconciled against broker truth with no unresolved discrepancy for the scope of that reconciliation pass (PID §7 step 17; PID §4.2). | `action_id`, `intent_id`, `order_id` where the pass is scoped to a specific action/intent/order lineage — absent for a broader sweep-level pass not scoped to one action; `correlation_id` |
| `reconciliation.failed` | Reconciliation surfaces a discrepancy between TRON's view and broker truth that is not resolved by broker state taking precedence (PID §4.2: broker state wins "unless the broker response itself is unavailable or demonstrably invalid"). | as `reconciliation.completed` — action/intent/order identities present where scoped to a specific lineage, absent for a sweep-level finding; `correlation_id` |
| `trade.completed` | The full lifecycle for one action — selection through execution, protection verification, and reconciliation — reaches a recorded terminal outcome (PID §7 step 18, RECORD OUTCOME). | `action_id`, `intent_id`, `order_id`, `execution_id` where a fill occurred, `correlation_id` |
| `system.degraded` | TRON's own operational health degrades in a way material to execution safety (e.g. broker connectivity loss, broker/instrument-state staleness, journal-write impairment, approaching a configured kill condition) — a cross-cutting system-level condition, not intrinsically tied to one action's lineage. | `correlation_id` (an operational/session-scoped correlation handle, since no single action-to-execution chain necessarily applies); `action_id` additionally present where the degraded condition was discovered while handling one specific action |
| `system.halted` | TRON enters a halted/kill-switch state and stops proposing or submitting new execution (PID §13's manual-kill-switch consideration; HR-14's fail-closed posture). | as `system.degraded` |

### 2.2 This catalogue is extensible

PID §15 states its list is "at minimum," and `tron.event.v1`'s `event_type` field is deliberately open-ended for exactly this reason. Consequently:

- The twenty event types above are the current, complete catalogue as of `WO-TRON-D1`. They are not exhaustive for all time.
- Future work items or increments (e.g. as PID §17's capability backlog — CLOSE/MODIFY/CANCEL lifecycle, periodic reconciliation, kill-switch operations, degraded-state handling — is implemented) may need additional dot-namespaced event types.
- Adding a new event type is a change to **this document's catalogue**, not to `tron.event.v1`'s schema — the schema's naming-shape constraint already permits it. This mirrors `05-CONTRACTS.md` §8's own statement that the catalogue is WI-G's to define and extend.
- A new event type must still conform to the naming pattern in §2 above, must still supply `correlation_id`, and must state, when added, which of `action_id`/`intent_id`/`order_id`/`execution_id` apply to it (or that none do), following the same convention as the table above.

---

## 3. Correlation

PID §15: "Correlation must allow reconstruction of an action from ingestion through execution and reconciliation."

`tron.event.v1` implements this by making `correlation_id` the **one field that is always required**, independent of which of `action_id`/`intent_id`/`order_id`/`execution_id` happen to exist for a given event (`05-CONTRACTS.md` §8; HR-15: "Every material execution decision must be reconstructable from durable events, configuration identity and observed evidence"). Practically:

- `correlation_id` is the stable top-level handle that ties together every event emitted across one action's full journey — from `action.received` through to `trade.completed` (or an earlier terminal state such as `action.rejected`, `action.expired`, or `protection.failed`) — even as the more specific identities (`intent_id`, `order_id`, `execution_id`) come into existence at later lifecycle stages and would not, by themselves, connect an early event to a later one.
- The four specific identities are supplied on an event **only where that identity exists at the point the event fires** — exactly as `tron.event.v1` documents each field ("where an … identity exists for this event. Absent means no … identity is applicable to this event"). This document's catalogue in §2.1 states, event type by event type, which identities are expected to exist; it does not require an event to carry an identity that has not yet been assigned.
- Reconstructing one action's full history is therefore: collect every event sharing a `correlation_id`, order them by `occurred_at_ms`, and read off the progressively-populated `action_id` → `intent_id` → `order_id`/`execution_id` chain as it appears.

---

## 4. Never log

PID §15 states this list; it is restated here verbatim as this document's authority for what must never appear in an event, a journal entry, or anything shipped to Trading Graylog:

- passwords;
- API credentials;
- secret material;
- account login identifiers;
- sensitive infrastructure identifiers.

This is one instance of the broader HR-10 requirement ("Secrets, credentials, account identifiers and sensitive infrastructure identifiers must not enter the repository or logs" — PID §5, restated in `02-REQUIREMENTS.md` §1) applied specifically to the events/Graylog path, and is elaborated further from the security-baseline side in `12-SECURITY.md`. Events carry only the identifiers this document's catalogue names (`action_id`, `intent_id`, `order_id`, `execution_id`, `correlation_id`) and event-type-specific operational detail in `payload` (`tron.event.v1`) — never the items above.
