"""
Modelo de dados para Cupom (Dados gerais da venda)
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Cupom:
    """
    Representa os dados gerais do cupom fiscal
    """
    total: Optional[str] = None                 # Valor total
    forma_pagamento: Optional[str] = None       # Forma de pagamento
    troco: Optional[str] = None                 # Valor do troco
    tributos: Optional[str] = None              # Valor aproximado de tributos
    data_hora: Optional[str] = None             # Data e hora da emissão
    qr_code: Optional[str] = None               # Dados do QR Code
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'total': self.total or 'N/A',
            'forma_pagamento': self.forma_pagamento or 'N/A',
            'troco': self.troco or 'N/A',
            'tributos': self.tributos or 'N/A',
            'data_hora': self.data_hora or 'N/A',
            'qr_code': self.qr_code or 'N/A',
        }