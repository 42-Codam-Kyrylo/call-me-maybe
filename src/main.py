import argparse
import sys
import json
from pathlib import Path
from src.engine import FunctionCallingEngine
from enum import StrEnum
from llm_sdk import Small_LLM_Model
from src.parsing import (
    parse_function_definitions,
    parse_function_calling_tests,
    parse_vocabulary,
)


class DefaultPath(StrEnum):
    FUNCTION_DEFINITION = "data/input/functions_definition.json"
    INPUT = "data/input/function_calling_tests.json"
    OUTPUT = "data/output/function_calling_results.json"


def exit() -> None:
    sys.exit(1)


def main() -> None:
    """Entry point for the function calling pipeline."""
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

    try:
        fd = parse_function_definitions(args.functions_definition)
        print(f"Successfully loaded {len(fd)} function definitions.")
    except Exception as e:
        print(f"Error loading function definitions: {e}")
        exit()

    try:
        tests = parse_function_calling_tests(args.input)
        print(f"Successfully loaded {len(tests)} function calling tests.")
    except Exception as e:
        print(f"Error loading function calling tests: {e}")
        exit()

    model = Small_LLM_Model()

    vocabulary_path = model.get_path_to_vocab_file()
    print(f"path of vocabulary: {vocabulary_path}")

    try:
        vocabulary = parse_vocabulary(vocabulary_path)
        print(f"Successfully loaded vocabulary with {len(vocabulary)} tokens.")
    except Exception as e:
        print(f"Error loading vocabulary: {e}")
        exit()

    engine = FunctionCallingEngine(model, vocabulary, fd)
    result = engine.run_tests(tests)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    print(f"Results successfully saved to {output_path}")


if __name__ == "__main__":
    main()


