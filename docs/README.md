# TRON — Documentation Index

**Increment:** `WO-TRON-D1` — Authoritative Architecture & Contract Baseline
**Source of truth:** `PID.md`, at the repository root. Every document below restates and organises material drawn from that PID; the PID itself is authoritative if any conflict is ever perceived.

This is the front door to the complete `WO-TRON-D1` deliverable set: a documentation-, contract-, schema- and test-focused architectural baseline for TRON, produced before any runtime implementation begins (PID §0). It does **not** implement TRON, submit broker orders, or resolve any OPEN product decision (PID §21).

Read the documents in the order below — each is written to build on the ones before it.

## Documents

| # | Document | Covers | Work item |
|---|---|---|---|
| 01 | [`01-CONTEXT.md`](01-CONTEXT.md) | Product purpose, conceptual flow, what TRON is not, system/trust boundaries (FALCON, NEO, broker). The high-level orientation document — points onward to `03-ARCHITECTURE.md` and `10-CAPABILITIES.md` for depth. | WI-A |
| 02 | [`02-REQUIREMENTS.md`](02-REQUIREMENTS.md) | The 16 Hard Rules (HR-01–HR-16) restated verbatim, plus a derived Functional Requirements Register (REQ-001–REQ-014) tracing each requirement to its Hard Rule(s) and any OPEN-decision dependency. | WI-A |
| 03 | [`03-ARCHITECTURE.md`](03-ARCHITECTURE.md) | Architecture doctrine: deterministic execution, broker truth, one-instance-per-broker-context, external adapter boundaries, configuration-over-hard-coding, incremental proof. The structural invariants every capability must obey. | WI-E |
| 04 | [`04-TRADE-LIFECYCLE.md`](04-TRADE-LIFECYCLE.md) | The 18-step canonical OPEN lifecycle, and the full state-machine design for the four distinct state representations (FALCON action state, TRON intent state, broker order state, resulting position state) required by PID §8. | WI-F |
| 05 | [`05-CONTRACTS.md`](05-CONTRACTS.md) | Shape of the five canonical message contracts (`falcon.trade_action.v1`, `tron.trade_intent.v1`, `tron.execution_report.v1`, `tron.check_report.v1`, `tron.event.v1`): field-level detail, versioning convention, unknown-field policy, and the valid/invalid example index. | WI-B |
| 06 | [`06-CHECKS-CATALOGUE.md`](06-CHECKS-CATALOGUE.md) | The canonical pre-trade check catalogue: 82 `CHK-NNN` IDs (73 from PID §13 verbatim, 9 engineer additions clearly marked `WI-C-ADD`), stage assignment, PASS/FAIL/ERROR semantics, and MVP/BACKLOG status. | WI-C |
| 07 | [`07-CONFIGURATION.md`](07-CONFIGURATION.md) | The seven-file configuration model, schema versioning convention, `additionalProperties` policy, the startup validation pipeline (load → schema validate → semantic validate → cross-config validate → hash → start), and where each OPEN decision touches configuration. | WI-D |
| 08 | [`08-BROKER-PROFILES.md`](08-BROKER-PROFILES.md) | Conceptual data model for broker/instrument profile facts (symbol mapping, contract size, tick size, margin semantics, etc.), classified as configured fact / observed runtime fact / derived value. No schema or config file is delivered for this in D1 — that is deliberate; see the document's §4. | WI-D |
| 09 | [`09-EVENTS-AND-GRAYLOG.md`](09-EVENTS-AND-GRAYLOG.md) | The journal/spool-then-ship delivery model to Trading Graylog, and the full 20-entry event-type catalogue (firing occasion and identity correlation for each). | WI-G |
| 10 | [`10-CAPABILITIES.md`](10-CAPABILITIES.md) | The canonical `CAP-nn` (CAP-00–CAP-06) and `BL-<CATEGORY>-nn` capability/backlog ID namespaces, with each item's scope and its D1 status (every item is `BACKLOG` — D1 defines, it does not implement, PID §21). | WI-E |
| 11 | [`11-DECISIONS.md`](11-DECISIONS.md) | The canonical decision register: every PID §19 OPEN decision (with the required DEC-OPEN-09 DECIDED/OPEN split) cross-referenced against everywhere else it is touched, plus the PID §30 DECIDED register, plus the T10 governing rule and this work item's reconciliation-sweep results. | WI-H |
| 12 | [`12-SECURITY.md`](12-SECURITY.md) | Security baseline (PID §22): least-privilege requirements, the public-repository consequences, HR-10, the observed live secret-scanning enforcement, and the standing requirement for a separate production-readiness review before live trading. | WI-G |

## Supporting directories

| Path | Purpose |
|---|---|
| [`../schemas/`](../schemas/) | The five canonical contract JSON Schemas (draft 2020-12) at the top level, the seven configuration-file schemas under `schemas/config/`, and the valid/invalid example messages under `schemas/examples/valid/` and `schemas/examples/invalid/` that prove those schemas behave as documented (PID §23 T2/T3). |
| [`../config.example/`](../config.example/) | One example configuration file per schema in `schemas/config/` (`mapping.falcon.yaml`, `routing.yaml`, `selection.yaml`, `sizing.yaml`, `execution.yaml`, `checks.yaml`, `limits.yaml`), each validating against its corresponding schema (PID §23 T4). Every concrete numeric or policy value in these files is an illustrative placeholder only — never a production value, and never a decided Product Authority requirement where it touches an entry in `11-DECISIONS.md`. |
| `../tests/` | **Does not exist yet.** `tests/test_docs_baseline.py` and `requirements-dev.txt` are WI-I's Wave 4 deliverable (PID §26, §20) — the mechanical quality-gate suite (T1–T10, PID §23) and the non-vacuity evidence (PID §24) that prove everything documented above. This index does not pretend that suite already exists in this worktree. |
| [`../PID.md`](../PID.md) | The Project Initiation Document for `WO-TRON-D1`. Sole authority for this increment; every document above restates and organises material drawn from it and defers to it if any conflict is ever perceived. |

## Reading order for a first-time reader

`01` → `02` → `03` → `04` → `05` → `06` → `07` → `08` → `09` → `10` → `11` → `12`, then the schemas/examples and config examples as needed for implementation-level detail. A reader who only needs to know what remains undecided before implementation can start should go directly to `11-DECISIONS.md`.
