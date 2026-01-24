"""
Modelo de dados para Consumidor (Destinatário / Cliente)
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Consumidor:
    """
    Representa o consumidor / destinatário do cupom
    
    Nota: Nem sempre está presente no cupom
    """
    cpf_cnpj: Optional[str] = None              # CPF ou CNPJ
    nome: Optional[str] = None                  # Nome / Razão Social
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'cpf_cnpj': self.cpf_cnpj or 'N/A',
            'nome': self.nome or 'N/A',
        }
    
    def esta_presente(self) -> bool:
        """Verifica se há dados do consumidor"""
        return bool(self.cpf_cnpj or self.nome)