import re
from dataclasses import dataclass

ADDRESS_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")


@dataclass
class WithdrawalOption:
    method: str
    eta: str
    fee_pct: float
    notes: str


def is_valid_address(address: str) -> bool:
    return bool(ADDRESS_RE.match(address))


def get_options(country: str | None = None) -> list[WithdrawalOption]:
    return [
        WithdrawalOption(method="moonpay", eta="variable", fee_pct=3.5, notes="External KYC may apply"),
        WithdrawalOption(method="external", eta="minutes", fee_pct=0.2, notes="USD external address"),
    ]
