import re
from collections.abc import Callable

from agentsphere.ai.schemas.inference import PromptMessage


class TokenCounter:
    def __init__(self) -> None:
        self._custom_counters: dict[str, Callable[[str], int]] = {}

    def register_tokenizer(self, model: str, counter_func: Callable[[str], int]) -> None:
        self._custom_counters[model.lower()] = counter_func

    def count_tokens(self, text: str, model: str | None = None) -> int:
        if not text:
            return 0

        model_key = model.lower() if model else None
        if model_key and model_key in self._custom_counters:
            try:
                return self._custom_counters[model_key](text)
            except Exception:
                pass  # Fallback on failure

        # Default robust fallback estimation:
        # Standard NLP estimation: 1 token ~ 4 characters, or ~0.75 words.
        # Let's count words using regex and combine both for accuracy.
        words = re.findall(r"\w+|[^\w\s]", text)
        word_count = len(words)
        char_count = len(text)

        # Average estimate
        est_by_chars = int(char_count / 3.8)
        est_by_words = int(word_count * 1.3)

        return max(1, int((est_by_chars + est_by_words) / 2))

    def count_messages_tokens(self, messages: list[PromptMessage], model: str | None = None) -> int:
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # overhead for message metadata (role/name)
            num_tokens += self.count_tokens(message.content, model)
            if message.name:
                num_tokens += self.count_tokens(message.name, model)
        num_tokens += 2  # overhead for priming the response assistant
        return num_tokens
