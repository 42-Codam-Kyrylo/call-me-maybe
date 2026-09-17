from enum import StrEnum
from llm_sdk import Small_LLM_Model
from src.parsing import Vocabulary, FunctionDefinition, FunctionCallingTest
from .utils import Cache
from src.utils import generate_prompt
import numpy as np
import json


class STATUS(StrEnum):
    # ORIGINAL_PROMPT = "original_prompt"
    FUNCTION_NAME = "function_name"
    FUNCTION_PARAMETERS = "function_parameters"
    WAITING_NUMBER = "waiting_number"


class FunctionCallingFSM:
    def __init__(
        self,
        model: Small_LLM_Model,
        vocabulary: Vocabulary,
        functions_definitions: list[FunctionDefinition],
    ):
        self.model = model
        self.vocabulary = vocabulary
        self.functions_definitions = functions_definitions

        self.fd_names = [f.name for f in self.functions_definitions]
        self.cache = Cache(self.model, self.vocabulary, self.fd_names)
        self.status = STATUS.FUNCTION_NAME

    def run_tests(
        self, calling_tests: list[FunctionCallingTest]
    ) -> list[dict]:
        result = []

        for test in calling_tests:
            item = {
                "prompt": test.prompt,
            }

            prompt = generate_prompt(self.functions_definitions, test.prompt)

            name = self._get_function_name(prompt)
            item["name"] = name

            parameters = self._generate_function_parameters(name, prompt)
            item["parameters"] = parameters

            # match self.status:
            #     case STATUS.FUNCTION_NAME:
            #         self.status = STATUS.FUNCTION_PARAMETERS
            #     case STATUS.FUNCTION_PARAMETERS:
            #         pass
            #     case STATUS.WAITING_NUMBER:
            #         pass

            result.append(item)

        return result

    def _get_function_name(self, prompt: str) -> str:
        prompt_with_injection = prompt + '{"name": "'

        prompt_tokens: list[int] = self.model.encode(
            prompt_with_injection
        ).tolist()[0]
        result_tokens: list[int] = []

        while True:
            allowed_token_ids = []
            matched_functions = 0
            last_matched_fd = None

            for fd_tokens in self.cache.tokenized_fds:
                if fd_tokens[: len(result_tokens)] == result_tokens:
                    matched_functions += 1
                    last_matched_fd = fd_tokens

                    if len(fd_tokens) > len(result_tokens):
                        next_token = fd_tokens[len(result_tokens)]
                        allowed_token_ids.append(next_token)

            allowed_token_ids = list(set(allowed_token_ids))

            if matched_functions == 1:
                return self.model.decode(last_matched_fd)

            if matched_functions == 0:
                break

            logits = self.model.get_logits_from_input_ids(prompt_tokens)
            last_logits = np.array(logits)

            masked_logits = np.full_like(last_logits, -np.inf)
            masked_logits[allowed_token_ids] = last_logits[allowed_token_ids]

            next_token = int(np.argmax(masked_logits))

            prompt_tokens.append(next_token)
            result_tokens.append(next_token)

        return self.model.decode(result_tokens)

    def _generate_function_parameters(self, fn_name: str, prompt: str) -> dict:
        params, args = self._get_fn_params(fn_name)

        prompt_with_injection = (
            prompt + f'{{"name": "{fn_name}", "parameters": {{'
        )
        prompt_tokens: list[int] = self.model.encode(
            prompt_with_injection
        ).tolist()[0]

        for agr in args:
            arg_tokens: list[int] = self.model.encode(f'"{agr}": ').tolist()[0]
            prompt_tokens.extend(arg_tokens)

            while True:
                logits = self.model.get_logits_from_input_ids(prompt_tokens)
                next_token = int(np.argmax(logits))
                prompt_tokens.append(next_token)

                value: str = self.model.decode([next_token])
                if "," in value:
                    whitespace_token = self.model.encode(" ").tolist()[0]
                    prompt_tokens.extend(whitespace_token)
                    break
                if "}" in value:
                    break

        prompt_str = self.model.decode(prompt_tokens)
        _, _, result = prompt_str.partition('"parameters":')
        result = result.strip().rstrip("}") + "}"
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {}

    def _get_fn_params(self, fn_name: str):
        for fd in self.functions_definitions:
            if fd.name == fn_name:
                return fd.parameters, [p for p in fd.parameters]
