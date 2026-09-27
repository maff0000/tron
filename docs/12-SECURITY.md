# 12 — Security Baseline

**Work item:** WI-G (`WO-TRON-D1`)
**Owns:** this document.

This document restates and grounds TRON's security baseline (PID §22) and the consequences of the repository's current public visibility (PID §1.2) for `WO-TRON-D1`. It does not perform, and is not a substitute for, the separate, explicit production-readiness security review PID §22 requires before live trading (§5 below) — that review is a distinct future exercise, out of scope for this document and for this Engineer.

Nothing in this document asserts a resolved position on any PID §19 OPEN decision. Where a requirement below intersects one (e.g. DEC-OPEN-07, production Graylog placement), that intersection is flagged, not resolved.

---

## 1. Least-privilege requirements (PID §22)

TRON follows least privilege. The following are the PID §22 requirements verbatim in substance, with a short grounding note against how they apply to this project's artifacts.

| Requirement (PID §22) | Grounding |
|---|---|
| Secrets never enter git | No commit, on any branch, may contain a secret. This is the requirement the pre-commit hook in §4 mechanically enforces. |
| Secrets never enter logs | Applies to the durable local journal and to every event shipped to Trading Graylog. See `09-EVENTS-AND-GRAYLOG.md` §4 (the never-log list) for the specific items this excludes. |
| Secrets are not placed in ordinary application configuration | TRON's configuration files (PID §10: `mapping.falcon.yaml`, `routing.yaml`, `selection.yaml`, `sizing.yaml`, `execution.yaml`, `checks.yaml`, `limits.yaml`, and their `config.example/` counterparts) are schema-validated operational policy, not a secrets store. PID §10 states this directly: "Secrets are not configuration and must not be stored in these files." A distinct, non-repository secrets-delivery mechanism is required; designing that mechanism is not within D1's scope (PID §21). |
| Examples use placeholders | Every configuration example and every canonical schema example (`schemas/examples/valid/`, `schemas/examples/invalid/`) uses placeholder values only — never a real account identifier, credential, or infrastructure address. |
| External inputs are untrusted | Every external input — candidate actions arriving from the board, broker adapter responses — is treated as untrusted until validated against its canonical schema. |
| Schemas validate canonical messages | All five canonical message contracts (PID §9; `05-CONTRACTS.md`) and all configuration files (PID §10; `07-CONFIGURATION.md`) are schema-validated before use. |
| Invalid messages fail closed | A message or configuration file that fails schema or semantic validation is rejected outright, never partially processed or coerced into a valid shape. For configuration specifically, PID §10 is explicit: "Invalid configuration means refuse startup." |
| Write authority is minimised | A component or credential is granted only the write authority its function requires — e.g. a component that only needs to read broker state is not additionally granted order-submission authority. |
| Read-only access is used where sufficient | Where a role only needs to observe state, it is given read-only access rather than broader access. This is the access-control expression of PID §6.2: NEO is an observer and consumes Trading Graylog; it is not granted execution-path access. |
| Execution authority is isolated from observers | Order-submission/execution authority is held separately from observer roles. This is HR-01's/HR-16's boundary made an access-control requirement: HR-16 — "No external observer, including NEO, may directly instruct TRON to place a trade" (PID §5). |
| Repository secret scanning remains active | OBSERVED as currently, mechanically true in this worktree — see §4. |
| Security hooks must not be bypassed | Same mechanism as above; `--no-verify` or any equivalent bypass of the repository's secret-scanning pre-commit hook is not permitted — see §4. |

---

## 2. Repository-is-public consequence (PID §1.2, §22)

The TRON repository (`maff0000/tron`) is intentionally **public** during the current architecture/build phase, so that Central Architecture can inspect the project directly (PID §1.2). Public visibility does not imply public write authority. This carries the following requirements, stated plainly:

- Because the repository is public, its content must be treated as **publicly readable information** — anything committed is available to any reader, not just the project team.
- Unauthorised users must not have write or merge authority; branch protection and repository permissions must preserve controlled integration (PID §1.2).
- Secrets, credentials, account identifiers, and sensitive broker or infrastructure details must never enter the repository (PID §1.2, §22) — not "must be redacted before merge," but must never be committed in the first place, on any branch.
- Configuration examples contain placeholders only (PID §1.2) — restated from §1 above because the public-visibility context is exactly why this matters: a placeholder that looks realistic enough to be mistaken for a real value is itself a risk once the repository is public.
- Production data must never enter the repository (PID §1.2).

**Repository visibility must be reconsidered before TRON is authorised for live production trading** (PID §1.2, §30 item 23). This is stated here as a plain requirement carried forward from the PID. It is **not decided** by this document, and it is not this document's job to decide it — whether, when, or how visibility changes ahead of live trading is a Product Authority question for that later stage, not a D1 deliverable.

---

## 3. HR-10

HR-10 (PID §5): **"Secrets, credentials, account identifiers and sensitive infrastructure identifiers must not enter the repository or logs."**

HR-10 is canonically listed, alongside all other Hard Rules, in `02-REQUIREMENTS.md` §1. It is restated here in full because §§1–2 of this document depend on it directly, but this document does not re-derive the Hard Rules register — `02-REQUIREMENTS.md` §1 is the canonical location for the complete HR-01 through HR-16 list and remains the single source of truth for their exact wording.

---

## 4. OBSERVED: repository secret-scanning enforcement is live

Per PID §28's evidence taxonomy, the following is recorded as **OBSERVED** — directly demonstrated by evidence produced during this work item's own execution, not merely asserted from the PID text or inferred:

- This worktree's git configuration sets `core.hooksPath=scripts/hooks` (confirmed directly against this worktree's `.git` configuration).
- `scripts/hooks/pre-commit` is present, executable, and its content was read directly. It:
  - fails the commit loudly (non-zero exit, explicit stderr message) if `gitleaks` is not installed on the host, with the hook's own comment stating why: *"public repo, no unscanned commits"*;
  - otherwise runs `gitleaks protect --staged --redact --verbose` against staged changes;
  - fails the commit loudly and blocks it if `gitleaks` reports a likely secret in staged changes, with an explicit message directing the fix to either resolve the finding or add a scoped rule to `.gitleaks.toml` — **and explicitly names `--no-verify` as not an acceptable response**.
- `gitleaks` is installed on this host, and a `.gitleaks.toml` scoping file exists in this worktree.

This is the live, mechanical enforcement of PID §22's "repository secret scanning remains active" and "security hooks must not be bypassed" requirements. It is recorded as OBSERVED rather than DEFINED or INFERRED specifically because it has been directly exercised/read as part of this work item (PID §28: OBSERVED = "directly demonstrated by evidence produced during the relevant TRON work"), not because this document asserts it unverified.

This document does not assert that the current `.gitleaks.toml` ruleset, or enforcement beyond this local pre-commit hook (e.g. CI-level scanning, §23 T9's mechanical suite check), is complete or sufficient for production use. That assessment belongs to the production-readiness review in §5.

---

## 5. Production-readiness review requirement

PID §22: **"Before live trading, the security architecture requires a separate explicit production-readiness review."**

This document does not perform that review. Conducting it is out of scope for `WO-TRON-D1` (PID §21) and out of scope for this Engineer's mandate. It is recorded here so that no downstream increment can treat D1's security baseline as a substitute for that later, explicit, separate review before TRON is authorised to trade live.
