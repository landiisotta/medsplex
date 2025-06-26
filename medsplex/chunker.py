import logging
import re
from typing import Dict, List

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Regex(BaseModel):
    regex: str = Field(..., description="Regex pattern for matching keywords.")

    @field_validator("regex")
    @staticmethod
    def validate_regex(value: str) -> str:
        try:
            re.compile(value)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {value}. Error: {e}")
        return value


class Chunker(BaseModel):
    """
    Helper
    """

    config: Dict[str, Regex]

    def run(self, text: str, nchr: int) -> List[Dict]:
        if not isinstance(nchr, int) or nchr <= 0:
            raise Exception(f"nchr should be integer >0, but found {nchr}.")
        chunks = []
        for keyword, options in self.config.items():
            pattern = options.regex
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - nchr)
                end = min(len(text), match.end() + nchr)
                chunks.append({"keyword": keyword, "text": text[start:end]})
                if len(text) < nchr:
                    logger.warning(f"Text length {len(text)} is less than {nchr}.")
        return chunks
