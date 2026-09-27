# TRON — Context

**Increment:** `WO-TRON-D1` — Authoritative Architecture & Contract Baseline
**Source of truth:** `PID.md` (this document restates and organises context drawn from that PID; the PID itself is authoritative if any conflict is ever perceived).

---

## 1. Product Purpose

TRON is the **deterministic trade-execution and execution-risk layer** of the trading platform (PID §2).

Its responsibility boundary is precise:

- it **begins** when potential trade actions become available from FALCON;
- it **ends** when the resulting broker state and execution outcome have been verified and recorded.

Everything upstream of "potential trade actions becoming available" (market analysis, signal generation, strategy judgement) is out of scope for TRON. Everything downstream of "broker state and execution outcome verified and recorded" (portfolio research, long-run analytics, observation) is likewise out of scope — TRON produces the record; it does not consume or interpret it for its own decision-making beyond the current trade lifecycle.

## 2. Conceptual Flow

The conceptual flow of a candidate trade action through the system is (PID §2):

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

FALCON publishes potential trade actions onto a Redis board. TRON ingests candidate actions from that board, validates, selects, negotiates, checks, and — where permitted — executes them through a Broker Adapter against the broker. In parallel, TRON writes to a local journal and ships structured events to the Trading Graylog, which NEO observes.

See `03-ARCHITECTURE.md` for the full architecture doctrine and capability model — this document does not restate that depth.

## 3. What TRON Is Not

TRON is explicitly **not** (PID §3):

- a strategy engine;
- a signal generator;
- a forecasting engine;
- an AI decision-maker;
- a market-data authority;
- an independent trading ledger;
- a portfolio research system;
- a substitute for the broker ledger;
- a place for discretionary judgement.

TRON does not decide whether a market is attractive. TRON decides only whether a supplied action may be executed **under deterministic rules and current observable state**.

## 4. System and Trust Boundaries

TRON's authority and communication are bounded on three sides (PID §6).

### 4.1 FALCON relationship

The relationship is strictly one-way:

```text
FALCON → board → TRON
```

- TRON does not negotiate with FALCON.
- TRON does not request better trades.
- TRON does not send execution advice back to FALCON.
- If no valid actions are available, TRON does nothing.
- FALCON is not yet the execution authority; TRON remains responsible for execution eligibility and safety regardless of what FALCON supplies.

### 4.2 NEO relationship

NEO is an observer only:

```text
TRON → Trading Graylog → NEO
```

NEO may analyse executions, rejected actions, check results, slippage, broker discrepancies, execution quality, and operational health.

NEO **cannot** place, modify, cancel or approve trades through TRON. No external observer, including NEO, may directly instruct TRON to place a trade (HR-16).

### 4.3 Broker boundary

TRON reaches broker functionality only through a **Broker Adapter**. TRON's core must not care how the adapter reaches the broker; broker-specific quirks belong behind this boundary or in broker-profile configuration, not throughout TRON core logic.

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

---

For the full architecture doctrine (execution flow through explicit adapters, deterministic-execution model, incremental-proof progression) and the capability model (CAP-00 through CAP-06 and the capability backlog), see `03-ARCHITECTURE.md` and `10-CAPABILITIES.md`.
