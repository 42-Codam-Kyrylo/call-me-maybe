from llm_sdk import Small_LLM_Model
from src.parsing import Vocabulary, FunctionDefinition, FunctionCallingTest
from .utils import Cache
from src.utils import generate_prompt
from typing import Any, cast
import numpy as np
import json


class FunctionCallingEngine:
    """Engine for executing constrained function calling using an LLM."""

    def __init__(
        self,
        model: Small_LLM_Model,
        vocabulary: Vocabulary,
        functions_definitions: list[FunctionDefinition],
        verbose: bool = False,
    ):
        self.model = model
        self.vocabulary = vocabulary
        self.functions_definitions = functions_definitions
        self.verbose = verbose

        self.fd_names = [f.name for f in self.functions_definitions]
        self.cache = Cache(self.model, self.vocabulary, self.fd_names)

    def _print(self, text: str) -> None:
        """Helper to print generated text in real-time if verbose is enabled."""
        if self.verbose:
            print(text, end="", flush=True)

    def run_tests(
        self, calling_tests: list[FunctionCallingTest]
    ) -> list[dict[str, Any]]:
        """Run function calling tests against the defined schemas.

        Args:
            calling_tests: A list of tests containing user prompts.

        Returns:
            A list of dictionaries with generated function calls.
        """
        result: list[dict[str, Any]] = []

        for test in calling_tests:
            if self.verbose:
                print(
                    f"\n\n\033[94m[Prompt]\033[0m {test.prompt}\n\033[92m[Generating]\033[0m ",
                    end="",
                    flush=True,
                )

            item: dict[str, Any] = {
                "prompt": test.prompt,
            }

            prompt = generate_prompt(self.functions_definitions, test.prompt)

            name = self._get_function_name(prompt)
            item["name"] = name

            parameters = self._generate_function_parameters(name, prompt)
            item["parameters"] = parameters

            result.append(item)

        return result

    def _get_function_name(self, prompt: str) -> str:
        """Predict a valid function name from the schema using constrained decoding.

        Args:
            prompt: The formatted prompt to feed the LLM.

        Returns:
            The generated valid function name.
        """
        prompt_with_injection = prompt + '{"name": "'
        self._print('{"name": "')

        prompt_tokens: list[int] = self.model.encode(
            prompt_with_injection
        ).tolist()[0]
        result_tokens: list[int] = []

        while True:
            allowed_token_ids = []
            matched_functions = 0
            last_matched_fd: list[int] = []

            for fd_tokens in self.cache.tokenized_fds:
                if fd_tokens[: len(result_tokens)] == result_tokens:
                    matched_functions += 1
                    last_matched_fd = fd_tokens

                    if len(fd_tokens) > len(result_tokens):
                        next_token = fd_tokens[len(result_tokens)]
                        allowed_token_ids.append(next_token)

            allowed_token_ids = list(set(allowed_token_ids))

            if matched_functions == 1 and last_matched_fd:
                remaining_tokens = last_matched_fd[len(result_tokens):]
                if remaining_tokens:
                    self._print(self.model.decode(remaining_tokens))
                return self.model.decode(last_matched_fd)

            if matched_functions == 0:
                break

            logits_list = self.model.get_logits_from_input_ids(prompt_tokens)
            last_logits = np.array(logits_list)

            masked_logits = np.full_like(last_logits, -np.inf)
            masked_logits[allowed_token_ids] = last_logits[allowed_token_ids]

            next_token = int(np.argmax(masked_logits))
            self._print(self.model.decode([next_token]))

            prompt_tokens.append(next_token)
            result_tokens.append(next_token)

        return self.model.decode(result_tokens)

    def _generate_function_parameters(
        self, fn_name: str, prompt: str
    ) -> dict[str, Any]:
        """Generate valid JSON parameters for a specific function.

        Args:
            fn_name: The name of the target function.
            prompt: The formatted prompt.

        Returns:
            A dictionary of extracted parameters.
        """
        params, arg_names = self._get_fn_params(fn_name)

        prompt_with_injection = (
            f'{prompt}{{"name": "{fn_name}", "parameters": {{'
        )
        self._print('", "parameters": {')

        prompt_tokens: list[int] = self.model.encode(
            prompt_with_injection
        ).tolist()[0]

        for index, arg_name in enumerate(arg_names):
            param_type = params[arg_name].type
            is_last_arg = index == len(arg_names) - 1

            self._generate_single_parameter(
                arg_name, param_type, prompt_tokens, is_last_arg
            )

        return self._parse_generated_parameters(prompt_tokens, fn_name)

    def _generate_single_parameter(
        self,
        arg_name: str,
        param_type: str,
        prompt_tokens: list[int],
        is_last_arg: bool,
    ) -> None:
        self._inject_parameter_key(arg_name, param_type, prompt_tokens)

        while True:
            next_token = self._predict_next_token(param_type, prompt_tokens)
            prompt_tokens.append(next_token)

            decoded_token: str = self.model.decode([next_token])
            self._print(decoded_token)

            is_complete = self._is_parameter_complete(
                param_type, decoded_token, prompt_tokens, is_last_arg
            )

            if is_complete:
                break

    def _inject_parameter_key(
        self, arg_name: str, param_type: str, prompt_tokens: list[int]
    ) -> None:
        QUOTE = '"'
        key_injection = f"{QUOTE}{arg_name}{QUOTE}: "

        if param_type == "string":
            key_injection += QUOTE

        self._print(key_injection)
        key_tokens = self.model.encode(key_injection).tolist()[0]
        prompt_tokens.extend(key_tokens)

    def _predict_next_token(
        self, param_type: str, prompt_tokens: list[int]
    ) -> int:
        logits: list[float] | np.ndarray = (
            self.model.get_logits_from_input_ids(prompt_tokens)
        )

        if param_type == "number":
            logits = self._apply_number_constraints(cast(list[float], logits))
        elif param_type == "boolean":
            logits = self._apply_boolean_constraints(cast(list[float], logits))

        return int(np.argmax(logits))

    def _apply_number_constraints(self, logits: list[float]) -> np.ndarray:
        logits_array = np.array(logits)
        masked_logits = np.full_like(logits_array, -np.inf)

        allowed_token_ids = (
            self.cache.valid_numbers_ids + self.cache.valid_stop_ids
        )
        masked_logits[allowed_token_ids] = logits_array[allowed_token_ids]

        return masked_logits

    def _apply_boolean_constraints(self, logits: list[float]) -> np.ndarray:
        logits_array = np.array(logits)
        masked_logits = np.full_like(logits_array, -np.inf)

        allowed_token_ids = (
            self.cache.valid_boolean_ids + self.cache.valid_stop_ids
        )
        masked_logits[allowed_token_ids] = logits_array[allowed_token_ids]

        return masked_logits

    def _is_parameter_complete(
        self,
        param_type: str,
        decoded_token: str,
        prompt_tokens: list[int],
        is_last_arg: bool,
    ) -> bool:
        if param_type == "string":
            return self._handle_string_stop_condition(
                decoded_token, prompt_tokens, is_last_arg
            )
        elif param_type == "boolean":
            return self._handle_default_stop_condition(
                decoded_token, prompt_tokens
            )
        else:
            return self._handle_default_stop_condition(
                decoded_token, prompt_tokens
            )

    def _handle_string_stop_condition(
        self, decoded_token: str, prompt_tokens: list[int], is_last_arg: bool
    ) -> bool:
        QUOTE = '"'
        COMMA = ","

        has_closing_quote = QUOTE in decoded_token
        if not has_closing_quote:
            return False

        needs_comma_separator = not is_last_arg and COMMA not in decoded_token
        if needs_comma_separator:
            self._print(", ")
            comma_tokens = self.model.encode(", ").tolist()[0]
            prompt_tokens.extend(comma_tokens)

        return True

    def _handle_default_stop_condition(
        self, decoded_token: str, prompt_tokens: list[int]
    ) -> bool:
        COMMA = ","
        BRACE = "}"

        if COMMA in decoded_token:
            self._print(" ")
            whitespace_token = self.model.encode(" ").tolist()[0]
            prompt_tokens.extend(whitespace_token)
            return True

        if BRACE in decoded_token:
            return True

        return False

    def _parse_generated_parameters(
        self, prompt_tokens: list[int], fn_name: str
    ) -> dict[str, Any]:
        PARAMETERS_KEY = '"parameters":'
        prompt_str = self.model.decode(prompt_tokens)

        _, _, result_str = prompt_str.partition(PARAMETERS_KEY)

        cleaned_result = result_str.strip().rstrip("}") + "}"
        try:
            return cast(dict[str, Any], json.loads(cleaned_result))
        except json.JSONDecodeError:
            print(
                f"JSONDecodeError for {fn_name}, result: {repr(cleaned_result)}"
            )
            return {}

    def _get_fn_params(self, fn_name: str) -> tuple[dict[str, Any], list[str]]:
        for fd in self.functions_definitions:
            if fd.name == fn_name:
                return fd.parameters, [p for p in fd.parameters]
        return {}, []
