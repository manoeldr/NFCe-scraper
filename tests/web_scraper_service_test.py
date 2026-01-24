"""
Testes unitários para WebScraperService
"""
from unittest.mock import Mock, MagicMock, patch
from src.services.web_scraper_service import WebScraperService
from src.models.produto import Produto
from src.models.emitente import Emitente
from src.models.consumidor import Consumidor
from src.models.cupom import Cupom
from src.models.local_entrega import LocalEntrega


class TestWebScraperService:
    """Testes para o serviço de web scraping"""
    
    def test_iniciar_navegador(self):
        """Testa inicialização do navegador"""
        service = WebScraperService(headless=True)
        
        with patch('src.services.web_scraper_service.webdriver.Chrome') as mock_chrome:
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
    
    def test_extrair_emitente(self):
        """Testa extração de dados do emitente"""
        service = WebScraperService()
        service.driver = Mock()
        
        # Mock dos elementos
        mock_nome = Mock()
        mock_nome.text = "Estabelecimento Teste"
        mock_cnpj = Mock()
        mock_cnpj.text = "12.345.678/0001-90"
        
        service.driver.find_element = Mock(side_effect=[mock_nome, mock_cnpj])
        
        with patch('src.config.campos_extracao.EXTRAIR_EMITENTE', {'nome': True, 'cnpj': True}):
            emitente = service.extrair_emitente()
        
        assert isinstance(emitente, Emitente)
    
    def test_extrair_consumidor(self):
        """Testa extração de dados do consumidor"""
        service = WebScraperService()
        service.driver = Mock()
        
        mock_nome = Mock()
        mock_nome.text = "Cliente Teste"
        
        service.driver.find_element = Mock(return_value=mock_nome)
        
        with patch('src.config.campos_extracao.EXTRAIR_CONSUMIDOR', {'ativo': True, 'nome': True}):
            consumidor = service.extrair_consumidor()
        
        assert consumidor is None or isinstance(consumidor, Consumidor)
    
    def test_extrair_cupom(self):
        """Testa extração de dados do cupom"""
        service = WebScraperService()
        service.driver = Mock()
        
        mock_total = Mock()
        mock_total.text = "100,00"
        
        service.driver.find_element = Mock(return_value=mock_total)
        
        with patch('src.config.campos_extracao.EXTRAIR_CUPOM', {'total': True}):
            cupom = service.extrair_cupom()
        
        assert isinstance(cupom, Cupom)
    
    def test_clicar_aba_local_entrega_nao_encontrada(self):
        """Testa quando aba de local de entrega não existe"""
        from selenium.common.exceptions import TimeoutException
        
        service = WebScraperService()
        service.driver = Mock()
        
        mock_wait = Mock()
        mock_wait.until.side_effect = TimeoutException()
        service.driver = Mock()
        
        with patch('src.services.web_scraper_service.WebDriverWait', return_value=mock_wait):
            resultado = service.clicar_aba_local_entrega()
        
        assert resultado is False
    
    def test_extrair_local_entrega_desativado(self):
        """Testa extração de local de entrega quando desativado"""
        service = WebScraperService()
        
        with patch('src.config.campos_extracao.EXTRAIR_LOCAL_ENTREGA', {'ativo': False}):
            local = service.extrair_local_entrega()
        
        assert local is None
    
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
    
    def test_extrair_produtos_com_ids(self):
        """Testa extração de produtos usando IDs específicos"""
        service = WebScraperService()
        service.driver = Mock()
        
        # Mock de elementos com IDs
        mock_ncm = Mock()
        mock_ncm.text = "39174090"
        mock_desc = Mock()
        mock_desc.text = "Produto Teste"
        mock_qtd = Mock()
        mock_qtd.text = "1,0000"
        mock_valor = Mock()
        mock_valor.text = "10,00"
        
        service.driver.find_element = Mock(side_effect=[mock_ncm, mock_desc, mock_qtd, mock_valor])
        
        mock_linha = Mock()
        mock_linha.find_elements = Mock(return_value=[Mock(), Mock()])
        
        mock_tabela = Mock()
        mock_tabela.find_elements = Mock(return_value=[Mock(), mock_linha])
        
        mock_wait = Mock()
        mock_wait.until.return_value = mock_tabela
        service.wait = mock_wait
        
        produtos = service.extrair_produtos()
        
        assert isinstance(produtos, list)
    
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