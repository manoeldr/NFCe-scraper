"""
Testes unitários para CupomController
"""
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.controller.cupom_controller import CupomController
from src.models.cupom_completo import CupomCompleto
from src.models.emitente import Emitente
from src.models.cupom import Cupom
from src.models.produto import Produto


class TestCupomController:
    """Testes para o controller de cupons"""
    
    def test_inicializacao(self):
        """Testa inicialização do controller"""
        controller = CupomController()
        
        assert controller.qrcode_service is not None
        assert controller.web_scraper is not None
        assert controller.csv_repository is not None
    
    def test_inicializacao_headless(self):
        """Testa inicialização com modo headless"""
        controller = CupomController(headless=True)
        
        assert controller.web_scraper.headless is True
    
    def test_inicializacao_com_diretorio_customizado(self):
        """Testa inicialização com diretório de saída customizado"""
        diretorio = Path("/tmp/teste")
        controller = CupomController(diretorio_saida=diretorio)
        
        assert controller.csv_repository.diretorio == diretorio
    
    def test_validar_chave_valida(self):
        """Testa validação de chave válida"""
        controller = CupomController()
        
        with patch.object(controller.qrcode_service, 'processar_entrada') as mock_processar:
            mock_processar.return_value = "12345678901234567890123456789012345678901234"
            
            valido, chave, mensagem = controller.validar_chave("1234 5678 9012...")
            
            assert valido is True
            assert chave == "12345678901234567890123456789012345678901234"
            assert mensagem == "Chave válida"
    
    def test_validar_chave_invalida(self):
        """Testa validação de chave inválida"""
        controller = CupomController()
        
        with patch.object(controller.qrcode_service, 'processar_entrada') as mock_processar:
            mock_processar.return_value = None
            
            valido, chave, mensagem = controller.validar_chave("chave_invalida")
            
            assert valido is False
            assert chave is None
            assert mensagem == "Chave inválida"
    
    def test_processar_cupom_chave_invalida(self):
        """Testa processamento com chave inválida"""
        controller = CupomController()
        
        with patch.object(controller.qrcode_service, 'processar_entrada') as mock_processar:
            mock_processar.return_value = None
            
            sucesso, cupom, arquivo, mensagem = controller.processar_cupom("chave_invalida")
            
            assert sucesso is False
            assert cupom is None
            assert arquivo is None
            assert "inválida" in mensagem
    
    def test_processar_cupom_sucesso_com_csv(self):
        """Testa processamento completo com sucesso e salvamento em CSV"""
        controller = CupomController()
        
        # Mock da chave válida
        chave_valida = "12345678901234567890123456789012345678901234"
        
        # Mock do cupom extraído
        cupom_mock = CupomCompleto(
            emitente=Emitente(nome="Loja Teste"),
            cupom=Cupom(total="100,00"),
            produtos=[
                Produto(
                    codigo_ncm="12345678",
                    descricao="Produto",
                    quantidade="1",
                    valor_liquido="100,00",
                    valor_total="100,00",
                    cod_produto="12345678",
                    cod_gtin=None
                )
            ]
        )
        
        # Mock do arquivo salvo
        arquivo_mock = Path("/tmp/teste.csv")
        
        with patch.object(controller.qrcode_service, 'processar_entrada') as mock_qr:
            mock_qr.return_value = chave_valida
            
            with patch.object(controller.web_scraper, 'extrair_dados_cupom') as mock_scraper:
                mock_scraper.return_value = cupom_mock
                
                with patch.object(controller.csv_repository, 'salvar') as mock_csv:
                    mock_csv.return_value = arquivo_mock
                    
                    sucesso, cupom, arquivo, mensagem = controller.processar_cupom(
                        chave_valida,
                        salvar_csv=True
                    )
                    
                    assert sucesso is True
                    assert cupom == cupom_mock
                    assert arquivo == arquivo_mock
                    assert "sucesso" in mensagem.lower()
    
    def test_processar_cupom_sucesso_sem_csv(self):
        """Testa processamento sem salvamento em CSV"""
        controller = CupomController()
        
        chave_valida = "12345678901234567890123456789012345678901234"
        
        cupom_mock = CupomCompleto(
            emitente=Emitente(nome="Loja"),
            cupom=Cupom(total="50,00"),
            produtos=[]
        )
        
        with patch.object(controller.qrcode_service, 'processar_entrada') as mock_qr:
            mock_qr.return_value = chave_valida
            
            with patch.object(controller.web_scraper, 'extrair_dados_cupom') as mock_scraper:
                mock_scraper.return_value = cupom_mock
                
                sucesso, cupom, arquivo, mensagem = controller.processar_cupom(
                    chave_valida,
                    salvar_csv=False
                )
                
                assert sucesso is True
                assert cupom == cupom_mock
                assert arquivo is None
                assert "processado com sucesso" in mensagem.lower()
    
    def test_processar_cupom_erro_extracao(self):
        """Testa erro durante extração"""
        controller = CupomController()
        
        chave_valida = "12345678901234567890123456789012345678901234"
        
        with patch.object(controller.qrcode_service, 'processar_entrada') as mock_qr:
            mock_qr.return_value = chave_valida
            
            with patch.object(controller.web_scraper, 'extrair_dados_cupom') as mock_scraper:
                mock_scraper.return_value = None
                
                sucesso, cupom, arquivo, mensagem = controller.processar_cupom(chave_valida)
                
                assert sucesso is False
                assert cupom is None
                assert "extrair" in mensagem.lower()
    
    def test_processar_cupom_erro_salvamento(self):
        """Testa erro durante salvamento mas extração bem-sucedida"""
        controller = CupomController()
        
        chave_valida = "12345678901234567890123456789012345678901234"
        
        cupom_mock = CupomCompleto(
            emitente=Emitente(nome="Loja"),
            cupom=Cupom(total="10,00"),
            produtos=[]
        )
        
        with patch.object(controller.qrcode_service, 'processar_entrada') as mock_qr:
            mock_qr.return_value = chave_valida
            
            with patch.object(controller.web_scraper, 'extrair_dados_cupom') as mock_scraper:
                mock_scraper.return_value = cupom_mock
                
                with patch.object(controller.csv_repository, 'salvar') as mock_csv:
                    mock_csv.side_effect = Exception("Erro ao salvar")
                    
                    sucesso, cupom, arquivo, mensagem = controller.processar_cupom(chave_valida)
                    
                    # Deve retornar sucesso=True porque extraiu os dados
                    assert sucesso is True
                    assert cupom == cupom_mock
                    assert arquivo is None
                    assert "erro ao salvar" in mensagem.lower()
    
    def test_processar_multiplos_cupons(self):
        """Testa processamento em lote"""
        controller = CupomController()
        
        chaves = [
            "12345678901234567890123456789012345678901234",
            "98765432109876543210987654321098765432109876",
            "11111111111111111111111111111111111111111111"
        ]
        
        cupom_mock = CupomCompleto(
            emitente=Emitente(nome="Loja"),
            cupom=Cupom(total="10,00"),
            produtos=[]
        )
        
        with patch.object(controller, 'processar_cupom') as mock_processar:
            # Simula 2 sucessos e 1 erro
            mock_processar.side_effect = [
                (True, cupom_mock, Path("/tmp/1.csv"), "Sucesso"),
                (True, cupom_mock, Path("/tmp/2.csv"), "Sucesso"),
                (False, None, None, "Erro"),
            ]
            
            resultados = controller.processar_multiplos_cupons(chaves)
            
            assert resultados['total'] == 3
            assert resultados['sucesso'] == 2
            assert resultados['erro'] == 1
            assert len(resultados['cupons']) == 3
    
    def test_processar_cupom_com_nome_arquivo_customizado(self):
        """Testa salvamento com nome de arquivo customizado"""
        controller = CupomController()
        
        chave_valida = "12345678901234567890123456789012345678901234"
        nome_custom = "meu_cupom.csv"
        
        cupom_mock = CupomCompleto(
            emitente=Emitente(nome="Loja"),
            cupom=Cupom(total="10,00"),
            produtos=[]
        )
        
        with patch.object(controller.qrcode_service, 'processar_entrada') as mock_qr:
            mock_qr.return_value = chave_valida
            
            with patch.object(controller.web_scraper, 'extrair_dados_cupom') as mock_scraper:
                mock_scraper.return_value = cupom_mock
                
                with patch.object(controller.csv_repository, 'salvar') as mock_csv:
                    mock_csv.return_value = Path("/tmp/meu_cupom.csv")
                    
                    sucesso, cupom, arquivo, mensagem = controller.processar_cupom(
                        chave_valida,
                        nome_arquivo=nome_custom
                    )
                    
                    # Verifica que salvou com nome customizado
                    mock_csv.assert_called_once()
                    args, kwargs = mock_csv.call_args
                    assert kwargs.get('nome_arquivo') == nome_custom