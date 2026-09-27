# 08 — Broker Profiles

**Work item:** WI-D (`WO-TRON-D1`)
**Owns:** this document.

This document is descriptive/conceptual only. It does not define a JSON Schema or configuration file in this increment — see §4. It does not decide product policy; nothing here upgrades a PID §19 OPEN proposal to a decided requirement.

---

## 1. Why broker profiles exist

Per PID §11: **broker and instrument differences are data, not reasons to fork TRON.** TRON's core logic must not contain broker-specific branches (`if broker == "X"`); broker- and instrument-specific facts are supplied as data a single TRON codebase consumes. This is the same doctrine as PID §4.5 (configuration over hard-coding) applied specifically to the broker boundary (PID §6.3): broker-specific quirks belong behind the Broker Adapter or in broker-profile data, not throughout TRON core.

A direct consequence (HR-09, restated in PID §11's closing line): **upstream systems do not need to know broker lot semantics.** FALCON and any other upstream producer of `falcon.trade_action.v1` deals exclusively in canonical instrument identifiers and canonical (non-lot) quantities. Broker lot size, step, and rounding are entirely a broker-profile/negotiation-boundary concern, invisible above `tron.trade_intent.v1`.

## 2. What a broker profile may describe

Per PID §11, a broker profile may describe:

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

## 3. Three categories — apply throughout

Every fact a broker profile touches must be classified as exactly one of:

- **configured fact** — a value TRON holds in its own configuration or profile data, set by an operator/engineer ahead of time, not read live from the broker at the moment of use.
- **observed runtime fact** — a value read live from the broker adapter at (or shortly before) the moment it is used, reflecting the broker's own current state.
- **derived value** — a value TRON computes from other configured facts and/or observed runtime facts; it is not itself stored as either a static configured value or a direct 1:1 broker read-back.

**Runtime broker state takes precedence over stale profile assumptions where the adapter exposes an authoritative current value.** A configured fact is a starting assumption or a fallback for when live state is unavailable — it is never treated as more current than an available live read. Where no authoritative live read is available and a configured fact cannot safely stand in for it, HR-14 governs: broker-state uncertainty that affects execution safety fails closed for new risk. This document does not decide, for any specific field below, exactly when a live read is "available" or "authoritative enough" — that is CAP-00/CAP-03 (Broker Adapter and negotiation) implementation behaviour, out of scope for D1.

The table below classifies each PID §11 item under its typical category. Where a broker adapter can expose a live value for an item that is more commonly configured, the runtime-precedence rule above still applies — the table states the typical/default category, not an exhaustive rule for every broker.

| Item | Typical category | Notes |
|---|---|---|
| Broker symbol mapping | Configured fact | Held in `mapping.falcon.yaml` (`07-CONFIGURATION.md`), not this document's schema. |
| Contract size | Configured fact | Should be reconciled against an adapter-reported instrument specification when available (PID §13: "Contract specification current"); a stale configured value that disagrees with a fresher observed one is exactly the kind of discrepancy that check exists to catch. |
| Quantity minimum / maximum / step | Configured fact | Same reconciliation posture as contract size; also feeds "Minimum quantity checked" / "Maximum quantity checked" / "Quantity increment/step checked" (PID §13). |
| Tick size / tick value | Configured fact | Same reconciliation posture; feeds "Price increment/tick size checked" (PID §13). |
| Stop-distance constraints | Configured fact, frequently also observed runtime fact | Many brokers report a live minimum stop distance ("freeze level") that can change with volatility; where the adapter exposes it live, the live value is authoritative over a stale configured assumption. |
| Freeze constraints | Observed runtime fact, where the adapter exposes it | A freeze window is inherently a current-market-state condition, not a fixed configured property, even though a configured fallback/assumption may exist for when it cannot be read live. |
| Supported order/filling modes | Configured fact | Declares what TRON is configured to attempt (see also `execution.yaml`'s `supported_execution_modes`, `07-CONFIGURATION.md`); cross-checked against adapter-reported capability where available — a mode configured but unsupported by the live adapter/instrument is not silently attempted. |
| Margin semantics | Configured fact (qualitative rules) | The *rules* (e.g. how margin is computed for an instrument class) are typically configured/known ahead of time; the resulting *numbers* (used margin, free margin, required margin) are observed runtime facts read from the broker ledger (PID §13: "Used margin checked" / "Free margin checked" / "Required margin checked"), never re-derived from a stale profile assumption. |
| Execution mode | Configured fact | e.g. an assumption about instant vs. market/request execution; actual behaviour at submission is proven only by observed execution outcome (`tron.execution_report.v1`), not assumed from the profile. |
| Account mode | Configured fact, frequently also observable | e.g. hedging vs. netting; many adapters can report this directly from account state, in which case the observed value takes precedence over a stale configured assumption. |
| Trading sessions | Configured fact | A configured schedule assumption; whether the market is *actually* open right now is an observed runtime fact (PID §13: "Market open", HR-11), never inferred solely from the configured session table when a live read is available. |
| Server-time characteristics | Configured fact (assumption) + derived value | A configured assumption about the broker server's time behaviour; the *actual offset* between broker server time and TRON's own clock is a derived value, computed from an observed runtime read of server time compared against local time (feeds PID §13's "server-time offset validity" consideration, §13 bullet list). |
| Commission/fee assumptions where known | Configured fact, where known | Explicitly qualified "where known" in PID §11 — absence of a configured assumption for a given instrument means no estimate is available for pre-trade cost checks (PID §13: "Commission/fee assumptions available"), not that commission is zero. Actual commission charged on a fill is an observed/reported fact carried on `tron.execution_report.v1`'s fill record (`05-CONTRACTS.md` §6), never inferred from the profile assumption after the fact. |

Representative **derived values** not already covered above: a broker-valid negotiated quantity (canonical requested quantity rounded to the configured/observed step and clamped to min/max — the value that becomes `tron.trade_intent.v1.negotiated_quantity`); an estimated transaction cost or spread-based cost ceiling check outcome; a server-time offset (as above); a margin-utilisation ratio computed from observed used/free margin. None of these are themselves stored as a static configured value or a raw 1:1 broker read-back — they are computed at the point of use.

## 4. No broker-profile schema/config file in this increment

The configuration file set this increment delivers (`07-CONFIGURATION.md` §1) contains `mapping.falcon.yaml` — symbol mapping only — but **no separate broker-profile schema or config file**. This is deliberate, not an oversight: WI-D's assigned deliverables (PID §20, PID §26 WI-D scope) list exactly six configuration schemas/examples, and none of them is a broker-profile file; D1's non-goals (PID §21) explicitly exclude implementing CAP-00 through CAP-06, and materialising the richer broker-profile data model above into a validated configuration file (or into Broker Adapter capability data) is foundation/negotiation implementation behaviour — CAP-00 and CAP-03's job, not D1's.

This document therefore serves as the **conceptual data model** a later capability increment must turn into schema-backed configuration and/or Broker Adapter capability data, once that increment is scoped and authorised. Nothing in this document should be read as an already-approved schema shape for that future file — in particular, the table in §3 is a classification aid, not a field list committing to specific property names, types, or a specific file structure.

## 5. Relationship to canonical contracts

`tron.trade_intent.v1.broker_instrument` (`05-CONTRACTS.md` §5) is the point where a broker profile's symbol-mapping fact (§2/§3 above, materialised today only as `mapping.falcon.yaml`) enters a canonical contract. No other broker-profile fact from §2 has a direct field on any canonical contract in this increment — quantity/tick/margin/session facts inform negotiation and pre-trade check *behaviour* (CAP-03/CAP-04, owned elsewhere), not the contract *shape* itself, which is intentionally broker-agnostic.
