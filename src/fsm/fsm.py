from enum import StrEnum
from llm_sdk import Small_LLM_Model
from src.parsing import Vocabulary, FunctionDefinition, FunctionCallingTest
from .utils import Cache
from src.utils import generate_prompt
import numpy as np


class STATUS(StrEnum):
    # ORIGINAL_PROMPT = "original_prompt"
    FUNCTION_NAME = "function_name"
    FUNCTION_PARAMETERS = "function_parameters"
    WAITING_NUMBER = "waiting_number"


def finite_state_machine(
    model: Small_LLM_Model,
    vocabulary: Vocabulary,
    functions_definitions: list[FunctionDefinition],
    calling_tests: list[FunctionCallingTest],
):
    result = list[dict]
    status = STATUS.FUNCTION_NAME
    fd_names = [f.name for f in functions_definitions]
    cache = Cache(model, vocabulary, fd_names)

    for test in calling_tests:
        item = {
            "prompt": test.prompt,
        }

        prompt = generate_prompt(functions_definitions, test.prompt)

        match status:
            case STATUS.FUNCTION_NAME:
                name = get_function_name()
                item.name = name
            case STATUS.FUNCTION_PARAMETERS:
                pass
            case STATUS.WAITING_NUMBER:
                pass

        result.append(item)


def get_function_name() -> str:
    pass
