"""
Serviço para realizar web scraping no site da SEFAZ-SP
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Optional
import time

from src.config import settings
from src.models.produto import Produto


class WebScraperService:
    """
    Serviço para extrair dados de cupons fiscais do site da SEFAZ-SP
    
    Fluxo:
    1. Acessa o site da SEFAZ-SP
    2. Preenche a chave de acesso
    3. PAUSA para o usuário resolver o captcha manualmente
    4. Clica em Consultar
    5. Navega até a aba Produtos/Serviços
    6. Extrai os dados da tabela
    
    Suporta navegadores: Chrome e Firefox
    """
    
    def __init__(self, headless: bool = False):
        """
        Inicializa o serviço de web scraping
        
        Args:
            headless: Se True, executa o navegador sem interface gráfica
        """
        self.headless = headless
        self.driver = None
        self.wait = None
    
    def iniciar_navegador(self):
        """Inicia o navegador Chrome com as configurações necessárias"""
        print("Iniciando navegador Chrome...")
        
        self._iniciar_chrome()
        
        # Configura timeout padrão
        self.wait = WebDriverWait(self.driver, settings.TIMEOUT_SEGUNDOS)
        
        print("SUCESSO: Navegador Chrome iniciado")
    
    def _iniciar_chrome(self):
        """Inicia o navegador Chrome"""
        options = webdriver.ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        # Configurações para melhor performance
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Desabilita notificações e popups
        options.add_argument('--disable-notifications')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # Usa o ChromeDriver instalado no sistema (via Homebrew)
        # Se não encontrar, o Selenium vai buscar automaticamente
        self.driver = webdriver.Chrome(options=options)
    
    def fechar_navegador(self):
        """Fecha o navegador e libera recursos"""
        if self.driver:
            self.driver.quit()
            print("Navegador fechado")
    
    def acessar_site(self):
        """Acessa o site da SEFAZ-SP"""
        print(f"Acessando {settings.URL_BASE}...")
        
        try:
            self.driver.get(settings.URL_BASE)
            print("SUCESSO: Site acessado")
            return True
        except Exception as e:
            print(f"ERRO ao acessar site: {str(e)}")
            return False
    
    def preencher_chave_acesso(self, chave: str):
        """
        Preenche o campo de chave de acesso
        
        Args:
            chave: Chave de acesso do cupom fiscal (44 dígitos)
        """
        print(f"Preenchendo chave de acesso: {chave}")
        
        try:
            # Aguarda o campo estar disponível
            campo_chave = self.wait.until(
                EC.presence_of_element_located((By.ID, "conteudo_txtChaveAcesso"))
            )
            
            # Limpa o campo e preenche
            campo_chave.clear()
            campo_chave.send_keys(chave)
            
            print("SUCESSO: Chave preenchida")
            return True
            
        except TimeoutException:
            print("ERRO: Timeout ao aguardar campo de chave")
            return False
        except Exception as e:
            print(f"ERRO ao preencher chave: {str(e)}")
            return False
    
    def aguardar_captcha_manual(self):
        """
        PAUSA o script para o usuário resolver o captcha manualmente
        
        O usuário deve:
        1. Resolver o captcha manualmente no navegador
        2. Pressionar ENTER no terminal para continuar
        """
        print("\n" + "="*70)
        print("ATENÇÃO: RESOLVA O CAPTCHA MANUALMENTE")
        print("="*70)
        print("\nPor favor:")
        print("1. Marque a caixa 'Não sou um robô'")
        print("2. Resolva o desafio do reCAPTCHA se aparecer")
        print("3. Aguarde a mensagem 'Sucesso na verificação do Captcha'")
        print("4. Pressione ENTER aqui no terminal para continuar")
        print("\n" + "="*70)
        
        input("\nPressione ENTER após resolver o captcha...")
        
        print("Continuando...")
        time.sleep(2)  # Pequena pausa para estabilizar
    
    def clicar_consultar(self):
        """Clica no botão Consultar"""
        print("Clicando em Consultar...")
        
        try:
            # Aguarda o botão estar clicável
            botao_consultar = self.wait.until(
                EC.element_to_be_clickable((By.ID, "conteudo_btnConsultar"))
            )
            
            botao_consultar.click()
            
            print("SUCESSO: Botão Consultar clicado")
            
            # Aguarda a página carregar
            time.sleep(3)
            return True
            
        except TimeoutException:
            print("ERRO: Timeout ao aguardar botão Consultar")
            return False
        except Exception as e:
            print(f"ERRO ao clicar em Consultar: {str(e)}")
            return False
    
    def clicar_detalhes(self):
        """
        Clica no botão Detalhes para acessar informações completas (incluindo NCM)
        
        IMPORTANTE: Este passo é OBRIGATÓRIO para ter acesso ao código NCM dos produtos
        """
        print("Clicando em Detalhes...")
        
        try:
            # Tenta múltiplos seletores
            botao_detalhes = None
            
            # Tentativa 1: Por ID
            try:
                botao_detalhes = self.wait.until(
                    EC.element_to_be_clickable((By.ID, "conteudo_btnDetalhes"))
                )
                print("Botão encontrado por ID")
            except:
                pass
            
            # Tentativa 2: Por valor do botão
            if not botao_detalhes:
                try:
                    botao_detalhes = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Detalhes']"))
                    )
                    print("Botão encontrado por valor")
                except:
                    pass
            
            # Tentativa 3: Por classe
            if not botao_detalhes:
                try:
                    # Procura todos os botões e pega o que tem texto "Detalhes"
                    botoes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='submit']")
                    for botao in botoes:
                        if botao.get_attribute('value') == 'Detalhes':
                            botao_detalhes = botao
                            print("Botão encontrado iterando pelos botões")
                            break
                except:
                    pass
            
            if not botao_detalhes:
                print("ERRO: Botão Detalhes não encontrado")
                return False
            
            # Scroll até o botão para garantir que está visível
            self.driver.execute_script("arguments[0].scrollIntoView(true);", botao_detalhes)
            time.sleep(1)
            
            # Clica no botão
            botao_detalhes.click()
            
            print("SUCESSO: Botão Detalhes clicado")
            time.sleep(3)  # Aguarda carregar
            return True
            
        except TimeoutException:
            print("ERRO: Timeout ao aguardar botão Detalhes")
            print("DICA: Verifique se o captcha foi resolvido corretamente")
            return False
        except Exception as e:
            print(f"ERRO ao clicar em Detalhes: {str(e)}")
            return False
    
    def clicar_aba_produtos(self):
        """
        Clica na aba Produtos/Serviços para ver tabela com NCM
        
        IMPORTANTE: Este passo é OBRIGATÓRIO para ter acesso ao código NCM dos produtos
        """
        print("Navegando para aba Produtos/Serviços...")
        
        try:
            # Aguarda a aba estar clicável
            aba_produtos = self.wait.until(
                EC.element_to_be_clickable((By.ID, "conteudo_tabProdutoServico"))
            )
            
            aba_produtos.click()
            
            print("SUCESSO: Aba Produtos/Serviços aberta")
            time.sleep(2)  # Aguarda tabela carregar
            return True
            
        except TimeoutException:
            print("ERRO: Timeout ao aguardar aba Produtos/Serviços")
            print("DICA: Verifique se chegou até a tela de detalhes")
            return False
        except Exception as e:
            print(f"ERRO ao clicar na aba Produtos: {str(e)}")
            return False
    
    def extrair_produtos(self) -> List[Produto]:
        """
        Extrai os produtos da tabela
        
        Returns:
            Lista de objetos Produto extraídos
        """
        print("Extraindo produtos da tabela...")
        
        produtos = []
        
        try:
            # Aguarda a tabela estar presente
            tabela = self.wait.until(
                EC.presence_of_element_located((By.ID, "conteudo_grvProdutosServicos"))
            )
            
            # Extrai todas as linhas da tabela (exceto cabeçalho)
            linhas = tabela.find_elements(By.TAG_NAME, "tr")[1:]  # Pula o header
            
            print(f"Encontradas {len(linhas)} linhas na tabela")
            
            for idx, linha in enumerate(linhas, 1):
                try:
                    # Extrai todas as células da linha
                    celulas = linha.find_elements(By.TAG_NAME, "td")
                    
                    # Extração usando IDs específicos dos elementos
                    # Índice da linha começa em 0
                    linha_idx = idx - 1
                    
                    try:
                        # NCM
                        ncm_element = self.driver.find_element(
                            By.ID, 
                            f"conteudo_grvProdutosServicos_lblProdutoServicoNcm_{linha_idx}"
                        )
                        codigo_ncm = ncm_element.text.strip()
                    except:
                        codigo_ncm = "00000000"
                        print(f"AVISO: NCM não encontrado para linha {idx}")
                    
                    try:
                        # Descrição
                        desc_element = self.driver.find_element(
                            By.ID,
                            f"conteudo_grvProdutosServicos_lblProdutoServicoDesc_{linha_idx}"
                        )
                        descricao = desc_element.text.strip()
                    except:
                        descricao = f"Produto {idx}"
                        print(f"AVISO: Descrição não encontrada para linha {idx}")
                    
                    try:
                        # Quantidade
                        qtd_element = self.driver.find_element(
                            By.ID,
                            f"conteudo_grvProdutosServicos_lblProdutoServicoQtd_{linha_idx}"
                        )
                        quantidade = qtd_element.text.strip()
                    except:
                        quantidade = "1,0000"
                        print(f"AVISO: Quantidade não encontrada para linha {idx}")
                    
                    try:
                        # Valor Líquido
                        valor_element = self.driver.find_element(
                            By.ID,
                            f"conteudo_grvProdutosServicos_lblProdutoServicoIcmsValorLiquidoItem_{linha_idx}"
                        )
                        valor_liquido = valor_element.text.strip()
                    except:
                        valor_liquido = "0,00"
                        print(f"AVISO: Valor líquido não encontrado para linha {idx}")
                    
                    # GTIN (não tem ID específico, vamos tentar pegar da primeira célula)
                    try:
                        cod_gtin = celulas[0].text.strip()
                        if not cod_gtin or cod_gtin == "Não Informado":
                            cod_gtin = None
                    except:
                        cod_gtin = None
                    
                    print(f"Produto {idx}: NCM={codigo_ncm}, Desc={descricao[:40]}, Qtd={quantidade}, Valor={valor_liquido}")
                    
                    # Cria o objeto Produto
                    produto = Produto(
                        codigo_ncm=codigo_ncm,
                        valor_liquido=valor_liquido,
                        cod_produto=codigo_ncm,  # Usando NCM como código
                        cod_gtin=cod_gtin,
                        valor_total=valor_liquido,  # Valor total = valor líquido
                        descricao=descricao,
                        quantidade=quantidade
                    )
                    
                    # Valida o produto
                    valido, erros = produto.validar()
                    
                    if valido:
                        produtos.append(produto)
                        print(f"Produto {idx}: {descricao[:30]}... - OK")
                    else:
                        print(f"AVISO: Produto {idx} inválido: {erros}")
                
                except Exception as e:
                    print(f"ERRO ao processar linha {idx}: {str(e)}")
                    continue
            
            print(f"\nSUCESSO: {len(produtos)} produtos extraídos")
            return produtos
            
        except TimeoutException:
            print("ERRO: Timeout ao aguardar tabela de produtos")
            return []
        except Exception as e:
            print(f"ERRO ao extrair produtos: {str(e)}")
            return []
    
    def extrair_dados_cupom(self, chave: str) -> Optional[List[Produto]]:
        """
        Fluxo completo: extrai dados de um cupom fiscal
        
        Args:
            chave: Chave de acesso do cupom (44 dígitos)
        
        Returns:
            Lista de produtos extraídos ou None em caso de erro
        """
        try:
            # 1. Inicia o navegador
            self.iniciar_navegador()
            
            # 2. Acessa o site
            if not self.acessar_site():
                return None
            
            # 3. Preenche a chave
            if not self.preencher_chave_acesso(chave):
                return None
            
            # 4. PAUSA para resolver captcha
            self.aguardar_captcha_manual()
            
            # 5. Clica em Consultar
            if not self.clicar_consultar():
                return None
            
            # 6. Clica em Detalhes (OBRIGATÓRIO para ver NCM)
            if not self.clicar_detalhes():
                print("ERRO: Não foi possível acessar a tela de detalhes")
                return None
            
            # 7. Clica na aba Produtos/Serviços (OBRIGATÓRIO para ver NCM)
            if not self.clicar_aba_produtos():
                print("ERRO: Não foi possível acessar a aba de produtos")
                return None
            
            # 8. Extrai os produtos com NCM
            produtos = self.extrair_produtos()
            
            if not produtos:
                print("AVISO: Nenhum produto foi extraído")
                return None
            
            return produtos
            
        except Exception as e:
            print(f"ERRO no fluxo de extração: {str(e)}")
            return None
        
        finally:
            # Sempre fecha o navegador
            self.fechar_navegador()