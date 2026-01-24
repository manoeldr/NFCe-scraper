"""
Modelo completo que agrupa todos os dados extraídos do cupom fiscal
"""
from dataclasses import dataclass
from typing import List, Optional

from src.models.emitente import Emitente
from src.models.consumidor import Consumidor
from src.models.cupom import Cupom
from src.models.local_entrega import LocalEntrega
from src.models.produto import Produto


@dataclass
class CupomCompleto:
    """
    Representa todos os dados extraídos de um cupom fiscal
    
    Agrupa: Emitente, Consumidor, Cupom, Local de Entrega e Produtos
    """
    emitente: Emitente
    cupom: Cupom
    produtos: List[Produto]
    consumidor: Optional[Consumidor] = None
    local_entrega: Optional[LocalEntrega] = None
    
    def to_dict(self) -> dict:
        """
        Converte para dicionário completo
        
        Returns:
            Dicionário com todos os dados do cupom
        """
        return {
            'emitente': self.emitente.to_dict(),
            'consumidor': self.consumidor.to_dict() if self.consumidor else None,
            'cupom': self.cupom.to_dict(),
            'local_entrega': self.local_entrega.to_dict() if self.local_entrega else None,
            'produtos': [p.to_dict() for p in self.produtos],
            'resumo': {
                'total_produtos': len(self.produtos),
                'valor_total': self.cupom.total,
                'tem_consumidor': self.consumidor is not None and self.consumidor.esta_presente(),
                'tem_local_entrega': self.local_entrega is not None and self.local_entrega.esta_presente(),
            }
        }
    
    def __str__(self) -> str:
        """Representação em string"""
        linhas = [
            "=" * 70,
            "CUPOM FISCAL COMPLETO",
            "=" * 70,
            "",
            f"Estabelecimento: {self.emitente.nome}",
            f"CNPJ: {self.emitente.cnpj}",
            f"Total: {self.cupom.total}",
            f"Data/Hora: {self.cupom.data_hora}",
            f"Produtos: {len(self.produtos)} itens",
            ""
        ]
        
        if self.consumidor and self.consumidor.esta_presente():
            linhas.append(f"Cliente: {self.consumidor.nome}")
        
        if self.local_entrega and self.local_entrega.esta_presente():
            linhas.append(f"Entrega: {self.local_entrega.municipio}/{self.local_entrega.uf}")
        
        linhas.append("=" * 70)
        
        return "\n".join(linhas)