from dataclasses import dataclass


@dataclass
class ExternalSource:
    name: str
    priority: int


def get_external_sources() -> list[ExternalSource]:
    return [
        ExternalSource(name="rent-a-human", priority=3),
        ExternalSource(name="exa", priority=4),
    ]
