"""
Modelo de dados para Emitente (Estabelecimento comercial)
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Emitente:
    """
    Representa o estabelecimento comercial que emitiu o cupom
    """
    ie: Optional[str] = None                    # Inscrição Estadual
    im: Optional[str] = None                    # Inscrição Municipal
    extrato_numero: Optional[str] = None        # Número do extrato
    sat_numero: Optional[str] = None            # Número do SAT
    nome: Optional[str] = None                  # Nome do estabelecimento
    cnpj: Optional[str] = None                  # CNPJ
    endereco: Optional[str] = None              # Endereço completo
    bairro: Optional[str] = None                # Bairro
    cep: Optional[str] = None                   # CEP
    uf: Optional[str] = None                    # UF (estado)
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'ie': self.ie or 'N/A',
            'im': self.im or 'N/A',
            'extrato_numero': self.extrato_numero or 'N/A',
            'sat_numero': self.sat_numero or 'N/A',
            'nome': self.nome or 'N/A',
            'cnpj': self.cnpj or 'N/A',
            'endereco': self.endereco or 'N/A',
            'bairro': self.bairro or 'N/A',
            'cep': self.cep or 'N/A',
            'uf': self.uf or 'N/A',
        }