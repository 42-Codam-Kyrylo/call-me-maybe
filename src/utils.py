from typing import List
from enum import StrEnum
from src.parsing import FunctionDefinition


class PROMPT(StrEnum):
    START = "You have access to the following functions: "
    USER_REQUEST = "User request:"
    END = "Function call: "


def generate_prompt(
    functions_definition: List[FunctionDefinition], user_request: str
) -> str:
    """Generates the main LLM system prompt integrating user requests and function schemas.

    Args:
        functions_definition: List of available functions.
        user_request: The textual query from the user.

    Returns:
        The formatted prompt string.
    """
    functions = format_function_definition(functions_definition)
    fd_strs = "\n".join(functions)

    result = f"""{PROMPT.START}
{fd_strs}

{PROMPT.USER_REQUEST} {user_request}

{PROMPT.END}"""

    return result


def format_function_definition(f_d: List[FunctionDefinition]) -> List[str]:
    """Formats a list of function definitions into readable strings.

    Args:
        f_d: A list of FunctionDefinition models.

    Returns:
        A list of formatted string representations for the prompt.
    """
    result: List[str] = []

    for f in f_d:
        parameters = ", ".join(
            f"{name}: {definition.type}"
            for name, definition in f.parameters.items()
        )
        record = f"{f.name}({parameters}): {f.description}"
        result.append(record)

    return result
