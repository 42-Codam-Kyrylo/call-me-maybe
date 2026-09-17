import pytest
from src.parsing import (
    parse_function_definitions,
    parse_function_calling_tests,
    parse_vocabulary,
)
from llm_sdk import Small_LLM_Model
from src.engine import FunctionCallingEngine


@pytest.fixture(scope="session")
def engine():
    fd = parse_function_definitions("data/input/functions_definition.json")
    model = Small_LLM_Model()
    vocabulary = parse_vocabulary(model.get_path_to_vocab_file())
    return FunctionCallingEngine(model, vocabulary, fd, verbose=False)


def test_engine_valid_json_outputs(engine):
    tests = parse_function_calling_tests(
        "data/input/function_calling_tests.json"
    )
    results = engine.run_tests(tests)

    # Check that we parsed results successfully
    assert len(results) == len(tests)

    for result in results:
        # Check standard JSON structure
        assert "prompt" in result
        assert "name" in result
        assert "parameters" in result

        # Ensure parameters are a dictionary (indicating successful JSON parse)
        assert isinstance(result["parameters"], dict)

        # Verify function name is matched
        assert result["name"] in [f.name for f in engine.functions_definitions]


def test_engine_edge_cases(engine):
    """Test engine against edge cases like empty strings, large numbers, special chars."""
    edge_cases = parse_function_calling_tests(
        "data/input/edge_cases_tests.json"
    )
    results = engine.run_tests(edge_cases)

    assert len(results) == len(edge_cases)

    for result in results:
        assert "prompt" in result
        assert "name" in result
        assert "parameters" in result
        assert isinstance(result["parameters"], dict)
        assert result["name"] in [f.name for f in engine.functions_definitions]
