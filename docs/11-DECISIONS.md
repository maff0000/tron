# 11 — Decisions

**Work item:** WI-H (`WO-TRON-D1`)
**Owns:** this document, and `README.md`.
**Source of truth:** `PID.md` §19 (Open Product Decisions) and §30 (Product Decisions Carried Into D1). This document restates and cross-references those sections; the PID itself is authoritative if any conflict is ever perceived.

This document is the **canonical, authoritative location for the current status of every PID §19 item**, and the companion canonical location for the PID §30 settled-decisions register. Wherever any other document in this repository states or implies the status of a `DEC-OPEN-nn` item, this document is the arbiter.

## 0. Governing rule (PID §23 T10)

> **No documentation may present an OPEN proposal as a decided requirement.**

This is PID §23's T10 mechanical gate, restated here as this document's own governing rule because this document is the register a reader — or an Auditor performing T10 — checks against. Every `DEC-OPEN-nn` item in Section 1 below is OPEN unless this document explicitly says otherwise (the sole exception, per the binding Central-Architecture ruling for this work item, is the ledger-authority clause folded into DEC-OPEN-09 — see 1.9). Section 2 (PID §30) is a **separate, independently-labelled** register of what is already DECIDED; the two registers are never blended into one list or one status line.

No Engineer may resolve an item in Section 1 by inventing Product Authority (PID §25). Where this document's cross-reference sweep (Section 3) found any other document appearing to do so, that finding is reported to the PL for adjudication, not silently corrected here (see Section 4).

---

## 1. OPEN Product Decisions (PID §19)

Each entry below gives: the decision's title, its exact current status, the PID's own "Proposed" text **verbatim**, clearly labelled as proposed/not decided, and a cross-reference to every other place in the integrated Wave 1+2 document set that touches it.

A "Proposed" value quoted anywhere in this document or elsewhere in the repository is **not** Product Authority. It is carried only as context for why a requirement, contract field, or configuration shape is built the way it is — never as a settled default.

### 1.1 DEC-OPEN-01 — conflicting candidate actions

**Status: OPEN.**

**PID §19 text (verbatim, proposed, not decided):**
> When qualifying LONG and SHORT actions exist for the same instrument.
>
> Proposed initial policy:
> ```
> skip the instrument for that selection cycle
> ```

**Cross-references in the integrated document set:**

| Document | What it says |
|---|---|
| `02-REQUIREMENTS.md` (REQ-003, REQ-004) | Names DEC-OPEN-01 as an open-decision dependency of the stale/duplicate-rejection and eligibility/selection/ranking requirements; explicitly notes conflict-handling is distinct from staleness/duplication. |
| `04-TRADE-LIFECYCLE.md` (§1 step 7 RESOLVE CONFLICT; §2.1 `SKIPPED` state; §2.1 transition table; §5) | Step 7's *existence* is DEFINED (PID §7 is settled); its *resolution policy* is flagged OPEN under DEC-OPEN-01. The FALCON action state `SKIPPED` is reached via, among other paths, a DEC-OPEN-01 conflict-skip — flagged OPEN at the point it is mentioned, not decided. |
| `07-CONFIGURATION.md` (§7 table) | `selection.schema.json`'s `conflict_policy` is kept as an extensible enum (not a single hard-coded value) precisely because this decision is OPEN; the config example's `"skip_instrument"` value is the PID's proposed direction only. |
| `schemas/config/selection.schema.json` (`conflict_policy` field description) | States `"skip_instrument"` corresponds to DEC-OPEN-01's proposed policy, not a decided requirement, and that further enum members may be added additively later. |
| `config.example/selection.yaml` | Inline comment flags `conflict_policy: "skip_instrument"` as reflecting DEC-OPEN-01's proposed (not decided) policy. |

### 1.2 DEC-OPEN-02 — existing-position policy

**Status: OPEN.**

**PID §19 text (verbatim, proposed, not decided):**
> Whether TRON may add to an existing position.
>
> Proposed MVP:
> ```
> one position per instrument
> ```

**Cross-references in the integrated document set:**

| Document | What it says |
|---|---|
| `02-REQUIREMENTS.md` (REQ-004) | Names DEC-OPEN-02 as an open-decision dependency of the eligibility/selection/ranking requirement. |
| `04-TRADE-LIFECYCLE.md` (§1 steps 8–9 RANK/SELECT; §2.4 position states and the dedicated "DEC-OPEN-02 flag" paragraph; §5) | RANK/SELECT's existence is DEFINED; whether an existing position at `OPEN_PENDING`/`PARTIALLY_FILLED`/`OPEN_UNPROTECTED`/`OPEN_PROTECTED` blocks a further OPEN for that instrument is exactly DEC-OPEN-02, explicitly flagged OPEN, not decided. |
| `06-CHECKS-CATALOGUE.md` (`CHK-022`, "Existing position state checked") | `CHK-022` is observation-only; the policy applied to an existing position (DEC-OPEN-02) remains OPEN and is not decided by that check. |
| `07-CONFIGURATION.md` (§7 table) | `selection.schema.json`'s `existing_position_policy` is kept as an enum of two named policies because this decision is OPEN; the example's `"one_position_per_instrument"` value is the PID's proposed MVP only. |
| `schemas/config/selection.schema.json` (`existing_position_policy` field description) | States `"one_position_per_instrument"` corresponds to DEC-OPEN-02's proposed MVP, not a decided requirement. |
| `config.example/selection.yaml` | Inline comment flags `existing_position_policy` as reflecting DEC-OPEN-02's proposed (not decided) MVP. |

### 1.3 DEC-OPEN-03 — response to hard-limit breach

**Status: OPEN.**

**PID §19 text (verbatim, proposed, not decided):**
> Whether an existing position is automatically exited when a hard account limit is breached.
>
> Proposed MVP:
> ```
> block new risk;
> existing positions remain protected by their broker-side SL/TP
> ```

**Cross-references in the integrated document set:**

| Document | What it says |
|---|---|
| `02-REQUIREMENTS.md` (REQ-008) | Names DEC-OPEN-03 as an open-decision dependency of the execution/risk-limit-enforcement requirement. |
| `07-CONFIGURATION.md` (§7 table) | `limits.schema.json`'s `on_hard_limit_breach` is kept as an enum of two named responses because this decision is OPEN; the example's `"block_new_risk"` value is the PID's proposed MVP only. |
| `schemas/config/limits.schema.json` (top-level description and `on_hard_limit_breach` field description) | States `"block_new_risk"` corresponds to DEC-OPEN-03's currently proposed MVP, not a decided requirement; the alternative `"flatten_all_positions"` enum member is named only so the schema does not foreclose a different eventual answer. |
| `config.example/limits.yaml` | Inline comment flags `on_hard_limit_breach` as reflecting DEC-OPEN-03's proposed (not decided) MVP. |

### 1.4 DEC-OPEN-04 — quantity ownership

**Status: OPEN.**

**PID §19 text (verbatim, proposed, not decided):**
> Whether canonical quantity originates upstream or is determined by TRON sizing policy.
>
> Proposed MVP:
> ```
> fixed canonical base quantity from TRON configuration
> ```

**Cross-references in the integrated document set:**

| Document | What it says |
|---|---|
| `02-REQUIREMENTS.md` (REQ-005) | Names DEC-OPEN-04 as an open-decision dependency of the negotiation/broker-valid-order-intent requirement. |
| `05-CONTRACTS.md` (§4 "Illustrative-only note"; §5 "DEC-OPEN-04 illustrative-only note") | `falcon.trade_action.v1` has no quantity field at all, so it cannot encode DEC-OPEN-04 either way. `tron.trade_intent.v1.canonical_requested_quantity`'s example value (`"0.0100"`) is illustrative only, proving schema validity; it does not establish whether canonical quantity originates upstream or from TRON sizing policy. |
| `07-CONFIGURATION.md` (§7 table) | `sizing.schema.json`'s entire shape implements the PID's proposed MVP quantity-ownership model; `sizing_mode` exists specifically so a different future Product Authority answer is representable as a new named mode rather than an implicit redefinition. |
| `schemas/config/sizing.schema.json` (top-level and `sizing_mode`/`base_quantities` field descriptions) | States the whole file is built to hold the proposed MVP's shape, that DEC-OPEN-04 remains OPEN, and that a different future model would require a new `sizing_mode` value. |
| `schemas/tron.trade_intent.v1.json` (`canonical_requested_quantity` field description) | States the contract records whatever value negotiation received without deciding whether it originates upstream or from TRON sizing policy; DEC-OPEN-04 remains OPEN. |
| `config.example/sizing.yaml` | Inline comment flags the file's entire shape as reflecting DEC-OPEN-04's proposed (not decided) MVP. |

### 1.5 DEC-OPEN-05 — board transport

**Status: OPEN.**

**PID §19 text (verbatim, proposed, not decided):**
> Initial polling versus a stream/consumer model.
>
> A one-minute polling cycle is acceptable for initial proving but is **not an immutable architectural requirement**.

**Cross-references in the integrated document set:**

| Document | What it says |
|---|---|
| `02-REQUIREMENTS.md` (REQ-001) | Names DEC-OPEN-05 ("polling vs. stream/consumer transport — not decided") as an open-decision dependency of the board-consumption requirement. |
| `03-ARCHITECTURE.md` (§4 Board Adapter; §8 closing note) | The Board Adapter exists specifically so TRON Core does not care whether polling or a stream/consumer model is in effect; DEC-OPEN-05 is named explicitly at that boundary and stated as not settled by the architecture document. |

No configuration schema or example encodes a specific transport mechanism; DEC-OPEN-05 is untouched at the configuration layer in this increment.

### 1.6 DEC-OPEN-06 — routing

**Status: OPEN.**

**PID §19 text (verbatim, proposed, not decided):**
> Whether upstream actions identify a broker/account destination.
>
> Proposed:
> ```
> actions remain broker-neutral;
> TRON instance configuration determines its eligible actions
> ```

**Cross-references in the integrated document set:**

| Document | What it says |
|---|---|
| `02-REQUIREMENTS.md` (REQ-001) | Names DEC-OPEN-06 ("whether actions are broker-neutral or destination-routed — proposed: broker-neutral") as an open-decision dependency of the board-consumption requirement. |
| `05-CONTRACTS.md` (§5 "DEC-OPEN-06 note") | Neither `falcon.trade_action.v1` nor `tron.trade_intent.v1` has a target broker/account field; per DEC-OPEN-06's proposed (not decided) policy, routing is out of scope for any per-message contract in this set by design, not merely by omission. |
| `07-CONFIGURATION.md` (§7 table) | `routing.yaml`/`routing.schema.json` deliberately contain no upstream-destination/routing field; the file only describes the instance's own scope (`instance_id`, `broker_context`, `eligible_instruments`, `eligible_actions`), which PID §4.3 establishes independently of how DEC-OPEN-06 is eventually resolved. |
| `schemas/config/routing.schema.json` (top-level description) | States explicitly that this is not an upstream-destination routing field, that the file exists per DEC-OPEN-06's proposed (not decided) policy, and that a future per-message routing field would not remove the need for the instance-scope fields this schema defines. |
| `config.example/routing.yaml` | Inline comment flags the whole file as reflecting DEC-OPEN-06's proposed (not decided) direction. |

### 1.7 DEC-OPEN-07 — production Graylog placement

**Status: OPEN.**

**PID §19 text (verbatim, proposed, not decided):**
> To be determined during production architecture.

**Cross-references in the integrated document set:**

| Document | What it says |
|---|---|
| `02-REQUIREMENTS.md` (REQ-013) | Names DEC-OPEN-07 explicitly: production placement of the Trading Graylog is not decided by D1; the durable audit-trail requirement governs the local journal and event production, not Graylog's eventual production siting. |
| `09-EVENTS-AND-GRAYLOG.md` (document preamble; §1 closing paragraph) | States plainly, twice, that where and how Trading Graylog is deployed in production, and the transport by which shipped events reach it, is DEC-OPEN-07 and is not settled by that document — it constrains only the journal-first, spool-then-ship *behaviour*, never a specific host, network path, or deployment topology. |
| `12-SECURITY.md` (document preamble) | Cites DEC-OPEN-07 as the worked example of a requirement that intersects, but does not resolve, a PID §19 OPEN decision. |

### 1.8 DEC-OPEN-08 — confidence calibration

**Status: OPEN.**

**PID §19 text (verbatim, proposed, not decided):**
> FALCON must eventually ensure confidence values are semantically comparable enough for any TRON rule that compares candidates from different strategies.
>
> Exact calibration contract remains open.

**Cross-references in the integrated document set:**

| Document | What it says |
|---|---|
| `02-REQUIREMENTS.md` (REQ-004) | Names DEC-OPEN-08 ("cross-strategy confidence calibration — exact contract not decided") as an open-decision dependency of the eligibility/selection/ranking requirement. |
| `04-TRADE-LIFECYCLE.md` (§1 steps 8–9 RANK/SELECT; §5) | RANK/SELECT touch DEC-OPEN-08 wherever ranking may use confidence; flagged OPEN, not decided. |
| `05-CONTRACTS.md` (§4 "Confidence scale" note) | Draws an explicit line: declaring *a* concrete `[0.0000, 1.0000]` decimal-string scale for the `confidence` field is a bounded WI-B contract-design detail (not a PID §19 item), and is explicitly **separate** from DEC-OPEN-08 (cross-strategy calibration — whether a `0.80` from one strategy means the same real-world thing as a `0.80` from another), which remains genuinely OPEN. |
| `schemas/falcon.trade_action.v1.json` (`confidence` field description) | Restates the same separation: the declared scale is a bounded contract-design detail, not DEC-OPEN-08 calibration, which remains OPEN. |

### 1.9 DEC-OPEN-09 — reconciliation cadence

**Status: SPLIT — this decision has two distinct, individually-labelled facts, per the binding Central-Architecture ruling for this work item. No single line below blends them.**

- **DECIDED:** the broker ledger is authoritative trading truth (HR-06).
- **OPEN:** the background reconciliation cadence/strategy beyond an immediate post-execution reconciliation. No fixed periodic interval is currently decided.

**PID §19 text (verbatim):**
> DECIDED:
> ```
> broker ledger = authoritative truth
> ```
>
> OPEN:
> ```
> background reconciliation cadence
> ```
>
> Potential design:
> ```
> live read before execution
> + immediate post-execution reconciliation
> + periodic full sweep
> ```
>
> No fixed periodic interval is decided by D1.

**Cross-references in the integrated document set:**

| Document | What it says |
|---|---|
| `02-REQUIREMENTS.md` (REQ-012) | States the split directly: "broker ledger authority itself is DECIDED; the background reconciliation cadence beyond live pre-execution read plus immediate post-execution reconciliation remains OPEN." |
| `03-ARCHITECTURE.md` (§2 Broker truth; §8 closing note) | §2 states HR-06/broker-truth as architectural doctrine (DECIDED). §8 names DEC-OPEN-09 explicitly at the persistence boundary (§7) as an item this document does not settle, without contradicting §2's DECIDED clause. |
| `04-TRADE-LIFECYCLE.md` (§1 step 17 RECONCILE; §2.2 `RECONCILED` state; §5) | States the split explicitly and repeatedly: broker-ledger authority is DECIDED (HR-06); background reconciliation *cadence* beyond an immediate post-execution reconciliation remains OPEN. §5's table labels this entry "SPLIT" using exactly that word. |
| `06-CHECKS-CATALOGUE.md` | Several BACKLOG checks in the ledger/reconciliation stage (`CHK-004`–`CHK-011`, `CHK-016`, `CHK-017`) are gated on PID §17's "periodic reconciliation"/"discrepancy classification" BACKLOG items, which are the mechanism DEC-OPEN-09's OPEN cadence clause would eventually govern; none of these checks assert a decided cadence. |
| `10-CAPABILITIES.md` (§3.2 Ledger and reconciliation) | States explicitly: "Background reconciliation cadence beyond live pre-execution read plus immediate post-execution reconciliation remains an OPEN product decision (`DEC-OPEN-09`); this backlog exists independently of that decision and does not resolve it." |

### 1.10 DEC-OPEN-10 — runtime implementation language/version

**Status: OPEN.**

**PID §19 text (verbatim, proposed, not decided):**
> Not decided by this documentation increment.

**Cross-references in the integrated document set:**

| Document | What it says |
|---|---|
| `03-ARCHITECTURE.md` (§8 closing note) | Lists DEC-OPEN-10 as part of the full DEC-OPEN-01 through DEC-OPEN-10 range not settled by that document. |

No other document in the integrated set references DEC-OPEN-10. This is expected and correct: D1 is documentation-, contract-, schema- and test-focused (PID §0) and explicitly does not choose the production runtime language (PID §21) — there is no runtime artifact in this increment for a language/version choice to touch.

---

## 2. Product Decisions Carried Into D1 (PID §30) — the DECIDED register

This is a **separate register from Section 1** and is never blended with it. These 24 items are settled unless Matt explicitly changes them (PID §30, verbatim):

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

Item 6 (broker state is authoritative trading truth) is the same DECIDED fact as DEC-OPEN-09's ledger-authority clause (§1.9 above) — restated here in its PID §30 form, not a second, independent decision.

---

## 3. Reconciliation sweep performed for this document

As part of Wave 3 reconciliation (this work item's purpose), the entire integrated Wave 1+2 document, schema and configuration-example set was checked for:

1. **Every `DEC-OPEN-nn` mention across `docs/`, `schemas/` and `config.example/`** — located by exhaustive grep, cross-referenced individually into Section 1 above. Every hit found is represented in this document; none was found unrepresented.
2. **OPEN-proposal-integration-hazard violations** — a search across every document and every schema/example for language that could be read as asserting a PID §19 "Proposed" item as settled/decided/default, outside the deliberately-illustrative examples already correctly flagged. **None found.** Every proposed value in every schema description, configuration example comment, and prose document was independently verified to carry an explicit "proposed, not decided" (or equivalent) qualification at the point it appears.
3. **T10 self-check** — every `DEC-OPEN-nn` mention outside this document was confirmed to treat that item as OPEN consistently, with the sole, correctly-labelled exception of DEC-OPEN-09's ledger-authority clause (DECIDED via HR-06), which is never merged into a single ambiguous status anywhere it appears.
4. **Cross-document terminology consistency** — spot-checked directly against the schemas and configuration examples rather than trusting prose:
   - `CHK-NNN` IDs: `docs/06-CHECKS-CATALOGUE.md` and `config.example/checks.yaml` were mechanically diffed (82 unique `CHK-NNN` references in each; zero discrepancies in either direction).
   - All JSON schemas in `schemas/` and `schemas/config/` were validated as structurally valid JSON Schema draft 2020-12 documents (`jsonschema.validators.validator_for(...).check_schema(...)`, zero failures across all twelve schema files).
   - Field names cited in this document (`conflict_policy`, `existing_position_policy`, `on_hard_limit_breach`, `sizing_mode`, `base_quantities`, `instance_id`, `broker_context`, `eligible_instruments`, `eligible_actions`, `canonical_requested_quantity`) were read directly from `config.example/*.yaml` and `schemas/config/*.schema.json`, not assumed from prose.
5. **T7 preview** — every relative markdown link/reference written in this document and in `README.md` was checked to resolve to a file that exists in this worktree (see `README.md` for the full listing).

**No cross-work-item violation requiring PL adjudication was found.** The Wave 1+2 document set is internally consistent on every OPEN decision and every cross-referenced identifier checked.
