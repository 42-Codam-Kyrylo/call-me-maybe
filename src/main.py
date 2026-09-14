import argparse
from enum import StrEnum

# from llm_sdk import Small_LLM_Model


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


if __name__ == "__main__":
    main()
