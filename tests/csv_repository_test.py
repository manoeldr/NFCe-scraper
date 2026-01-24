"""
Testes unitários para CSVRepository
"""
import csv
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile

from src.repositories.csv_repository import CSVRepository
from src.models.cupom_completo import CupomCompleto
from src.models.emitente import Emitente
from src.models.consumidor import Consumidor
from src.models.cupom import Cupom
from src.models.local_entrega import LocalEntrega
from src.models.produto import Produto


class TestCSVRepository:
    """Testes para o repositório CSV"""
    
    def test_inicializacao(self):
        """Testa inicialização do repositório"""
        repo = CSVRepository()
        
        assert repo.diretorio is not None
        assert isinstance(repo.diretorio, Path)
    
    def test_inicializacao_com_diretorio_customizado(self):
        """Testa inicialização com diretório customizado"""
        with tempfile.TemporaryDirectory() as tmpdir:
            diretorio = Path(tmpdir)
            repo = CSVRepository(diretorio=diretorio)
            
            assert repo.diretorio == diretorio
    
    def test_gerar_cabecalho(self):
        """Testa geração do cabeçalho CSV"""
        repo = CSVRepository()
        cabecalho = repo._gerar_cabecalho()
        
        assert isinstance(cabecalho, list)
        assert len(cabecalho) == 30  # Total de colunas
        assert 'Emitente_Nome' in cabecalho
        assert 'Produto_NCM' in cabecalho
        assert 'Cupom_Total' in cabecalho
    
    def test_gerar_linha_base_completa(self):
        """Testa geração de linha com todos os dados"""
        repo = CSVRepository()
        
        # Cria objetos de teste
        emitente = Emitente(
            nome="Loja Teste",
            cnpj="12.345.678/0001-90",
            ie="123456789",
            im="987654",
            endereco="Rua Teste, 123",
            bairro="Centro",
            cep="01234-567",
            uf="SP"
        )
        
        consumidor = Consumidor(
            nome="Cliente Teste",
            cpf_cnpj="123.456.789-00"
        )
        
        cupom = Cupom(
            total="100,00",
            data_hora="2026-01-22 20:00:00",
            forma_pagamento="Dinheiro"
        )
        
        produto = Produto(
            codigo_ncm="39174090",
            descricao="Produto Teste",
            quantidade="1,0000",
            valor_liquido="10,50",
            valor_total="10,50",
            cod_produto="39174090",
            cod_gtin=None
        )
        
        cupom_completo = CupomCompleto(
            emitente=emitente,
            consumidor=consumidor,
            cupom=cupom,
            produtos=[produto]
        )
        
        linha = repo._gerar_linha_base(cupom_completo, produto)
        
        assert isinstance(linha, list)
        assert len(linha) == 30  # Total de colunas
        assert "Loja Teste" in linha
        assert "Cliente Teste" in linha
        assert "Produto Teste" in linha
    
    def test_gerar_linha_base_sem_consumidor(self):
        """Testa geração de linha sem consumidor"""
        repo = CSVRepository()
        
        emitente = Emitente(nome="Loja Teste")
        cupom = Cupom(total="50,00")
        produto = Produto(
            codigo_ncm="12345678",
            descricao="Produto",
            quantidade="1",
            valor_liquido="50,00",
            valor_total="50,00",
            cod_produto="12345678",
            cod_gtin=None
        )
        
        cupom_completo = CupomCompleto(
            emitente=emitente,
            cupom=cupom,
            consumidor=None,
            produtos=[produto]
        )
        
        linha = repo._gerar_linha_base(cupom_completo, produto)
        
        # Verifica se tem N/A nos campos de consumidor
        assert 'N/A' in linha
    
    def test_gerar_linha_base_sem_local_entrega(self):
        """Testa geração de linha sem local de entrega"""
        repo = CSVRepository()
        
        emitente = Emitente(nome="Loja")
        cupom = Cupom(total="10,00")
        produto = Produto(
            codigo_ncm="11111111",
            descricao="Item",
            quantidade="1",
            valor_liquido="10,00",
            valor_total="10,00",
            cod_produto="11111111",
            cod_gtin=None
        )
        
        cupom_completo = CupomCompleto(
            emitente=emitente,
            cupom=cupom,
            local_entrega=None,
            produtos=[produto]
        )
        
        linha = repo._gerar_linha_base(cupom_completo, produto)
        
        # Verifica se tem N/A nos campos de entrega
        assert linha.count('N/A') > 0
    
    def test_gerar_linhas_com_multiplos_produtos(self):
        """Testa geração de múltiplas linhas (um produto por linha)"""
        repo = CSVRepository()
        
        emitente = Emitente(nome="Loja")
        cupom = Cupom(total="30,00")
        
        produtos = [
            Produto(codigo_ncm="111", descricao="P1", quantidade="1", 
                   valor_liquido="10", valor_total="10", cod_produto="111", cod_gtin=None),
            Produto(codigo_ncm="222", descricao="P2", quantidade="2", 
                   valor_liquido="10", valor_total="20", cod_produto="222", cod_gtin=None),
        ]
        
        cupom_completo = CupomCompleto(
            emitente=emitente,
            cupom=cupom,
            produtos=produtos
        )
        
        linhas = repo._gerar_linhas(cupom_completo)
        
        assert len(linhas) == 2  # Uma linha por produto
        assert any("P1" in str(linha) for linha in linhas)
        assert any("P2" in str(linha) for linha in linhas)
    
    def test_gerar_linhas_sem_produtos(self):
        """Testa geração de linha quando não há produtos"""
        repo = CSVRepository()
        
        emitente = Emitente(nome="Loja")
        cupom = Cupom(total="0,00")
        
        cupom_completo = CupomCompleto(
            emitente=emitente,
            cupom=cupom,
            produtos=[]
        )
        
        linhas = repo._gerar_linhas(cupom_completo)
        
        assert len(linhas) == 1  # Uma linha mesmo sem produtos
    
    def test_salvar_arquivo_csv(self):
        """Testa salvamento de arquivo CSV"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = CSVRepository(diretorio=Path(tmpdir))
            
            emitente = Emitente(
                nome="Estabelecimento",
                cnpj="12345678000190"
            )
            cupom = Cupom(total="100,00")
            produto = Produto(
                codigo_ncm="12345678",
                descricao="Produto X",
                quantidade="1",
                valor_liquido="100,00",
                valor_total="100,00",
                cod_produto="12345678",
                cod_gtin=None
            )
            
            cupom_completo = CupomCompleto(
                emitente=emitente,
                cupom=cupom,
                produtos=[produto]
            )
            
            # Salva
            caminho = repo.salvar(cupom_completo, nome_arquivo="teste.csv")
            
            # Verifica que foi criado
            assert caminho.exists()
            assert caminho.name == "teste.csv"
            
            # Verifica conteúdo
            with open(caminho, 'r', encoding='utf-8-sig') as f:
                leitor = csv.reader(f, delimiter=';')
                linhas = list(leitor)
                
                assert len(linhas) == 2  # Header + 1 linha de dados
                assert "Emitente_Nome" in linhas[0]
                assert "Estabelecimento" in linhas[1]
    
    def test_salvar_arquivo_nome_automatico(self):
        """Testa salvamento com nome automático"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = CSVRepository(diretorio=Path(tmpdir))
            
            emitente = Emitente(nome="Loja", cnpj="12345678000190")
            cupom = Cupom(total="50,00")
            produto = Produto(
                codigo_ncm="11111111",
                descricao="Item",
                quantidade="1",
                valor_liquido="50,00",
                valor_total="50,00",
                cod_produto="11111111",
                cod_gtin=None
            )
            
            cupom_completo = CupomCompleto(
                emitente=emitente,
                cupom=cupom,
                produtos=[produto]
            )
            
            caminho = repo.salvar(cupom_completo)
            
            assert caminho.exists()
            assert caminho.name.startswith("cupom_12345678000190_")
            assert caminho.name.endswith(".csv")
    
    def test_salvar_adiciona_extensao_csv(self):
        """Testa que adiciona extensão .csv se não fornecida"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = CSVRepository(diretorio=Path(tmpdir))
            
            emitente = Emitente(nome="Loja")
            cupom = Cupom(total="10,00")
            produto = Produto(
                codigo_ncm="99999999",
                descricao="X",
                quantidade="1",
                valor_liquido="10,00",
                valor_total="10,00",
                cod_produto="99999999",
                cod_gtin=None
            )
            
            cupom_completo = CupomCompleto(
                emitente=emitente,
                cupom=cupom,
                produtos=[produto]
            )
            
            caminho = repo.salvar(cupom_completo, nome_arquivo="arquivo_sem_extensao")
            
            assert caminho.name == "arquivo_sem_extensao.csv"