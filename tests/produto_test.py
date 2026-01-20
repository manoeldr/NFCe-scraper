"""
Testes unitários para o modelo Produto
"""
import pytest
from src.models.produto import Produto


class TestProduto:
    """Testes para o modelo de dados Produto"""
    
    def test_criar_produto_basico(self):
        """Testa criação de produto com dados básicos"""
        produto = Produto(
            codigo_ncm="12345678",
            valor_liquido=10.50,
            cod_produto="PROD001",
            cod_gtin="7891234567890",
            valor_total=12.00
        )
        
        assert produto.codigo_ncm == "12345678"
        assert produto.valor_liquido == 10.50
        assert produto.cod_produto == "PROD001"
        assert produto.cod_gtin == "7891234567890"
        assert produto.valor_total == 12.00
    
    def test_criar_produto_com_dados_opcionais(self):
        """Testa criação de produto com dados opcionais"""
        produto = Produto(
            codigo_ncm="12345678",
            valor_liquido=10.50,
            cod_produto="PROD001",
            cod_gtin=None,
            valor_total=12.00,
            descricao="Produto Teste",
            quantidade=2.5
        )
        
        assert produto.descricao == "Produto Teste"
        assert produto.quantidade == 2.5
        assert produto.cod_gtin is None
    
    def test_conversao_valores_para_float(self):
        """Testa conversão automática de strings para float"""
        produto = Produto(
            codigo_ncm="12345678",
            valor_liquido="10.50",  # String
            cod_produto="PROD001",
            cod_gtin="7891234567890",
            valor_total="12.00"  # String
        )
        
        assert isinstance(produto.valor_liquido, float)
        assert isinstance(produto.valor_total, float)
        assert produto.valor_liquido == 10.50
        assert produto.valor_total == 12.00
    
    def test_conversao_valor_com_virgula(self):
        """Testa conversão de valor com vírgula (formato brasileiro)"""
        produto = Produto(
            codigo_ncm="12345678",
            valor_liquido="10,50",  # Vírgula
            cod_produto="PROD001",
            cod_gtin="7891234567890",
            valor_total="12,00"  # Vírgula
        )
        
        assert produto.valor_liquido == 10.50
        assert produto.valor_total == 12.00
    
    def test_to_dict(self):
        """Testa conversão de produto para dicionário"""
        produto = Produto(
            codigo_ncm="12345678",
            valor_liquido=10.50,
            cod_produto="PROD001",
            cod_gtin="7891234567890",
            valor_total=12.00,
            descricao="Produto Teste",
            quantidade=2.0
        )
        
        resultado = produto.to_dict()
        
        assert isinstance(resultado, dict)
        assert resultado['Codigo_NCM'] == "12345678"
        assert resultado['Valor_Liquido'] == 10.50
        assert resultado['Cod_Produto'] == "PROD001"
        assert resultado['Cod_GTIN'] == "7891234567890"
        assert resultado['Valor_Total'] == 12.00
        assert resultado['Descricao'] == "Produto Teste"
        assert resultado['Quantidade'] == 2.0
    
    def test_to_dict_com_valores_none(self):
        """Testa conversão para dict com valores None"""
        produto = Produto(
            codigo_ncm="12345678",
            valor_liquido=10.50,
            cod_produto="PROD001",
            cod_gtin=None,
            valor_total=12.00
        )
        
        resultado = produto.to_dict()
        
        assert resultado['Cod_GTIN'] == ''
        assert resultado['Descricao'] == ''
        assert resultado['Quantidade'] == ''
    
    def test_conversao_quantidade_para_float(self):
        """Testa conversão de quantidade string para float"""
        produto = Produto(
            codigo_ncm="12345678",
            valor_liquido=10.50,
            cod_produto="PROD001",
            cod_gtin="7891234567890",
            valor_total=12.00,
            quantidade="3.5"  # String
        )
        
        assert isinstance(produto.quantidade, float)
        assert produto.quantidade == 3.5
    
    def test_repr(self):
        """Testa representação string do produto"""
        produto = Produto(
            codigo_ncm="12345678",
            valor_liquido=10.50,
            cod_produto="PROD001",
            cod_gtin="7891234567890",
            valor_total=12.00
        )
        
        repr_str = repr(produto)
        
        assert "PROD001" in repr_str
        assert "12345678" in repr_str
        assert "12.00" in repr_str
    
    def test_validar_produto_valido(self):
        """Testa validação de produto válido"""
        produto = Produto(
            codigo_ncm="12345678",
            valor_liquido=10.50,
            cod_produto="PROD001",
            cod_gtin="7891234567890",
            valor_total=12.00,
            quantidade=1.0
        )
        
        valido, erros = produto.validar()
        
        assert valido is True
        assert len(erros) == 0
    
    def test_validar_ncm_invalido(self):
        """Testa validação de NCM inválido"""
        produto = Produto(
            codigo_ncm="123",  # Muito curto
            valor_liquido=10.50,
            cod_produto="PROD001",
            cod_gtin="7891234567890",
            valor_total=12.00
        )
        
        valido, erros = produto.validar()
        
        assert valido is False
        assert len(erros) > 0
        assert "NCM inválido" in erros[0]
    
    def test_validar_valores_negativos(self):
        """Testa validação de valores negativos"""
        produto = Produto(
            codigo_ncm="12345678",
            valor_liquido=-10.50,
            cod_produto="PROD001",
            cod_gtin="7891234567890",
            valor_total=-12.00
        )
        
        valido, erros = produto.validar()
        
        assert valido is False
        assert len(erros) >= 2
    
    def test_validar_quantidade_invalida(self):
        """Testa validação de quantidade inválida"""
        produto = Produto(
            codigo_ncm="12345678",
            valor_liquido=10.50,
            cod_produto="PROD001",
            cod_gtin="7891234567890",
            valor_total=12.00,
            quantidade=-1.0
        )
        
        valido, erros = produto.validar()
        
        assert valido is False
        assert any("Quantidade inválida" in erro for erro in erros)
    
    def test_limpeza_de_espacos(self):
        """Testa remoção de espaços extras"""
        produto = Produto(
            codigo_ncm="  12345678  ",
            valor_liquido=10.50,
            cod_produto="  PROD001  ",
            cod_gtin="  7891234567890  ",
            valor_total=12.00,
            descricao="  Produto Teste  "
        )
        
        assert produto.codigo_ncm == "12345678"
        assert produto.cod_produto == "PROD001"
        assert produto.cod_gtin == "7891234567890"
        assert produto.descricao == "Produto Teste"