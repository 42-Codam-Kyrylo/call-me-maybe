import json
import os
from typing import Dict, List, Type, TypeVar
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ParameterDefinition(BaseModel):
    type: str


class ReturnDefinition(BaseModel):
    type: str


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, ParameterDefinition]
    returns: ReturnDefinition


class FunctionCallingTest(BaseModel):
    prompt: str


def _parse_json_list_file(filepath: str, model_class: Type[T]) -> List[T]:
    """
    Generic helper function to load and validate a list of Pydantic models from a JSON file.
    Includes error handling for missing files, invalid JSON, and schema validation.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {filepath}: {e}")

    if not isinstance(data, list):
        raise ValueError(
            f"Expected a list of objects in {filepath}, got {type(data).__name__}"
        )

    items = []
    for index, item in enumerate(data):
        try:
            items.append(model_class.model_validate(item))
        except ValidationError as e:
            raise ValueError(
                f"Schema validation error in {filepath} at index {index}:\n{e}"
            )

    return items


def parse_function_definitions(filepath: str) -> List[FunctionDefinition]:
    """Loads and validates function definitions from a JSON file."""
    return _parse_json_list_file(filepath, FunctionDefinition)


def parse_function_calling_tests(filepath: str) -> List[FunctionCallingTest]:
    """Loads and validates function calling tests from a JSON file."""
    return _parse_json_list_file(filepath, FunctionCallingTest)
