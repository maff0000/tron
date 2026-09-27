"""WO-TRON-D1 -- mechanical quality-gate suite (PID.md Section 23, T1-T8 and T10).

Work item: WI-I ("Tests & Evidence"), Wave 4 of WO-TRON-D1.

This suite mechanically proves the D1 documentation/contract/schema/config
baseline against PID.md Section 23's gates T1 through T10, with one explicit
exception:

    T9 (repository/branch secret scanning is clean) is PL-owned operational
    evidence per the binding Central-Architecture ruling for this work item.
    It is NOT implemented here -- this suite never shells out to gitleaks.
    See docs/evidence/WO-TRON-D1.md's dedicated "T9" section, populated
    separately by the PL.

Every other assertion below is derived mechanically from the repository's own
content (PID.md, docs/*.md, schemas/**, config.example/*.yaml) rather than
from restated expectations, so that a future edit which breaks a documented
guarantee is caught here rather than merely trusted.

Non-vacuity (PID.md Section 24) is addressed two ways:
  1. Several tests below assert their own input set is non-empty before
     asserting properties of it (see the "*_is_not_vacuous" tests), so a
     silently-empty match set cannot pass as a false positive.
  2. The full non-vacuity demonstration (deliberate mutation -> observed
     failure -> revert -> clean rerun) is recorded, with real commands and
     real output, in docs/evidence/WO-TRON-D1.md.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"
SCHEMAS_DIR = REPO_ROOT / "schemas"
CONFIG_SCHEMAS_DIR = SCHEMAS_DIR / "config"
EXAMPLES_DIR = SCHEMAS_DIR / "examples"
VALID_DIR = EXAMPLES_DIR / "valid"
INVALID_DIR = EXAMPLES_DIR / "invalid"
CONFIG_EXAMPLE_DIR = REPO_ROOT / "config.example"


def _load_json(path: Path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _load_yaml(path: Path):
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# ===========================================================================
# T1 -- Schema validity: every JSON Schema is itself valid draft 2020-12.
# ===========================================================================

ALL_SCHEMA_FILES = sorted(SCHEMAS_DIR.glob("*.json")) + sorted(CONFIG_SCHEMAS_DIR.glob("*.json"))


def test_t1_twelve_schema_files_discovered():
    # 5 canonical contracts (schemas/*.json) + 7 configuration schemas
    # (schemas/config/*.json), per PID.md Section 20's deliverable list.
    assert len(ALL_SCHEMA_FILES) == 12, [p.name for p in ALL_SCHEMA_FILES]


@pytest.mark.parametrize("schema_path", ALL_SCHEMA_FILES, ids=lambda p: p.name)
def test_t1_schema_is_valid_draft202012(schema_path):
    schema = _load_json(schema_path)
    assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", (
        f"{schema_path.name} does not declare the draft 2020-12 $schema URI"
    )
    Draft202012Validator.check_schema(schema)


# ===========================================================================
# T2 -- Valid examples: every valid example validates against its schema.
# Source of truth: docs/05-CONTRACTS.md Section 9 and docs/07-CONFIGURATION.md
# Section 8.
# ===========================================================================

CANONICAL_VALID_EXAMPLES = {
    "falcon_trade_action_open_valid.json": "falcon.trade_action.v1.json",
    "tron_trade_intent_valid.json": "tron.trade_intent.v1.json",
    "tron_execution_report_valid.json": "tron.execution_report.v1.json",
    "tron_check_report_pass_valid.json": "tron.check_report.v1.json",
    "tron_check_report_fail_with_reason_valid.json": "tron.check_report.v1.json",
    "tron_event_valid.json": "tron.event.v1.json",
}

CONFIG_SCHEMA_BY_EXAMPLE = {
    "mapping.falcon.yaml": "mapping.schema.json",
    "routing.yaml": "routing.schema.json",
    "selection.yaml": "selection.schema.json",
    "sizing.yaml": "sizing.schema.json",
    "execution.yaml": "execution.schema.json",
    "limits.yaml": "limits.schema.json",
    "checks.yaml": "checks.schema.json",
}


def test_t2_canonical_valid_examples_directory_matches_expected_set():
    on_disk = {p.name for p in VALID_DIR.glob("*.json")}
    assert on_disk == set(CANONICAL_VALID_EXAMPLES), (
        f"extra={on_disk - set(CANONICAL_VALID_EXAMPLES)} "
        f"missing={set(CANONICAL_VALID_EXAMPLES) - on_disk}"
    )


@pytest.mark.parametrize("example_name,schema_name", sorted(CANONICAL_VALID_EXAMPLES.items()))
def test_t2_canonical_valid_example_validates(example_name, schema_name):
    schema = _load_json(SCHEMAS_DIR / schema_name)
    instance = _load_json(VALID_DIR / example_name)
    Draft202012Validator(schema).validate(instance)


def test_t2_config_example_directory_matches_expected_set():
    on_disk = {p.name for p in CONFIG_EXAMPLE_DIR.glob("*.yaml")}
    assert on_disk == set(CONFIG_SCHEMA_BY_EXAMPLE), (
        f"extra={on_disk - set(CONFIG_SCHEMA_BY_EXAMPLE)} "
        f"missing={set(CONFIG_SCHEMA_BY_EXAMPLE) - on_disk}"
    )


@pytest.mark.parametrize("example_name,schema_name", sorted(CONFIG_SCHEMA_BY_EXAMPLE.items()))
def test_t2_config_example_validates(example_name, schema_name):
    schema = _load_json(CONFIG_SCHEMAS_DIR / schema_name)
    instance = _load_yaml(CONFIG_EXAMPLE_DIR / example_name)
    Draft202012Validator(schema).validate(instance)


# ===========================================================================
# T3 -- Invalid examples (canonical contracts): each fails for its intended
# reason. Expected validator keyword / path / schema_path taken verbatim from
# docs/05-CONTRACTS.md Section 9's table (the documented source of truth) and
# independently confirmed against jsonschema 4.10.3's actual error output
# before being encoded here.
# ===========================================================================

# (example filename, schema filename, expected error.validator,
#  expected list(error.path), substring expected in error.message,
#  element expected in list(error.schema_path))
T3_CANONICAL_CASES = [
    ("falcon_trade_action_open_missing_stop_loss.json", "falcon.trade_action.v1.json",
     "required", [], "'stop_loss'", "then"),
    ("falcon_trade_action_open_missing_take_profit.json", "falcon.trade_action.v1.json",
     "required", [], "'take_profit'", "then"),
    ("falcon_trade_action_stop_loss_numeric_price.json", "falcon.trade_action.v1.json",
     "type", ["stop_loss"], "not of type 'string'", "properties"),
    ("falcon_trade_action_unsupported_action_value.json", "falcon.trade_action.v1.json",
     "enum", ["action"], "'REVERSE'", "properties"),
    ("falcon_trade_action_invalid_confidence_value.json", "falcon.trade_action.v1.json",
     "pattern", ["confidence"], "'1.5000'", "properties"),
    ("falcon_trade_action_broker_lot_quantity_present.json", "falcon.trade_action.v1.json",
     "additionalProperties", [], "'lot_quantity'", "additionalProperties"),
    ("falcon_trade_action_malformed_timestamp.json", "falcon.trade_action.v1.json",
     "type", ["valid_until_ms"], "not of type 'integer'", "properties"),
    ("tron_check_report_unknown_field_present.json", "tron.check_report.v1.json",
     "additionalProperties", [], "'debug_note'", "additionalProperties"),
    ("tron_check_report_fail_missing_reason.json", "tron.check_report.v1.json",
     "required", [], "'reason'", "then"),
    ("tron_execution_report_invalid_state_value.json", "tron.execution_report.v1.json",
     "enum", ["order_state"], "'Suspended'", "properties"),
    ("tron_trade_intent_quantity_numeric_not_decimal_string.json", "tron.trade_intent.v1.json",
     "type", ["negotiated_quantity"], "not of type 'string'", "properties"),
]


@pytest.mark.parametrize(
    "example_name,schema_name,expected_validator,expected_path,message_substr,schema_path_elem",
    T3_CANONICAL_CASES,
    ids=[c[0] for c in T3_CANONICAL_CASES],
)
def test_t3_canonical_invalid_example_fails_for_intended_reason(
    example_name, schema_name, expected_validator, expected_path, message_substr, schema_path_elem
):
    schema = _load_json(SCHEMAS_DIR / schema_name)
    instance = _load_json(INVALID_DIR / example_name)
    validator = Draft202012Validator(schema)
    errors = list(validator.iter_errors(instance))
    assert errors, f"{example_name} unexpectedly VALIDATED against {schema_name}"
    assert len(errors) == 1, f"{example_name} produced {len(errors)} errors, expected exactly 1: {errors}"
    error = errors[0]
    assert error.validator == expected_validator, (
        f"{example_name}: expected failing keyword {expected_validator!r}, got {error.validator!r} ({error.message})"
    )
    assert list(error.path) == expected_path, (
        f"{example_name}: expected failing path {expected_path}, got {list(error.path)}"
    )
    assert message_substr in error.message, f"{example_name}: {message_substr!r} not in {error.message!r}"
    assert schema_path_elem in list(error.schema_path), (
        f"{example_name}: expected {schema_path_elem!r} in schema_path {list(error.schema_path)}"
    )


# PID.md Section 23 T3's eight explicitly-named minimum negative cases.
T3_MINIMUM_REQUIRED_CASES = {
    "OPEN missing stop-loss": "falcon_trade_action_open_missing_stop_loss.json",
    "OPEN missing take-profit": "falcon_trade_action_open_missing_take_profit.json",
    "numeric price instead of decimal-string": "falcon_trade_action_stop_loss_numeric_price.json",
    "unsupported action value": "falcon_trade_action_unsupported_action_value.json",
    "invalid confidence value": "falcon_trade_action_invalid_confidence_value.json",
    "upstream broker-lot quantity": "falcon_trade_action_broker_lot_quantity_present.json",
    "malformed timestamp": "falcon_trade_action_malformed_timestamp.json",
    "prohibited/unknown field": "tron_check_report_unknown_field_present.json",
}


def test_t3_all_eight_pid_minimum_cases_are_named():
    assert len(T3_MINIMUM_REQUIRED_CASES) == 8


@pytest.mark.parametrize("case_name,filename", sorted(T3_MINIMUM_REQUIRED_CASES.items()))
def test_t3_minimum_required_case_is_present_and_covered(case_name, filename):
    assert (INVALID_DIR / filename).is_file(), f"PID Section 23 T3 minimum case {case_name!r} missing: {filename}"
    assert filename in {c[0] for c in T3_CANONICAL_CASES}, (
        f"{filename} exists but is not exercised by test_t3_canonical_invalid_example_fails_for_intended_reason"
    )


# ===========================================================================
# T4 -- Configuration validation: every config.example/*.yaml validates
# (see also T2 above, which asserts the same thing -- kept under both names
# per PID.md Section 23's own numbering), and every one of the 7 config
# schemas has at least one deliberate negative example.
# ===========================================================================


@pytest.mark.parametrize("example_name,schema_name", sorted(CONFIG_SCHEMA_BY_EXAMPLE.items()))
def test_t4_config_example_validates(example_name, schema_name):
    schema = _load_json(CONFIG_SCHEMAS_DIR / schema_name)
    instance = _load_yaml(CONFIG_EXAMPLE_DIR / example_name)
    Draft202012Validator(schema).validate(instance)


T4_CONFIG_INVALID_JSON_CASES = [
    ("config_mapping_missing_broker_instrument.json", "mapping.schema.json",
     "required", ["mappings", "BTCUSD"], "'broker_instrument'", "required"),
    ("config_routing_missing_broker_context.json", "routing.schema.json",
     "required", [], "'broker_context'", "required"),
    ("config_selection_invalid_conflict_policy_enum.json", "selection.schema.json",
     "enum", ["conflict_policy"], "'allow_both'", "enum"),
    ("config_sizing_quantity_numeric_not_decimal_string.json", "sizing.schema.json",
     "type", ["base_quantities", "BTCUSD"], "not of type 'string'", "type"),
    ("config_execution_unsupported_mode_enum.json", "execution.schema.json",
     "enum", ["supported_execution_modes", 0], "'stop'", "enum"),
    ("config_limits_missing_on_hard_limit_breach.json", "limits.schema.json",
     "required", [], "'on_hard_limit_breach'", "required"),
]

T4_CONFIG_INVALID_YAML_CASES = [
    ("checks_config_invalid_stage_value.yaml", "checks.schema.json",
     "enum", ["checks", "CHK-058", "stage"], "is not one of", "enum"),
    ("checks_config_unknown_field.yaml", "checks.schema.json",
     "additionalProperties", ["checks", "CHK-001"], "'debug_note'", "additionalProperties"),
]


@pytest.mark.parametrize(
    "example_name,schema_name,expected_validator,expected_path,message_substr,schema_path_elem",
    T4_CONFIG_INVALID_JSON_CASES,
    ids=[c[0] for c in T4_CONFIG_INVALID_JSON_CASES],
)
def test_t4_config_invalid_json_example_fails_for_intended_reason(
    example_name, schema_name, expected_validator, expected_path, message_substr, schema_path_elem
):
    schema = _load_json(CONFIG_SCHEMAS_DIR / schema_name)
    instance = _load_json(INVALID_DIR / example_name)
    errors = list(Draft202012Validator(schema).iter_errors(instance))
    assert errors, f"{example_name} unexpectedly VALIDATED against {schema_name}"
    assert len(errors) == 1, f"{example_name} produced {len(errors)} errors, expected exactly 1: {errors}"
    error = errors[0]
    assert error.validator == expected_validator
    assert list(error.path) == expected_path
    assert message_substr in error.message
    assert schema_path_elem in list(error.schema_path)


@pytest.mark.parametrize(
    "example_name,schema_name,expected_validator,expected_path,message_substr,schema_path_elem",
    T4_CONFIG_INVALID_YAML_CASES,
    ids=[c[0] for c in T4_CONFIG_INVALID_YAML_CASES],
)
def test_t4_config_invalid_yaml_example_fails_for_intended_reason(
    example_name, schema_name, expected_validator, expected_path, message_substr, schema_path_elem
):
    schema = _load_json(CONFIG_SCHEMAS_DIR / schema_name)
    instance = _load_yaml(INVALID_DIR / example_name)
    errors = list(Draft202012Validator(schema).iter_errors(instance))
    assert errors, f"{example_name} unexpectedly VALIDATED against {schema_name}"
    assert len(errors) == 1, f"{example_name} produced {len(errors)} errors, expected exactly 1: {errors}"
    error = errors[0]
    assert error.validator == expected_validator
    assert list(error.path) == expected_path
    assert message_substr in error.message
    assert schema_path_elem in list(error.schema_path)


def test_t4_every_config_schema_has_at_least_one_negative_example():
    schemas_with_negative = {name for _f, name, *_rest in T4_CONFIG_INVALID_JSON_CASES}
    schemas_with_negative |= {name for _f, name, *_rest in T4_CONFIG_INVALID_YAML_CASES}
    all_config_schemas = {p.name for p in CONFIG_SCHEMAS_DIR.glob("*.json")}
    assert all_config_schemas, "no config schemas found -- test would be vacuous"
    assert schemas_with_negative == all_config_schemas, (
        f"schemas with no negative example: {all_config_schemas - schemas_with_negative}"
    )


def test_t3_t4_every_invalid_example_file_on_disk_is_exercised():
    """Cross-check: nothing sits in schemas/examples/invalid/ untested, and
    nothing tested above has silently disappeared from disk."""
    on_disk = {p.name for p in INVALID_DIR.iterdir() if p.is_file()}
    covered = (
        {c[0] for c in T3_CANONICAL_CASES}
        | {c[0] for c in T4_CONFIG_INVALID_JSON_CASES}
        | {c[0] for c in T4_CONFIG_INVALID_YAML_CASES}
    )
    assert on_disk == covered, f"on_disk_only={on_disk - covered} covered_only={covered - on_disk}"


# ===========================================================================
# T5 -- Check catalogue integrity: docs/06-CHECKS-CATALOGUE.md <->
# config.example/checks.yaml <-> PID.md Section 13's flat list all
# reconcile, in both directions, with zero orphans. PID.md Section 13's list
# is re-parsed directly from PID.md (not hard-coded), per the assignment.
# ===========================================================================


def _pid_text() -> str:
    return (REPO_ROOT / "PID.md").read_text(encoding="utf-8")


def _pid_section13_items() -> list[str]:
    text = _pid_text()
    m = re.search(r"# 13\. Canonical Check Catalogue\s*\n\n(.*?)\n\nUnder HR-01:", text, re.S)
    assert m, "Could not locate PID Section 13's flat check list in PID.md -- has the heading text changed?"
    block = m.group(1).strip()
    paragraphs = [p.strip() for p in block.split("\n\n") if "·" in p]
    assert len(paragraphs) == 1, (
        f"Expected exactly one middot-separated paragraph in PID Section 13, found {len(paragraphs)}"
    )
    return [item.strip().rstrip(".").strip() for item in paragraphs[0].split("·")]


def _catalogue_text() -> str:
    return (DOCS_DIR / "06-CHECKS-CATALOGUE.md").read_text(encoding="utf-8")


def _catalogue_section5_ids() -> list[str]:
    text = _catalogue_text()
    m = re.search(r"## 5\. The catalogue\n(.*?)\n## 6\.", text, re.S)
    assert m, "Could not locate catalogue Section 5 in docs/06-CHECKS-CATALOGUE.md"
    return re.findall(r"^\|\s*`(CHK-\d{3})`\s*\|", m.group(1), re.MULTILINE)


def _catalogue_section6_rows() -> list[tuple[str, str]]:
    text = _catalogue_text()
    m = re.search(r"## 6\. Section 13 verbatim cross-check\n(.*?)\n---", text, re.S)
    assert m, "Could not locate catalogue Section 6 cross-check table in docs/06-CHECKS-CATALOGUE.md"
    return re.findall(r"^\|\s*\d+\s*\|\s*(.*?)\s*\|\s*`(CHK-\d{3})`\s*\|", m.group(1), re.MULTILINE)


def _load_checks_yaml() -> dict:
    return _load_yaml(CONFIG_EXAMPLE_DIR / "checks.yaml")


def test_t5_pid_section13_reparse_yields_73_items():
    items = _pid_section13_items()
    assert len(items) == 73, f"expected 73 PID Section 13 items, got {len(items)}"
    assert items[0] == "Ledger available"
    assert items[-1] == "Final post-trade account state within configured limits"


def test_t5_catalogue_section5_has_82_unique_ids():
    ids = _catalogue_section5_ids()
    assert len(ids) == 82, f"expected 82 catalogue entries, got {len(ids)}"
    assert len(set(ids)) == 82, "duplicate CHK-NNN id found in docs/06-CHECKS-CATALOGUE.md Section 5"


def test_t5_catalogue_reconciles_with_checks_yaml_both_directions():
    doc_ids = set(_catalogue_section5_ids())
    checks_yaml = _load_checks_yaml()
    yaml_ids = set(checks_yaml["checks"].keys())
    assert doc_ids, "no catalogue ids found -- test would be vacuous"
    assert doc_ids == yaml_ids, f"doc-only={doc_ids - yaml_ids} yaml-only={yaml_ids - doc_ids}"
    for key, definition in checks_yaml["checks"].items():
        assert definition["check_id"] == key, (
            f"{key}: checks.yaml entry's own check_id field {definition['check_id']!r} != its map key"
        )


def test_t5_pid_section13_matches_catalogue_crosscheck_table_exactly_in_order():
    pid_items = _pid_section13_items()
    rows = _catalogue_section6_rows()
    assert len(rows) == 73, f"expected 73 cross-check rows, got {len(rows)}"
    catalogue_items = [name for name, _cid in rows]
    assert catalogue_items == pid_items, (
        "docs/06-CHECKS-CATALOGUE.md Section 6's cross-check table does not match "
        "PID.md Section 13's flat list re-split on the middot, item-for-item and in order"
    )


def test_t5_every_pid_section13_check_appears_exactly_once_with_origin_pa13():
    rows = _catalogue_section6_rows()
    checks_yaml = _load_checks_yaml()
    seen_ids = [cid for _name, cid in rows]
    assert len(seen_ids) == len(set(seen_ids)), "a PID Section 13 item was mapped to a duplicate CHK id"
    for name, cid in rows:
        assert cid in checks_yaml["checks"], f"{cid} ({name}) missing from config.example/checks.yaml"
        origin = checks_yaml["checks"][cid]["origin"]
        assert origin == "PA-13", f"{cid} ({name}) should carry origin PA-13 in checks.yaml, has {origin!r}"


def test_t5_wi_c_additions_are_exactly_the_remaining_nine_with_origin_wi_c_add():
    doc_ids = set(_catalogue_section5_ids())
    pa13_ids = {cid for _name, cid in _catalogue_section6_rows()}
    additions = doc_ids - pa13_ids
    assert len(additions) == 9, f"expected 9 WI-C-ADD entries, got {len(additions)}: {sorted(additions)}"
    checks_yaml = _load_checks_yaml()
    for cid in additions:
        origin = checks_yaml["checks"][cid]["origin"]
        assert origin == "WI-C-ADD", f"{cid} should carry origin WI-C-ADD in checks.yaml, has {origin!r}"


# ===========================================================================
# T6 -- Capability integrity: every CAP-nn / BL-<CATEGORY>-nn id referenced
# anywhere in the repository resolves to an entry in docs/10-CAPABILITIES.md.
# ===========================================================================


def _capabilities_text() -> str:
    return (DOCS_DIR / "10-CAPABILITIES.md").read_text(encoding="utf-8")


def _defined_capability_ids() -> set[str]:
    return set(re.findall(r"^\|\s*(CAP-\d{2})\s*\|", _capabilities_text(), re.MULTILINE))


def _defined_backlog_ids() -> set[str]:
    return set(re.findall(r"^\|\s*(BL-[A-Z]+-\d{2})\s*\|", _capabilities_text(), re.MULTILINE))


CAP_REF_RE = re.compile(r"\bCAP-\d{2}\b")
BL_REF_RE = re.compile(r"\bBL-[A-Z]+-\d{2}\b")


def _tree_files_for_id_scan() -> list[Path]:
    return (
        sorted(DOCS_DIR.glob("*.md"))
        + sorted(SCHEMAS_DIR.rglob("*.json"))
        + sorted(CONFIG_EXAMPLE_DIR.glob("*.yaml"))
    )


def test_t6_capability_namespace_defines_cap00_through_cap06():
    assert _defined_capability_ids() == {f"CAP-0{i}" for i in range(7)}


def test_t6_backlog_namespace_has_32_defined_items():
    assert len(_defined_backlog_ids()) == 32


def test_t6_every_referenced_capability_id_resolves():
    defined = _defined_capability_ids()
    referenced: set[str] = set()
    for f in _tree_files_for_id_scan():
        referenced |= set(CAP_REF_RE.findall(f.read_text(encoding="utf-8")))
    assert referenced, "no CAP-nn references found anywhere -- test would be vacuous"
    unresolved = referenced - defined
    assert not unresolved, f"CAP ids referenced but not defined in docs/10-CAPABILITIES.md: {sorted(unresolved)}"


def test_t6_every_referenced_backlog_id_resolves():
    defined = _defined_backlog_ids()
    referenced: set[str] = set()
    for f in _tree_files_for_id_scan():
        referenced |= set(BL_REF_RE.findall(f.read_text(encoding="utf-8")))
    assert referenced, "no BL-<CATEGORY>-nn references found anywhere -- test would be vacuous"
    unresolved = referenced - defined
    assert not unresolved, f"BL ids referenced but not defined in docs/10-CAPABILITIES.md: {sorted(unresolved)}"


# ===========================================================================
# T7 -- Documentation links: every relative markdown link in every docs/*.md
# file resolves to a file/directory that actually exists.
# ===========================================================================

MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _all_doc_markdown_files() -> list[Path]:
    return sorted(DOCS_DIR.glob("*.md"))


def _internal_link_targets(md_path: Path) -> list[str]:
    text = md_path.read_text(encoding="utf-8")
    targets = []
    for target in MARKDOWN_LINK_RE.findall(text):
        target = target.strip()
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        targets.append(target)
    return targets


def test_t7_internal_links_are_not_vacuous():
    total = sum(len(_internal_link_targets(f)) for f in _all_doc_markdown_files())
    assert total > 0, "no internal documentation links found anywhere -- test would be vacuous"


@pytest.mark.parametrize("md_path", _all_doc_markdown_files(), ids=lambda p: p.name)
def test_t7_internal_links_resolve(md_path):
    for target in _internal_link_targets(md_path):
        resolved = (md_path.parent / target).resolve()
        assert resolved.exists(), f"{md_path.name}: link target does not exist: {target!r} -> {resolved}"


# ===========================================================================
# T8 -- TRON resource naming (HR-12).
#
# Non-vacuity finding (confirmed independently before writing this test): as
# of the integrated Wave 1+2+3 baseline (commit d6748cf), no concrete Docker
# resource NAME is represented anywhere in the documentation baseline -- only
# the HR-12 naming *convention* is described in prose (02-REQUIREMENTS.md,
# 03-ARCHITECTURE.md, 11-DECISIONS.md). A T8 test with nothing concrete to
# check would pass vacuously, which would violate PID.md Section 24.
#
# Resolved within WI-I's own ownership boundary: one small, clearly
# illustrative "T8 test fixture" example resource name was added to
# docs/evidence/WO-TRON-D1.md (owned by WI-I) -- see that file's dedicated
# T8 section for the fixture text and the reasoning. This test scans the
# whole documentation baseline, INCLUDING that evidence file, for resource
# names presented in a container/image/volume/network naming context, and
# checks HR-12 compliance (both the "-tron" suffix and the
# "proteus.project=tron" label) against whatever it finds.
# ===========================================================================

RESOURCE_NAME_CONTEXT_RE = re.compile(
    r"\b(?:container|image|volume|network)\b(?:\s+(?:named|called))?\s*`([A-Za-z0-9][\w.-]*)`"
)
PROTEUS_LABEL_RE = re.compile(r"proteus\.project=([A-Za-z0-9_.-]+)")


def _t8_scan_files() -> list[Path]:
    # The documentation baseline, explicitly including WI-I's own evidence
    # file (see module docstring above for why that inclusion is required).
    return sorted(DOCS_DIR.glob("*.md")) + sorted((DOCS_DIR / "evidence").glob("*.md"))


def _t8_resource_name_matches() -> list[tuple[str, str]]:
    matches = []
    for f in _t8_scan_files():
        for m in RESOURCE_NAME_CONTEXT_RE.finditer(f.read_text(encoding="utf-8")):
            matches.append((f.name, m.group(1)))
    return matches


def _t8_label_matches() -> list[tuple[str, str]]:
    matches = []
    for f in _t8_scan_files():
        for m in PROTEUS_LABEL_RE.finditer(f.read_text(encoding="utf-8")):
            matches.append((f.name, m.group(1)))
    return matches


def test_t8_resource_naming_scan_is_not_vacuous():
    matches = _t8_resource_name_matches()
    assert matches, (
        "no TRON Docker resource name found in a container/image/volume/network "
        "naming context anywhere in the documentation baseline -- see the T8 "
        "fixture note in docs/evidence/WO-TRON-D1.md"
    )


@pytest.mark.parametrize("filename,name", _t8_resource_name_matches())
def test_t8_resource_name_complies_with_hr12_suffix(filename, name):
    assert name.endswith("-tron"), f"{filename}: TRON-owned resource name {name!r} does not end in '-tron' (HR-12)"


def test_t8_proteus_project_label_scan_is_not_vacuous_and_all_say_tron():
    matches = _t8_label_matches()
    assert matches, "no proteus.project= label found anywhere in the documentation baseline"
    for filename, value in matches:
        assert value == "tron", f"{filename}: proteus.project={value!r}, expected 'tron' (HR-12)"


# ===========================================================================
# T10 -- Decision integrity: every DEC-OPEN-nn mention is treated as OPEN,
# with the sole sanctioned exception of DEC-OPEN-09's ledger-authority
# clause (legitimately DECIDED via HR-06, per the binding Central-Architecture
# ruling recorded in docs/11-DECISIONS.md Section 0 / Section 1.9).
#
# Method: for every line of every scanned file, split the line into
# sentence-like segments on '.', ';' and '|' (the last so a markdown table
# row's unrelated cells don't cross-contaminate each other). Within each
# segment, if a DEC-OPEN-nn other than DEC-OPEN-09 is mentioned, that same
# segment must not also carry unnegated decided/settled/default language
# (a preceding not/never/nothing/no/n't/without within 60 characters counts
# as negation, covering phrasing such as "not a decided requirement" or
# "is not settled by this document").
# ===========================================================================

DEC_OPEN_RE = re.compile(r"DEC-OPEN-(\d{2})")
DECIDED_TERM_RE = re.compile(r"decided|settled|default", re.IGNORECASE)
NEGATION_RE = re.compile(r"\bnot\b|\bnever\b|\bnothing\b|\bno\b|n't\b|\bwithout\b", re.IGNORECASE)
SEGMENT_SPLIT_RE = re.compile(r"[.;|]")
T10_EXEMPT_DECISION = "09"


def _t10_scan_files() -> list[Path]:
    return (
        sorted(DOCS_DIR.glob("*.md"))
        + sorted(SCHEMAS_DIR.rglob("*.json"))
        + sorted(CONFIG_EXAMPLE_DIR.glob("*.yaml"))
    )


def _t10_violations_in_text(text: str) -> list[tuple[int, list[str], str]]:
    violations = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for segment in SEGMENT_SPLIT_RE.split(line):
            nums = set(DEC_OPEN_RE.findall(segment))
            non_exempt = nums - {T10_EXEMPT_DECISION}
            if not non_exempt:
                continue
            for term_match in DECIDED_TERM_RE.finditer(segment):
                window = segment[max(0, term_match.start() - 60): term_match.start()]
                if NEGATION_RE.search(window):
                    continue
                violations.append((lineno, sorted(non_exempt), segment.strip()))
                break
    return violations


def test_t10_scan_is_not_vacuous():
    found_any = any(DEC_OPEN_RE.search(f.read_text(encoding="utf-8")) for f in _t10_scan_files())
    assert found_any, "no DEC-OPEN-nn mention found anywhere -- test would be vacuous"


@pytest.mark.parametrize(
    "doc_path", _t10_scan_files(), ids=[str(p.relative_to(REPO_ROOT)) for p in _t10_scan_files()]
)
def test_t10_no_open_decision_presented_as_decided(doc_path):
    text = doc_path.read_text(encoding="utf-8")
    violations = _t10_violations_in_text(text)
    assert not violations, (
        f"{doc_path.relative_to(REPO_ROOT)}: DEC-OPEN-nn (other than the sanctioned DEC-OPEN-09 "
        f"ledger-authority exception) paired with decided/settled/default language: {violations}"
    )
