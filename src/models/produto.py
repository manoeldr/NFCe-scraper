from dataclasses import dataclass, field
from typing import Optional
from decimal import Decimal

@dataclass
class Produto:
    """
    Representa um produto do cupom fiscal SAT
    
    Attributes:
        codigo_ncm: Código NCM
        
        valor_liquido: Valor do produto sem impostos
        cod_produto: Código interno do produto no estabelecimento
        valor_total: Valor final do produto com impostos
        
        cod_gtin: Código GTIN/EAN (código de barras) - opcional
        descricao: Descrição do produto - opcional
        quantidade: Quantidade vendida - opcional
    """
    codigo_ncm: str
    valor_liquido: float
    cod_produto: str
    cod_gtin: Optional[str]
    valor_total: float
    descricao: Optional[str] = None
    quantidade: Optional[float] = None
    
    def __post_init__(self):
        """Validação e normalização dos dados após inicialização"""
        # Converte valores para float (aceita strings)
        self.valor_liquido = self._converter_para_float(self.valor_liquido)
        self.valor_total = self._converter_para_float(self.valor_total)
        
        if self.quantidade is not None:
            self.quantidade = self._converter_para_float(self.quantidade)
        
        # Limpa espaços extras
        self.codigo_ncm = str(self.codigo_ncm).strip()
        self.cod_produto = str(self.cod_produto).strip()
        
        if self.cod_gtin:
            self.cod_gtin = str(self.cod_gtin).strip()
        
        if self.descricao:
            self.descricao = str(self.descricao).strip()
    
    @staticmethod
    def _converter_para_float(valor) -> float:
        """
        Converte um valor para float, aceitando strings e números
        
        Args:
            valor: Valor a ser convertido (str, int, float)
        
        Returns:
            Valor float
        """
        if isinstance(valor, (int, float)):
            return float(valor)
        
        # Remove espaços e substitui vírgula por ponto
        valor_str = str(valor).strip().replace(',', '.')
        
        # Remove caracteres não numéricos (exceto ponto e sinal negativo)
        valor_limpo = ''.join(c for c in valor_str if c.isdigit() or c in '.-')
        
        try:
            return float(valor_limpo) if valor_limpo else 0.0
        except ValueError:
            return 0.0
    
    def to_dict(self) -> dict:
        """
        Converte o produto para dicionário (CSV)
        
        Returns:
            Dicionário com os dados do produto
        """
        return {
            'Codigo_NCM': self.codigo_ncm,
            'Valor_Liquido': self.valor_liquido,
            'Cod_Produto': self.cod_produto,
            'Cod_GTIN': self.cod_gtin or '',
            'Valor_Total': self.valor_total,
            'Descricao': self.descricao or '',
            'Quantidade': self.quantidade if self.quantidade is not None else ''
        }
    
    def __repr__(self) -> str:
        """Representação legível do produto"""
        return (f"Produto(cod={self.cod_produto}, "
                f"ncm={self.codigo_ncm}, "
                f"valor=R${self.valor_total:.2f})")
    
    def validar(self) -> tuple[bool, list[str]]:
        """
        Valida os dados do produto
        
        Returns:
            Tupla (valido, lista_de_erros)
        """
        erros = []
        
        # Valida NCM (deve ter 8 dígitos)
        if not self.codigo_ncm.isdigit() or len(self.codigo_ncm) != 8:
            erros.append(f"NCM inválido: {self.codigo_ncm} (deve ter 8 dígitos)")
        
        # Valida valores positivos
        if self.valor_liquido < 0:
            erros.append(f"Valor líquido negativo: {self.valor_liquido}")
        
        if self.valor_total < 0:
            erros.append(f"Valor total negativo: {self.valor_total}")
        
        # Valida quantidade se presente
        if self.quantidade is not None and self.quantidade <= 0:
            erros.append(f"Quantidade inválida: {self.quantidade}")
        
        # Valida código do produto não vazio
        if not self.cod_produto:
            erros.append("Código do produto está vazio")
        
        return (len(erros) == 0, erros)
