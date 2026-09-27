# 07 — Configuration

**Work item:** WI-D (`WO-TRON-D1`)
**Owns:** this document, `08-BROKER-PROFILES.md`, and the six configuration schemas/examples: `schemas/config/mapping.schema.json`, `schemas/config/routing.schema.json`, `schemas/config/selection.schema.json`, `schemas/config/sizing.schema.json`, `schemas/config/execution.schema.json`, `schemas/config/limits.schema.json`, and `config.example/mapping.falcon.yaml`, `config.example/routing.yaml`, `config.example/selection.yaml`, `config.example/sizing.yaml`, `config.example/execution.yaml`, `config.example/limits.yaml`.

This document does not decide product policy. Anything here that touches a PID §19 OPEN decision is explicitly flagged as such; nothing here upgrades an OPEN proposal to a decided requirement.

It does not own `schemas/config/checks.schema.json` or `config.example/checks.yaml` — those files and `06-CHECKS-CATALOGUE.md` belong to WI-C, which controls the check-ID namespace. This document treats `checks.yaml` as part of the same configuration model (PID §10 lists it alongside the files WI-D owns) but does not define its shape.

---

## 1. The configuration file set

Per PID §10, TRON's configuration is separated by responsibility into these files:

| File | Schema | Owner |
|---|---|---|
| `mapping.falcon.yaml` | `schemas/config/mapping.schema.json` | WI-D |
| `routing.yaml` | `schemas/config/routing.schema.json` | WI-D |
| `selection.yaml` | `schemas/config/selection.schema.json` | WI-D |
| `sizing.yaml` | `schemas/config/sizing.schema.json` | WI-D |
| `execution.yaml` | `schemas/config/execution.schema.json` | WI-D |
| `checks.yaml` | `schemas/config/checks.schema.json` | WI-C |
| `limits.yaml` | `schemas/config/limits.schema.json` | WI-D |

Each file is a distinct, independently schema-validated unit. A parameter belongs in exactly one file according to its responsibility; this document does not introduce a general-purpose or catch-all configuration file (PID §4.5 — configuration must not become an embedded programming language).

Broker-profile data (contract size, tick size, quantity constraints, and the rest of PID §11's list) is **not** one of the seven files above and has no schema in this increment — see `08-BROKER-PROFILES.md` §4 for why, and what that means for later capability delivery.

## 2. Configuration schema versioning

Each of the six schemas WI-D owns declares a `config_schema_version` string property, `const "1"`, mirroring the `contract_version` convention `05-CONTRACTS.md` §2 establishes for the canonical message contracts:

- A **backward-compatible** change (adding a new optional field, widening an enum by adding a member, adding a new map key convention) is released **within the same file**, `config_schema_version` stays `"1"`.
- A **breaking** change (removing/renaming a field, changing required-ness or type, narrowing an existing enum) requires incrementing `config_schema_version` and is treated as a new configuration schema major version, documented here when it happens. It is not decided silently by an example update.

This convention is a WI-D configuration-design detail, not a Product Authority decision — it exists purely so a loaded configuration file's structural generation is self-declared and checkable, the same way message contracts are.

## 3. `additionalProperties` policy

Every configuration schema sets `additionalProperties` explicitly, following the same posture WI-B established for the canonical contracts (`05-CONTRACTS.md` §3): **`false`** at the top level and on every fixed-shape nested object. An unrecognised field in a configuration file is a validation failure, not silently ignored — this is how "no operational configuration is hard-coded into TRON business logic" (HR-02) stays mechanically checkable: a new parameter requires a schema change, not an undeclared field slipped into an existing file.

The deliberate exceptions, all genuinely open-keyed maps rather than fixed contract surfaces:

- `mapping.schema.json`'s `mappings` — keyed by canonical instrument, an open set defined by which instruments FALCON/TRON currently support, not fixed by this schema.
- `sizing.schema.json`'s `base_quantities` — keyed the same way.
- `limits.schema.json`'s `max_instrument_exposure` and `max_order_size` — keyed the same way.

These are the only places additional properties are permitted anywhere in the configuration schema set WI-D owns.

## 4. Startup validation pipeline

Per PID §10, TRON's startup sequence is:

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

**load** — each configuration file is read from its configured location and parsed (YAML, per the file extensions in PID §20).

**schema validate** — each parsed file is validated against its corresponding JSON Schema (draft 2020-12) from the table in §1. This stage catches structural defects: wrong types, missing required fields, values outside a declared pattern or enum, unrecognised fields.

**semantic validate** — business-rule constraints that are not expressible (or not reasonably expressible) as JSON Schema are checked here. For example: `limits.yaml`'s `max_drawdown_pct` is schema-constrained only to be a non-negative decimal string (JSON Schema patterns cannot bound an arbitrary-precision decimal string's numeric value); a percentage's upper bound of 100 is a semantic-validate concern. Likewise, whether a configured numeric ceiling is internally coherent (e.g. `default_max_order_size` not being smaller than every per-instrument override that is meant to be an exception to it) is a semantic-validate concern, not a schema concern. This document does not enumerate every semantic rule — it establishes that schema validity and semantic validity are two distinct, sequential gates, and that a config passing schema validation is not yet proven usable.

**cross-config validate** — referential and consistency checks that span more than one file. For example: a canonical instrument referenced in `sizing.yaml.base_quantities`, `limits.yaml.max_instrument_exposure`/`max_order_size`, or `routing.yaml.eligible_instruments` is expected to also exist as a key in `mapping.falcon.yaml.mappings` — otherwise TRON would be configured to size, limit, or route an instrument it has no broker symbol resolution for. Defining the exact cross-config rule set exhaustively is implementation behaviour for a later capability (CAP-00), not a D1 documentation deliverable; this section establishes that the pipeline stage exists and names representative examples of what it is for.

**hash** — once a configuration set passes every validation stage, TRON computes and records the identity/hash of that configuration set. This is the configuration identity referenced by HR-15 and by `tron.trade_intent.v1.config_identities` (`05-CONTRACTS.md` §5): a map from configuration-file identity name (`mapping`, `routing`, `selection`, `sizing`, `execution`, `checks`, `limits` — the same seven names as §1's table) to the hash/version identity of the configuration responsible for a given negotiated intent. Because `config_identities` is an open-keyed map (not fixed by the contract itself), this document is the authoritative source for which keys are expected to appear in it for a fully configured TRON instance.

**start** — only once every prior stage has succeeded does TRON begin operating.

### Hard requirement: invalid configuration means refuse startup

**If any configuration file fails schema validation, semantic validation, or cross-config validation, TRON must refuse to start.** There is no partial start, no degraded-mode start on unvalidated configuration, and no silent fallback to defaults not present in the validated configuration set. This is stated plainly because PID §10 states it plainly: "Invalid configuration means refuse startup." A TRON instance that has started is, by construction, one whose entire configuration set has already passed all four validation stages.

## 5. Configuration identity ties to every execution decision

Per HR-15 ("Every material execution decision must be reconstructable from durable events, configuration identity and observed evidence") and PID §10's closing line ("TRON records the identity/hash of the configuration set responsible for every execution decision"): the hash computed at the **hash** pipeline stage is not a one-time startup artifact. It is attached to the negotiated intent that produced any given execution (`tron.trade_intent.v1.config_identities`) and, transitively, to every event and journal record correlated to that intent. A later reconstruction of "why did TRON do this" must be able to answer "under exactly which configuration content" without ambiguity.

## 6. Secrets are not configuration

**Secrets, credentials, account identifiers, and other sensitive infrastructure identifiers must not be stored in any of the seven files in §1's table (HR-10).** None of the six schemas WI-D owns has a field intended to carry such a value — see each schema's `identifier`/`instance_id`/`broker_context` field descriptions, which are explicit that these are symbolic labels, never literal account numbers, logins, or credential material.

Where a runtime capability eventually needs an actual credential (e.g. a broker API key, an account login) to resolve a symbolic label such as `routing.yaml`'s `broker_context`, that resolution mechanism is external to these configuration files — sourced from a separate, non-repository secrets store, consistent with the repository's `.gitignore` (`secrets/`, `*.secret`, `*.pem`, `*.key`, `credentials.json`, `.env*`) and PID §1.2/§22. **Defining that secrets-resolution mechanism itself is out of scope for D1** — it is runtime/infrastructure implementation behaviour for a later capability, not a documentation-only increment's deliverable.

## 7. OPEN decisions reflected in this configuration set

The following configuration schemas/examples touch a PID §19 OPEN decision. In every case the schema itself is kept as decision-agnostic as reasonably possible, and only the example's concrete value reflects the PID's currently proposed (not decided) direction:

| Decision | File(s) | How it is kept OPEN |
|---|---|---|
| **DEC-OPEN-01** (conflicting candidate actions) | `selection.schema.json` / `selection.yaml` | `conflict_policy` is an enum of three named policies, not a single hard-coded value; the example uses `"skip_instrument"` (the PID's proposed initial policy), clearly labelled as proposed, not decided. |
| **DEC-OPEN-02** (existing-position policy) | `selection.schema.json` / `selection.yaml` | `existing_position_policy` is an enum of two named policies; the example uses `"one_position_per_instrument"` (the PID's proposed MVP), clearly labelled as proposed, not decided. |
| **DEC-OPEN-03** (response to hard-limit breach) | `limits.schema.json` / `limits.yaml` | `on_hard_limit_breach` is an enum of two named responses; the example uses `"block_new_risk"` (the PID's proposed MVP), clearly labelled as proposed, not decided. |
| **DEC-OPEN-04** (quantity ownership) | `sizing.schema.json` / `sizing.yaml` | The entire file's shape (`sizing_mode: "fixed_canonical_quantity"` plus `base_quantities`) implements exactly the PID's proposed MVP quantity-ownership model, per this work item's explicit instruction to build the schema to hold that shape. `sizing_mode` is included precisely so that a different eventual Product Authority answer is representable as a new named mode rather than an implicit redefinition of an existing field. The proposed/not-decided status is stated in the schema's own `description`, in this document, and in `11-DECISIONS.md`. |
| **DEC-OPEN-06** (routing) | `routing.schema.json` / `routing.yaml` | This file deliberately contains no upstream-destination/routing field of any kind — consistent with `falcon.trade_action.v1` and `tron.trade_intent.v1` having none (`05-CONTRACTS.md` §4/§5). It only describes this instance's own scope (`instance_id`, `broker_context`, `eligible_instruments`, `eligible_actions`), which PID §4.3 already establishes independently of how DEC-OPEN-06 is eventually resolved — even a future per-message routing field would not remove the need for an instance to know its own broker/account context. |

None of the above example values may be read as a decided Product Authority requirement. `11-DECISIONS.md` (WI-H) is authoritative for the current status of every PID §19 item.

## 8. Example index (for WI-I)

### Valid (`config.example/`) — each validates against its corresponding schema, satisfying PID §23 T4's first clause

| File | Schema |
|---|---|
| `mapping.falcon.yaml` | `mapping.schema.json` |
| `routing.yaml` | `routing.schema.json` |
| `selection.yaml` | `selection.schema.json` |
| `sizing.yaml` | `sizing.schema.json` |
| `execution.yaml` | `execution.schema.json` |
| `limits.yaml` | `limits.schema.json` |

### Invalid (`schemas/examples/invalid/`) — each must fail validation for the stated reason, satisfying PID §23 T4's second clause

| File | Schema | Intended failure | Failing keyword/path observed |
|---|---|---|---|
| `config_mapping_missing_broker_instrument.json` | `mapping.schema.json` | mapping entry missing required `broker_instrument` | `required` under `/properties/mappings/additionalProperties` |
| `config_routing_missing_broker_context.json` | `routing.schema.json` | missing required `broker_context` | `required` at top level |
| `config_selection_invalid_conflict_policy_enum.json` | `selection.schema.json` | unsupported `conflict_policy` value (`"allow_both"`) | `enum` at `/properties/conflict_policy` |
| `config_sizing_quantity_numeric_not_decimal_string.json` | `sizing.schema.json` | numeric (not decimal-string) quantity | `type` under `/properties/base_quantities/additionalProperties` (expected string, got number) |
| `config_execution_unsupported_mode_enum.json` | `execution.schema.json` | unsupported execution mode value (`"stop"`) | `enum` under `/properties/supported_execution_modes/items` |
| `config_limits_missing_on_hard_limit_breach.json` | `limits.schema.json` | missing required `on_hard_limit_breach` | `required` at top level |

This table gives every one of WI-D's six configuration schemas at least one deliberate negative example, per PID §23 T4.
