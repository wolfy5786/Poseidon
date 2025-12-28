from core.api_parser import specs_validator as tgsv
import pytest

tgsv_ = tgsv.ConfigValidator("./config/specs_schema_v2.json")

incorrect_config = {

}

@pytest.mark.positive
def test_load_schema_1():
    r = tgsv_.load_schema()
    result = tgsv_.schema

    assert r == True
    assert result["type"] == "object"
    assert len(result) > 1
    assert "metadata" in result["properties"]
    assert "base_url" in result["properties"]
    

@pytest.mark.negative
def test_load_schema_2():
    obj = tgsv.ConfigValidator("invalid/file.json")
    result = obj.load_schema()
    assert result == False

@pytest.mark.positive
def test_validate_file():
    result = tgsv_.validate_file(config_path= "./config/sample_specs.json",verbose=True)
    assert result == True


