# 05 — Contracts & Canonical Schemas

**Work item:** WI-B (`WO-TRON-D1`)
**Owns:** this document, and `schemas/falcon.trade_action.v1.json`, `schemas/tron.trade_intent.v1.json`, `schemas/tron.execution_report.v1.json`, `schemas/tron.check_report.v1.json`, `schemas/tron.event.v1.json`, and their examples under `schemas/examples/`.

This document is authoritative for the **shape** of TRON's five canonical message contracts. It does not decide product policy. Anything here that touches a PID section 19 OPEN decision is explicitly flagged as such; nothing here upgrades an OPEN proposal to a decided requirement.

It does not define trade-lifecycle transition semantics (owned by WI-F, `04-TRADE-LIFECYCLE.md`), the check catalogue (owned by WI-C, `06-CHECKS-CATALOGUE.md`), the event-type catalogue (owned by WI-G, `09-EVENTS-AND-GRAYLOG.md`), or configuration file schemas (owned by WI-D, `07-CONFIGURATION.md`).

---

## 1. Conventions applied to all five contracts

These are the common rules from PID §9.1, made concrete and applied identically across all five schemas.

| Rule | Concrete convention |
|---|---|
| JSON Schema draft | `"$schema": "https://json-schema.org/draft/2020-12/schema"` on every schema file. |
| Timestamps | UTC epoch milliseconds, JSON `integer`, `minimum: 0` (HR-04). Field names end `_ms` (e.g. `valid_until_ms`, `occurred_at_ms`), except `tron.check_report.v1`'s `timestamp` field, which is named literally `timestamp` because that is the exact field name PID §9.5 lists (kept identical for easy cross-referencing by WI-I / WI-C). |
| Prices, monetary amounts, quantities | Decimal strings, never binary floats (HR-05). Non-negative fields (prices, quantities) use pattern `^\d+(\.\d+)?$`; fields that may legitimately be signed (e.g. commission, or an adjustment's before/after value) use `^-?\d+(\.\d+)?$`. Never `"type": "number"` for these. |
| Currencies | ISO 4217 three-letter codes, pattern `^[A-Z]{3}$`, used where a contract carries a currency (only `tron.execution_report.v1`'s fill `commission_currency` does today). |
| Stable identifiers | Explicit named string fields (`action_id`, `intent_id`, `report_id`, `check_id`, `event_id`, `correlation_id`, etc.), pattern `^[A-Za-z0-9_.:-]+$`, 1–128 chars. |
| Contract version | See §2 below. |
| Unknown-field behaviour | See §3 below. |
| Optional-field semantics | Every optional field's absence meaning is documented in prose in this file and in the schema's own `description`, not left implicit. |

## 2. Versioning convention

Every canonical contract is identified two ways, applied consistently:

1. The major version is embedded in the filename and `$id` (e.g. `falcon.trade_action.v1.json`, `$id: https://tron.internal/schemas/falcon.trade_action.v1.json`).
2. Every message instance also carries a required `contract_version` field (a string, e.g. `"1"`), equal to the same version number. This is deliberately redundant with (1) so that a consumer inspecting a single message payload — without out-of-band knowledge of which topic/file produced it — can still identify its exact contract version.

**Evolution policy (kept deliberately simple):**

- A **backward-compatible** change (adding a new *optional* field, widening a pattern, adding a new enum member in a schema that isn't used as a closed catalogue gate) is released as a schema update **within the same `v1` file**, `contract_version` stays `"1"`. Existing required fields, their types, and their semantics never change under a stationary version.
- A **breaking** change (removing/renaming a field, changing a field's required-ness or type, narrowing/changing the meaning of an existing enum value) requires a **new major contract**: a new file (`*.v2.json`), a new `$id`, and `contract_version: "2"`. The `v1` file and its examples are **not deleted**; both are published side by side until producers/consumers have migrated, at which point `v1`'s deprecation is recorded in this document — it is never silently removed.
- Consumers should treat an unrecognised `contract_version` value for a schema they consume as a hard validation failure, not as a value to guess-parse.

## 3. Unknown-field (`additionalProperties`) policy per contract

Every object schema sets `additionalProperties` explicitly. The default posture is **`false`** at every canonical contract's top level and on every fixed-shape nested object (e.g. `fill_event`, `protection`, adjustment entries) — an unrecognised field on a canonical message is a validation failure, not silently ignored, so upstream/downstream drift is caught immediately (this is also how HR-09's "no broker lot quantity upstream" is mechanically enforced for `falcon.trade_action.v1`: there is no field for it, and `additionalProperties: false` means one cannot be smuggled in).

Two deliberate, documented exceptions to `false`, both set to `additionalProperties: true` because they are **intentionally open-keyed maps**, not fixed contract surfaces:

- `tron.trade_intent.v1.config_identities` — keys are configuration-file identity names (owned by WI-D's `07-CONFIGURATION.md`), not fixed by this contract.
- `tron.check_report.v1.observed_evidence` and `configured_parameters` — shape varies per `check_id` (owned by WI-C's catalogue).
- `falcon.trade_action.v1.extensions` and `tron.event.v1.payload` — explicit forward-compatible extension bags; canonical fields never live inside them.

These exceptions are the only places additional properties are permitted anywhere in the contract set.

## 4. `falcon.trade_action.v1`

File: `schemas/falcon.trade_action.v1.json`.

Required always: `contract_version`, `action_id`, `action`, `instrument`, `valid_until_ms`, `strategy_ref`.
Required additionally when `action == "OPEN"` (via `if`/`then`): `side`, `stop_loss`, `take_profit`, `confidence` (HR-01).
Optional, with documented absence-semantics in the schema: `signal_ref`, `supersedes_action_id`, `position_action_ref`, `extensions`, and `side`/`stop_loss`/`take_profit`/`confidence` for non-OPEN actions.

**Confidence scale — WI-B contract-design detail (not a Product Authority decision).** Confidence is a decimal string on a closed `[0.0000, 1.0000]` scale, pattern `^(0(\.\d{1,4})?|1(\.0{1,4})?)$` (up to 4 decimal places), consistent with HR-05's decimal-string rule. Declaring *a* concrete scale so the field is structurally testable is a bounded contract-design detail within WI-B's authority (the PID does not list it under §19 OPEN items). This is explicitly **separate** from **DEC-OPEN-08** (cross-strategy confidence *calibration* — i.e. whether a `0.80` from one strategy means the same real-world thing as a `0.80` from another). DEC-OPEN-08 remains genuinely OPEN; nothing here decides it. The `0.7500` value used in the valid example is illustrative only, to prove schema validity — it asserts no calibration meaning.

**HR-09 (no broker lot quantity upstream):** enforced structurally — the schema has no quantity field of any kind, and `additionalProperties: false` prevents one being added. Canonical/negotiated quantity only exists from `tron.trade_intent.v1` onward, past TRON's negotiation boundary.

**Illustrative-only note:** none of this contract's example field values encode `DEC-OPEN-04` or `DEC-OPEN-06` (this schema has no quantity or routing/broker-destination field at all — see §7 below).

## 5. `tron.trade_intent.v1`

File: `schemas/tron.trade_intent.v1.json`.

Required: `contract_version`, `intent_id`, `source_action_id`, `canonical_instrument`, `broker_instrument`, `direction`, `canonical_requested_quantity`, `negotiated_quantity`, `config_identities`, `created_at_ms`, `negotiated_at_ms`, `correlation_id`.
Optional, documented: `requested_protection`, `negotiated_protection` (a shared `protection` sub-schema requiring `stop_loss`+`take_profit` together when the object is present at all; absence means "not applicable to this intent," not a waiver of HR-01), `permitted_adjustments` (absent or `[]` both mean "no adjustments made" — documented as equivalent representations).

**DEC-OPEN-04 illustrative-only note.** `canonical_requested_quantity` (`"0.0100"` in the valid example) is a concrete value used solely to prove the schema validates a well-formed decimal-string quantity. It does **not** establish whether canonical quantity originates upstream from FALCON or from TRON sizing configuration — that is exactly **DEC-OPEN-04**, which remains OPEN. The schema records whatever value negotiation received/produced without taking a position on its origin.

**DEC-OPEN-06 note.** This contract has no "target broker/account" field. Per DEC-OPEN-06's proposed policy (actions remain broker-neutral; a TRON instance's own configuration determines its eligible actions), routing is not part of any per-message contract in this set — it is out of scope for `tron.trade_intent.v1` by design, not merely by omission.

## 6. `tron.execution_report.v1`

File: `schemas/tron.execution_report.v1.json`.

Required: `contract_version`, `report_id`, `intent_id`, `action_id`, `order_state`, `instrument`, `direction`, `requested_quantity`, `cumulative_filled_quantity`, `fills`, `last_updated_ms`, `correlation_id`.
Optional: `broker_order_id` (absent = broker never acknowledged/assigned an order id, e.g. a pre-submission Rejected), `leaves_quantity` (absent = not read back for this snapshot; its absence asserts nothing about `order_state`), `rejection_reason` (conditionally **required** when `order_state == "Rejected"`, via `if`/`then` — a rejection is never left unexplained).

**Multiple execution events / partial fills.** `fills` is an array of `fill_event` objects (`execution_id`, `filled_at_ms`, `fill_quantity`, `fill_price`, optional `commission`/`commission_currency`), so one report can represent zero, one, or many broker execution events for the same order — an order is never modelled as necessarily atomic. The valid example demonstrates two fills summing to `cumulative_filled_quantity`.

**Lifecycle-semantics boundary (binding ruling).** `order_state` uses **exactly** the six values named in PID §8: `New`, `PartiallyFilled`, `Filled`, `Canceled`, `Rejected`, `Expired`. No additional states are added. This contract does not encode *how* an order reaches a given state, does not encode transition rules, and does not distinguish FALCON-action-state / TRON-intent-state / broker-order-state / position-state from each other beyond what this one contract represents (broker-order-state only) — that full distinction, and all transition logic, belongs entirely to WI-F's `04-TRADE-LIFECYCLE.md`.

## 7. `tron.check_report.v1`

File: `schemas/tron.check_report.v1.json`.

Required: `contract_version`, `check_id`, `stage` (integer `0`–`6`, per PID §12's stage table), `result` (`PASS`/`FAIL`/`ERROR`), `observed_evidence`, `configured_parameters`, `timestamp`.
`reason` is **conditionally required when `result == "FAIL"`** (via `if`/`then`), per PID §9.5's "a failed check must explain why it failed." It remains optional (but permitted) for `PASS` and `ERROR`.

This contract intentionally carries exactly PID §9.5's seven listed fields plus `contract_version` — no additional fields (e.g. no correlation identifiers) were added, to avoid WI-B expanding this contract's surface beyond what the PID specifies; joining a check report to a specific action/intent is a journal/event-correlation concern, not this envelope's.

## 8. `tron.event.v1`

File: `schemas/tron.event.v1.json`.

Required: `contract_version`, `event_id`, `event_type`, `occurred_at_ms`, `correlation_id`.
Optional/conditional (present **"where those identities exist"**, per PID §9.6 — never force-required uniformly): `action_id`, `intent_id`, `order_id`, `execution_id`. `payload` is an optional open extension object.

`correlation_id` is the one identity that **is** always required, independent of which of the four specific identities exist for a given event — it is the top-level chain-correlation handle that HR-15 needs regardless of which lifecycle stage produced the event.

`event_type` is a pattern-constrained (dot-namespaced, e.g. `action.received`) free-form string, **not** a closed enum against PID §15's list. PID §15 explicitly says its list is events "at minimum," so closing the enum here would wrongly forbid legitimate future event types that are WI-G's (`09-EVENTS-AND-GRAYLOG.md`) catalogue to define, not WI-B's.

## 9. Example index (for WI-I)

### Valid (`schemas/examples/valid/`) — each validates against its named schema

| File | Schema | Purpose |
|---|---|---|
| `falcon_trade_action_open_valid.json` | `falcon.trade_action.v1` | Well-formed OPEN action with all conditional fields present. |
| `tron_trade_intent_valid.json` | `tron.trade_intent.v1` | Full negotiated intent including a recorded adjustment and multi-key `config_identities`. |
| `tron_execution_report_valid.json` | `tron.execution_report.v1` | `Filled` order built from **two** fill events, proving multi-event support. |
| `tron_check_report_pass_valid.json` | `tron.check_report.v1` | `PASS` result, `reason` legitimately absent. |
| `tron_check_report_fail_with_reason_valid.json` | `tron.check_report.v1` | `FAIL` result **with** `reason` present, proving the conditional-required path is satisfiable. |
| `tron_event_valid.json` | `tron.event.v1` | Event with all four correlated identities present plus `payload`. |

### Invalid (`schemas/examples/invalid/`) — each must fail validation for the stated reason

| File | Schema | Intended failure | Failing keyword/path observed |
|---|---|---|---|
| `falcon_trade_action_open_missing_stop_loss.json` | `falcon.trade_action.v1` | OPEN missing `stop_loss` | `required` under the `then` branch (`if`/`then`), missing `stop_loss` |
| `falcon_trade_action_open_missing_take_profit.json` | `falcon.trade_action.v1` | OPEN missing `take_profit` | `required` under the `then` branch, missing `take_profit` |
| `falcon_trade_action_stop_loss_numeric_price.json` | `falcon.trade_action.v1` | numeric (not decimal-string) price | `type` at `/properties/stop_loss` (expected string, got number) |
| `falcon_trade_action_unsupported_action_value.json` | `falcon.trade_action.v1` | unsupported `action` value (`"REVERSE"`) | `enum` at `/properties/action` |
| `falcon_trade_action_invalid_confidence_value.json` | `falcon.trade_action.v1` | out-of-scale confidence (`"1.5000"`) | `pattern` at `/properties/confidence` |
| `falcon_trade_action_broker_lot_quantity_present.json` | `falcon.trade_action.v1` | upstream broker-lot quantity present (`lot_quantity`) | `additionalProperties` (HR-09) |
| `falcon_trade_action_malformed_timestamp.json` | `falcon.trade_action.v1` | malformed timestamp (ISO-8601 string instead of epoch ms) | `type` at `/properties/valid_until_ms` (expected integer, got string) |
| `tron_check_report_unknown_field_present.json` | `tron.check_report.v1` | prohibited/unknown field (`debug_note`) | `additionalProperties` |
| `tron_check_report_fail_missing_reason.json` | `tron.check_report.v1` | `FAIL` without `reason` | `required` under the `then` branch, missing `reason` |
| `tron_execution_report_invalid_state_value.json` | `tron.execution_report.v1` | unsupported `order_state` value (`"Suspended"`) | `enum` at `/properties/order_state` |
| `tron_trade_intent_quantity_numeric_not_decimal_string.json` | `tron.trade_intent.v1` | numeric (not decimal-string) quantity | `type` at `/properties/negotiated_quantity` (expected string, got number) |

This table covers all eight PID §23 T3 minimum negative cases (missing stop-loss, missing take-profit, numeric price, unsupported action, invalid confidence, broker-lot quantity, malformed timestamp, prohibited/unknown field) plus three additional cases (FAIL result on `tron.check_report.v1` without a required `reason`, invalid `order_state` enum value, numeric quantity on `tron.trade_intent.v1`) for broader coverage across the contract set.
