# GOLD-AUD-D mirror note: TRON facts

Mirror note of the read-only audit `GOLD-AUD-D` (GOLD MVP lane D). The primary evidence is in `maff0000/GOAL` at `audits/2026-10-15/gold-mvp/lanes/GOLD-AUD-D/` on branch `wo/GOLD-AUD-D-evidence` (opened for review as `maff0000/GOAL` pull request #14). This note carries only the TRON facts, and is written to the public-repository standard: no addresses, hostnames, ports, account or credential identifiers. It changes nothing outside `docs/evidence/GOLD-AUD-D/`.

## 1. Revisions read

| Ref | Full SHA |
|---|---|
| `main` | `5577039b5db05e70effef72c7e59df14db408419` |
| `wo/WO-TRON-D1` | `37d5f009a080d25930eea37cf8c627bb0f3a1ff4` |

Nine branches `wo/WO-TRON-D1-wi-a` to `-wi-i` (tips `b884fd4`, `c4b605a`, `4c2e907`, `b18c338`, `45ddefc`, `0458277`, `87e9453`, `8186127`, `32f4f54`) were each checked with `git merge-base --is-ancestor <branch> origin/wo/WO-TRON-D1`: all nine are ancestors of D1.

## 2. Inventory (re-confirmed, read-only)

- `main` holds four files: `.gitignore`, `.gitleaks.toml`, `PID.md`, `scripts/hooks/pre-commit`. There is no runtime code.
- D1 is 20 commits ahead of `main` (11 non-merge), 60 files changed, 5044 insertions, 0 deletions. Its one Python file is `tests/test_docs_baseline.py`, which imports only `json`, `re`, `pathlib`, `pytest`, `yaml`, `jsonschema`. Nothing on any ref executes, signs, or calls a broker.
- `python3 -m pytest -q tests` in a scratch copy of D1: `148 passed`. This proves document, schema and example consistency only (D1 PID section 29).
- `gh pr list --state all` shows one pull request (#1, merged, gitleaks rules). There is no pull request for D1.
- D1's own secret-scan evidence says "14 commits scanned"; 23 commits are reachable at the commit it names and 24 at the tip. The count is unexplained; a full-history scan is a ratification precondition.

## 3. Gate coverage against the minimum DEMO path

Script over `config.example/checks.yaml` at D1: 82 checks, 44 MVP (enabled) and 38 BACKLOG (disabled).

| Required element | D1 state |
|---|---|
| Fixed base quantity from configuration | `schemas/config/sizing.schema.json` and `config.example/sizing.yaml` exist (placeholder values; the quantity-ownership decision is proposed, not decided) |
| One position per instrument | policy proposed only; the check that touches it (CHK-022) observes and decides nothing |
| Maximum open positions | `max_position_count` in the limits schema; CHK-038 is BACKLOG, disabled |
| Daily loss guard | `max_daily_loss` in the limits schema; CHK-041, 042, 044 BACKLOG, disabled |
| Daily trade-count guard | `max_trades_per_day` exists only as a parameter of CHK-047 in `checks.yaml`; no key in the limits schema |
| Kill switch with a setter | CHK-074 is MVP and enabled; its setter (capability BL-OPS-01) is BACKLOG. A separate stage-0 check, CHK-064 (risk lock), has its own state store |
| Hard gates before submit, fail-closed | exposure, order-size, drawdown, risk-lock checks BACKLOG, disabled; ERROR-never-PASS semantics are documented and in the check-report schema |

## 4. Execution journal (minimum behaviour for the first path)

Journal commit before the first submit call; deterministic idempotent identity with store-enforced uniqueness; claim and exactly one terminal disposition per trigger; uncertain submissions recorded UNKNOWN and never resubmitted; reconcile before any new write after a start; outbox written in the journal transaction; integrity state feeding the "no new risk" input. An in-memory implementation behind a journal port suffices up to the DEMO read-only increments; a durable implementation is required before the restart proof. The store choice (decision R-4) is not made here.

## 5. Trigger-intake assumptions

D1 assumes a Redis board of `falcon.trade_action.v1` with an `action_id` identity, no signature, `valid_until_ms` expiry, stop and target on every OPEN, and terminal states REJECTED, EXPIRED, DUPLICATE, NEGOTIATED. Against the `GOAL-TRIGGER-001` candidate (not yet an authority): 23 assumptions recorded, 8 covered, 10 contradicted, 5 unspecified (primary evidence `TRIGGER-ASSUMPTIONS.md`). D1 has no signature, signing or key-trust concept anywhere.

## 6. Findings that concern this repository

Primary evidence ids: F-D-01 (single kill switch: on the CA arrangement of 16 Oct 2026 `TRON-T3A` owns the kill state and `TRON-T3` extends it; the extension is not yet expressed as a dependency, and adding it is acyclic), F-D-03 (D1 unratified), F-D-04 (no risk gate in the MVP check set), F-D-05 (promotion list gaps), F-D-06 (trade-count key has no limits home), F-D-07 (no stop-distance policy owner), F-D-08 (negotiation unowned), F-D-12 (no signature concept), F-D-13 (scan count anomaly). Findings only: nothing in this repository was changed and no ratification decision is taken or implied.
