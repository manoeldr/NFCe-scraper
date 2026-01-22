"""
Testes unitários para WebScraperService
"""
from unittest.mock import Mock, MagicMock, patch
from src.services.web_scraper_service import WebScraperService
from src.models.produto import Produto


class TestWebScraperService:
    """Testes para o serviço de web scraping"""
    
    def test_iniciar_navegador(self):
        """Testa inicialização do navegador"""
        service = WebScraperService(headless=True)
        
        with patch('src.services.web_scraper_service.webdriver.Chrome') as mock_chrome:
            with patch('src.services.web_scraper_service.ChromeDriverManager') as mock_manager:
                mock_manager.return_value.install.return_value = '/fake/path'
                
                service.iniciar_navegador()
                
                assert service.driver is not None
                assert service.wait is not None
    
    def test_fechar_navegador(self):
        """Testa fechamento do navegador"""
        service = WebScraperService()
        service.driver = Mock()
        
        service.fechar_navegador()
        
        service.driver.quit.assert_called_once()
    
    def test_acessar_site_sucesso(self):
        """Testa acesso ao site com sucesso"""
        service = WebScraperService()
        service.driver = Mock()
        
        resultado = service.acessar_site()
        
        assert resultado is True
        service.driver.get.assert_called_once()
    
    def test_acessar_site_erro(self):
        """Testa acesso ao site com erro"""
        service = WebScraperService()
        service.driver = Mock()
        service.driver.get.side_effect = Exception("Erro de conexão")
        
        resultado = service.acessar_site()
        
        assert resultado is False
    
    def test_preencher_chave_acesso_sucesso(self):
        """Testa preenchimento da chave com sucesso"""
        service = WebScraperService()
        
        mock_element = Mock()
        mock_wait = Mock()
        mock_wait.until.return_value = mock_element
        
        service.wait = mock_wait
        
        resultado = service.preencher_chave_acesso("12345678901234567890123456789012345678901234")
        
        assert resultado is True
        mock_element.clear.assert_called_once()
        mock_element.send_keys.assert_called_once()
    
    def test_preencher_chave_acesso_timeout(self):
        """Testa timeout ao preencher chave"""
        from selenium.common.exceptions import TimeoutException
        
        service = WebScraperService()
        mock_wait = Mock()
        mock_wait.until.side_effect = TimeoutException()
        
        service.wait = mock_wait
        
        resultado = service.preencher_chave_acesso("12345678901234567890123456789012345678901234")
        
        assert resultado is False
    
    def test_clicar_consultar_sucesso(self):
        """Testa clique no botão Consultar"""
        service = WebScraperService()
        
        mock_button = Mock()
        mock_wait = Mock()
        mock_wait.until.return_value = mock_button
        
        service.wait = mock_wait
        
        with patch('time.sleep'):
            resultado = service.clicar_consultar()
        
        assert resultado is True
        mock_button.click.assert_called_once()
    
    def test_clicar_aba_produtos_sucesso(self):
        """Testa clique na aba Produtos"""
        service = WebScraperService()
        
        mock_tab = Mock()
        mock_wait = Mock()
        mock_wait.until.return_value = mock_tab
        
        service.wait = mock_wait
        
        with patch('time.sleep'):
            resultado = service.clicar_aba_produtos()
        
        assert resultado is True
        mock_tab.click.assert_called_once()
    
    def test_extrair_produtos_sucesso(self):
        """Testa extração de produtos da tabela"""
        service = WebScraperService()
        
        # Mock da tabela e linhas
        mock_celula1 = Mock()
        mock_celula1.text = "1"
        
        mock_celula2 = Mock()
        mock_celula2.text = "EMENDA MANG FILTRO 1/4"
        
        mock_celula3 = Mock()
        mock_celula3.text = "1,0000"
        
        mock_celula4 = Mock()
        mock_celula4.text = "UN"
        
        mock_celula5 = Mock()
        mock_celula5.text = "14,50"
        
        mock_celula6 = Mock()
        mock_celula6.text = "208329"
        
        mock_celula7 = Mock()
        mock_celula7.text = "Não Informado"
        
        mock_linha = Mock()
        mock_linha.find_elements.return_value = [
            mock_celula1, mock_celula2, mock_celula3, 
            mock_celula4, mock_celula5, mock_celula6, mock_celula7
        ]
        
        mock_tabela = Mock()
        mock_tabela.find_elements.return_value = [Mock(), mock_linha]  # Header + 1 linha
        
        mock_wait = Mock()
        mock_wait.until.return_value = mock_tabela
        
        service.wait = mock_wait
        
        produtos = service.extrair_produtos()
        
        assert len(produtos) == 1
        assert produtos[0].descricao == "EMENDA MANG FILTRO 1/4"
        assert produtos[0].cod_produto == "208329"
    
    def test_extrair_produtos_tabela_vazia(self):
        """Testa extração com tabela vazia"""
        service = WebScraperService()
        
        mock_tabela = Mock()
        mock_tabela.find_elements.return_value = [Mock()]  # Só o header
        
        mock_wait = Mock()
        mock_wait.until.return_value = mock_tabela
        
        service.wait = mock_wait
        
        produtos = service.extrair_produtos()
        
        assert len(produtos) == 0
    
    def test_extrair_produtos_timeout(self):
        """Testa timeout ao extrair produtos"""
        from selenium.common.exceptions import TimeoutException
        
        service = WebScraperService()
        mock_wait = Mock()
        mock_wait.until.side_effect = TimeoutException()
        
        service.wait = mock_wait
        
        produtos = service.extrair_produtos()
        
        assert len(produtos) == 0
    
    def test_aguardar_captcha_manual(self):
        """Testa pausa para captcha manual"""
        service = WebScraperService()
        
        with patch('builtins.input', return_value=''):
            with patch('time.sleep'):
                # Não deve gerar exceção
                service.aguardar_captcha_manual()
    
    def test_headless_mode_true(self):
        """Testa criação do serviço em modo headless"""
        service = WebScraperService(headless=True)
        
        assert service.headless is True
    
    def test_headless_mode_false(self):
        """Testa criação do serviço com interface gráfica"""
        service = WebScraperService(headless=False)
        
        assert service.headless is False