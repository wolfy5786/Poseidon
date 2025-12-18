import pytest
import json
from jsonschema import ValidationError
from core.api_parser import test_gen_schema_verifier_helper as helper

# --- Sample JSON Configs ---

# Positive configs
minimal_config = {
    "tests": [{"name": "test1", "order": 1}]
}

valid_auth_config = {"global_auth": {"type": "bearer", "bearer": {"token": "abc"}}}

valid_schema_data = {"name": "test1", "order": 1}

# Negative configs
duplicate_order_config = {
    "tests": [{"name": "t1", "order": 1}, {"name": "t2", "order": 1}]
}

dependency_config = {
    "tests": [
        {"name": "t1", "order": 1},
        {"name": "t2", "order": 2, "depends_on": ["nonexistent"]}
    ]
}

circular_config = {
    "tests": [
        {"name": "A", "depends_on": ["B"]},
        {"name": "B", "depends_on": ["C"]},
        {"name": "C", "depends_on": ["A"]}
    ]
}

invalid_schema_data = {"name": "test2"}  # missing 'order'

invalid_auth_configs = {
    "bearer_missing": {"global_auth": {"type": "bearer"}},
    "basic_missing": {"global_auth": {"type": "basic"}},
    "api_key_missing": {"global_auth": {"type": "api_key"}},
}

# --- Schema ---
sample_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "order": {"type": "number"}
    },
    "required": ["name", "order"]
}

# -------------------
# Tests
# -------------------

# ---- load_json_file ----
@pytest.mark.positive
def test_load_json_file(tmp_path):
    file_path = tmp_path / "temp.json"
    data_to_write = {"foo": "bar"}
    file_path.write_text(json.dumps(data_to_write))
    loaded_data = helper.load_json_file(file_path)
    assert loaded_data == data_to_write

# ---- validate_against_schema ----
@pytest.mark.positive
def test_validate_against_schema_valid():
    is_valid, errors = helper.validate_against_schema(valid_schema_data, sample_schema)
    assert is_valid
    assert errors == []

@pytest.mark.negative
def test_validate_against_schema_invalid():
    is_valid, errors = helper.validate_against_schema(invalid_schema_data, sample_schema)
    assert not is_valid
    assert len(errors) == 1
    assert "order" in errors[0]

# ---- check_unique_orders ----
@pytest.mark.positive
def test_check_unique_orders_no_duplicates():
    errors = helper.check_unique_orders(minimal_config)
    assert errors == []

@pytest.mark.negative
def test_check_unique_orders_with_duplicates():
    errors = helper.check_unique_orders(duplicate_order_config)
    assert len(errors) == 1
    assert "Duplicate test orders" in errors[0]

# ---- check_test_dependencies ----
@pytest.mark.negative
def test_check_test_dependencies_missing_reference():
    errors = helper.check_test_dependencies(dependency_config)
    assert len(errors) == 1
    assert "depends on non-existent" in errors[0]

# ---- check_circular_dependencies ----
@pytest.mark.negative
def test_check_circular_dependencies_detects_cycle():
    errors = helper.check_circular_dependencies(circular_config)
    assert len(errors) == 1
    assert "Circular dependency detected" in errors[0]

# ---- check_required_auth_fields ----
@pytest.mark.positive
def test_check_required_auth_fields_valid():
    errors = helper.check_required_auth_fields(valid_auth_config)
    assert errors == []

@pytest.mark.negative
@pytest.mark.parametrize("config,key,expected_error", [
    (invalid_auth_configs["bearer_missing"], "bearer", "Bearer auth missing"),
    (invalid_auth_configs["basic_missing"], "basic", "Basic auth missing"),
    (invalid_auth_configs["api_key_missing"], "api_key", "API key auth missing"),
])
def test_check_required_auth_fields_missing(config, key, expected_error):
    errors = helper.check_required_auth_fields(config)
    assert len(errors) == 1
    assert expected_error in errors[0]

# ---- run_custom_validations ----
@pytest.mark.negative
def test_run_custom_validations_combined_errors():
    combined_config = {
        "tests": [
            {"name": "X", "order": 1, "depends_on": ["Y"]},
            {"name": "Y", "order": 1, "depends_on": ["X"]},
        ]
    }
    errors = helper.run_custom_validations(combined_config)
    assert any("Duplicate test orders" in e for e in errors)
    assert any("Circular dependency detected" in e for e in errors)
