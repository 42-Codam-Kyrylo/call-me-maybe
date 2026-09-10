import argparse
from llm_sdk import Small_LLM_Model

# TODO:  You must implement proper JSON error handling for input files,
# as they may contain invalid JSON or be missing entirely


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--functions_definition",
        default="data/input/functions_definition.json",
    )
    parser.add_argument(
        "--input",
        default="data/input/function_calling_tests.json",
    )
    parser.add_argument(
        "--output ",
        default="data/output/function_calling_results.json",
    )

    args = parser.parse_args()
    print("input:", args.input)

    model = Small_LLM_Model()

    # Кодируем текст в токены
    prompt = "Function to call: "
    tokens = model.encode(prompt).squeeze().tolist()

    # Получаем логиты для следующего токена
    logits = model.get_logits_from_input_ids(tokens)
    print(f"Количество токенов в словаре: {len(logits)}")


if __name__ == "__main__":
    main()
