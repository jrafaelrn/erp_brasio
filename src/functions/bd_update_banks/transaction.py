from dataclasses import dataclass
from datetime import date

try:
    import extract
except Exception:
    from . import extract

@dataclass
class Transaction:
    
    transaction_date: date
    description: str
    pre_type: str
    value: float
    balance_after: float
    
    type: str = None
    entity_document: str = None
    entity_name: str = None

    def __post_init__(self):
        doc, nome = extract.extract_cpf_cnpj_cliente_fornecedor_from_description(self.description)
        self.entity_document = doc
        self.entity_name = nome
        
        self.type = extract.extract_type(self.description, self.pre_type)