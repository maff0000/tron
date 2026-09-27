# TRON — Project Initiation Document

**Increment:** `WO-TRON-D1` — Design documentation baseline
**PID author:** Matt (Human, product authority), drafted with Claude (claude.ai, TRADING - PLUTUS project)
**PL-sponsor:** Rogue — acts on Matt's behalf: lands this PID, boots the PL, relays product-authority questions, reports
**PL:** a Forge PL session booted from `/srv/forge` on dell-debian with `PROJECT_ROOT=/srv/tron`
**Date:** 2026-09-27

This PID follows Forge's `docs/PID-TEMPLATE.md`. Two fields are adapted
rather than answered mechanically; §0 says why.

## 0. Why this PID is adapted, and what kind of increment this is

This is a **documentation-only increment**. It produces TRON's design
baseline — requirements, architecture, contracts, check catalogue,
configuration model, capability backlog and decision register — so that the
later implementation PIDs (starting with the MVP capabilities CAP-00 to
CAP-06, §6.2) can be written against settled ground instead of re-deciding
architecture inside an Engineer dispatch.

Adapted fields:

- **§5 Presentation Target.** TRON has no user-facing surface, in this
  increment or later. No target applies. The Auditor's real-browser gate does
  not fire. See §5.
- **§12 Quality and Testing.** A documentation increment still gets
  mechanical tests: the contracts and configuration model are delivered as
  machine-checkable JSON Schemas with valid and invalid examples, and the
  tests must be able to fail (§12).

Nothing in this increment connects to a broker, to FALCON, to Redis or to
Graylog.

## 1. Identity

```text
PROJECT_ROOT:

/srv/tron   (on dell-debian)

GitHub repository:

maff0000/tron   (PRIVATE since 2026-09-27)

Remote:

git@github.com:maff0000/tron.git   (SSH via the repo-scoped deploy key)
```

**Stated by the Human, not yet verified by the PL.** The remote form above is
inferred from the deploy-key setup HELM reported on 2026-09-26 (SSH remote
plus `core.sshCommand`); it has not been driven by the author of this PID.
The PL must verify all three fields against `git -C /srv/tron remote -v` and
`git log` before relying on them, and correct this section (via the
correction rule in Forge's `docs/FORGE-NORTH-STAR.md#durable-truth`) if they
differ.

**Host constraint (hard):** all work for this project runs on
**dell-debian**. Trinity is the core agent server and AI platform and must
not host TRON work. The PL boots from a Forge hub on dell-debian
(`/srv/forge`). If no Forge hub exists on dell-debian, that is a
product-authority gap: stop and report it; do not boot from trinity.

## 2. Purpose

TRON is the **deterministic trade-execution layer** of the trading stack. It
reads potential trades posted by FALCON, applies configured rules to select
and negotiate them into broker orders, runs ordered pre-trade checks against
the broker's live state, executes through an MT5 gateway with a stop-loss and
take-profit **always** set at the broker, verifies the protection is in
place, and records every step as a structured event in Trading Graylog, where
NEO observes it.

TRON has **no intelligence**. Every decision it makes is either carried in the
posted trade or written as a declarative rule in configuration. One TRON
instance serves one broker. The broker's ledger is the source of truth.

## 3. Target Outcome

For this increment: a documentation set in `/srv/tron/docs/` (§6.1) that is:

1. **Complete** — every product decision in Appendix A is reflected, every
   check in Appendix B is catalogued, every open decision in Appendix C is
   recorded as open;
2. **Consistent** — contracts, lifecycle, checks catalogue, configuration
   model and capability list agree with each other;
3. **Machine-checkable** where it defines data — schemas and examples
   validate, and invalid examples are rejected;
4. **Honest about evidence** — every claim about broker or gateway behaviour
   is labelled MEASURED (with a source) or INFERRED (§12.3).

"Done" for the Human: Matt can read the set, confirm or change the open
decisions, and the next PID (MVP implementation) can be written by
referencing these documents rather than restating them.

## 4. Readers (adapted from §4 Users)

- **Matt** — product authority; confirms open decisions.
- **Rogue (PL-sponsor)**, the **Forge PL** session, and its **Engineer/Auditor** dispatches — this increment
  and every later TRON PID.
- **HELM / R2D2** — ops agents who build Graylog and the gateway instances
  TRON depends on.
- **FALCON builders** — consumers of the `falcon.trade_action` contract.
- **NEO** — indirect reader: consumes the `tron.event` schema via Graylog.

## 5. Presentation Target

**None applies.** TRON is a headless service; this increment is documents and
schemas. Declared explicitly so no Auditor applies, or skips, a
browser-verification gate by assumption.

## 6. Scope

### 6.1 Deliverables

All under `/srv/tron`:

```text
docs/
├── README.md                    index of the set, reading order
├── 01-CONTEXT.md                system context, trust boundaries, what TRON is not
├── 02-REQUIREMENTS.md           functional + non-functional requirements (REQ-nnn)
│                                and hard rules (HR-nn, §6.3), each traceable
├── 03-ARCHITECTURE.md           components, capability model, planned code layout,
│                                per-cycle data flow, instance/deployment layout
├── 04-TRADE-LIFECYCLE.md        pipeline steps and FIX-aligned state machines
├── 05-CONTRACTS.md              contract definitions, versioning and evolution rules
├── 06-CHECKS-CATALOGUE.md       every check: ID, stage, data source, params, MVP/backlog
├── 07-CONFIGURATION.md          config file set, validation-at-startup, config hashing
├── 08-BROKER-PROFILES.md        what varies per broker, capture method, time offset,
│                                symbol mapping
├── 09-EVENTS-AND-GRAYLOG.md     event types, GELF mapping, spool-then-ship
├── 10-CAPABILITIES.md           MVP CAP-00..06 + backlog, with a status column
├── 11-DECISIONS.md              decision register: DECIDED vs OPEN (Appendix A, C)
├── 12-SECURITY.md               secrets, least privilege, inherited risk acceptances
└── evidence/
    └── WO-TRON-D1.md            PL's evidence file for this increment

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
    ├── valid/                   ≥1 per contract schema
    └── invalid/                 the negative cases required by §12.1

config.example/                  one file per config schema, placeholders only
├── mapping.falcon.yaml
├── routing.yaml
├── selection.yaml
├── sizing.yaml
├── execution.yaml
├── checks.yaml
└── limits.yaml

tests/
└── test_docs_baseline.py        the §12.1 mechanical tests

requirements-dev.txt             test-only dependencies (pinned)
```

### 6.2 Required content, by document

**01-CONTEXT.** The flow, as decided (Appendix A):

```text
FALCON ──posts──► Redis board ──pulled by──► TRON ──► mt5-gateway ──► broker
                                               │
                                               └──► local journal ──► Trading Graylog ──► NEO (observer only)
```

It also states: one TRON per broker; FALCON down means no trading; NEO never
sends anything; what TRON is not (not a strategy engine, not a ledger of
record, not an AI agent).

**02-REQUIREMENTS.** Functional and non-functional requirements with IDs,
plus the hard rules in §6.3. Every requirement cites the Appendix A decision
it comes from, or is marked as proposed by the design partner.

**03-ARCHITECTURE.**

- The capability model: deterministic handlers, one per lifecycle step,
  enabled in config, each with its own tests and events.
- The planned code layout.
- The instance layout on the host, mirroring mt5-gateway:
  `/srv/tron-instances/<component>-<broker>-<env>-tron/{instance.env, config/, secrets/}`.
- A **Docker naming table** (HR-12) listing every container, image, volume
  and network this project will create, for example:
  - `executor-vantage-paper-tron` (one TRON executor per broker and
    environment);
  - `graylog-tron`, `opensearch-tron`, `mongodb-tron` (Trading Graylog
    stack);
  - `teststrategy-btc-tron` (the fixed BTCUSD test strategy);
  - `board-redis-tron` (the test board, if one is needed before FALCON
    exists).

  The component names are proposals; the `-tron` suffix is not.
- How TRON reaches a gateway: through its compose-scoped network, over the
  existing bridge. The bridge is unauthenticated RPyC classic; that must be
  stated, with a reference to 12-SECURITY.
- Where durable state lives (§10).

**04-TRADE-LIFECYCLE.**

- The per-cycle pipeline: pull → validate → expire → dedupe → eligibility →
  threshold → conflict → rank → select → negotiate → checks → execute →
  verify protection → record.
- Action lifecycle states.
- An order state machine aligned to FIX OrdStatus: New, PartiallyFilled,
  Filled, Canceled, Rejected, Expired.
- The TP/SL protection sequence, including the two-step fallback: open, then
  attach SL/TP, then close at once if attaching fails. It must be marked
  INFERRED as to whether any given broker needs it.

**05-CONTRACTS + schemas/.**

- `falcon.trade_action` v1:
  - `action` ∈ {OPEN, CLOSE, MODIFY, CANCEL};
  - canonical instrument;
  - `stop_loss` and `take_profit` REQUIRED on OPEN;
  - `confidence` with a declared scale;
  - `valid_until_ms`;
  - `refs` (`signal_id`, `supersedes`, `position_action_id`);
  - `extensions`.
- `tron.trade_intent` v1, including the `negotiation` block (config versions
  and an adjustments list naming the permitting rule).
- `tron.execution_report` v1 (FIX ExecutionReport semantics).
- `tron.check_report` v1: per check, its ID, stage, result, the evidence
  values it used and its config parameters.
- `tron.event` v1: the envelope that maps onto GELF.

Rules for all contracts: decimals as strings, timestamps as epoch UTC in
milliseconds, ISO 4217 currencies, JSON Schema draft 2020-12, and an explicit
policy for unknown fields.

**06-CHECKS-CATALOGUE.** Every item in Appendix B, verbatim name preserved,
plus the additions proposed in design:

- algo trading enabled in the terminal
- server-time offset known and fresh
- manual kill switch
- symbol selected in Market Watch
- filling mode supported
- tick fresh
- spread below maximum

Each check gets:

- a stable ID
- a stage (0–6, see below)
- the MT5 data it reads (named fields, e.g. `account_info().margin_level`)
- its parameters (which must exist in `checks.yaml`)
- its failure semantics
- MVP or backlog

Where an Appendix B item does not map cleanly onto MT5 (for example,
rejected orders not appearing in broker history), the document says so and
states the adapted form. It must not silently drop the item.

The stages are:

| Stage | Covers |
|---|---|
| 0 | kill switches and health |
| 1 | ledger integrity |
| 2 | idempotency and existing state |
| 3 | instrument and order validity |
| 4 | account and risk limits |
| 5 | cost |
| 6 | final post-trade projection |

Rule: all checks in a stage are evaluated; the first failing stage stops the
trade. Checks are pure functions over one consistent snapshot.

**07-CONFIGURATION.**

- The seven config files: their purpose and schemas.
- The "no config in code, ever" rule.
- Validate-or-refuse at startup.
- The hash of every config file in force is recorded in every intent and
  event.
- Honest limit: new *behaviour* needs code; new carried fields need only
  schema and mapping.

**08-BROKER-PROFILES.** What varies per broker and symbol:

- symbol names
- contract size and lot meaning
- volume min, step and max
- tick size and value
- stops and freeze level
- filling and execution modes
- margin mode
- swap
- sessions
- server timezone
- hedging versus netting

It must also state the rule that **quantity is never specified in lots
upstream**, and describe the time-offset measurement method: a live tick
compared against true UTC, rounded to 30 minutes, using a 24/7 symbol as
the weekend reference, and re-measured so daylight-saving changes are
caught.

**09-EVENTS-AND-GRAYLOG.**

- The event types.
- The GELF field mapping: key fields top-level, full payload as JSON.
- Correlation by intent ID.
- Spool-then-ship: no trade without a local journal write; a Graylog outage
  does not block trading and loses nothing.
- Never log secrets or account identifiers.
- Graylog is the audit and analysis record, not the ledger.
- Graylog's prod placement is OPEN (Appendix C).

**10-CAPABILITIES.** The MVP set, with status:

| ID | Capability |
|---|---|
| CAP-00 | foundation: config, adapter-read, symbol map, time offset, journal and shipper |
| CAP-01 | board reader |
| CAP-02 | selection |
| CAP-03 | negotiation |
| CAP-04 | MVP pre-trade checks |
| CAP-05 | open market with protection |
| CAP-06 | protection verification |

Plus the full backlog, grouped as lifecycle, ledger/reconciliation, risk,
execution robustness and operations. Each backlog item gets an ID and a
status (BACKLOG / IN-PID / DONE).

**11-DECISIONS.** Every Appendix A item as DECIDED, with its source. Every
Appendix C item as OPEN, with the options and the design partner's proposed
default, clearly labelled as a proposal. No OPEN item may be presented
anywhere in the set as if decided.

**12-SECURITY.**

- Secrets: host-only, Docker secrets, never environment variables or the
  repo.
- A read-only Redis ACL user for the FALCON board.
- Least privilege throughout.
- The risk acceptances inherited from mt5-gateway, restated with their
  revisit triggers:
  - root on dell-debian (paper only);
  - the broad gh token (extended until live credentials are used);
  - the unauthenticated bridge (must be resolved before prod);
  - KasmVNC Basic Auth over HTTP (dev only).
- A note on prop-firm rule compliance.

### 6.3 Hard rules the documents must state consistently

| ID | Rule |
|---|---|
| HR-01 | Every OPEN carries a stop-loss AND a take-profit, set at the broker and read back. No exceptions. |
| HR-02 | No configuration in code, ever. |
| HR-03 | TRON has no intelligence: rules come from config; judgement comes from the posted trade. |
| HR-04 | Timestamps are epoch UTC in milliseconds; broker server time is converted at the adapter boundary. |
| HR-05 | Prices and quantities are decimal strings, never floats. |
| HR-06 | The broker ledger is the source of truth. TRON mirrors it and never maintains an independent ledger. |
| HR-07 | Redis is messaging only. Nothing durable lives in Redis. |
| HR-08 | No trade without a durable local journal write. |
| HR-09 | Quantities are never expressed in lots upstream of TRON's negotiation step. |
| HR-10 | No secrets, account login numbers or broker/host IPs in the repository. |
| HR-11 | Market closed for an instrument means no trading on that instrument. |
| HR-12 | Everything this project builds is Docker-container based. Every container, image, volume and network it creates is named with the suffix `-tron`, and carries the Docker label `proteus.project=tron`. Volumes and networks get explicit `name:` values in compose, so Compose's default `<project>_<name>` form cannot break the suffix. The mt5-gateway containers (`mt5-<broker>-<env>`) belong to the mt5-gateway project and are not renamed. |

## 7. Non-Goals

- **No TRON implementation code.** The only code permitted is
  `tests/test_docs_baseline.py`.
- No Graylog installation, no Redis setup, no FALCON work, no broker
  connection.
- **No changes to mt5-gateway, any gateway instance, or any existing system**
  on trinity or dell-debian. No host, firewall or Docker network changes.
- **No decision on any Appendix C item.** Record it; do not decide it.
- No choice of a Python version, framework or library for the future runtime
  beyond what §8 fixes. Where the docs need one, mark it OPEN.
- Do not rewrite existing git history (see §8, "Repository lineage").

## 8. Architecture

Existing structure the work must fit:

- The repo has a gitleaks baseline: `.gitignore`, `.gitleaks.toml`, and
  `scripts/hooks/pre-commit` (via `core.hooksPath`). Keep it active; never
  bypass it with `--no-verify`.
- **Vocabulary is FIX-aligned.** NewOrderSingle maps to TradeIntent, and
  ExecutionReport keeps its name. Order states follow FIX OrdStatus. The FIX
  wire protocol is **not** adopted.
- Data is defined as JSON Schema draft 2020-12. Configuration is YAML,
  validated against JSON Schemas.
- The gateway interface is the existing mt5-gateway bridge: the MetaTrader5
  Python API surface over RPyC. Its measured behaviour is in Appendix D.
- The tests use Python with `pytest` and `jsonschema`, pinned in
  `requirements-dev.txt`. This is test tooling only, not a decision about
  TRON's runtime.

**Repository lineage.** The first commits on `main` come from the shared
mt5-gateway/tron safety baseline (`WO-MT5GW-0001`/`0002`: `.gitignore`,
`.gitleaks.toml`, the pre-commit hook). This is intentional and stays:

- Those commits are already cited by SHA in mt5-gateway's audit trail, and
  Forge doctrine forbids rewriting a commit something else points at
  (`docs/FORGE-NORTH-STAR.md#durable-truth`).
- The pending gitleaks branch was fast-forward merged into `main` on
  2026-09-27, before this PID landed.
- From this PID onward, TRON work uses its own numbering: `WO-TRON-*`.
- `docs/README.md` states this lineage in one paragraph, so a reader of the
  first commit is not misled.

May change only with a PID update: the hard rules (§6.3), the contract field
semantics listed in §6.2, and the document set in §6.1.

## 9. Repository Security

The repository is **private**. The rules below hold regardless of
visibility:

- Never commit secrets, account login numbers, account names, broker server
  names tied to an account, broker server IPs, or host IPs other than private
  addresses already used in documentation.
- Every configuration example uses placeholders only.
- The gitleaks pre-commit hook must be active. The PL verifies
  `core.hooksPath` before the first commit.
- An Auditor grep for identifiers is part of acceptance (§13).

## 10. Persistence and Durable Truth

For this increment: **git only**. The documents, schemas and tests are the
durable output.

For TRON as designed (to be documented in 03 and 09):

- The broker ledger is the source of truth.
- Redis carries the FALCON board. It is **messaging only**, per Forge's hard
  constraint; nothing durable lives there.
- TRON's durable state (processed action IDs, the intent and event journal)
  lives in a local append-only journal on the instance's persistent volume.
- Graylog is the audit and analysis record, never the ledger.

## 11. Git and GitHub

- **The Forge PL alone commits, branches and manages the PR** for the
  increment's work. The one exception is landing this PID on `main`, which
  Rogue does as PL-sponsor before the PL boots, since the startup gate
  requires it. Engineers
  never commit. This restates Forge doctrine.
- Branch: `wo/WO-TRON-D1-docs-baseline`. Commit prefix: `[WO-TRON-D1]`. One
  PR to `main`.
- Push uses the repo's deploy key. The `gh` token is used for PR operations
  on `maff0000/tron` only, per the recorded risk acceptance: never for
  settings, admin, other repositories or deletes.
- Merge happens after the Auditor's GREEN and **Matt's final acceptance**.
- The Auditor's dispatch prompt is preserved verbatim in
  `docs/evidence/WO-TRON-D1.md` beside the verdict, per Forge `SKILL.md` §8.

## 12. Quality and Testing

### 12.1 Mechanical tests (`tests/test_docs_baseline.py`)

- **T1** — every schema in `schemas/` is a valid draft 2020-12 schema.
- **T2** — every file in `schemas/examples/valid/` validates against its
  schema.
- **T3** — every file in `schemas/examples/invalid/` **fails** validation,
  and fails for its intended reason: the test asserts the failing keyword or
  path, not just "invalid". Required negative cases, at minimum:
  - an OPEN action missing `stop_loss`;
  - an OPEN action missing `take_profit`;
  - a price given as a JSON number instead of a string;
  - an unknown `action` value;
  - `confidence` outside its declared scale;
  - a `falcon.trade_action` carrying a lot quantity (HR-09).
- **T4** — every file in `config.example/` validates against its config
  schema. At least one invalid config example per schema is rejected for its
  intended reason.
- **T5** — cross-references:
  - every check ID in `06-CHECKS-CATALOGUE.md` exists in `checks.schema.json`
    and in `config.example/checks.yaml`, and the reverse;
  - every CAP ID used anywhere in `docs/` is defined in
    `10-CAPABILITIES.md`;
  - every Appendix B item appears in 06 by its verbatim name.
- **T6** — `gitleaks` is clean over the working tree and the branch
  history.
- **T7** — every relative link in `docs/` resolves.
- **T8** — every name in the 03-ARCHITECTURE Docker naming table ends in
  `-tron`. The test must fail if a non-conforming name is added: demonstrate
  this under §12.2.

### 12.2 Non-vacuity (Forge `docs/EVIDENCE-DOCTRINE.md`)

The tests must be able to fail:

- **T3 and T4 are the load-bearing proof** that the contract layer enforces
  HR-01 and HR-09. A T3 that passes because an invalid example is
  malformed for some *other* reason is vacuous. That is why the failing
  keyword or path is asserted.
- The Engineer demonstrates non-vacuity (Forge engineer rule 14) and records
  it in the evidence file:
  1. Temporarily relax a required field and show T3 then fails.
  2. Temporarily delete one Appendix B item from 06 and show T5 fails.
  3. Temporarily add a name without the `-tron` suffix to the naming table
     and show T8 fails.
  4. Revert all three.

### 12.3 Measured versus inferred

**Every claim in the documents about broker, gateway or MT5 behaviour is
labelled** either:

- **MEASURED**, with its source (a repo evidence file, or a dated HELM report
  named in Appendix D); or
- **INFERRED**, with its basis.

**No broker-behaviour claim can be proven in this increment.** The
load-bearing gate for those claims is the **live paper broker**, in the
future implementation PIDs, not any test here. The documents must say so
wherever such a claim appears. Examples of claims that must stay INFERRED
until driven:

- whether SL/TP can be attached to a market order on a given broker;
- partial-fill behaviour;
- commission reporting.

The Auditor checks this labelling (§13).

## 13. Acceptance Definition

GREEN requires all of:

1. Every §6.1 deliverable exists.
2. T1–T8 pass on the PL-integrated commit.
3. Non-vacuity is demonstrated and recorded (§12.2).
4. The Auditor independently confirms:
   - **Coverage:** every Appendix A decision appears in 11-DECISIONS as
     DECIDED; every Appendix B check appears in 06; every Appendix C item
     appears as OPEN and is nowhere presented as decided.
   - **Consistency:** the contracts, lifecycle, checks catalogue,
     configuration schemas and capability list agree. For example, every
     field a check reads exists in a contract or in the named MT5 data
     source.
   - **Hard rules:** HR-01 to HR-12 are stated identically wherever they
     appear, and nothing in the set contradicts them.
   - **Evidence labelling:** MEASURED/INFERRED labelling per §12.3, with a
     sample of MEASURED claims traced to their cited source.
   - **Security:** there are no identifiers or secrets (manual grep, with
     counts reported), and `config.example/` holds placeholders only.
   - **Naming (HR-12):** every container, image, volume and network name in
     the documents ends in `-tron`. The Auditor greps for the names used and
     reports any that break the rule.
5. The Auditor's prompt is preserved verbatim beside the verdict in
   `docs/evidence/WO-TRON-D1.md`.
6. **Matt's final acceptance** of the documentation set.

Presentation target: none (§5). No browser gate.

## 14. Development Inputs

Read before starting:

- This PID, including Appendices A–D.
- Forge: `docs/PID-TEMPLATE.md`, `docs/EVIDENCE-DOCTRINE.md`,
  `docs/FORGE-NORTH-STAR.md`, `.claude/skills/forge/SKILL.md`, and both
  agent files.
- **mt5-gateway** repository (read-only; do not modify):
  - `docs/DESIGN.md`
  - `docs/evidence/WO-MT5GW-0002.md` to the latest
  - `deploy/compose.instance.yml`
  - `bridge/rpyc_server.py`
  - `start.sh`
  - `docs/broker-profiles/vantage.json`, *if it exists* (it was requested of
    HELM, not confirmed delivered). If absent, every broker-profile value in
    08 is INFERRED or OPEN.
- tron repository: the existing baseline files on `main`.

---

## Appendix A — Product decisions (DECIDED, stated by Matt)

1. **NEO only observes**, via Trading Graylog. NEO never sends trades.
2. **FALCON is a one-way message board.** It posts potential trades to
   Redis. There is no two-way interaction between TRON and FALCON. If FALCON
   is down or has posted nothing, TRON does not trade.
3. **TRON pulls the board every 1 minute.** Accepted provisionally; the pull
   mechanism is to be revisited (Appendix C, item 5).
4. **TRON has no intelligence.** A posted trade must carry everything TRON
   needs to act. Selection is by configured rules. Example: BTCUSD requires
   confidence ≥ 90; of several qualifying posts, TRON actions the highest
   confidence.
5. **A take-profit and a stop-loss are ALWAYS set.**
6. **No configuration in code, ever.** Contracts are adjustable by adding or
   removing variables through config and schema.
7. **Lifecycle handlers are called "capabilities."** Matt delegated the choice
   of term; "skill" was rejected because it implies agent judgement.
8. **Start with only the capabilities needed to set a trade with TP/SL.**
   Keep a backlog of every capability needed for robustness and
   predictability.
9. **BTCUSD first** (the market is always open), **then XAUUSD.**
10. **The input is controlled** by a fixed, simple BTCUSD test strategy that
    triggers often. It is external to TRON and posts in FALCON's format.
11. **Trading Graylog records every trade set and completion** in JSON; NEO
    reads it; HELM builds Graylog.
12. **The broker ledger is the source of truth.** TRON reflects it rather
    than keeping its own ledger history (Matt, 2026-09-26: "a 5 min ledger
    refresh from broker"). The refresh design is in Appendix C, item 9.
13. **One TRON per broker.** Brokers: Vantage and Oanda, paper accounts.
14. **Timestamps are epoch UTC.**
15. **TRON is market-timing aware.** A closed market means no trading on that
    instrument.
16. **Market standards are used where possible.**
17. **Build step by step**; each step is proven before the next.
18. **FALCON is pre-MVP**, so the FALCON board contract is TRON's to define.
19. **Everything is built as Docker containers**, and everything this project
    builds is labelled `*-tron` so it is identifiable as belonging to TRON
    (Matt, 2026-09-27). Encoded as HR-12.

## Appendix B — Pre-trade checks specified by Matt (verbatim)

Ledger available · Ledger current · Last reconciliation successful · Account
balance reconciled · Account equity reconciled · Open positions reconciled ·
Pending orders reconciled · Filled orders reconciled · Cancelled orders
reconciled · Rejected orders reconciled · Partial fills reconciled · No orphan
positions · No orphan orders · No duplicate orders · No duplicate fills · No
unresolved execution discrepancies · No unresolved position discrepancies ·
No stale account state · No stale broker state · Proposed order not already
submitted · Proposed order not already filled · Existing position state
checked · Existing pending order state checked · Available cash checked ·
Available margin checked · Used margin checked · Free margin checked ·
Required margin checked · Projected post-trade margin checked · Projected
post-trade free margin checked · Current leverage checked · Projected
leverage checked · Current gross exposure checked · Current net exposure
checked · Projected gross exposure checked · Projected net exposure checked ·
Instrument exposure checked · Position count checked · Maximum position size
checked · Maximum order size checked · Daily realised P&L checked · Daily
unrealised P&L checked · Current account drawdown checked · Daily loss limit
checked · Maximum drawdown limit checked · Consecutive loss count checked ·
Trades-today count checked · Trading limit status checked · Stop-loss present
where required · Stop-loss distance valid · Take-profit valid where required ·
Order quantity valid · Minimum quantity checked · Maximum quantity checked ·
Quantity increment/step checked · Price increment/tick size checked ·
Contract specification current · Instrument tradable · Market open · No
trading halt · No account restriction · No margin call state · No liquidation
state · No active risk lock · No unresolved ledger exception · No unresolved
broker exception · Account currency checked · Instrument currency checked ·
FX conversion available where required · Commission/fee assumptions
available · Estimated transaction cost checked · Estimated slippage checked ·
Final post-trade account state within configured limits

**Note on "where required":** under HR-01, "Stop-loss present where required"
and "Take-profit valid where required" apply to **every** OPEN. The catalogue
keeps Matt's verbatim names and states this interpretation explicitly.

## Appendix C — OPEN decisions (record; do not decide)

For each item, 11-DECISIONS lists the options and marks the design partner's
proposal **as a proposal**.

1. **Conflict policy** when long and short actions both clear the threshold.
   Proposed: skip that instrument this cycle.
2. **Existing-position policy.** Proposed for MVP: at most one position per
   instrument; ignore new actions while one is open.
3. **Safety exits on a hard-limit breach.** Proposed for MVP: none. A breach
   blocks new trades; exits are left to broker-side SL/TP.
4. **Who owns quantity:** FALCON's post, or TRON's `sizing.yaml`. Proposed:
   fixed base-unit size in TRON config for MVP.
5. **Pull mechanism:** 1-minute polling versus Redis Streams consumer groups
   (latency and acknowledgement trade-off).
6. **Routing:** whether posts name an account, or are broker-neutral with
   TRON's routing deciding. Proposed: broker-neutral.
7. **Graylog placement in prod.** Proposed: a separate host from the
   execution VPS, fed from TRON's local spool.
8. **FALCON confidence calibration:** the requirement that confidence be
   comparable across strategies (FALCON's responsibility).
9. **Ledger mirror refresh design.** Proposed: pre-trade live read,
   post-trade deal read, and a 5-minute full sweep.
10. **TRON runtime language and version.** Python is inferred from the
    gateway bridge; not decided.
11. **Independent PID review** by CGPT, per Forge's operating model: whether
    it applies to TRON PIDs, or the claude.ai design partner fills the role.

## Appendix D — Facts available from mt5-gateway work

These were reported by HELM. Provenance is stated per Forge
`docs/EVIDENCE-DOCTRINE.md`. **Where a fact exists only in a chat report and
not in a repo evidence file, the docs cite it as "HELM report, date"; the PL
does not treat it as repo evidence.**

**MEASURED, Vantage demo on mt5-gateway rc6 (HELM, 2026-09-26/27):**

- With an ESTABLISHED broker TCP connection, the bridge calls `initialize()`,
  `terminal_info()`, `version()`, `account_info().trade_mode` (= DEMO),
  `symbol_info_tick()` and `positions_total()` all returned successfully.
  Terminal build 6230.
- BTCUSD ticks advanced over a 60-second weekend window.
- Tick timestamps read about 3 hours ahead of UTC, consistent with broker
  server time of UTC+3 in late September.
- Broker symbol names include variants: `XAUUSD` and `XAUUSD.crp`, plus
  several BTC crosses.
- `symbol_info_tick("XAUUSD")` failed with "Not found" until
  `symbol_select("XAUUSD", True)` was called, then succeeded.

**INFERRED, not established:**

- **The cause of the historical `-10005` IPC timeout.** It is **unexplained.**
  The shared `servers.dat` seed coincided with the fix, but a May 2026 test
  with a warmed `servers.dat` still failed. Documents must not state a cause.
- **Whether the broker time offset follows EU or US daylight-saving dates.**
  Undetermined; the offset must be measured, never hard-coded.
- **OANDA MT5 specifics** (server naming, the OANDA One account type, and
  the reported GMT+2/+3 server time) come from OANDA's public pages, not from
  measurement.
