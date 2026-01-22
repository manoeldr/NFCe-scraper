"""
Testes unitários para QRCodeService
"""
from src.services.qrcode_service import QRCodeService


class TestQRCodeService:
    """Testes para o serviço de QR Code"""
    
    # Testes de chave digitada
    def test_limpar_chave_digitada_apenas_numeros(self):
        """Testa limpeza de chave com apenas números"""
        service = QRCodeService()
        chave = "12345678901234567890123456789012345678901234"
        
        resultado = service.limpar_chave_digitada(chave)
        
        assert resultado == chave
    
    def test_limpar_chave_digitada_com_espacos(self):
        """Testa limpeza de chave com espaços"""
        service = QRCodeService()
        chave = "1234 5678 9012 3456 7890 1234 5678 9012 3456 7890 1234"
        
        resultado = service.limpar_chave_digitada(chave)
        
        assert resultado == "12345678901234567890123456789012345678901234"
        assert len(resultado) == 44
    
    def test_limpar_chave_digitada_com_hifens(self):
        """Testa limpeza de chave com hífens"""
        service = QRCodeService()
        chave = "1234-5678-9012-3456-7890-1234-5678-9012-3456-7890-1234"
        
        resultado = service.limpar_chave_digitada(chave)
        
        assert resultado == "12345678901234567890123456789012345678901234"
    
    def test_limpar_chave_digitada_com_caracteres_especiais(self):
        """Testa limpeza de chave com vários caracteres especiais"""
        service = QRCodeService()
        chave = "1234.5678/9012-3456 7890_1234|5678,9012;3456:7890!1234"
        
        resultado = service.limpar_chave_digitada(chave)
        
        assert resultado == "12345678901234567890123456789012345678901234"
    
    def test_processar_entrada_chave_valida(self):
        """Testa processamento de chave digitada válida"""
        service = QRCodeService()
        chave = "12345678901234567890123456789012345678901234"
        
        resultado = service.processar_entrada(chave)
        
        assert resultado == chave
    
    def test_processar_entrada_chave_com_espacos(self):
        """Testa processamento de chave com espaços"""
        service = QRCodeService()
        chave = "1234 5678 9012 3456 7890 1234 5678 9012 3456 7890 1234"
        
        resultado = service.processar_entrada(chave)
        
        assert resultado == "12345678901234567890123456789012345678901234"
    
    def test_processar_entrada_chave_invalida(self):
        """Testa processamento de chave inválida (tamanho errado)"""
        service = QRCodeService()
        chave = "123456789"
        
        resultado = service.processar_entrada(chave)
        
        assert resultado is None
    
    # Testes de extração de URL
    def test_extrair_chave_da_url_formato_completo(self):
        """Testa extração de chave de URL completa"""
        service = QRCodeService()
        url = "https://satsp.fazenda.sp.gov.br/...?p=12345678901234567890123456789012345678901234"
        
        chave = service.extrair_chave_da_url(url)
        
        assert chave == "12345678901234567890123456789012345678901234"
        assert len(chave) == 44
    
    def test_extrair_chave_da_url_apenas_numeros(self):
        """Testa extração de chave quando há apenas números na URL"""
        service = QRCodeService()
        url = "12345678901234567890123456789012345678901234|outro_dado"
        
        chave = service.extrair_chave_da_url(url)
        
        assert chave == "12345678901234567890123456789012345678901234"
    
    def test_extrair_chave_da_url_com_pipe(self):
        """Testa extração de chave separada por pipe"""
        service = QRCodeService()
        url = "12345678901234567890123456789012345678901234|20260119|143000"
        
        chave = service.extrair_chave_da_url(url)
        
        assert chave == "12345678901234567890123456789012345678901234"
    
    def test_extrair_chave_da_url_parametro_chave(self):
        """Testa extração de chave em parâmetro 'chave'"""
        service = QRCodeService()
        url = "https://example.com?chave=12345678901234567890123456789012345678901234"
        
        chave = service.extrair_chave_da_url(url)
        
        assert chave == "12345678901234567890123456789012345678901234"
    
    def test_extrair_chave_da_url_invalida(self):
        """Testa extração de URL sem chave válida"""
        service = QRCodeService()
        url = "https://exemplo.com/sem-chave"
        
        chave = service.extrair_chave_da_url(url)
        
        assert chave is None
    
    def test_extrair_chave_da_url_vazia(self):
        """Testa extração de URL vazia"""
        service = QRCodeService()
        chave = service.extrair_chave_da_url("")
        
        assert chave is None
    
    def test_extrair_chave_da_url_none(self):
        """Testa extração de URL None"""
        service = QRCodeService()
        chave = service.extrair_chave_da_url(None)
        
        assert chave is None
    
    # Testes de validação
    def test_validar_chave_acesso_valida(self):
        """Testa validação de chave válida"""
        service = QRCodeService()
        chave = "12345678901234567890123456789012345678901234"
        
        resultado = service.validar_chave_acesso(chave)
        
        assert resultado is True
    
    def test_validar_chave_acesso_tamanho_errado(self):
        """Testa validação de chave com tamanho incorreto"""
        service = QRCodeService()
        chave = "123456789"  # Muito curta
        
        resultado = service.validar_chave_acesso(chave)
        
        assert resultado is False
    
    def test_validar_chave_acesso_com_letras(self):
        """Testa validação de chave com caracteres não numéricos"""
        service = QRCodeService()
        chave = "1234567890123456789012345678901234567890ABCD"
        
        resultado = service.validar_chave_acesso(chave)
        
        assert resultado is False
    
    def test_validar_chave_acesso_vazia(self):
        """Testa validação de chave vazia"""
        service = QRCodeService()
        resultado = service.validar_chave_acesso("")
        
        assert resultado is False
    
    def test_validar_chave_acesso_none(self):
        """Testa validação de chave None"""
        service = QRCodeService()
        resultado = service.validar_chave_acesso(None)
        
        assert resultado is False
    
    def test_validar_chave_acesso_com_espacos(self):
        """Testa validação de chave com espaços"""
        service = QRCodeService()
        chave = "12345678901234567890 12345678901234567890123"
        
        resultado = service.validar_chave_acesso(chave)
        
        assert resultado is False
    
    # Testes de constantes
    def test_formatos_suportados(self):
        """Testa se os formatos suportados estão definidos"""
        formatos = QRCodeService.FORMATOS_SUPORTADOS
        
        assert '.png' in formatos
        assert '.jpg' in formatos
        assert '.jpeg' in formatos
        assert len(formatos) > 0