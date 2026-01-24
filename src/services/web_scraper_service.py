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
from src.config import campos_extracao
from src.models.produto import Produto
from src.models.emitente import Emitente
from src.models.consumidor import Consumidor
from src.models.cupom import Cupom
from src.models.local_entrega import LocalEntrega
from src.models.cupom_completo import CupomCompleto


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
    
    def extrair_emitente(self) -> Emitente:
        """
        Extrai dados do emitente (estabelecimento) da primeira tela
        
        Executa ANTES de clicar no botão Detalhes
        
        Returns:
            Objeto Emitente com os dados extraídos
        """
        print("Extraindo dados do emitente...")
        
        emitente = Emitente()
        config = campos_extracao.EXTRAIR_EMITENTE
        
        try:
            # IE
            if config.get('ie'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblIeEmitente")
                    emitente.ie = elem.text.strip()
                except:
                    pass
            
            # IM
            if config.get('im'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblImEmintente")
                    emitente.im = elem.text.strip()
                except:
                    pass
            
            # Extrato Número
            if config.get('extrato_numero'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblNumeroCfe")
                    emitente.extrato_numero = elem.text.strip()
                except:
                    pass
            
            # SAT Número
            if config.get('sat_numero'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblRazaoSocial")
                    emitente.sat_numero = elem.text.strip()
                except:
                    pass
            
            # Nome
            if config.get('nome'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblNomeEmitente")
                    emitente.nome = elem.text.strip()
                except:
                    pass
            
            # CNPJ
            if config.get('cnpj'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblCnpjEmitente")
                    emitente.cnpj = elem.text.strip()
                except:
                    pass
            
            # Endereço
            if config.get('endereco'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblEnderecoEmintente")
                    emitente.endereco = elem.text.strip()
                except:
                    pass
            
            # Bairro
            if config.get('bairro'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblBairroEmitente")
                    emitente.bairro = elem.text.strip()
                except:
                    pass
            
            # CEP
            if config.get('cep'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblCepEmitente")
                    emitente.cep = elem.text.strip()
                except:
                    pass
            
            # UF
            if config.get('uf'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblMunicipioEmitente")
                    emitente.uf = elem.text.strip()
                except:
                    pass
            
            print(f"SUCESSO: Dados do emitente extraídos - {emitente.nome}")
            return emitente
            
        except Exception as e:
            print(f"ERRO ao extrair dados do emitente: {str(e)}")
            return emitente
    
    def extrair_consumidor(self) -> Optional[Consumidor]:
        """
        Extrai dados do consumidor da primeira tela
        
        Executa ANTES de clicar no botão Detalhes
        
        Returns:
            Objeto Consumidor ou None se não configurado/não encontrado
        """
        config = campos_extracao.EXTRAIR_CONSUMIDOR
        
        if not config.get('ativo'):
            return None
        
        print("Extraindo dados do consumidor...")
        
        consumidor = Consumidor()
        
        try:
            # CPF/CNPJ
            if config.get('cpf_cnpj'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblCpfConsumidor")
                    consumidor.cpf_cnpj = elem.text.strip()
                except:
                    pass
            
            # Nome / Razão Social
            if config.get('nome'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblRazaoSocial")
                    consumidor.nome = elem.text.strip()
                except:
                    pass
            
            if consumidor.esta_presente():
                print(f"SUCESSO: Dados do consumidor extraídos - {consumidor.nome}")
                return consumidor
            else:
                print("INFO: Consumidor não identificado no cupom")
                return None
            
        except Exception as e:
            print(f"AVISO ao extrair dados do consumidor: {str(e)}")
            return None
    
    def extrair_cupom(self) -> Cupom:
        """
        Extrai dados gerais do cupom da primeira tela
        
        Executa ANTES de clicar no botão Detalhes
        
        Returns:
            Objeto Cupom com os dados extraídos
        """
        print("Extraindo dados do cupom...")
        
        cupom = Cupom()
        config = campos_extracao.EXTRAIR_CUPOM
        
        try:
            # Total
            if config.get('total'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblTotal")
                    cupom.total = elem.text.strip()
                except:
                    pass
            
            # Forma de Pagamento
            if config.get('forma_pagamento'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_DivMeiosPagamento")
                    cupom.forma_pagamento = elem.text.strip()
                except:
                    pass
            
            # Troco
            if config.get('troco'):
                try:
                    elem = self.driver.find_element(By.ID, "CupomDetalhe2")
                    cupom.troco = elem.text.strip()
                except:
                    pass
            
            # Tributos
            if config.get('tributos'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblTotal12741")
                    cupom.tributos = elem.text.strip()
                except:
                    pass
            
            # Data e Hora
            if config.get('data_hora'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblDataEmissao")
                    cupom.data_hora = elem.text.strip()
                except:
                    pass
            
            # QR Code
            if config.get('qr_code'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblIdCfe")
                    cupom.qr_code = elem.text.strip()
                except:
                    pass
            
            print(f"SUCESSO: Dados do cupom extraídos - Total: {cupom.total}")
            return cupom
            
        except Exception as e:
            print(f"ERRO ao extrair dados do cupom: {str(e)}")
            return cupom
    
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
    
    def clicar_aba_local_entrega(self) -> bool:
        """
        Clica na aba "Local de Entrega" (se existir)
        
        Returns:
            True se clicou com sucesso, False se não encontrou
        """
        print("Verificando aba Local de Entrega...")
        
        try:
            # Aguarda menos tempo (5 segundos)
            wait_curto = WebDriverWait(self.driver, 5)
            
            aba_local = wait_curto.until(
                EC.element_to_be_clickable((By.ID, "conteudo_tabEmissao"))
            )
            
            aba_local.click()
            print("SUCESSO: Aba Local de Entrega clicada")
            time.sleep(2)
            return True
            
        except TimeoutException:
            print("INFO: Aba Local de Entrega não encontrada")
            return False
        except Exception as e:
            print(f"AVISO: Erro ao clicar em Local de Entrega: {str(e)}")
            return False
    
    def extrair_local_entrega(self) -> Optional[LocalEntrega]:
        """
        Extrai dados do local de entrega (se existir)
        
        Executa DEPOIS de clicar no botão Detalhes, na aba "Local de Entrega"
        
        Returns:
            Objeto LocalEntrega ou None se não configurado/não encontrado
        """
        config = campos_extracao.EXTRAIR_LOCAL_ENTREGA
        
        if not config.get('ativo'):
            return None
        
        # Tenta clicar na aba
        if not self.clicar_aba_local_entrega():
            return None
        
        print("Extraindo dados do local de entrega...")
        
        local = LocalEntrega()
        
        try:
            # Endereço
            if config.get('endereco'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblDadosLocalEntregaEndereco")
                    local.endereco = elem.text.strip()
                except:
                    pass
            
            # Bairro
            if config.get('bairro'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblDadosLocalEntregaBairro")
                    local.bairro = elem.text.strip()
                except:
                    pass
            
            # Município
            if config.get('municipio'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblDadosLocalEntregaMunicipio")
                    local.municipio = elem.text.strip()
                except:
                    pass
            
            # UF
            if config.get('uf'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblDadosLocalEntregaUF")
                    local.uf = elem.text.strip()
                except:
                    pass
            
            # Número CF-e
            if config.get('numero_cfe'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblCfeNumero")
                    local.numero_cfe = elem.text.strip()
                except:
                    pass
            
            # Chave de Acesso
            if config.get('chave_acesso'):
                try:
                    elem = self.driver.find_element(By.ID, "conteudo_lblChaveAcesso")
                    local.chave_acesso = elem.text.strip()
                except:
                    pass
            
            if local.esta_presente():
                print(f"SUCESSO: Local de entrega encontrado - {local.municipio}/{local.uf}")
                return local
            else:
                print("INFO: Local de entrega não preenchido")
                return None
            
        except Exception as e:
            print(f"AVISO ao extrair local de entrega: {str(e)}")
            return None
    
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
    
    def extrair_dados_cupom(self, chave: str) -> Optional[CupomCompleto]:
        """
        Fluxo completo: extrai TODOS os dados de um cupom fiscal
        
        Args:
            chave: Chave de acesso do cupom (44 dígitos)
        
        Returns:
            CupomCompleto com todos os dados ou None em caso de erro
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
            
            # 6. Extrai dados da PRIMEIRA TELA (antes de clicar Detalhes)
            print("\n" + "="*70)
            print("EXTRAINDO DADOS DA PRIMEIRA TELA")
            print("="*70)
            
            emitente = self.extrair_emitente()
            consumidor = self.extrair_consumidor()
            cupom = self.extrair_cupom()
            
            # 7. Clica em Detalhes (para acessar abas)
            if not self.clicar_detalhes():
                print("ERRO: Não foi possível acessar a tela de detalhes")
                return None
            
            # 8. Extrai Local de Entrega (se configurado)
            print("\n" + "="*70)
            print("EXTRAINDO LOCAL DE ENTREGA")
            print("="*70)
            
            local_entrega = self.extrair_local_entrega()
            
            # 9. Clica na aba Produtos/Serviços
            print("\n" + "="*70)
            print("EXTRAINDO PRODUTOS")
            print("="*70)
            
            if not self.clicar_aba_produtos():
                print("ERRO: Não foi possível acessar a aba de produtos")
                return None
            
            # 10. Extrai os produtos
            config_produtos = campos_extracao.EXTRAIR_PRODUTOS
            
            if not config_produtos.get('ativo'):
                print("INFO: Extração de produtos desativada na configuração")
                produtos = []
            else:
                produtos = self.extrair_produtos()
                
                if not produtos:
                    print("AVISO: Nenhum produto foi extraído")
            
            # 11. Monta o objeto completo
            cupom_completo = CupomCompleto(
                emitente=emitente,
                consumidor=consumidor,
                cupom=cupom,
                local_entrega=local_entrega,
                produtos=produtos
            )
            
            print("\n" + "="*70)
            print("EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("="*70)
            print(cupom_completo)
            
            return cupom_completo
            
        except Exception as e:
            print(f"\nERRO no fluxo de extração: {str(e)}")
            return None
        
        finally:
            # Sempre fecha o navegador
            self.fechar_navegador()