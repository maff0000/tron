# TRON — Requirements

**Increment:** `WO-TRON-D1` — Authoritative Architecture & Contract Baseline
**Source of truth:** `PID.md` (this document restates and derives requirements from that PID; the PID itself is authoritative if any conflict is ever perceived).

This document has two parts:

1. the **Hard Rules** (PID §5) — restated verbatim as the non-negotiable requirement baseline, with their exact IDs preserved;
2. a **Functional Requirements Register** derived from the responsibility list in PID §2, each with a stable ID and, where applicable, traced to the Hard Rule(s) it exists to satisfy.

Changes to the Hard Rules require explicit Product Authority approval and a PID amendment (PID §5). Nothing in this document may be read as amending them.

---

## 1. Hard Rules (PID §5)

These rules are architectural invariants.

| ID | Rule |
|---|---|
| HR-01 | Every OPEN trade must have both stop-loss and take-profit protection at the broker. Protection must be read back and verified. |
| HR-02 | No operational configuration is hard-coded into TRON business logic. |
| HR-03 | TRON contains no AI judgement or discretionary trading intelligence. |
| HR-04 | Canonical timestamps are UTC epoch milliseconds. External time representations are normalised at their adapter boundary. |
| HR-05 | Monetary values, prices and quantities use exact decimal representations; binary floating-point values must not cross canonical contracts. |
| HR-06 | The broker ledger is authoritative trading truth. |
| HR-07 | Redis is transport/messaging, not durable truth. |
| HR-08 | No execution may proceed unless the intent and decision are durably journalled before broker submission. |
| HR-09 | Upstream trade quantities are not expressed as broker lots. Broker-specific quantity conversion occurs at TRON's negotiation boundary. |
| HR-10 | Secrets, credentials, account identifiers and sensitive infrastructure identifiers must not enter the repository or logs. |
| HR-11 | TRON must not open a trade when the relevant instrument is not currently tradable. |
| HR-12 | TRON-owned deployable infrastructure is containerised. TRON-owned container, image, volume and network names end in `-tron` and carry `proteus.project=tron`. |
| HR-13 | Execution must be idempotent with respect to an incoming action identity. A retry must not silently become a second trade. |
| HR-14 | A broker-state uncertainty that affects execution safety fails closed for new risk. |
| HR-15 | Every material execution decision must be reconstructable from durable events, configuration identity and observed evidence. |
| HR-16 | No external observer, including NEO, may directly instruct TRON to place a trade. |

---

## 2. Functional Requirements Register

Each requirement below is derived from a single item in the PID §2 responsibility list ("TRON is responsible for: …"). Where a Hard Rule exists to enforce or constrain the requirement, it is listed in the "Traces to" column. A requirement may trace to more than one Hard Rule, or to none, where no Hard Rule directly governs it (in which case it stands on PID §2 alone).

Where a requirement's realisation depends on a decision left OPEN in PID §19, that dependency is named explicitly by its `DEC-OPEN-nn` ID. A "Proposed" value recorded against an OPEN decision in PID §19 is **not** Product Authority and is not treated here as settled; it is noted only as the currently proposed (not decided) direction.

| ID | Requirement | Derived from (PID §2) | Traces to | Open-decision dependency |
|---|---|---|---|---|
| REQ-001 | TRON must consume candidate trade actions made available by FALCON via the Redis board. | consuming candidate trade actions | HR-07 (board is transport, not durable truth — consumption must not treat it as authoritative history) | DEC-OPEN-05 (polling vs. stream/consumer transport — not decided); DEC-OPEN-06 (whether actions are broker-neutral or destination-routed — proposed: broker-neutral) |
| REQ-002 | TRON must validate the contract of every consumed candidate action against its canonical schema before further processing, and must not process a structurally or semantically invalid action. | validating their contracts | HR-04 (canonical UTC epoch millisecond timestamps); HR-05 (exact decimal representations for prices/quantities/money) | — |
| REQ-003 | TRON must reject actions that are stale (past their validity window) or duplicates of an action already processed, rather than acting on them. | rejecting stale or duplicate actions | HR-13 (idempotency with respect to incoming action identity) | DEC-OPEN-01 (conflicting LONG/SHORT candidates for the same instrument — proposed: skip the instrument for that cycle; this is a conflict-handling decision distinct from staleness/duplication) |
| REQ-004 | TRON must apply deterministic, configuration-driven eligibility, confidence and ranking rules to select among qualifying candidate actions. | applying deterministic eligibility and selection rules | HR-02 (no hard-coded operational configuration); HR-03 (no AI judgement or discretionary intelligence in the decision) | DEC-OPEN-01 (conflicting candidates); DEC-OPEN-02 (whether TRON may add to an existing position — proposed MVP: one position per instrument); DEC-OPEN-08 (cross-strategy confidence calibration — exact contract not decided) |
| REQ-005 | TRON must convert a selected canonical trade intent into broker-valid order intent, including resolving broker-specific quantity semantics at the negotiation boundary. | converting canonical trade intent into broker-valid order intent | HR-09 (broker lot conversion occurs only at TRON's negotiation boundary, never upstream) | DEC-OPEN-04 (whether canonical quantity originates upstream or from TRON sizing policy — proposed MVP: fixed canonical base quantity from configuration) |
| REQ-006 | TRON must obtain current broker/account/instrument state as needed to support selection, negotiation, checks and execution decisions. | obtaining current broker/account/instrument state | HR-06 (broker ledger is authoritative trading truth); HR-14 (state uncertainty affecting execution safety fails closed for new risk) | — |
| REQ-007 | TRON must run the applicable pre-trade checks over a consistent execution snapshot before any order may be submitted. | performing pre-trade checks | HR-01 (SL/TP presence and verification for every OPEN); HR-11 (instrument must be currently tradable); HR-14 (fail closed on uncertainty) | — |
| REQ-008 | TRON must enforce configured execution and risk limits, blocking any action that would breach them. | enforcing configured execution and risk limits | HR-02 (limits are configuration, not hard-coded logic); HR-14 (fail closed on uncertainty) | DEC-OPEN-03 (response to a hard-limit breach on an existing position — proposed MVP: block new risk, existing positions remain protected by their broker-side SL/TP) |
| REQ-009 | TRON must submit only orders that have passed all applicable checks, and submission must be idempotent with respect to the originating action identity. | submitting permitted orders | HR-08 (intent and decision durably journalled before broker submission); HR-13 (idempotent execution; a retry must not become a second trade) | — |
| REQ-010 | TRON must ensure mandatory broker-side protection (stop-loss and take-profit) exists for every OPEN trade before that trade is considered successfully executed. | ensuring mandatory broker-side protection exists | HR-01 (every OPEN trade must have SL and TP at the broker) | — |
| REQ-011 | TRON must read back resulting broker state after submission and verify it matches the intended outcome, including verifying that mandatory protection is actually in place. | verifying resulting broker state | HR-01 (protection must be read back and verified); HR-06 (broker ledger is authoritative) | — |
| REQ-012 | TRON must reconcile its own view of state against broker truth and surface any discrepancy; broker state wins unless the broker response is unavailable or demonstrably invalid. | reconciling its view against broker truth | HR-06 (broker ledger authoritative); HR-15 (material decisions reconstructable from durable events, configuration identity and observed evidence) | DEC-OPEN-09 (broker ledger authority itself is DECIDED; the background reconciliation cadence beyond live pre-execution read plus immediate post-execution reconciliation remains OPEN) |
| REQ-013 | TRON must produce a durable, structured audit trail sufficient to reconstruct every material execution decision, without recording secrets or sensitive identifiers. | producing a durable structured audit trail | HR-08 (durable journal before submission); HR-10 (no secrets/credentials/account identifiers/sensitive infrastructure identifiers in repository or logs); HR-15 (reconstructability from durable events, configuration identity and observed evidence) | DEC-OPEN-07 (production placement of the Trading Graylog is not decided by D1; this requirement governs the durable local journal and event production, not Graylog's eventual production siting) |

## 3. State Representation Requirement (PID §8)

REQ-014: TRON must distinguish, as separate, non-collapsed representations:

- FALCON action state;
- TRON intent state;
- broker order state;
- resulting position state.

These must not be collapsed into one ambiguous `status` field, and state transitions must be explicit and testable (PID §8).

This requirement states the necessity of the distinction only. The concrete state machine — the specific states, allowed transitions, and field-level design for each of the four representations — is not defined here. Per the Central Architecture ruling for this run, that mechanism is owned by WI-F (`04-TRADE-LIFECYCLE.md`). This document does not pre-empt that design.

## 4. Notes on Scope

- This register is derived solely from the responsibility list in PID §2 and the state-distinction requirement in PID §8. It does not extend the scope of `WO-TRON-D1` (PID §21, D1 Non-Goals) — in particular, it does not implement any runtime, submit any broker order, or resolve any OPEN product decision.
- Every `DEC-OPEN-nn` reference above points to the corresponding entry in PID §19. Where PID §19 records a "Proposed" policy, that proposal is carried here only as context for why a requirement's exact behaviour is not yet fixed — it is not asserted as a settled requirement, default, or policy. Final OPEN-decision disposition is WI-H's (`11-DECISIONS.md`) territory in Wave 3, not this document's.
