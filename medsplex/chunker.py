import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class ConfigFile:
    pass


class Chunker:
    """
    Helper
    """

    def __init__(self, config: ConfigFile):
        self._config = config

    def run(self, text: str, nchr: int) -> List[Dict]:
        if not isinstance(nchr, int) or nchr <= 0:
            raise Exception(f"nchr should be integer >0, but found {nchr}.")
        chunks = []
        for keyword, options in self._config.items():
            pattern = options.get("regex", keyword)
            for match in re.finditer(pattern, text, re.IGNORECASE):
                start = max(0, match.start() - nchr)
                end = min(len(text), match.end() + nchr)
                chunks.append({"keyword": keyword, "text": text[start:end]})
                if len(text) < nchr:
                    logger.warning(f"Text length {len(text)} is less than {nchr}.")
        return chunks
