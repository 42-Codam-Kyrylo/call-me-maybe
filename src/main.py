import argparse
import numpy as np
from enum import StrEnum
from llm_sdk import Small_LLM_Model

# TODO:  You must implement proper JSON error handling for input files,
# as they may contain invalid JSON or be missing entirely


class DefaultPath(StrEnum):
    FUNCTION_DEFINITION = "data/input/functions_definition.json"
    INPUT = "data/input/function_calling_tests.json"
    OUTPUT = "data/output/function_calling_results.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--functions_definition",
        default=DefaultPath.FUNCTION_DEFINITION,
    )
    parser.add_argument(
        "--input",
        default=DefaultPath.INPUT,
    )
    parser.add_argument(
        "--output",
        default=DefaultPath.OUTPUT,
    )

    args = parser.parse_args()
    print("input:", args.input)

    from parsing.parsing import parse_function_definitions, parse_function_calling_tests
    
    try:
        functions = parse_function_definitions(args.functions_definition)
        print(f"Successfully loaded {len(functions)} function definitions.")
    except Exception as e:
        print(f"Error loading function definitions: {e}")

    try:
        tests = parse_function_calling_tests(args.input)
        print(f"Successfully loaded {len(tests)} function calling tests.")
    except Exception as e:
        print(f"Error loading function calling tests: {e}")

    # model = Small_LLM_Model()
    # prompt = "The capital of France is"

    # tokens: list[int] = model.encode(prompt).tolist()[0]
    # max_new_tokens = 10

    # for _ in range(max_new_tokens):
    #     logits = model.get_logits_from_input_ids(tokens)
    #     next_token = int(np.argmax(logits))

    #     tokens.append(next_token)
    #     print(model.decode([next_token]), end="", flush=True)

    # full_text = model.decode(tokens)
    # print()
    # print(full_text)


if __name__ == "__main__":
    main()
