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
        WithdrawalOption(method="bank", eta="1-2 business days (PY), 2-5 days (intl)", fee_pct=1.5, notes="Bank transfer via operator"),
        WithdrawalOption(method="crypto", eta="minutes", fee_pct=0.2, notes="USDC external address"),
        WithdrawalOption(method="moonpay", eta="variable", fee_pct=3.5, notes="External KYC may apply"),
    ]
