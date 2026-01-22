"""
Serviço para leitura de QR Codes de cupons fiscais SAT
"""
from pyzbar import pyzbar
from PIL import Image
from typing import Optional
from pathlib import Path
import re

from src.config import settings


class QRCodeService:
    """
    Serviço para decodificar QR Codes de cupons fiscais
    
    Suporta:
    - Leitura de QR Code de imagens (PNG, JPG, JPEG, BMP)
    - Chave de acesso digitada manualmente
    
    Cada imagem deve conter apenas um QR Code de cupom fiscal
    """
    
    # Formatos de imagem suportados
    FORMATOS_SUPORTADOS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
    
    @staticmethod
    def processar_entrada(entrada: str) -> Optional[str]:
        """
        Processa a entrada do usuário (pode ser caminho de imagem ou chave digitada)
        
        Args:
            entrada: Caminho da imagem do QR Code OU chave de acesso digitada
        
        Returns:
            Chave de acesso (44 dígitos) ou None se inválida
        """
        entrada = entrada.strip()
        
        # Verifica se é um caminho de arquivo (tem extensão de imagem)
        caminho = Path(entrada)
        
        if caminho.suffix.lower() in QRCodeService.FORMATOS_SUPORTADOS:
            # É um caminho de imagem, extrai do QR Code
            print("Detectado: Imagem de QR Code")
            return QRCodeService.extrair_chave_acesso(entrada)
        
        # Assume que é uma chave digitada
        print("Detectado: Chave digitada manualmente")
        chave = QRCodeService.limpar_chave_digitada(entrada)
        
        if QRCodeService.validar_chave_acesso(chave):
            print(f"SUCESSO: Chave válida: {chave}")
            return chave
        else:
            print(f"ERRO: Chave inválida. Deve ter exatamente {settings.TAMANHO_CHAVE_ACESSO} dígitos.")
            return None
    
    @staticmethod
    def limpar_chave_digitada(chave: str) -> str:
        """
        Limpa uma chave digitada removendo espaços, hífens e outros caracteres
        
        Args:
            chave: Chave digitada pelo usuário
        
        Returns:
            Chave apenas com dígitos
        """
        # Remove tudo que não for dígito
        chave_limpa = re.sub(r'\D', '', chave)
        return chave_limpa
    
    @staticmethod
    def extrair_chave_acesso(caminho_imagem: str) -> Optional[str]:
        """
        Extrai a chave de acesso de um QR Code de cupom fiscal
        
        Args:
            caminho_imagem: Caminho para a imagem do QR Code
        
        Returns:
            Chave de acesso (44 dígitos) ou None se não encontrada
        
        Raises:
            FileNotFoundError: Se o arquivo não existir
            ValueError: Se o formato do arquivo não for suportado
        """
        # Valida caminho
        caminho = Path(caminho_imagem)
        
        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho_imagem}")
        
        # Valida extensão
        if caminho.suffix.lower() not in QRCodeService.FORMATOS_SUPORTADOS:
            raise ValueError(
                f"Formato não suportado: {caminho.suffix}. "
                f"Use: {', '.join(QRCodeService.FORMATOS_SUPORTADOS)}"
            )
        
        try:
            # Carrega a imagem
            with Image.open(caminho_imagem) as imagem:
                print(f"Processando imagem: {caminho.name}")
                
                # Decodifica o QR Code
                codigos = pyzbar.decode(imagem)
                
                if not codigos:
                    print("ERRO: Nenhum QR Code encontrado na imagem")
                    print("DICA: Certifique-se de que a imagem está nítida e bem iluminada")
                    return None
                
                # Pega o primeiro QR Code (assumimos apenas um por imagem)
                codigo = codigos[0]
                
                if len(codigos) > 1:
                    print(f"AVISO: Múltiplos QR Codes encontrados ({len(codigos)}). Usando o primeiro.")
                
                try:
                    # Decodifica os dados
                    dados = codigo.data.decode('utf-8')
                    print(f"Dados extraídos: {dados[:60]}{'...' if len(dados) > 60 else ''}")
                    
                    # Extrai a chave de acesso
                    chave = QRCodeService.extrair_chave_da_url(dados)
                    
                    if chave:
                        # Valida a chave extraída
                        if QRCodeService.validar_chave_acesso(chave):
                            print(f"SUCESSO: Chave de acesso extraída: {chave}")
                            return chave
                        else:
                            print(f"ERRO: Chave inválida encontrada: {chave}")
                            return None
                    else:
                        print("ERRO: Nenhuma chave de acesso encontrada no QR Code")
                        return None
                
                except UnicodeDecodeError:
                    print("ERRO: Não foi possível decodificar o QR Code")
                    return None
                
        except Exception as e:
            print(f"ERRO ao processar QR Code: {str(e)}")
            raise
    
    @staticmethod
    def extrair_chave_da_url(url: str) -> Optional[str]:
        """
        Extrai a chave de acesso de uma URL ou string do QR Code
        
        A chave de acesso tem exatamente 44 dígitos numéricos
        
        Padrões reconhecidos:
        - Sequência direta de 44 dígitos
        - Parâmetro URL: ?chave=... ou ?p=...
        - Pipe separado: chave|data|hora
        
        Args:
            url: URL completa ou dados do QR Code
        
        Returns:
            Chave de acesso ou None se não encontrada
        """
        if not url:
            return None
        
        # Padrão 1: Procura por sequência de exatamente 44 dígitos
        match = re.search(r'\b(\d{44})\b', url)
        if match:
            return match.group(1)
        
        # Padrão 2: Parâmetro na URL (case insensitive)
        match = re.search(r'[?&](?:chave|p|key)=(\d{44})', url, re.IGNORECASE)
        if match:
            return match.group(1)
        
        # Padrão 3: Separado por pipe ou outros delimitadores
        match = re.search(r'(\d{44})(?:[|\s,;]|$)', url)
        if match:
            return match.group(1)
        
        # Padrão 4: Qualquer sequência de dígitos (se tiver exatamente 44)
        todos_digitos = re.findall(r'\d+', url)
        for digitos in todos_digitos:
            if len(digitos) == 44:
                return digitos
        
        return None
    
    @staticmethod
    def validar_chave_acesso(chave: str) -> bool:
        """
        Valida se a chave de acesso está no formato correto
        
        Regras de validação:
        - Deve ter exatamente 44 caracteres
        - Todos os caracteres devem ser dígitos numéricos
        - Não pode ser None ou vazia
        
        Args:
            chave: Chave de acesso a validar
        
        Returns:
            True se válida, False caso contrário
        """
        # Verifica None ou vazio
        if not chave:
            return False
        
        # Verifica tamanho (usa constante do settings)
        if len(chave) != settings.TAMANHO_CHAVE_ACESSO:
            return False
        
        # Verifica se são apenas números
        if not chave.isdigit():
            return False
        
        return True