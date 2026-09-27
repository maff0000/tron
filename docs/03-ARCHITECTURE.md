# 03 — Architecture

**Work item:** WI-E (`WO-TRON-D1`)
**Owns:** this document, and `10-CAPABILITIES.md`.
**Source of truth:** `PID.md` (this document restates and organises the architecture doctrine from PID §4; the PID itself is authoritative if any conflict is ever perceived).

This document is authoritative for TRON's **architecture doctrine** — the structural and behavioural invariants that every capability and every implementation increment must honour, regardless of which capability is currently being built.

It does **not** define:

- the canonical trade-lifecycle state machine or order/action state transition semantics (PID §7, §8) — owned by WI-F, `04-TRADE-LIFECYCLE.md`. This document describes *what* a capability does at a capability-scope level (consistent with PID §16), never the detailed state-transition logic that governs *how* an action or order moves between states;
- the shape of the canonical message contracts — owned by WI-B, `05-CONTRACTS.md`;
- the check catalogue — owned by WI-C, `06-CHECKS-CATALOGUE.md`;
- configuration file schemas or broker-profile structure — owned by WI-D, `07-CONFIGURATION.md` / `08-BROKER-PROFILES.md`;
- the event-type catalogue — owned by WI-G, `09-EVENTS-AND-GRAYLOG.md`.

This document owns the `CAP-nn` capability-ID namespace jointly with `10-CAPABILITIES.md`; `10-CAPABILITIES.md` is the canonical resolution point for every capability and capability-backlog ID referenced anywhere in the repository (PID §23 T6).

---

## 1. Deterministic execution (PID §4.1)

TRON has **no intelligence**. Every execution decision must be derivable from exactly four inputs:

1. the incoming trade action;
2. current broker/account/instrument state;
3. versioned configuration;
4. deterministic code.

Given equivalent inputs, state and configuration, TRON must reach the same decision. This is not a style preference — it is what makes TRON's decisions reconstructable and auditable (HR-15) and what makes HR-03 ("no AI judgement or discretionary trading intelligence") a checkable property rather than an aspiration.

AI may **observe** TRON — for example, NEO consuming Trading Graylog events (see §4 below and PID §6.2). AI never **participates** in TRON's execution path. No component upstream, downstream, or beside TRON's core decision logic may supply a fifth, non-deterministic input that the decision depends on.

## 2. Broker truth (PID §4.2)

The **broker ledger is authoritative** for:

- balances;
- equity;
- open positions;
- pending orders;
- fills;
- broker-recognised execution state.

TRON may maintain local operational state and journals (see §7 below and PID §14.2), but must never construct or present an alternative authoritative trading ledger. Where TRON's local view conflicts with broker state, the discrepancy must be surfaced, not silently reconciled away, and broker state wins — unless the broker response itself is unavailable or demonstrably invalid, in which case HR-14 governs (a broker-state uncertainty that affects execution safety fails closed for new risk).

This is HR-06 made architectural: it is not merely a rule TRON's logic must obey, it is a structural property — TRON's persistence layer (§7) is designed so that there is no code path capable of promoting the local journal to authoritative status.

## 3. One execution instance per broker/account context (PID §4.3)

A single TRON execution instance operates against exactly **one** configured broker/account context. Multi-broker or multi-account support is achieved by running multiple independently configured instances, never by embedding broker-specific branching logic into one monolithic runtime.

This has direct consequences for the other doctrines in this document:

- broker-specific quirks belong behind the Broker Adapter boundary (§4) or in broker-profile configuration (PID §11, owned by WI-D), never as `if broker == X` conditionals inside TRON core logic;
- configuration identity (§5) is scoped per instance — the configuration set responsible for a given execution decision is attributable to the one broker/account context that instance serves;
- HR-12's `-tron`-suffixed, `proteus.project=tron`-labelled deployable infrastructure convention applies per instance, so that multiple instances remain independently identifiable and operable.

## 4. External boundaries (PID §4.4)

TRON communicates through explicit adapters. At minimum:

```text
FALCON / board
      │
      ▼
Board Adapter
      │
      ▼
TRON Core
      │
      ├── Broker Adapter ──► broker execution boundary
      │
      ├── Journal
      │
      └── Event Shipper ──► Trading Graylog
```

TRON business logic must not depend directly on transport-specific implementation details. Concretely:

- **Board Adapter** — isolates TRON Core from however candidate actions actually arrive (PID DEC-OPEN-05 leaves polling-vs-stream transport OPEN; TRON Core must not care which is in effect). It is responsible for producing validated `falcon.trade_action.v1` messages (see `05-CONTRACTS.md`) to TRON Core; it is not responsible for eligibility, selection or negotiation decisions.
- **Broker Adapter** — exposes the broker capabilities and state TRON Core requires (PID §6.3: account state, positions, pending orders, instrument metadata, live tradability, price/tick state, margin information, order validation, submission, modification, cancellation, execution/deal history, protection read-back). The underlying execution transport used to reach the broker is outside this PID; TRON Core's logic is written against the adapter's contract, not against any specific broker transport.
- **Journal** — TRON Core's durable local operational record (PID §14.2; see §7 below). It receives writes from TRON Core; it does not feed decisions back into TRON Core as if it were broker truth.
- **Event Shipper** — ships structured events (PID §15, owned by WI-G) to Trading Graylog using a journal/spool-then-ship model, so that a Graylog outage does not cause execution history to disappear (PID §14.3).

Because business logic is written against adapter contracts rather than transport details, a transport change (for example, a different board delivery mechanism, or a different broker execution transport) is contained to the relevant adapter and does not require TRON Core's decision logic to change.

## 5. Configuration over hard-coding (PID §4.5)

Operational policy belongs in validated configuration (PID §10, owned by WI-D for the remaining schemas; `checks.yaml` schema owned by WI-C). Code implements *behaviour*; configuration *selects and parameterises* that behaviour.

Two consequences follow directly, and both are testable:

- a **new parameter** (a different threshold, limit, mapping, or toggle within existing behaviour) should normally require only a configuration/schema change;
- **genuinely new behaviour** (a new kind of decision TRON's code did not previously know how to make) requires a code change.

Configuration must not become an embedded programming language — it selects and parameterises deterministic code (§1), it does not itself encode conditional decision logic that would make configuration changes equivalent to redeploying new behaviour without review. This is HR-02 ("no operational configuration is hard-coded into TRON business logic") read together with its inverse: configuration is not permitted to swallow logic that belongs in reviewed, versioned code.

Every execution decision is attributable to the identity/hash of the configuration set in force at the time (PID §10), which is what makes HR-15 (reconstructability) hold even as configuration evolves over time.

## 6. Incremental proof (PID §4.6)

TRON is built **vertically**. Each capability must be proven before execution authority expands, and no later stage may be used to conceal an unproven earlier one. The intended progression is:

```text
contracts
   ↓
read-only broker state
   ↓
board ingestion
   ↓
selection
   ↓
negotiation
   ↓
checks
   ↓
dry-run decision
   ↓
minimum-size paper execution
   ↓
protection verification
   ↓
reconciliation
   ↓
broader execution capabilities
```

**No later stage is used to conceal an unproven earlier stage.** A later stage passing its own tests is never evidence that an earlier stage in this progression is sound; each stage must be independently proven on its own terms before the next stage's proof is treated as meaningful. This is the architectural reading of PID §28's evidence discipline (DEFINED / OBSERVED / INFERRED / OPEN): passing a later stage's tests must never be allowed to silently upgrade an earlier, unproven stage from INFERRED to OBSERVED.

### 6.1 Ground already laid (Wave 1)

The first rung of this progression — **contracts** — is not abstract for TRON: it is concretely realised by the five canonical contracts defined in `05-CONTRACTS.md` and their schemas (`schemas/falcon.trade_action.v1.json`, `schemas/tron.trade_intent.v1.json`, `schemas/tron.execution_report.v1.json`, `schemas/tron.check_report.v1.json`, `schemas/tron.event.v1.json`), together with the Hard Rules restated in `02-REQUIREMENTS.md` §1 that those contracts and the rest of this progression must satisfy (in particular HR-04, HR-05 and HR-09, which are encoded directly into the contract shapes rather than left to be enforced only at runtime). Every subsequent rung in the progression above consumes or produces messages conforming to those contracts; none of them re-derives contract shape independently.

### 6.2 Mapping to capabilities

The progression above is realised, capability by capability, in `10-CAPABILITIES.md` (CAP-00 through CAP-06). That document is authoritative for capability scope, sequencing and status; this document is authoritative for the doctrine the capabilities must obey while being built. Neither document repeats the other's detail.

## 7. Persistence architecture (supporting doctrine, PID §14)

This document does not restate PID §14 in full (see `07-CONFIGURATION.md` / journal-adjacent detail owned elsewhere as it is defined), but the architectural boundary is stated here because it is load-bearing for §2 and §4 above: TRON has three distinct persistence concepts — the broker ledger (authoritative, external, §2), the local journal (durable, append-oriented, operational, owned by TRON, never authoritative), and Trading Graylog (operational audit/analysis record, fed via the Event Shipper). No execution may occur when the required local durable journal write cannot be made (PID §14.3) — this is a structural precondition on the Broker Adapter path in the diagram at §4, not merely a preference.

---

## 8. Relationship to capabilities and other work items

- Capability scope, sequencing, and status (including the honest statement that D1 implements none of CAP-00 through CAP-06) live in `10-CAPABILITIES.md`.
- Detailed order/action state-machine semantics live in `04-TRADE-LIFECYCLE.md` (WI-F). Where this document mentions a capability's purpose (§6.2), it describes intent and scope only, at the same level of detail as PID §16 — it does not define transition logic.
- Canonical contract shapes live in `05-CONTRACTS.md` (WI-B).
- Anything in PID §19 that remains an OPEN product decision (DEC-OPEN-01 through DEC-OPEN-10) is not settled by this document. Where this document's doctrine intersects an OPEN decision (for example, DEC-OPEN-05 at §4's Board Adapter, or DEC-OPEN-09 at §7's persistence boundary), that intersection is named explicitly and the decision remains OPEN — this document does not upgrade any OPEN proposal to a decided requirement (PID §23 T10).
