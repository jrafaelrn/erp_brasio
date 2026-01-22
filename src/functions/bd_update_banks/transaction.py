from dataclasses import dataclass
from datetime import date

@dataclass
class Transaction:
    id: int
    amount: float
    balance_after: float
    date: date
    description: str
    type: str
    document: str
    entity: str
