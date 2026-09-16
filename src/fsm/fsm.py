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

    def run_tests(self, calling_tests: list[FunctionCallingTest]) -> list[dict]:
        result = []

        for test in calling_tests:
            item = {
                "prompt": test.prompt,
            }

            prompt = generate_prompt(self.functions_definitions, test.prompt)

            match self.status:
                case STATUS.FUNCTION_NAME:
                    name = self._get_function_name(prompt)
                    item["name"] = name
                case STATUS.FUNCTION_PARAMETERS:
                    pass
                case STATUS.WAITING_NUMBER:
                    pass

            result.append(item)
            
        return result

    def _get_function_name(self, prompt: str) -> str:
        # TODO: 
        # result = []
        # while len(autocomplite(model.decode(result))) != 1 // going through all functions and returns all functions that starts from model.decode(result)
        # encode prompt + inject "name": "fn_ (add check if all fd starts with fn_)
        # logits = self.model.get_logits_from_input_ids(promt_tokens)
        # through np allow only tokens in cache.valid_fd_ids
        # choose - next_token =  int(np.argmax(logits))
        # prompt_tokens.append(next_token)
        # result.append(next_token)
        #
        pass
