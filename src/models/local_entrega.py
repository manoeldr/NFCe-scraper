"""
Modelo de dados para Local de Entrega
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class LocalEntrega:
    """
    Representa o local de entrega do cupom
    
    Nota: Nem sempre está presente no cupom
    """
    endereco: Optional[str] = None              # Endereço de entrega
    bairro: Optional[str] = None                # Bairro / Distrito
    municipio: Optional[str] = None             # Município
    uf: Optional[str] = None                    # UF (estado)
    numero_cfe: Optional[str] = None            # Número da CF-e
    chave_acesso: Optional[str] = None          # Chave de acesso
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'endereco': self.endereco or 'N/A',
            'bairro': self.bairro or 'N/A',
            'municipio': self.municipio or 'N/A',
            'uf': self.uf or 'N/A',
            'numero_cfe': self.numero_cfe or 'N/A',
            'chave_acesso': self.chave_acesso or 'N/A',
        }
    
    def esta_presente(self) -> bool:
        """Verifica se há dados de local de entrega"""
        return bool(self.endereco or self.municipio)