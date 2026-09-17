import re
from enum import StrEnum
from llm_sdk import Small_LLM_Model
from src.parsing import Vocabulary


class RegExp(StrEnum):
    """Regular expressions for detecting specific token types."""
    NUMBERS = r"[Ġ\s]*[-0-9.]+"
    BOOLEANS = r"[Ġ\s]*(true|false|True|False)"


class Cache:
    """Pre-caches vocabulary token IDs for constrained decoding."""

    def __init__(
        self, model: Small_LLM_Model, vocabulary: Vocabulary, fd: list[str]
    ):
        """Initializes the Cache by pre-computing valid token IDs.

        Args:
            model: The LLM model instance.
            vocabulary: The parsed vocabulary dictionary.
            fd: List of available function names.
        """
        self.model = model
        self.vocabulary = vocabulary
        self.fd = fd
        self.valid_numbers_ids: list[int] = []
        self.valid_boolean_ids: list[int] = []
        self.valid_stop_ids: list[int] = []
        self.tokenized_fds: list[list[int]] = []

        self.find_valid_numbers_ids()
        self.find_valid_boolean_ids()
        self.find_valid_stop_ids()
        self.find_valid_fd_ids()

    def find_valid_numbers_ids(self) -> None:
        """Finds and caches token IDs that represent valid numbers."""
        for token_text, token_id in self.vocabulary.items():
            if re.fullmatch(RegExp.NUMBERS, token_text):
                self.valid_numbers_ids.append(token_id)

    def find_valid_boolean_ids(self) -> None:
        """Finds and caches token IDs that represent valid booleans."""
        for token_text, token_id in self.vocabulary.items():
            if re.fullmatch(RegExp.BOOLEANS, token_text):
                self.valid_boolean_ids.append(token_id)

    def find_valid_stop_ids(self) -> None:
        """Finds and caches token IDs that represent valid stop conditions (like commas)."""
        for token_text, token_id in self.vocabulary.items():
            if "," in token_text or "}" in token_text:
                self.valid_stop_ids.append(token_id)

    def find_valid_fd_ids(self) -> None:
        """Tokenizes and caches all available function names."""
        for f in self.fd:
            fd_tokens: list[int] = self.model.encode(f).tolist()[0]
            self.tokenized_fds.append(fd_tokens)
