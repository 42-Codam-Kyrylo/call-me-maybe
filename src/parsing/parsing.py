import json
import os
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ParameterDefinition(BaseModel):
    """Pydantic model representing a single parameter definition."""
    type: str


class ReturnDefinition(BaseModel):
    """Pydantic model representing a function's return type definition."""
    type: str


class FunctionDefinition(BaseModel):
    """Pydantic model representing a complete function definition."""
    name: str
    description: str
    parameters: dict[str, ParameterDefinition]
    returns: ReturnDefinition


class FunctionCallingTest(BaseModel):
    """Pydantic model representing a test prompt for function calling."""
    prompt: str


Vocabulary = dict[str, int]


def _parse_json_list_file(filepath: str, model_class: Type[T]) -> list[T]:
    """Generic helper function to load and validate a list of Pydantic models.

    Args:
        filepath: Path to the JSON file.
        model_class: Pydantic model class to validate against.

    Returns:
        A list of validated models.
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


def parse_function_definitions(filepath: str) -> list[FunctionDefinition]:
    """Loads and validates function definitions from a JSON file.

    Args:
        filepath: Path to the JSON file.

    Returns:
        A list of validated FunctionDefinition models.
    """
    return _parse_json_list_file(filepath, FunctionDefinition)


def parse_function_calling_tests(filepath: str) -> list[FunctionCallingTest]:
    """Loads and validates function calling tests from a JSON file.

    Args:
        filepath: Path to the JSON file.

    Returns:
        A list of validated FunctionCallingTest models.
    """
    return _parse_json_list_file(filepath, FunctionCallingTest)


def parse_vocabulary(filepath: str) -> Vocabulary:
    """Loads a vocabulary dictionary from a JSON file.

    Args:
        filepath: Path to the vocab.json file.

    Returns:
        A dictionary mapping tokens to their IDs.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Vocabulary file not found: {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format in {filepath}: {e}")

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected a dictionary in {filepath}, got {type(data).__name__}"
        )

    return data
