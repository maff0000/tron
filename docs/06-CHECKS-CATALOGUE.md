# 06 — Pre-Trade Check Catalogue

**Work item:** WI-C (`WO-TRON-D1`)
**Owns:** this document, `schemas/config/checks.schema.json`, `config.example/checks.yaml`, and the negative examples under `schemas/examples/invalid/checks_config_*`.

This document is the canonical, individually-mapped check catalogue required by PID section 13. It assigns every check named in PID section 13 a stable ID, and defines the shared vocabulary (`06-CHECKS-CATALOGUE.md` <-> `schemas/config/checks.schema.json` <-> `config.example/checks.yaml`) that PID section 23's T4/T5 mechanical gates reconcile.

It does not decide product policy. Any concrete numeric parameter shown below or in `config.example/checks.yaml` is an **illustrative placeholder only** (PID section 1.2, section 21 D1 Non-Goals) -- never a production threshold. Where a check's very existence or scope touches a PID section 17 backlog item or a PID section 19 OPEN decision, this is called out explicitly in that check's Notes column; nothing here upgrades a BACKLOG capability or an OPEN decision to DECIDED (PID section 28).

It does not define the `tron.check_report.v1` envelope shape (owned by WI-B, `05-CONTRACTS.md` section 7 / `schemas/tron.check_report.v1.json`), the trade-lifecycle stage transitions that invoke checks (owned by WI-F, `04-TRADE-LIFECYCLE.md`), or the capability sequencing that decides which checks actually run in which implementation increment (owned by WI-E, `10-CAPABILITIES.md`, and by each capability's own future delivery PID).

---

## 1. ID assignment convention

WI-C is the sole owner of the check-ID namespace (PID section 26). IDs are `CHK-NNN`, zero-padded to three digits, matching the `tron.check_report.v1.check_id` identifier pattern `^[A-Za-z0-9_.:-]+$` (1-128 chars).

- **`CHK-001` through `CHK-073`** are assigned in the **exact order** PID section 13's flat Product Authority list presents them, left to right, top to bottom, split on the middot (`·`) separator. `CHK-001` is section 13's first item ('Ledger available'); `CHK-073` is its last ('Final post-trade account state within configured limits'). This makes the mapping mechanically reproducible and auditable by any reader: re-split PID section 13's sentence, count entries, and the sequence numbers must line up 1:1 with no gaps and no reordering.
- **`CHK-074` through `CHK-082`** are **WI-C engineer additions**, drawn from PID section 12's 'at minimum the design must consider' list (manual kill switch, execution service health, broker connectivity, broker-state freshness, instrument-state freshness, server-time offset validity, symbol availability, supported execution mode, spread/cost ceiling). PID section 13 explicitly permits this: 'Additional system-level checks may be proposed by the Architect/Engineer, but must be clearly identified as additions rather than silently attributed to Product Authority.' Every such check's Origin is `WI-C-ADD`, never `PA-13`, both in this table and in `config.example/checks.yaml`'s `origin` field.

Every Product Authority check listed in PID section 13 appears in this catalogue **exactly once** (73 of 82 total catalogue entries; the remaining 9 are WI-C additions). See section 7 for the full reconciliation index.

---

## 2. Stages (PID section 12)

| Stage | Purpose |
|---|---|
| 0 | operational safety and kill state |
| 1 | ledger/reconciliation integrity |
| 2 | idempotency and existing trade state |
| 3 | instrument and order validity |
| 4 | account and risk limits |
| 5 | execution cost |
| 6 | projected post-trade state |

Stated plainly, per PID section 12:

> All checks in a stage execute; if any check in a stage fails, later stages do not execute.

> `ERROR` is not equivalent to `PASS`; where an error creates execution uncertainty, TRON fails closed for new risk (HR-14).

---

## 3. PASS / FAIL / ERROR semantics

These semantics are uniform across every check in this catalogue (PID section 12); they are stated once here rather than repeated per row. Section 6's per-check **FAIL reason (expected)** and **ERROR condition** columns give the check-specific detail.

| Result | Meaning |
|---|---|
| `PASS` | The check's stated condition holds, using the required inputs and any configured parameters listed for that check. No `reason` is required (`tron.check_report.v1` leaves `reason` optional for `PASS`). |
| `FAIL` | The check's stated condition is violated. The stage is blocked and no later stage executes. `reason` is **required** (`tron.check_report.v1` section 9.5 / WI-B's `if`/`then`): it must explain why, using language consistent with this catalogue's FAIL reason expectation for that `check_id`. |
| `ERROR` | The check could not be evaluated to a confident PASS/FAIL -- typically because a required input listed in that check's Required Inputs column was unavailable, stale beyond what an earlier stage-0/stage-1 gate already covers, or the evaluation itself raised an unexpected fault. `ERROR` is never treated as `PASS`. Where the resulting uncertainty affects execution safety, TRON fails closed for new risk (HR-14) -- i.e. an `ERROR` blocks the stage exactly as a `FAIL` would for any check whose failure mode is safety-relevant, which is every check in stages 0-4 and every check listed below. `reason` is optional for `ERROR` (the fault detail may instead live in the durable event/journal record, per `05-CONTRACTS.md` section 7). |

---

## 4. MVP / BACKLOG status methodology

**This status column is WI-C's own documentation-level categorisation, not a new capability authorisation.** It does not decide which checks CAP-04 ('MVP pre-trade checks', PID section 16) actually implements -- that remains the CAP-04 implementation increment's own decision, made under its own PID and Product Authority sign-off. The rule applied here is mechanical and traceable to text already in this PID, so it introduces no new product decision:

1. A check that exists purely to enforce a Hard Rule (HR-01, HR-11, HR-13, HR-14) or a basic read/freshness precondition already implied by CAP-00's broker-adapter read path is marked `MVP`.
2. A check whose necessary capability is **explicitly named** in PID section 17's capability backlog (e.g. 'periodic reconciliation', 'orphan detection', 'discrepancy classification', 'account exposure limits', 'instrument exposure limits', 'drawdown limits', 'daily loss limits', 'position limits', 'order limits', 'consecutive-loss policy', 'active risk lock', 'slippage handling') is marked `BACKLOG`, because the mechanism the check depends on is itself PID section 17 BACKLOG, not because the check's Product-Authority status changes.
3. Everything else defaults to the more conservative reading available from the PID text; where a check pairs a 'current' and a 'projected' variant (e.g. exposure, margin, leverage), both variants carry the same status as the underlying capability.

Of the 82 catalogue entries, **44 are `MVP`** and **38 are `BACKLOG`** under this methodology.

---

## 5. The catalogue

Columns: **ID**, **Name** (verbatim from PID section 13 for `PA-13` origin checks), **Status** (section 4), **Required Inputs**, **Configuration Parameters** (illustrative placeholders only -- see the preamble), **FAIL reason (expected)**, **ERROR condition**, **Notes**.

### Stage 0 -- operational safety and kill state

| ID | Name | Status | Required Inputs | Configuration Parameters | FAIL reason (expected) | ERROR condition | Notes |
|---|---|---|---|---|---|---|---|
| `CHK-061` | No account restriction | MVP | Broker-reported account restriction/compliance-hold flag. | None. | Broker account carries an active trading restriction. | Broker adapter account-status query failed. |  |
| `CHK-062` | No margin call state | MVP | Broker-reported margin-call flag. | None. | Broker account is currently in margin-call state. | Broker adapter account-status query failed. |  |
| `CHK-063` | No liquidation state | MVP | Broker-reported stop-out/liquidation flag. | None. | Broker account is currently in stop-out/liquidation state. | Broker adapter account-status query failed. |  |
| `CHK-064` | No active risk lock | BACKLOG | TRON-internal risk-lock state. | None (mechanism not yet implemented). | An internal TRON risk lock is currently engaged, blocking new risk. | Risk-lock state store unavailable. | PID section 17 'active risk lock' is BACKLOG; mechanism not yet built. |
| `CHK-074` | Manual kill switch engaged *(WI-C addition)* | MVP | Operator-set kill-switch flag (runtime control surface). | None (binary operator control). | Manual kill switch is currently engaged; no new execution is permitted. | Kill-switch state store unreachable. | Engineer addition, not a PID section 13 item. |
| `CHK-075` | Execution service health *(WI-C addition)* | MVP | TRON process/service self-health signal (dependency connectivity, internal error state). | `max_consecutive_internal_errors` (illustrative placeholder). | TRON execution service reports a degraded/unhealthy internal state. | Health-check subsystem itself failed to report. | Engineer addition, not a PID section 13 item. |
| `CHK-076` | Broker connectivity *(WI-C addition)* | MVP | Broker adapter connectivity/session state. | `connectivity_timeout_ms` (illustrative placeholder). | Broker adapter reports no active/healthy connection to the broker. | Connectivity state itself could not be read. | Engineer addition, not a PID section 13 item. |
| `CHK-077` | Broker-state freshness *(WI-C addition)* | MVP | Broker adapter last-successful-read timestamp (adapter-level, distinct from CHK-019's decision-scoped snapshot). | `max_broker_state_age_ms` (illustrative placeholder). | Most recent broker state read exceeds the configured maximum age. | Last-read timestamp unavailable. | Engineer addition, not a PID section 13 item; HR-14. |
| `CHK-078` | Instrument-state freshness *(WI-C addition)* | MVP | Instrument/tick data last-update timestamp. | `max_instrument_state_age_ms` (illustrative placeholder). | Most recent instrument/tick state exceeds the configured maximum age. | Last-update timestamp unavailable. | Engineer addition, not a PID section 13 item; HR-14. |
| `CHK-079` | Server-time offset validity *(WI-C addition)* | MVP | Broker/server time vs canonical TRON time (UTC epoch ms, HR-04). | `max_clock_offset_ms` (illustrative placeholder). | Observed offset between broker/server time and canonical TRON time exceeds the configured maximum. | Server time could not be read from the broker adapter. | Engineer addition, not a PID section 13 item. |

### Stage 1 -- ledger/reconciliation integrity

| ID | Name | Status | Required Inputs | Configuration Parameters | FAIL reason (expected) | ERROR condition | Notes |
|---|---|---|---|---|---|---|---|
| `CHK-001` | Ledger available | MVP | Broker adapter ledger/account read result for this cycle. | None. | Broker ledger read did not succeed or returned no usable snapshot. | Broker adapter call raised an error or timed out before any snapshot was obtained. |  |
| `CHK-002` | Ledger current | MVP | Ledger snapshot timestamp. | `max_ledger_age_ms` (illustrative placeholder). | Ledger snapshot exceeds the configured maximum age and is not considered current. | Snapshot timestamp is missing or unparseable. | HR-14: staleness beyond threshold fails closed for new risk. |
| `CHK-003` | Last reconciliation successful | MVP | Most recent reconciliation-run outcome record (local journal). | None. | Most recent reconciliation run did not complete successfully, or its outcome is unknown. | No reconciliation-run record exists yet to evaluate. |  |
| `CHK-004` | Account balance reconciled | BACKLOG | Local journal balance vs broker-reported balance. | `balance_tolerance` (illustrative placeholder; policy BACKLOG). | Local record of account balance does not match broker-reported balance within tolerance. | Either source value unavailable for comparison. | PID section 17 'periodic reconciliation' is BACKLOG; mechanism not yet implemented. |
| `CHK-005` | Account equity reconciled | BACKLOG | Local journal equity vs broker-reported equity. | `equity_tolerance` (illustrative placeholder; policy BACKLOG). | Local record of account equity does not match broker-reported equity within tolerance. | Either source value unavailable for comparison. | PID section 17 'periodic reconciliation' is BACKLOG. |
| `CHK-006` | Open positions reconciled | BACKLOG | Local journal open positions vs broker-reported open positions. | None. | Local record of open positions does not match broker-reported open positions. | Either source set unavailable for comparison. | PID section 17 'periodic reconciliation' is BACKLOG. |
| `CHK-007` | Pending orders reconciled | BACKLOG | Local journal pending orders vs broker-reported pending orders. | None. | Local record of pending orders does not match broker-reported pending orders. | Either source set unavailable for comparison. | PID section 17 'periodic reconciliation' is BACKLOG. |
| `CHK-008` | Filled orders reconciled | BACKLOG | Local journal filled orders vs broker execution/deal history. | None. | Local record of filled orders does not match broker execution/deal history. | Either source set unavailable for comparison. | PID section 17 'periodic reconciliation' is BACKLOG. |
| `CHK-009` | Cancelled orders reconciled | BACKLOG | Local journal cancelled orders vs broker order history. | None. | Local record of cancelled orders does not match broker order history. | Either source set unavailable for comparison. | PID section 17 'periodic reconciliation' is BACKLOG. |
| `CHK-010` | Rejected orders reconciled | BACKLOG | Local journal rejected orders vs broker order history. | None. | Local record of rejected orders does not match broker order history. | Either source set unavailable for comparison. | PID section 17 'periodic reconciliation' is BACKLOG. |
| `CHK-011` | Partial fills reconciled | BACKLOG | Local journal partial-fill records vs broker execution/deal history. | None. | Local record of partial fills does not match broker execution/deal history. | Either source set unavailable for comparison. | PID section 17 'periodic reconciliation' is BACKLOG. |
| `CHK-012` | No orphan positions | BACKLOG | Broker-reported open positions vs local journal position records. | None. | A broker-reported position has no corresponding local journal record, or vice versa. | Either source set unavailable for comparison. | PID section 17 'orphan detection' is BACKLOG. |
| `CHK-013` | No orphan orders | BACKLOG | Broker-reported orders vs local journal order records. | None. | A broker-reported order has no corresponding local journal record, or vice versa. | Either source set unavailable for comparison. | PID section 17 'orphan detection' is BACKLOG. |
| `CHK-014` | No duplicate orders | BACKLOG | Broker-reported order set (ledger-level integrity, distinct from CHK-020's per-action idempotency). | None. | Broker ledger appears to contain duplicate order records for the same intent. | Order set unavailable for inspection. | Same capability family as PID section 17 'orphan detection' / 'discrepancy classification', BACKLOG. |
| `CHK-015` | No duplicate fills | BACKLOG | Broker execution/deal history. | None. | Broker execution/deal history appears to contain duplicate fill records. | Execution/deal history unavailable for inspection. | Same capability family as PID section 17 'discrepancy classification', BACKLOG. |
| `CHK-016` | No unresolved execution discrepancies | BACKLOG | Open discrepancy records from prior reconciliation runs. | None. | One or more previously identified execution discrepancies remain unresolved. | Discrepancy-record store unavailable. | PID section 17 'discrepancy classification' is BACKLOG. |
| `CHK-017` | No unresolved position discrepancies | BACKLOG | Open discrepancy records from prior reconciliation runs. | None. | One or more previously identified position discrepancies remain unresolved. | Discrepancy-record store unavailable. | PID section 17 'discrepancy classification' is BACKLOG. |
| `CHK-018` | No stale account state | MVP | Timestamp of the account-state snapshot used for this decision. | `max_account_state_age_ms` (illustrative placeholder). | Account state snapshot used for this check exceeds the configured maximum age. | Snapshot timestamp missing or unparseable. | HR-14: staleness beyond threshold fails closed for new risk. |
| `CHK-019` | No stale broker state | MVP | Timestamp of the broker-state snapshot used for this decision. | `max_broker_state_age_ms` (illustrative placeholder). | Broker state snapshot used for this check exceeds the configured maximum age. | Snapshot timestamp missing or unparseable. | HR-14: staleness beyond threshold fails closed for new risk. |
| `CHK-065` | No unresolved ledger exception | BACKLOG | Open ledger-exception records. | None. | One or more previously raised ledger exceptions remain unresolved. | Exception-record store unavailable. | Same capability family as PID section 17 'discrepancy classification', BACKLOG. |
| `CHK-066` | No unresolved broker exception | BACKLOG | Open broker-adapter-exception records. | None. | One or more previously raised broker-adapter exceptions remain unresolved. | Exception-record store unavailable. | Same capability family as PID section 17 'discrepancy classification', BACKLOG. |

### Stage 2 -- idempotency and existing trade state

| ID | Name | Status | Required Inputs | Configuration Parameters | FAIL reason (expected) | ERROR condition | Notes |
|---|---|---|---|---|---|---|---|
| `CHK-020` | Proposed order not already submitted | MVP | Proposed action identity vs journal of previously submitted intents/orders. | None. | An order for this action identity has already been submitted; resubmission is blocked. | Journal lookup could not be completed. | HR-13: execution must be idempotent with respect to action identity. |
| `CHK-021` | Proposed order not already filled | MVP | Proposed action identity vs journal/broker fill records. | None. | This action identity is already associated with a filled order. | Journal/broker lookup could not be completed. | HR-13. |
| `CHK-022` | Existing position state checked | MVP | Broker-reported existing position for the instrument, if any. | None. | Existing position state for this instrument could not be determined. | Broker adapter position query failed. | Observation only; the policy applied to an existing position (DEC-OPEN-02) remains OPEN and is not decided by this check. |
| `CHK-023` | Existing pending order state checked | MVP | Broker-reported pending orders for the instrument, if any. | None. | Existing pending-order state for this instrument could not be determined. | Broker adapter order query failed. |  |

### Stage 3 -- instrument and order validity

| ID | Name | Status | Required Inputs | Configuration Parameters | FAIL reason (expected) | ERROR condition | Notes |
|---|---|---|---|---|---|---|---|
| `CHK-049` | Stop-loss present where required | MVP | Trade intent `stop_loss` field, for `action == OPEN`. | None; unconditional for OPEN. | Proposed OPEN action has no stop-loss set. | Trade intent could not be read. | HR-01: every OPEN trade must have stop-loss protection. |
| `CHK-050` | Stop-loss distance valid | MVP | Proposed stop-loss price; instrument stop-distance constraint (broker profile). | None (constraint sourced from broker/instrument profile, PID section 11). | Proposed stop-loss distance is inside the instrument's minimum stop-distance constraint. | Broker profile stop-distance constraint unavailable. |  |
| `CHK-051` | Take-profit valid where required | MVP | Trade intent `take_profit` field, for `action == OPEN`. | None; unconditional for OPEN. | Proposed OPEN action has no valid take-profit set. | Trade intent could not be read. | HR-01: every OPEN trade must have take-profit protection. |
| `CHK-052` | Order quantity valid | MVP | Negotiated broker order quantity. | None (composite of CHK-053/054/055). | Negotiated order quantity is not valid for this instrument. | One or more contributing checks returned ERROR. | Composite gate over CHK-053, CHK-054, CHK-055. |
| `CHK-053` | Minimum quantity checked | MVP | Negotiated quantity; instrument minimum-quantity constraint (broker profile). | None (constraint sourced from broker profile). | Negotiated quantity is below the instrument's minimum tradable quantity. | Broker profile minimum-quantity constraint unavailable. |  |
| `CHK-054` | Maximum quantity checked | MVP | Negotiated quantity; instrument maximum-quantity constraint (broker profile). | None (constraint sourced from broker profile). | Negotiated quantity exceeds the instrument's maximum tradable quantity. | Broker profile maximum-quantity constraint unavailable. |  |
| `CHK-055` | Quantity increment/step checked | MVP | Negotiated quantity; instrument quantity-step constraint (broker profile). | None (constraint sourced from broker profile). | Negotiated quantity is not an exact multiple of the instrument's quantity step. | Broker profile quantity-step constraint unavailable. |  |
| `CHK-056` | Price increment/tick size checked | MVP | Any explicit order price; instrument tick-size constraint (broker profile). | None (constraint sourced from broker profile). | Order price is not aligned to the instrument's tick size. | Broker profile tick-size constraint unavailable. |  |
| `CHK-057` | Contract specification current | MVP | Locally cached instrument contract specification vs broker adapter's current specification. | `max_contract_spec_age_ms` (illustrative placeholder). | Locally held contract specification for this instrument is stale or mismatched. | Broker adapter contract-specification query failed. |  |
| `CHK-058` | Instrument tradable | MVP | Broker-reported instrument tradability flag. | None. | Instrument is not currently tradable. | Broker adapter tradability query failed. | HR-11: no OPEN when the instrument is not currently tradable. |
| `CHK-059` | Market open | MVP | Broker-reported/trading-session market state for the instrument. | None (session definition sourced from broker profile, PID section 11). | Instrument's market/trading session is not currently open. | Session-state query failed. |  |
| `CHK-060` | No trading halt | MVP | Broker-reported trading-halt state for the instrument. | None. | Instrument is currently subject to a trading halt. | Halt-state query failed. |  |
| `CHK-067` | Account currency checked | MVP | Account base currency (broker adapter). | None. | Account base currency could not be determined or is not recognised. | Broker adapter account query failed. |  |
| `CHK-068` | Instrument currency checked | MVP | Instrument quote/settlement currency (broker profile/adapter). | None. | Instrument currency could not be determined or is not recognised. | Broker profile/adapter query failed. |  |
| `CHK-069` | FX conversion available where required | MVP | Account currency (CHK-067), instrument currency (CHK-068), available FX conversion rate/path. | None. | Account and instrument currencies differ and no FX conversion path/rate is currently available. | FX-rate source unavailable or unreachable. | HR-14: unavailable required conversion fails closed for new risk. |
| `CHK-080` | Symbol availability *(WI-C addition)* | MVP | Canonical instrument; broker symbol-mapping/profile resolution result. | None. | Canonical instrument does not resolve to a broker-tradable symbol. | Symbol-mapping table unavailable. | Engineer addition, not a PID section 13 item. |
| `CHK-081` | Supported execution/filling mode *(WI-C addition)* | MVP | Broker-reported supported order/filling modes for the instrument (broker profile). | `required_execution_mode` (illustrative placeholder). | Instrument does not currently support the execution/filling mode TRON requires. | Broker profile/adapter execution-mode query failed. | Engineer addition, not a PID section 13 item. |

### Stage 4 -- account and risk limits

| ID | Name | Status | Required Inputs | Configuration Parameters | FAIL reason (expected) | ERROR condition | Notes |
|---|---|---|---|---|---|---|---|
| `CHK-024` | Available cash checked | MVP | Broker-reported available cash. | None (compared against the proposed order's cash requirement). | Insufficient available cash for the proposed order. | Broker adapter account query failed. |  |
| `CHK-025` | Available margin checked | MVP | Broker-reported available margin. | None. | Insufficient available margin for the proposed order. | Broker adapter account query failed. |  |
| `CHK-026` | Used margin checked | MVP | Broker-reported used margin. | None. | Used margin could not be determined from the current broker snapshot. | Broker adapter account query failed. | Primarily an observed-evidence input feeding CHK-025/027/029. |
| `CHK-027` | Free margin checked | MVP | Broker-reported free margin. | None. | Free margin could not be determined, or is insufficient for the proposed order. | Broker adapter account query failed. |  |
| `CHK-028` | Required margin checked | MVP | Broker adapter's order-margin estimate for the proposed order. | None. | Required margin for the proposed order could not be determined. | Broker adapter margin-estimate call failed. |  |
| `CHK-031` | Current leverage checked | MVP | Broker-reported current account leverage. | `max_leverage` (illustrative placeholder). | Current account leverage exceeds the configured maximum. | Broker adapter account query failed. |  |
| `CHK-033` | Current gross exposure checked | BACKLOG | Sum of broker-reported open-position notional (gross). | `max_gross_exposure` (illustrative placeholder; policy BACKLOG). | Current gross exposure exceeds the configured maximum. | Position set unavailable for aggregation. | PID section 17 'account exposure limits' is BACKLOG. |
| `CHK-034` | Current net exposure checked | BACKLOG | Sum of broker-reported open-position notional (net). | `max_net_exposure` (illustrative placeholder; policy BACKLOG). | Current net exposure exceeds the configured maximum. | Position set unavailable for aggregation. | PID section 17 'account exposure limits' is BACKLOG. |
| `CHK-037` | Instrument exposure checked | BACKLOG | Broker-reported open-position notional for this instrument. | `max_instrument_exposure` (illustrative placeholder; policy BACKLOG). | Exposure to this instrument exceeds the configured maximum. | Position query for this instrument failed. | PID section 17 'instrument exposure limits' is BACKLOG. |
| `CHK-038` | Position count checked | BACKLOG | Broker-reported open position count. | `max_position_count` (illustrative placeholder; policy BACKLOG). | Open position count is at or above the configured maximum. | Position set unavailable. | PID section 17 'position limits' is BACKLOG. |
| `CHK-039` | Maximum position size checked | BACKLOG | Broker-reported/projected position size for this instrument. | `max_position_size` (illustrative placeholder; policy BACKLOG). | Resulting position size would exceed the configured maximum. | Position size cannot be determined. | PID section 17 'position limits' is BACKLOG. |
| `CHK-040` | Maximum order size checked | BACKLOG | Negotiated order quantity/notional. | `max_order_size` (illustrative placeholder; policy BACKLOG). | Proposed order size exceeds the configured maximum. | Negotiated quantity unavailable. | PID section 17 'order limits' is BACKLOG. |
| `CHK-041` | Daily realised P&L checked | BACKLOG | Journal/broker daily realised P&L. | None. | Daily realised P&L could not be determined. | Journal/broker query failed. | Input to CHK-044 (daily loss limit); PID section 17 'daily loss limits' is BACKLOG. |
| `CHK-042` | Daily unrealised P&L checked | BACKLOG | Journal/broker daily unrealised P&L. | None. | Daily unrealised P&L could not be determined. | Journal/broker query failed. | Input to CHK-044 (daily loss limit); PID section 17 'daily loss limits' is BACKLOG. |
| `CHK-043` | Current account drawdown checked | BACKLOG | Broker-reported equity vs configured/reference high-water mark. | `drawdown_reference_basis` (illustrative placeholder; policy BACKLOG). | Current account drawdown could not be determined. | Reference high-water mark unavailable. | PID section 17 'drawdown limits' is BACKLOG. |
| `CHK-044` | Daily loss limit checked | BACKLOG | Daily realised + unrealised P&L (CHK-041, CHK-042). | `daily_loss_limit` (illustrative placeholder; policy BACKLOG). | Daily loss limit is breached. | Upstream P&L inputs unavailable. | PID section 17 'daily loss limits' is BACKLOG. |
| `CHK-045` | Maximum drawdown limit checked | BACKLOG | Current account drawdown (CHK-043). | `max_drawdown_limit` (illustrative placeholder; policy BACKLOG). | Maximum drawdown limit is breached. | Upstream drawdown input (CHK-043) unavailable. | PID section 17 'drawdown limits' is BACKLOG. |
| `CHK-046` | Consecutive loss count checked | BACKLOG | Journal record of recent trade outcomes. | `max_consecutive_losses` (illustrative placeholder; policy BACKLOG). | Consecutive loss count is at or above the configured maximum. | Journal trade-outcome history unavailable. | PID section 17 'consecutive-loss policy' is BACKLOG. |
| `CHK-047` | Trades-today count checked | BACKLOG | Journal record of trades executed today. | `max_trades_per_day` (illustrative placeholder; policy BACKLOG). | Trades-today count is at or above the configured maximum. | Journal trade history unavailable. | Same capability family as PID section 17 'consecutive-loss policy' / trading-limit BACKLOG items. |
| `CHK-048` | Trading limit status checked | BACKLOG | Aggregate trading-limit state (composite of CHK-044, CHK-045, CHK-046, CHK-047). | None (composite; each contributing limit is independently configured). | One or more configured trading limits are currently breached. | One or more contributing checks returned ERROR. | Composite of BACKLOG limit checks; PID section 17. |

### Stage 5 -- execution cost

| ID | Name | Status | Required Inputs | Configuration Parameters | FAIL reason (expected) | ERROR condition | Notes |
|---|---|---|---|---|---|---|---|
| `CHK-070` | Commission/fee assumptions available | BACKLOG | Broker profile commission/fee schedule. | None. | No commission/fee assumption is available for this instrument/broker combination. | Broker profile has no commission/fee data configured. | Feeds CHK-071; PID section 12 minimum-consideration list, engineering scope BACKLOG pending cost-estimation capability. |
| `CHK-071` | Estimated transaction cost checked | BACKLOG | Current spread/price, negotiated quantity, commission assumptions (CHK-070). | `max_estimated_transaction_cost` (illustrative placeholder; policy BACKLOG). | Estimated transaction cost exceeds the configured maximum. | Upstream inputs (price/commission) unavailable. | Cost-estimation capability not yet built; BACKLOG. |
| `CHK-072` | Estimated slippage checked | BACKLOG | Recent observed slippage / current spread and liquidity signal. | `max_estimated_slippage` (illustrative placeholder; policy BACKLOG). | Estimated slippage exceeds the configured maximum. | Liquidity/spread signal unavailable. | PID section 17 'slippage handling' is BACKLOG. |
| `CHK-082` | Spread/cost ceiling *(WI-C addition)* | BACKLOG | Current observed spread for the instrument. | `max_acceptable_spread` (illustrative placeholder; policy BACKLOG). | Current spread exceeds the configured ceiling. | Spread/quote data unavailable. | Engineer addition, not a PID section 13 item; grouped with cost-estimation BACKLOG items. |

### Stage 6 -- projected post-trade state

| ID | Name | Status | Required Inputs | Configuration Parameters | FAIL reason (expected) | ERROR condition | Notes |
|---|---|---|---|---|---|---|---|
| `CHK-029` | Projected post-trade margin checked | MVP | Broker adapter's projected margin-after-fill estimate for the proposed order. | None. | Projected post-trade margin could not be determined, or would be insufficient. | Broker adapter projection call failed. |  |
| `CHK-030` | Projected post-trade free margin checked | MVP | Projected post-trade margin (CHK-029) and projected post-trade equity. | `min_projected_free_margin` (illustrative placeholder). | Projected post-trade free margin would fall below the configured minimum. | Upstream projection (CHK-029) unavailable. |  |
| `CHK-032` | Projected leverage checked | MVP | Projected post-trade equity and exposure. | `max_projected_leverage` (illustrative placeholder). | Projected post-trade leverage would exceed the configured maximum. | Projection inputs unavailable. |  |
| `CHK-035` | Projected gross exposure checked | BACKLOG | Current gross exposure (CHK-033) plus the proposed order's notional. | `max_gross_exposure` (illustrative placeholder; policy BACKLOG). | Projected post-trade gross exposure would exceed the configured maximum. | Upstream aggregation (CHK-033) unavailable. | Pairs with CHK-033; PID section 17 'account exposure limits' is BACKLOG. |
| `CHK-036` | Projected net exposure checked | BACKLOG | Current net exposure (CHK-034) plus the proposed order's signed notional. | `max_net_exposure` (illustrative placeholder; policy BACKLOG). | Projected post-trade net exposure would exceed the configured maximum. | Upstream aggregation (CHK-034) unavailable. | Pairs with CHK-034; PID section 17 'account exposure limits' is BACKLOG. |
| `CHK-073` | Final post-trade account state within configured limits | BACKLOG | Composite of all stage-4 and stage-6 projected/limit checks. | None (composite gate; each contributing limit is independently configured). | Projected post-trade account state would breach one or more configured limits. | One or more contributing checks returned ERROR. | Composite capstone check; full semantics depend on currently-BACKLOG limit checks (e.g. CHK-035/036/045). A minimal MVP variant restricted to margin/leverage sufficiency (CHK-029/030/032) may be exercised earlier under CAP-05; the complete check as stated is BACKLOG. |

---

## 6. Section 13 verbatim cross-check

For independent verification, PID section 13's flat list is reproduced here split into its 73 constituent items in original order, each paired with the `CHK-NNN` this document assigned it. An auditor can re-split PID section 13's sentence on `·` and diff the result against this list.

| # | PID section 13 item (verbatim) | Assigned ID |
|---|---|---|
| 1 | Ledger available | `CHK-001` |
| 2 | Ledger current | `CHK-002` |
| 3 | Last reconciliation successful | `CHK-003` |
| 4 | Account balance reconciled | `CHK-004` |
| 5 | Account equity reconciled | `CHK-005` |
| 6 | Open positions reconciled | `CHK-006` |
| 7 | Pending orders reconciled | `CHK-007` |
| 8 | Filled orders reconciled | `CHK-008` |
| 9 | Cancelled orders reconciled | `CHK-009` |
| 10 | Rejected orders reconciled | `CHK-010` |
| 11 | Partial fills reconciled | `CHK-011` |
| 12 | No orphan positions | `CHK-012` |
| 13 | No orphan orders | `CHK-013` |
| 14 | No duplicate orders | `CHK-014` |
| 15 | No duplicate fills | `CHK-015` |
| 16 | No unresolved execution discrepancies | `CHK-016` |
| 17 | No unresolved position discrepancies | `CHK-017` |
| 18 | No stale account state | `CHK-018` |
| 19 | No stale broker state | `CHK-019` |
| 20 | Proposed order not already submitted | `CHK-020` |
| 21 | Proposed order not already filled | `CHK-021` |
| 22 | Existing position state checked | `CHK-022` |
| 23 | Existing pending order state checked | `CHK-023` |
| 24 | Available cash checked | `CHK-024` |
| 25 | Available margin checked | `CHK-025` |
| 26 | Used margin checked | `CHK-026` |
| 27 | Free margin checked | `CHK-027` |
| 28 | Required margin checked | `CHK-028` |
| 29 | Projected post-trade margin checked | `CHK-029` |
| 30 | Projected post-trade free margin checked | `CHK-030` |
| 31 | Current leverage checked | `CHK-031` |
| 32 | Projected leverage checked | `CHK-032` |
| 33 | Current gross exposure checked | `CHK-033` |
| 34 | Current net exposure checked | `CHK-034` |
| 35 | Projected gross exposure checked | `CHK-035` |
| 36 | Projected net exposure checked | `CHK-036` |
| 37 | Instrument exposure checked | `CHK-037` |
| 38 | Position count checked | `CHK-038` |
| 39 | Maximum position size checked | `CHK-039` |
| 40 | Maximum order size checked | `CHK-040` |
| 41 | Daily realised P&L checked | `CHK-041` |
| 42 | Daily unrealised P&L checked | `CHK-042` |
| 43 | Current account drawdown checked | `CHK-043` |
| 44 | Daily loss limit checked | `CHK-044` |
| 45 | Maximum drawdown limit checked | `CHK-045` |
| 46 | Consecutive loss count checked | `CHK-046` |
| 47 | Trades-today count checked | `CHK-047` |
| 48 | Trading limit status checked | `CHK-048` |
| 49 | Stop-loss present where required | `CHK-049` |
| 50 | Stop-loss distance valid | `CHK-050` |
| 51 | Take-profit valid where required | `CHK-051` |
| 52 | Order quantity valid | `CHK-052` |
| 53 | Minimum quantity checked | `CHK-053` |
| 54 | Maximum quantity checked | `CHK-054` |
| 55 | Quantity increment/step checked | `CHK-055` |
| 56 | Price increment/tick size checked | `CHK-056` |
| 57 | Contract specification current | `CHK-057` |
| 58 | Instrument tradable | `CHK-058` |
| 59 | Market open | `CHK-059` |
| 60 | No trading halt | `CHK-060` |
| 61 | No account restriction | `CHK-061` |
| 62 | No margin call state | `CHK-062` |
| 63 | No liquidation state | `CHK-063` |
| 64 | No active risk lock | `CHK-064` |
| 65 | No unresolved ledger exception | `CHK-065` |
| 66 | No unresolved broker exception | `CHK-066` |
| 67 | Account currency checked | `CHK-067` |
| 68 | Instrument currency checked | `CHK-068` |
| 69 | FX conversion available where required | `CHK-069` |
| 70 | Commission/fee assumptions available | `CHK-070` |
| 71 | Estimated transaction cost checked | `CHK-071` |
| 72 | Estimated slippage checked | `CHK-072` |
| 73 | Final post-trade account state within configured limits | `CHK-073` |

---

## 7. Reconciliation index (for PID section 23 T5)

All `CHK-NNN` identifiers used by this catalogue, for direct diffing against `schemas/config/checks.schema.json` and `config.example/checks.yaml`:

```text
CHK-001, CHK-002, CHK-003, CHK-004, CHK-005, CHK-006, CHK-007, CHK-008, CHK-009, CHK-010, CHK-011, CHK-012, CHK-013, CHK-014, CHK-015, CHK-016, CHK-017, CHK-018, CHK-019, CHK-020, CHK-021, CHK-022, CHK-023, CHK-024, CHK-025, CHK-026, CHK-027, CHK-028, CHK-029, CHK-030, CHK-031, CHK-032, CHK-033, CHK-034, CHK-035, CHK-036, CHK-037, CHK-038, CHK-039, CHK-040, CHK-041, CHK-042, CHK-043, CHK-044, CHK-045, CHK-046, CHK-047, CHK-048, CHK-049, CHK-050, CHK-051, CHK-052, CHK-053, CHK-054, CHK-055, CHK-056, CHK-057, CHK-058, CHK-059, CHK-060, CHK-061, CHK-062, CHK-063, CHK-064, CHK-065, CHK-066, CHK-067, CHK-068, CHK-069, CHK-070, CHK-071, CHK-072, CHK-073, CHK-074, CHK-075, CHK-076, CHK-077, CHK-078, CHK-079, CHK-080, CHK-081, CHK-082
```

Total: 82 (`CHK-001`-`CHK-073` = PID section 13, 73 items; `CHK-074`-`CHK-082` = WI-C additions, 9 items). Every ID in this list appears in exactly one row of section 5 and exactly one entry of `config.example/checks.yaml`'s `checks` map -- see the evidence in the WI-C handback report for the actual diff command and output.

