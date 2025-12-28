from core.api_parser import specs_validator as spv
import pytest

sv = spv.ConfigValidator("./config/specs_schema_v2.json")

incorrect_config = {

}

@pytest.mark.positive
def test_load_schema_1():
    r = sv.load_schema()
    result = sv.schema

    assert r == True
    assert result["type"] == "object"
    assert len(result) > 1
    assert "metadata" in result["properties"]
    assert "base_url" in result["properties"]
    

@pytest.mark.negative
def test_load_schema_2():
    obj = spv.ConfigValidator("invalid/file.json")
    result = obj.load_schema()
    assert result == False

@pytest.mark.positive
def test_validate_file():
    result = sv.validate_file(config_path= "./config/sample_specs.json",verbose=True)
    assert result == True


@pytest.mark.negative()
def test_validate_file_with_invalid_schema():
    result = sv.validate_file(config_path="./core/tests/invalid_specss.json",verbose=True)
    assert result == False

