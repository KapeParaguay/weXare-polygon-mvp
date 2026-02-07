from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str


class LLMProvider:
    name: str = "base"

    def available(self) -> bool:
        raise NotImplementedError

    def generate(self, prompt: str) -> LLMResponse:
        raise NotImplementedError
