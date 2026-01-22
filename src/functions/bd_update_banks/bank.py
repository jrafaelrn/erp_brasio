from dataclasses import dataclass
from typing import List
from .transaction import Transaction

@dataclass
class Bank:
    name: str
    transactions: List[Transaction]
