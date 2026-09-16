from enum import StrEnum
from src.parsing import Vocabulary
import numpy as np

class STATUS(StrEnum):
    ORIGINAL_PROMPT = "original_prompt"
    FUNCTION_NAME = "function_name"
    FUNCTION_PARAMETER = "function_parameter"

def finite_state_machine(vocabulary: Vocabulary):
    
