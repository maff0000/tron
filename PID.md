# TRON — Project Initiation Document

**Increment:** `WO-TRON-D1` — Authoritative Architecture & Contract Baseline  
**Product Authority:** Matt  
**Lead Architect:** ChatGPT  
**Delivery:** Forge  
**PL Sponsor:** Rogue  
**Project Root:** `/srv/tron` on `dell-debian`  
**Repository:** `maff0000/tron`  
**Date:** 2026-09-27

---

# 0. Increment Intent

TRON is entering its own product lifecycle.

This increment establishes the **authoritative architectural baseline for TRON** before runtime implementation begins.

It is deliberately documentation-, contract-, schema- and test-focused.

The objective is not to predict every future requirement. It is to settle enough architecture that subsequent implementation increments can build capabilities without repeatedly redesigning the execution engine.

This PID governs TRON only.

Existing external systems are dependencies at defined boundaries. Their implementation history, internal design, previous work orders and outstanding operational work are not part of this increment.

No external system is modified by `WO-TRON-D1`.

---

# 1. Identity and Working Environment

## 1.1 Project

```text
PROJECT_ROOT=/srv/tron
```

Development host:

```text
dell-debian
```

Repository:

```text
maff0000/tron
```

The Forge PL must verify the repository, remote, current branch and repository state before starting work.

## 1.2 Repository visibility

The TRON repository is intentionally **PUBLIC during the architecture/build phase** so that Central Architecture can inspect the project directly.

Public visibility does not imply public write authority.

Requirements:

- unauthorised users must not have write or merge authority;
- branch protection and repository permissions must preserve controlled integration;
- secrets and credentials must never enter the repository;
- account identifiers must never enter the repository;
- sensitive broker or infrastructure details must never enter the repository;
- configuration examples contain placeholders only;
- production data must never enter the repository.

Repository visibility must be reconsidered before TRON is authorised for live production trading.

## 1.3 Host boundary

All TRON development for this increment occurs on `dell-debian`.

Do not perform TRON development on Trinity.

Do not modify unrelated existing services, containers, networks, firewall rules or host configuration.

---

# 2. Product Purpose

TRON is the **deterministic trade-execution and execution-risk layer** of the trading platform.

Its responsibility begins when potential trade actions become available from FALCON and ends when the resulting broker state and execution outcome have been verified and recorded.

Conceptually:

```text
                         ┌─────────────────────┐
                         │       FALCON        │
                         │ potential actions   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                              Redis board
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────┐
│                           TRON                               │
│                                                              │
│  ingest → validate → select → negotiate → checks → execute   │
│                                  │                 │         │
│                                  │                 ▼         │
│                                  │          verify broker    │
│                                  │              state        │
│                                  │                 │         │
│                                  └─────────────────┘         │
└───────────────────────┬──────────────────────┬───────────────┘
                        │                      │
                        ▼                      ▼
                 Broker adapter         Local journal
                        │                      │
                        ▼                      ▼
                     Broker              Trading Graylog
                                               │
                                               ▼
                                              NEO
                                         observer only
```

TRON is responsible for:

- consuming candidate trade actions;
- validating their contracts;
- rejecting stale or duplicate actions;
- applying deterministic eligibility and selection rules;
- converting canonical trade intent into broker-valid order intent;
- obtaining current broker/account/instrument state;
- performing pre-trade checks;
- enforcing configured execution and risk limits;
- submitting permitted orders;
- ensuring mandatory broker-side protection exists;
- verifying resulting broker state;
- reconciling its view against broker truth;
- producing a durable structured audit trail.

---

# 3. What TRON Is Not

TRON is **not**:

- a strategy engine;
- a signal generator;
- a forecasting engine;
- an AI decision-maker;
- a market-data authority;
- an independent trading ledger;
- a portfolio research system;
- a substitute for the broker ledger;
- a place for discretionary judgement.

TRON does not decide whether a market is attractive.

TRON decides only whether a supplied action may be executed **under deterministic rules and current observable state**.

---

# 4. Core Architecture Doctrine

## 4.1 Deterministic execution

TRON has **no intelligence**.

Every execution decision must be derivable from:

1. the incoming trade action;
2. current broker/account/instrument state;
3. versioned configuration;
4. deterministic code.

Given equivalent inputs, state and configuration, TRON should reach the same decision.

AI may observe TRON.

AI does not participate in TRON's execution path.

## 4.2 Broker truth

The **broker ledger is authoritative** for:

- balances;
- equity;
- open positions;
- pending orders;
- fills;
- broker-recognised execution state.

TRON may maintain local operational state and journals, but must never create an alternative authoritative trading ledger.

Where local state conflicts with broker state, the discrepancy must be surfaced and broker state wins unless the broker response itself is unavailable or demonstrably invalid.

## 4.3 One execution instance per broker/account context

A TRON execution instance operates against one configured broker/account context.

Multi-broker support comes from multiple independently configured instances, not broker-specific logic embedded into one monolithic runtime.

## 4.4 External boundaries

TRON communicates through explicit adapters.

At minimum:

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

TRON business logic must not depend directly on transport-specific implementation details.

The broker adapter exposes the broker capabilities and state TRON requires.

The underlying execution transport is outside this PID.

## 4.5 Configuration over hard-coding

Operational policy belongs in validated configuration.

Code implements behaviour.

Configuration selects and parameterises behaviour.

Configuration must not become an embedded programming language.

A new parameter should normally require configuration/schema change.

A genuinely new behaviour requires code.

## 4.6 Incremental proof

TRON is built vertically.

Each capability must be proven before execution authority expands.

The intended progression is:

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

No later stage is used to conceal an unproven earlier stage.

---

# 5. Hard Rules

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

Changes to these hard rules require explicit Product Authority approval and a PID amendment.

---

# 6. System Boundaries

## 6.1 FALCON

FALCON supplies **potential trade actions**.

The relationship is one-way:

```text
FALCON → board → TRON
```

TRON does not negotiate with FALCON.

TRON does not request better trades.

TRON does not send execution advice back to FALCON.

If no valid actions are available, TRON does nothing.

FALCON is not yet the execution authority; TRON remains responsible for execution eligibility and safety.

## 6.2 NEO

NEO is an observer.

Conceptually:

```text
TRON → Trading Graylog → NEO
```

NEO may analyse:

- executions;
- rejected actions;
- check results;
- slippage;
- broker discrepancies;
- execution quality;
- operational health.

NEO cannot place, modify, cancel or approve trades through TRON.

## 6.3 Broker boundary

TRON reaches broker functionality through a **Broker Adapter**.

TRON's core must not care how the adapter reaches the broker.

The adapter contract must support the functionality required by TRON, including where applicable:

- account state;
- positions;
- pending orders;
- instrument metadata;
- live tradability;
- price/tick state;
- margin information;
- order validation;
- order submission;
- modification;
- cancellation;
- execution/deal history;
- protection read-back.

Broker-specific quirks belong behind this boundary or in broker-profile configuration, not throughout TRON core logic.

---

# 7. Canonical Trade Lifecycle

The canonical OPEN lifecycle is:

```text
1. INGEST
2. VALIDATE
3. EXPIRE
4. DEDUPLICATE
5. DETERMINE ELIGIBILITY
6. APPLY THRESHOLD
7. RESOLVE CONFLICT
8. RANK
9. SELECT
10. NEGOTIATE
11. SNAPSHOT REQUIRED STATE
12. RUN PRE-TRADE CHECKS
13. JOURNAL EXECUTION INTENT
14. EXECUTE
15. READ BACK BROKER STATE
16. VERIFY SL/TP PROTECTION
17. RECONCILE
18. RECORD OUTCOME
```

Failure before execution produces no new broker risk.

Failure after broker submission enters an explicit recovery/reconciliation path.

A failed protection verification is a **critical execution condition** and may never be silently accepted.

---

# 8. Order and Action State

TRON uses market-standard/FIX-aligned terminology where useful without adopting the FIX wire protocol.

Execution states include at minimum:

```text
New
PartiallyFilled
Filled
Canceled
Rejected
Expired
```

TRON must distinguish between:

- FALCON action state;
- TRON intent state;
- broker order state;
- resulting position state.

These must not be collapsed into one ambiguous `status` field.

State transitions must be explicit and testable.

---

# 9. Contracts

This increment defines the following canonical contracts:

```text
falcon.trade_action.v1
tron.trade_intent.v1
tron.execution_report.v1
tron.check_report.v1
tron.event.v1
```

All canonical contracts use JSON Schema draft 2020-12.

## 9.1 Common contract rules

- timestamps: UTC epoch milliseconds;
- prices: decimal strings;
- monetary amounts: decimal strings;
- quantities: decimal strings;
- currencies: ISO 4217 where applicable;
- stable identifiers are explicit;
- contract version is explicit;
- unknown-field behaviour is explicitly defined;
- optional does not mean semantically undefined.

## 9.2 `falcon.trade_action.v1`

Must support:

```text
action_id
action
instrument
side
stop_loss
take_profit
confidence
valid_until_ms
strategy reference
signal reference
supersedes reference
position_action reference
extensions
```

`action` initially supports:

```text
OPEN
CLOSE
MODIFY
CANCEL
```

For `OPEN`:

```text
stop_loss  REQUIRED
take_profit REQUIRED
```

Confidence must have a declared scale.

Broker lot quantity is forbidden in the upstream action.

## 9.3 `tron.trade_intent.v1`

Represents the exact executable intent produced after negotiation.

It records:

- source action;
- canonical instrument;
- broker-resolved instrument;
- direction;
- canonical requested quantity;
- negotiated broker quantity;
- requested protection;
- negotiated protection;
- permitted adjustments;
- rule responsible for each adjustment;
- configuration identities;
- timestamps;
- correlation identifiers.

## 9.4 `tron.execution_report.v1`

Represents execution outcome using FIX-aligned semantics.

It must support partial fills and multiple broker execution events without pretending every order is atomic.

## 9.5 `tron.check_report.v1`

Every check records:

```text
check_id
stage
result
observed evidence
configured parameters
reason
timestamp
```

A failed check must explain why it failed.

## 9.6 `tron.event.v1`

Provides the canonical event envelope used for operational/audit events.

Every material event is correlated to the appropriate:

```text
action_id
intent_id
order identity
execution identity
```

where those identities exist.

---

# 10. Configuration Model

TRON configuration is separated by responsibility.

Initial files:

```text
mapping.falcon.yaml
routing.yaml
selection.yaml
sizing.yaml
execution.yaml
checks.yaml
limits.yaml
```

Each has a corresponding JSON Schema.

Startup behaviour is:

```text
load
  ↓
schema validate
  ↓
semantic validate
  ↓
cross-config validate
  ↓
hash
  ↓
start
```

Invalid configuration means **refuse startup**.

TRON records the identity/hash of the configuration set responsible for every execution decision.

Secrets are not configuration and must not be stored in these files.

---

# 11. Broker Profiles

Broker and instrument differences are data, not reasons to fork TRON.

Profiles may describe:

- broker symbol mapping;
- contract size;
- quantity minimum;
- quantity maximum;
- quantity step;
- tick size;
- tick value;
- stop-distance constraints;
- freeze constraints;
- supported order/filling modes;
- margin semantics;
- execution mode;
- account mode;
- trading sessions;
- server-time characteristics;
- commission/fee assumptions where known.

Runtime broker state takes precedence over stale profile assumptions where the adapter exposes authoritative current values.

Profiles must clearly distinguish:

```text
configured fact
observed runtime fact
derived value
```

Upstream systems do not need to know broker lot semantics.

---

# 12. Pre-Trade Check Architecture

Checks are deterministic functions over a **consistent execution snapshot**.

Checks are grouped into ordered stages.

All checks in a stage execute.

If any check in a stage fails, later stages do not execute and the proposed trade is blocked.

Stages:

| Stage | Purpose |
|---|---|
| 0 | operational safety and kill state |
| 1 | ledger/reconciliation integrity |
| 2 | idempotency and existing trade state |
| 3 | instrument and order validity |
| 4 | account and risk limits |
| 5 | execution cost |
| 6 | projected post-trade state |

Every check has:

```text
check_id
name
stage
required inputs
configuration parameters
PASS / FAIL / ERROR semantics
failure reason
MVP/backlog status
```

`ERROR` is not equivalent to `PASS`.

Where an error creates execution uncertainty, TRON fails closed for new risk.

---

# 13. Canonical Check Catalogue

The following Product Authority requirements must be preserved and individually mapped to stable check IDs:

Ledger available · Ledger current · Last reconciliation successful · Account balance reconciled · Account equity reconciled · Open positions reconciled · Pending orders reconciled · Filled orders reconciled · Cancelled orders reconciled · Rejected orders reconciled · Partial fills reconciled · No orphan positions · No orphan orders · No duplicate orders · No duplicate fills · No unresolved execution discrepancies · No unresolved position discrepancies · No stale account state · No stale broker state · Proposed order not already submitted · Proposed order not already filled · Existing position state checked · Existing pending order state checked · Available cash checked · Available margin checked · Used margin checked · Free margin checked · Required margin checked · Projected post-trade margin checked · Projected post-trade free margin checked · Current leverage checked · Projected leverage checked · Current gross exposure checked · Current net exposure checked · Projected gross exposure checked · Projected net exposure checked · Instrument exposure checked · Position count checked · Maximum position size checked · Maximum order size checked · Daily realised P&L checked · Daily unrealised P&L checked · Current account drawdown checked · Daily loss limit checked · Maximum drawdown limit checked · Consecutive loss count checked · Trades-today count checked · Trading limit status checked · Stop-loss present where required · Stop-loss distance valid · Take-profit valid where required · Order quantity valid · Minimum quantity checked · Maximum quantity checked · Quantity increment/step checked · Price increment/tick size checked · Contract specification current · Instrument tradable · Market open · No trading halt · No account restriction · No margin call state · No liquidation state · No active risk lock · No unresolved ledger exception · No unresolved broker exception · Account currency checked · Instrument currency checked · FX conversion available where required · Commission/fee assumptions available · Estimated transaction cost checked · Estimated slippage checked · Final post-trade account state within configured limits.

Under HR-01:

```text
Stop-loss present where required
Take-profit valid where required
```

means **every OPEN trade**.

Additional system-level checks may be proposed by the Architect/Engineer, but must be clearly identified as additions rather than silently attributed to Product Authority.

At minimum the design must consider:

- manual kill switch;
- execution service health;
- broker connectivity;
- broker-state freshness;
- instrument state freshness;
- server-time offset validity;
- symbol availability;
- supported execution mode;
- spread/cost ceiling.

---

# 14. Persistence and Durable Truth

TRON has three distinct persistence concepts.

## 14.1 Broker ledger

Authoritative trading truth.

## 14.2 Local journal

TRON's durable operational record.

At minimum it records:

- consumed action identity;
- decision;
- negotiated intent;
- check results;
- broker submission attempt;
- broker response;
- protection verification;
- reconciliation outcome;
- events awaiting shipment.

The journal is append-oriented.

It exists to support:

- idempotency;
- crash recovery;
- auditability;
- event delivery;
- reconciliation.

It does **not** supersede broker truth.

## 14.3 Trading Graylog

Graylog is the operational audit and analysis record.

TRON uses a **journal/spool then ship** model.

A Graylog outage must not cause execution history to disappear.

A Graylog outage alone does not necessarily stop trading if the durable local journal remains healthy.

No execution may occur when the required local durable journal write cannot be made.

---

# 15. Events and Observability

TRON emits structured events for material lifecycle transitions.

At minimum:

```text
action.received
action.rejected
action.expired
action.duplicate
action.selected
intent.created
check.stage.completed
check.failed
execution.submitted
execution.accepted
execution.rejected
execution.partial_fill
execution.filled
protection.verified
protection.failed
reconciliation.completed
reconciliation.failed
trade.completed
system.degraded
system.halted
```

Events must be machine-readable.

Correlation must allow reconstruction of an action from ingestion through execution and reconciliation.

Never log:

- passwords;
- API credentials;
- secret material;
- account login identifiers;
- sensitive infrastructure identifiers.

---

# 16. Capabilities

TRON is implemented as bounded deterministic capabilities.

The initial capability sequence is:

| ID | Capability |
|---|---|
| CAP-00 | Foundation |
| CAP-01 | Board ingestion |
| CAP-02 | Selection |
| CAP-03 | Negotiation |
| CAP-04 | MVP pre-trade checks |
| CAP-05 | Protected OPEN execution |
| CAP-06 | Protection verification |

## CAP-00 — Foundation

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

## CAP-01 — Board ingestion

Consumes candidate actions without executing them.

Proves:

```text
board → contract validation → durable ingestion
```

## CAP-02 — Selection

Applies configured eligibility, confidence and ranking policy.

No broker execution.

## CAP-03 — Negotiation

Transforms a canonical candidate into broker-valid executable intent.

This is where broker-specific quantity semantics are resolved.

No broker execution.

## CAP-04 — MVP pre-trade checks

Runs the minimum approved check set over a consistent snapshot.

Initial mode is dry-run.

## CAP-05 — Protected OPEN execution

Introduces broker-side execution at minimum paper size.

No OPEN is considered successful until mandatory protection requirements are satisfied.

## CAP-06 — Protection verification

Reads resulting broker state and proves SL/TP protection exists as intended.

A failure enters explicit recovery/reconciliation handling.

---

# 17. Capability Backlog

D1 must produce a capability backlog covering at least:

### Lifecycle

- CLOSE
- MODIFY
- CANCEL
- expiry handling
- supersession
- conflict handling

### Ledger and reconciliation

- periodic reconciliation
- orphan detection
- discrepancy classification
- crash recovery
- restart reconciliation

### Risk

- account exposure limits
- instrument exposure limits
- drawdown limits
- daily loss limits
- position limits
- order limits
- consecutive-loss policy
- active risk lock

### Execution robustness

- partial fills
- execution retries
- ambiguous broker response recovery
- protection repair
- slippage handling
- rejection classification

### Operations

- kill switch
- degraded-state handling
- health reporting
- configuration change detection
- journal replay
- event replay
- operational alerts

Each capability receives a stable ID and status:

```text
BACKLOG
IN-PID
DONE
```

---

# 18. Initial Test Strategy

The first controlled execution path uses a deliberately simple external test strategy producing frequent BTCUSD candidate actions.

BTCUSD is selected first because it generally offers broad trading availability, including weekend availability on suitable broker offerings.

TRON must **not** assume BTCUSD is permanently tradable.

HR-11 remains authoritative:

```text
instrument not currently tradable
        ↓
no new OPEN
```

After the complete path is proven with BTCUSD:

```text
BTCUSD
   ↓
XAUUSD
   ↓
additional instruments
```

The purpose of the test strategy is deterministic input generation, not profitability.

---

# 19. Open Product Decisions

The following remain OPEN and must not be silently decided by an Engineer.

## DEC-OPEN-01 — conflicting candidate actions

When qualifying LONG and SHORT actions exist for the same instrument.

Proposed initial policy:

```text
skip the instrument for that selection cycle
```

## DEC-OPEN-02 — existing-position policy

Whether TRON may add to an existing position.

Proposed MVP:

```text
one position per instrument
```

## DEC-OPEN-03 — response to hard-limit breach

Whether an existing position is automatically exited when a hard account limit is breached.

Proposed MVP:

```text
block new risk;
existing positions remain protected by their broker-side SL/TP
```

## DEC-OPEN-04 — quantity ownership

Whether canonical quantity originates upstream or is determined by TRON sizing policy.

Proposed MVP:

```text
fixed canonical base quantity from TRON configuration
```

## DEC-OPEN-05 — board transport

Initial polling versus a stream/consumer model.

A one-minute polling cycle is acceptable for initial proving but is **not an immutable architectural requirement**.

## DEC-OPEN-06 — routing

Whether upstream actions identify a broker/account destination.

Proposed:

```text
actions remain broker-neutral;
TRON instance configuration determines its eligible actions
```

## DEC-OPEN-07 — production Graylog placement

To be determined during production architecture.

## DEC-OPEN-08 — confidence calibration

FALCON must eventually ensure confidence values are semantically comparable enough for any TRON rule that compares candidates from different strategies.

Exact calibration contract remains open.

## DEC-OPEN-09 — reconciliation cadence

DECIDED:

```text
broker ledger = authoritative truth
```

OPEN:

```text
background reconciliation cadence
```

Potential design:

```text
live read before execution
+ immediate post-execution reconciliation
+ periodic full sweep
```

No fixed periodic interval is decided by D1.

## DEC-OPEN-10 — runtime implementation language/version

Not decided by this documentation increment.

---

# 20. D1 Deliverables

`WO-TRON-D1` produces:

```text
docs/
├── README.md
├── 01-CONTEXT.md
├── 02-REQUIREMENTS.md
├── 03-ARCHITECTURE.md
├── 04-TRADE-LIFECYCLE.md
├── 05-CONTRACTS.md
├── 06-CHECKS-CATALOGUE.md
├── 07-CONFIGURATION.md
├── 08-BROKER-PROFILES.md
├── 09-EVENTS-AND-GRAYLOG.md
├── 10-CAPABILITIES.md
├── 11-DECISIONS.md
├── 12-SECURITY.md
└── evidence/
    └── WO-TRON-D1.md

schemas/
├── falcon.trade_action.v1.json
├── tron.trade_intent.v1.json
├── tron.execution_report.v1.json
├── tron.check_report.v1.json
├── tron.event.v1.json
├── config/
│   ├── mapping.schema.json
│   ├── routing.schema.json
│   ├── selection.schema.json
│   ├── sizing.schema.json
│   ├── execution.schema.json
│   ├── checks.schema.json
│   └── limits.schema.json
└── examples/
    ├── valid/
    └── invalid/

config.example/
├── mapping.falcon.yaml
├── routing.yaml
├── selection.yaml
├── sizing.yaml
├── execution.yaml
├── checks.yaml
└── limits.yaml

tests/
└── test_docs_baseline.py

requirements-dev.txt
```

---

# 21. D1 Non-Goals

This increment does **not**:

- implement the TRON runtime;
- submit broker orders;
- connect to live or paper accounts;
- install Redis;
- install Graylog;
- implement FALCON;
- implement NEO;
- implement the BTCUSD test strategy;
- make infrastructure changes;
- modify unrelated systems;
- resolve OPEN product decisions without Product Authority;
- choose production infrastructure;
- choose the production runtime language;
- implement CAP-00 through CAP-06.

D1 defines the ground on which those implementation increments are subsequently built.

---

# 22. Security Baseline

TRON follows least privilege.

Requirements:

- secrets never enter git;
- secrets never enter logs;
- secrets are not placed in ordinary application configuration;
- examples use placeholders;
- external inputs are treated as untrusted;
- schemas validate canonical messages;
- invalid messages fail closed;
- write authority is minimised;
- read-only access is used where sufficient;
- execution authority is isolated from observers;
- repository secret scanning remains active;
- security hooks must not be bypassed.

Because the repository is public during development, repository content must be treated as **publicly readable information**.

Before live trading, the security architecture requires a separate explicit production-readiness review.

---

# 23. Mechanical Quality Gates

`tests/test_docs_baseline.py` must provide at least:

## T1 — Schema validity

Every JSON Schema is itself valid draft 2020-12.

## T2 — Valid examples

Every valid example validates against its intended schema.

## T3 — Invalid examples

Every invalid example fails for its intended reason.

Minimum negative cases:

- OPEN missing stop-loss;
- OPEN missing take-profit;
- numeric rather than decimal-string price;
- unsupported action;
- invalid confidence;
- upstream broker-lot quantity;
- malformed timestamp;
- prohibited/unknown field where the contract forbids it.

Tests assert the expected failing path/keyword so failure cannot pass accidentally.

## T4 — Configuration validation

Every example configuration validates.

Every configuration schema has at least one deliberate negative example.

## T5 — Check catalogue integrity

Every check ID:

```text
documentation
↔ schema
↔ example configuration
```

must reconcile in both directions.

Every Product Authority check listed in §13 must appear exactly once in the catalogue.

## T6 — Capability integrity

Every referenced capability ID exists in `10-CAPABILITIES.md`.

## T7 — Documentation links

All internal relative documentation links resolve.

## T8 — TRON resource naming

Every TRON-owned Docker resource name represented by the documentation baseline must comply with HR-12.

This test is **not limited to one architecture table**.

## T9 — Security scan

Repository/branch secret scanning is clean.

## T10 — Decision integrity

Every OPEN decision is represented as OPEN.

No documentation may present an OPEN proposal as a decided requirement.

---

# 24. Non-Vacuity

Passing tests are insufficient unless the tests are capable of detecting the failures they claim to guard against.

The evidence record must demonstrate at minimum:

1. temporarily remove mandatory OPEN protection and prove the relevant test fails;
2. temporarily remove one required Product Authority check and prove catalogue-integrity testing fails;
3. temporarily introduce a non-compliant TRON Docker resource name and prove naming validation fails;
4. temporarily represent an OPEN decision as DECIDED and prove decision-integrity testing fails;
5. revert every deliberate mutation;
6. rerun the clean suite successfully.

The evidence record captures commands, expected failure and observed result.

---

# 25. Forge Delivery Model

The PID is authoritative for this increment.

Rogue acts as PL sponsor.

The Forge PL owns integration.

Engineers perform bounded work but do not independently reinterpret unresolved product decisions.

The PL alone owns:

- integration branch;
- commits;
- reconciliation between work items;
- PR creation/management.

A fresh independent Auditor performs final acceptance review.

No Engineer may resolve ambiguity by inventing Product Authority.

When an unresolved issue materially affects architecture or contract semantics:

```text
STOP
→ report the exact question
→ obtain Product Authority / Architecture ruling
→ continue
```

---

# 26. Approved Work Decomposition

## Wave 1 — Foundations

### WI-A — Context & Requirements

Owns:

```text
01-CONTEXT.md
02-REQUIREMENTS.md
```

### WI-B — Contracts & Canonical Schemas

Owns:

```text
05-CONTRACTS.md
canonical contract schemas
valid examples
invalid examples
```

Wave 1 establishes shared vocabulary.

---

## Wave 2 — Domain Design

After Wave 1 integration:

### WI-C — Checks

Owns:

```text
06-CHECKS-CATALOGUE.md
checks.schema.json
checks.yaml example
```

One owner controls the check-ID namespace.

### WI-D — Configuration & Broker Profiles

Owns:

```text
07-CONFIGURATION.md
08-BROKER-PROFILES.md
remaining configuration schemas
configuration examples
```

### WI-E — Architecture & Capabilities

Owns:

```text
03-ARCHITECTURE.md
10-CAPABILITIES.md
```

One owner controls the capability namespace.

### WI-F — Trade Lifecycle

Owns:

```text
04-TRADE-LIFECYCLE.md
```

### WI-G — Events & Security

Owns:

```text
09-EVENTS-AND-GRAYLOG.md
12-SECURITY.md
```

---

## Wave 3 — Reconciliation

### WI-H — Decisions & Documentation Index

Owns:

```text
11-DECISIONS.md
README.md
```

This work item reconciles the entire set and ensures OPEN decisions remain OPEN.

---

## Wave 4 — Mechanical Assurance

### WI-I — Tests & Evidence

Owns:

```text
test_docs_baseline.py
requirements-dev.txt
D1 mechanical evidence
non-vacuity demonstrations
```

---

# 27. Acceptance Definition

`WO-TRON-D1` is GREEN only when:

1. every D1 deliverable exists;
2. all canonical schemas are valid;
3. valid examples pass;
4. negative examples fail for their intended reasons;
5. configuration examples validate;
6. the complete Product Authority check catalogue is mapped;
7. capability IDs reconcile;
8. OPEN decisions remain OPEN everywhere;
9. HR-01 through HR-16 are consistently represented;
10. TRON Docker naming complies with HR-12;
11. repository security scanning is clean;
12. internal documentation links resolve;
13. required non-vacuity demonstrations are recorded;
14. the complete mechanical suite is GREEN on the PL-integrated commit;
15. an independent Auditor reviews the complete integrated result and returns GREEN;
16. the Auditor confirms no Engineer has silently introduced a product decision;
17. the Auditor confirms no secrets, account identifiers or sensitive infrastructure identifiers are present;
18. the Auditor prompt and verdict are preserved in the evidence record;
19. **Matt gives explicit final acceptance.**

Auditor GREEN does not authorise merge without Matt's acceptance.

---

# 28. D1 Evidence Standard

Evidence must distinguish:

```text
DEFINED
OBSERVED
INFERRED
OPEN
```

**DEFINED**  
A requirement, contract or architecture decision established by this PID.

**OBSERVED**  
Something directly demonstrated by evidence produced during the relevant TRON work.

**INFERRED**  
A technically reasonable assumption that has not yet crossed its load-bearing real-world gate.

**OPEN**  
A product or architectural decision intentionally unresolved.

Documentation must never upgrade:

```text
INFERRED → OBSERVED
OPEN → DEFINED
```

without the required evidence or authority.

For future execution increments, broker behaviour is proven only by exercising the relevant behaviour against an authorised paper environment.

Mocks prove TRON logic.

Mocks do not prove broker behaviour.

---

# 29. Subsequent Delivery Direction

After D1 closes GREEN, implementation proceeds through separate bounded PIDs.

Expected sequence:

```text
D1  authoritative design baseline
 ↓
CAP-00 foundation
 ↓
CAP-01 board ingestion
 ↓
CAP-02 deterministic selection
 ↓
CAP-03 negotiation
 ↓
CAP-04 checks / dry-run
 ↓
CAP-05 minimum-size protected paper OPEN
 ↓
CAP-06 protection verification
 ↓
reconciliation / recovery capabilities
 ↓
XAUUSD proving
 ↓
expanded capability backlog
 ↓
production-readiness programme
```

Each increment gets its own evidence and independent audit.

Passing D1 proves the design baseline.

It does **not** prove that TRON can trade.

Passing dry-run proves decision behaviour.

It does **not** prove execution.

Only controlled broker execution can prove the execution path.

---

# 30. Product Decisions Carried Into D1

The following are settled unless Matt explicitly changes them:

1. TRON is deterministic.
2. TRON contains no AI trading judgement.
3. FALCON supplies candidate actions one-way.
4. NEO observes and never instructs execution.
5. Every OPEN has broker-side SL and TP.
6. Broker state is authoritative trading truth.
7. Redis is messaging, not durable state.
8. TRON maintains a durable local operational journal.
9. Trading Graylog receives structured execution events.
10. One TRON execution instance serves one configured broker/account context.
11. Canonical time is UTC epoch milliseconds.
12. Exact decimal representations are used for prices, quantities and money.
13. Broker lot semantics do not propagate upstream.
14. Configuration is external, schema-validated and attributable.
15. Market/instrument tradability is checked before OPEN.
16. Contracts use market-standard/FIX-aligned semantics where appropriate.
17. TRON is built capability by capability.
18. BTCUSD is the first controlled execution instrument.
19. XAUUSD follows once the execution path is proven.
20. TRON-owned deployable infrastructure is containerised and identifiable by the `-tron` convention.
21. Every meaningful execution decision must be auditable.
22. Safety-relevant uncertainty fails closed for new risk.
23. The repository remains public during the current architecture/build phase so Central Architecture can directly inspect it, subject to the security controls in this PID.
24. Final D1 merge requires independent Auditor GREEN and Matt's explicit acceptance.

---

# 31. Start Instruction

The Forge PL must:

1. read this PID as a complete set;
2. verify the TRON repository and working state;
3. verify repository security hooks are active;
4. verify the repository's public visibility does not grant unauthorised write/merge authority;
5. compare the approved decomposition in §26 with current work state;
6. discard assumptions or work derived solely from the superseded PID where they conflict with this PID;
7. report any existing work that now conflicts with this PID before integrating it;
8. execute the approved waves in dependency order;
9. stop for Product Authority where this PID explicitly leaves a decision OPEN;
10. produce the complete D1 evidence package;
11. dispatch one fresh independent Auditor after integration and mechanical GREEN;
12. STOP after Auditor GREEN for Matt's final acceptance.

No unrelated work.

No runtime implementation under `WO-TRON-D1`.

No modification of external execution infrastructure.

---

**END — WO-TRON-D1**
