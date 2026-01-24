"""
Controller principal para orquestração do fluxo completo de extração
"""
from pathlib import Path
from typing import Optional, Tuple

from src.services.qrcode_service import QRCodeService
from src.services.web_scraper_service import WebScraperService
from src.repositories.csv_repository import CSVRepository
from src.models.cupom_completo import CupomCompleto


class CupomController:
    """
    Controller responsável por orquestrar o fluxo completo de extração de cupons
    
    Fluxo:
    1. Validação da chave de acesso
    2. Extração dos dados (web scraping)
    3. Salvamento em arquivo (CSV)
    """
    
    def __init__(self, headless: bool = False, diretorio_saida: Optional[Path] = None):
        """
        Inicializa o controller
        
        Args:
            headless: Se True, executa navegador em modo headless (sem interface)
            diretorio_saida: Diretório onde salvar os arquivos (opcional)
        """
        self.qrcode_service = QRCodeService()
        self.web_scraper = WebScraperService(headless=headless)
        self.csv_repository = CSVRepository(diretorio=diretorio_saida)
    
    def processar_cupom(
        self, 
        entrada: str, 
        salvar_csv: bool = True,
        nome_arquivo: Optional[str] = None
    ) -> Tuple[bool, Optional[CupomCompleto], Optional[Path], str]:
        """
        Processa um cupom fiscal completo
        
        Args:
            entrada: Chave de acesso (digitada, com espaços/hífens) ou caminho para imagem QR
            salvar_csv: Se True, salva automaticamente em CSV
            nome_arquivo: Nome customizado para o arquivo CSV (opcional)
        
        Returns:
            Tupla com:
            - sucesso (bool): True se processou com sucesso
            - cupom (CupomCompleto): Dados extraídos (ou None se erro)
            - arquivo (Path): Caminho do arquivo salvo (ou None se não salvou)
            - mensagem (str): Mensagem de status/erro
        """
        print("\n" + "="*70)
        print("INICIANDO PROCESSAMENTO DO CUPOM")
        print("="*70)
        
        # 1. Validação da chave
        print("\n[1/3] Validando chave de acesso...")
        chave = self.qrcode_service.processar_entrada(entrada)
        
        if not chave:
            mensagem = "ERRO: Chave de acesso inválida"
            print(f"\n{mensagem}")
            return False, None, None, mensagem
        
        print(f"SUCESSO: Chave válida - {chave}")
        
        # 2. Extração dos dados
        print("\n[2/3] Extraindo dados do cupom (navegador será aberto)...")
        print("IMPORTANTE: Você precisará resolver o captcha manualmente!\n")
        
        try:
            cupom_completo = self.web_scraper.extrair_dados_cupom(chave)
            
            if not cupom_completo:
                mensagem = "ERRO: Não foi possível extrair os dados do cupom"
                print(f"\n{mensagem}")
                return False, None, None, mensagem
            
            print("\nSUCESSO: Dados extraídos com sucesso!")
            
        except Exception as e:
            mensagem = f"ERRO na extração: {str(e)}"
            print(f"\n{mensagem}")
            return False, None, None, mensagem
        
        # 3. Salvamento (opcional)
        arquivo_salvo = None
        
        if salvar_csv:
            print("\n[3/3] Salvando dados em CSV...")
            
            try:
                arquivo_salvo = self.csv_repository.salvar(
                    cupom_completo, 
                    nome_arquivo=nome_arquivo
                )
                print(f"SUCESSO: Arquivo salvo em {arquivo_salvo}")
                
            except Exception as e:
                mensagem = f"AVISO: Dados extraídos mas erro ao salvar CSV: {str(e)}"
                print(f"\n{mensagem}")
                return True, cupom_completo, None, mensagem
        else:
            print("\n[3/3] Salvamento em CSV desabilitado")
        
        # Sucesso total
        print("\n" + "="*70)
        print("PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print("="*70)
        
        mensagem = "Cupom processado e salvo com sucesso" if salvar_csv else "Cupom processado com sucesso"
        return True, cupom_completo, arquivo_salvo, mensagem
    
    def processar_multiplos_cupons(
        self,
        chaves: list,
        salvar_csv: bool = True
    ) -> dict:
        """
        Processa múltiplos cupons em lote
        
        Args:
            chaves: Lista de chaves de acesso
            salvar_csv: Se True, salva cada cupom em CSV
        
        Returns:
            Dicionário com estatísticas:
            - total: número total de cupons
            - sucesso: número de cupons processados com sucesso
            - erro: número de cupons com erro
            - cupons: lista com resultados individuais
        """
        print("\n" + "="*70)
        print(f"PROCESSAMENTO EM LOTE - {len(chaves)} CUPONS")
        print("="*70)
        
        resultados = {
            'total': len(chaves),
            'sucesso': 0,
            'erro': 0,
            'cupons': []
        }
        
        for idx, entrada in enumerate(chaves, 1):
            print(f"\n\n>>> Processando cupom {idx}/{len(chaves)}")
            
            sucesso, cupom, arquivo, mensagem = self.processar_cupom(
                entrada, 
                salvar_csv=salvar_csv
            )
            
            if sucesso:
                resultados['sucesso'] += 1
            else:
                resultados['erro'] += 1
            
            resultados['cupons'].append({
                'chave': entrada[:20] + "..." if len(entrada) > 20 else entrada,
                'sucesso': sucesso,
                'arquivo': str(arquivo) if arquivo else None,
                'mensagem': mensagem
            })
        
        # Resumo final
        print("\n\n" + "="*70)
        print("RESUMO DO PROCESSAMENTO EM LOTE")
        print("="*70)
        print(f"Total: {resultados['total']}")
        print(f"Sucesso: {resultados['sucesso']}")
        print(f"Erro: {resultados['erro']}")
        print("="*70)
        
        return resultados
    
    def validar_chave(self, entrada: str) -> Tuple[bool, Optional[str], str]:
        """
        Apenas valida uma chave sem processar
        
        Args:
            entrada: Chave de acesso ou caminho para imagem QR
        
        Returns:
            Tupla com:
            - valido (bool): True se válida
            - chave (str): Chave limpa e formatada (ou None)
            - mensagem (str): Mensagem de status
        """
        chave = self.qrcode_service.processar_entrada(entrada)
        
        if chave:
            return True, chave, "Chave válida"
        else:
            return False, None, "Chave inválida"