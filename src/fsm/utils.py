import re
from enum import StrEnum
from llm_sdk import Small_LLM_Model
from src.parsing import Vocabulary


class RegExp(StrEnum):
    NUMBERS = r"[Ġ\s]*[-0-9.]+"


class Cache:
    def __init__(
        self, model: Small_LLM_Model, vocabulary: Vocabulary, fd: list[str]
    ):
        self.model = model
        self.vocabulary = vocabulary
        self.fd = fd
        self.valid_numbers_ids: list[int] = []
        self.valid_fd_ids: list[int] = []

        self.find_valid_numbers_ids()
        self.find_valid_fd_ids()

    def find_valid_numbers_ids(self) -> None:
        for token_text, token_id in self.vocabulary.items():
            if re.fullmatch(RegExp.NUMBERS, token_text):
                self.valid_numbers_ids.append(token_id)

    def find_valid_fd_ids(self) -> None:
        for f in self.fd:
            fd_tokens: list[int] = self.model.encode(f).tolist()[0]
            self.valid_fd_ids.extend(fd_tokens)
