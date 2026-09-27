# 10 — Capabilities

**Work item:** WI-E (`WO-TRON-D1`)
**Owns:** this document, and `03-ARCHITECTURE.md`.
**Source of truth:** `PID.md` (this document restates and organises the capability model from PID §16–§17; the PID itself is authoritative if any conflict is ever perceived).

This document is **authoritative and canonical for the `CAP-nn` capability-ID namespace and for the capability-backlog ID namespace** (PID §23 T6: "every referenced capability ID exists in `10-CAPABILITIES.md`"). Any `CAP-nn` or backlog ID referenced anywhere else in this repository — documentation, schemas, configuration examples, tests — must resolve to an entry in §1 or §3 of this document. This document does not renumber or reuse IDs already assigned in the PID.

This document does **not** define:

- the architecture doctrine each capability must obey while being built (owned by `03-ARCHITECTURE.md`, WI-E's sibling deliverable);
- detailed order/action state-transition logic for any capability (owned by WI-F, `04-TRADE-LIFECYCLE.md`) — capability descriptions below are stated at the same capability-scope level as PID §16, never as state-machine detail;
- the shape of any canonical contract (owned by WI-B, `05-CONTRACTS.md`);
- the check catalogue content (owned by WI-C, `06-CHECKS-CATALOGUE.md`).

---

## 0. Status discipline — read this before the tables below

**`WO-TRON-D1` (this increment) does not implement any of CAP-00 through CAP-06.** This is explicit in PID §21 (D1 Non-Goals): "implement CAP-00 through CAP-06" is listed as something this increment does **not** do. D1 is documentation-, contract-, schema- and test-focused (PID §0); it establishes the design baseline that later, separate, independently-audited PIDs implement against (PID §29).

The status vocabulary is fixed by PID §17:

```text
BACKLOG   — defined, not yet the subject of an active implementation PID
IN-PID    — an implementation PID for this item currently exists / is in flight
DONE      — implemented, proven, and accepted
```

Because `WO-TRON-D1` is a documentation-only increment and is not itself an implementation PID for any capability, **every capability and backlog item in this document is `BACKLOG`**. None is `IN-PID` (no implementation PID for any of them has yet been opened as part of this increment) and none is `DONE`. This document must never mark a capability `DONE` on the strength of its having been *designed*; `DONE` is reserved for a capability that has actually been implemented, proven and accepted under its own future PID (PID §27, §28 — evidence discipline: DEFINED ≠ OBSERVED).

Put plainly: every row below records that the capability is **DEFINED** by this PID, and **BACKLOG** for implementation purposes. "Defined" and "done" are not the same thing, and this document does not conflate them.

---

## 1. Initial capability sequence (PID §16)

TRON is implemented as bounded deterministic capabilities, built in the order below (this is also the incremental-proof progression mapped in `03-ARCHITECTURE.md` §6.2).

| ID | Capability | D1 status |
|---|---|---|
| CAP-00 | Foundation | BACKLOG |
| CAP-01 | Board ingestion | BACKLOG |
| CAP-02 | Selection | BACKLOG |
| CAP-03 | Negotiation | BACKLOG |
| CAP-04 | MVP pre-trade checks | BACKLOG |
| CAP-05 | Protected OPEN execution | BACKLOG |
| CAP-06 | Protection verification | BACKLOG |

These IDs are preserved exactly as assigned in PID §16 and must never be renumbered or reused for a different capability.

### CAP-00 — Foundation

**Status: BACKLOG (defined by D1; not implemented by D1 — PID §21).**

Establishes:

- configuration loading;
- schema validation;
- broker-adapter read path;
- symbol mapping;
- canonical time handling;
- durable journal;
- event creation;
- event shipping;
- health state.

### CAP-01 — Board ingestion

**Status: BACKLOG (defined by D1; not implemented by D1 — PID §21).**

Consumes candidate actions without executing them. Proves:

```text
board → contract validation → durable ingestion
```

### CAP-02 — Selection

**Status: BACKLOG (defined by D1; not implemented by D1 — PID §21).**

Applies configured eligibility, confidence and ranking policy. No broker execution.

### CAP-03 — Negotiation

**Status: BACKLOG (defined by D1; not implemented by D1 — PID §21).**

Transforms a canonical candidate into broker-valid executable intent. This is where broker-specific quantity semantics are resolved (HR-09). No broker execution.

### CAP-04 — MVP pre-trade checks

**Status: BACKLOG (defined by D1; not implemented by D1 — PID §21).**

Runs the minimum approved check set over a consistent snapshot. Initial mode is dry-run.

### CAP-05 — Protected OPEN execution

**Status: BACKLOG (defined by D1; not implemented by D1 — PID §21).**

Introduces broker-side execution at minimum paper size. No OPEN is considered successful until mandatory protection requirements are satisfied (HR-01).

### CAP-06 — Protection verification

**Status: BACKLOG (defined by D1; not implemented by D1 — PID §21).**

Reads resulting broker state and proves SL/TP protection exists as intended. A failure enters explicit recovery/reconciliation handling — the recovery/reconciliation handling itself is capability backlog (see `BL-EXEC-04`, `BL-LEDGER-*` below), not defined in transition-level detail by this document.

---

## 2. Capability-backlog ID convention

Backlog items are identified with the prefix `BL-<CATEGORY>-<NN>`, where `<CATEGORY>` is one of `LIFECYCLE`, `LEDGER`, `RISK`, `EXEC`, `OPS` (matching the five groupings in PID §17), and `<NN>` is a two-digit sequence number starting at `01` within that category. This scheme is deliberately distinct from `CAP-nn` so that a reader can never confuse a bounded initial capability (§1) with a backlog item awaiting scheduling into a future capability or PID.

All backlog items below are **BACKLOG** (PID §17 vocabulary). None is in this PID (PID §21); none is done.

## 3. Capability backlog (PID §17)

### 3.1 Lifecycle

| ID | Item | Status |
|---|---|---|
| BL-LIFECYCLE-01 | CLOSE action handling | BACKLOG |
| BL-LIFECYCLE-02 | MODIFY action handling | BACKLOG |
| BL-LIFECYCLE-03 | CANCEL action handling | BACKLOG |
| BL-LIFECYCLE-04 | Expiry handling | BACKLOG |
| BL-LIFECYCLE-05 | Supersession handling | BACKLOG |
| BL-LIFECYCLE-06 | Conflict handling | BACKLOG |

`falcon.trade_action.v1` already declares `CLOSE`, `MODIFY` and `CANCEL` as supported `action` values at the contract level (`05-CONTRACTS.md`, PID §9.2); the deterministic handling behaviour for each beyond CAP-00–CAP-06's OPEN-centred path is backlog, not yet designed in transition-level detail (owned, when scheduled, by WI-F's successor work under a future PID).

### 3.2 Ledger and reconciliation

| ID | Item | Status |
|---|---|---|
| BL-LEDGER-01 | Periodic reconciliation | BACKLOG |
| BL-LEDGER-02 | Orphan detection | BACKLOG |
| BL-LEDGER-03 | Discrepancy classification | BACKLOG |
| BL-LEDGER-04 | Crash recovery | BACKLOG |
| BL-LEDGER-05 | Restart reconciliation | BACKLOG |

Background reconciliation cadence beyond live pre-execution read plus immediate post-execution reconciliation remains an OPEN product decision (`DEC-OPEN-09`); this backlog exists independently of that decision and does not resolve it.

### 3.3 Risk

| ID | Item | Status |
|---|---|---|
| BL-RISK-01 | Account exposure limits | BACKLOG |
| BL-RISK-02 | Instrument exposure limits | BACKLOG |
| BL-RISK-03 | Drawdown limits | BACKLOG |
| BL-RISK-04 | Daily loss limits | BACKLOG |
| BL-RISK-05 | Position limits | BACKLOG |
| BL-RISK-06 | Order limits | BACKLOG |
| BL-RISK-07 | Consecutive-loss policy | BACKLOG |
| BL-RISK-08 | Active risk lock | BACKLOG |

These correspond to checks already named at catalogue level in PID §13 (e.g. "Maximum drawdown limit checked", "Daily loss limit checked", "Consecutive loss count checked", "No active risk lock"); the check-ID mapping itself is owned by WI-C (`06-CHECKS-CATALOGUE.md`), which is the authority for check IDs. This backlog records the risk-policy *capability* each check family will eventually enforce, not the check ID itself.

### 3.4 Execution robustness

| ID | Item | Status |
|---|---|---|
| BL-EXEC-01 | Partial fills | BACKLOG |
| BL-EXEC-02 | Execution retries | BACKLOG |
| BL-EXEC-03 | Ambiguous broker response recovery | BACKLOG |
| BL-EXEC-04 | Protection repair | BACKLOG |
| BL-EXEC-05 | Slippage handling | BACKLOG |
| BL-EXEC-06 | Rejection classification | BACKLOG |

`tron.execution_report.v1` already models partial fills and multiple broker execution events at the contract level (PID §9.4, `05-CONTRACTS.md`); the deterministic *handling* behaviour for partial fills, retries, ambiguous responses and protection repair is backlog.

### 3.5 Operations

| ID | Item | Status |
|---|---|---|
| BL-OPS-01 | Kill switch | BACKLOG |
| BL-OPS-02 | Degraded-state handling | BACKLOG |
| BL-OPS-03 | Health reporting | BACKLOG |
| BL-OPS-04 | Configuration change detection | BACKLOG |
| BL-OPS-05 | Journal replay | BACKLOG |
| BL-OPS-06 | Event replay | BACKLOG |
| BL-OPS-07 | Operational alerts | BACKLOG |

CAP-00 (Foundation) establishes baseline health state; the fuller operational surface above (kill switch, degraded-state handling, replay, alerting) is backlog beyond CAP-00's foundation scope.

---

## 4. Capability-ID cross-reference (PID §23 T6)

This document is the single canonical location every `CAP-nn` and `BL-<CATEGORY>-nn` identifier in this repository must resolve against. A mechanical check (owned by WI-I, `tests/test_docs_baseline.py`, T6) verifies that every capability ID referenced anywhere in the documentation, schema or configuration baseline exists in §1 or §3 above. Any future capability or backlog item must be added here — with a stable ID that is never reused or renumbered — before it may be referenced elsewhere in the repository.

As of this increment, `CAP-00` through `CAP-06` are referenced outside this document only as capability-scope pointers (for example, in schema field descriptions in `schemas/falcon.trade_action.v1.json` and `schemas/tron.trade_intent.v1.json`, and in the conceptual-flow cross-reference in `01-CONTEXT.md`); none of those references assert an implementation status different from the `BACKLOG` status recorded in §1 above.
