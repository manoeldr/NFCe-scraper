import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (se existir)
load_dotenv()

# DIRETÓRIOS
BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / 'output'
TEMP_DIR = BASE_DIR / 'temp'
LOGS_DIR = BASE_DIR / 'logs'

# Cria diretórios se não existirem
OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# URLs
SEFAZ_SP_URL = "https://satsp.fazenda.sp.gov.br/COMSAT/Public/ConsultaPublica/ConsultaPublicaCfe.aspx"

# SELENIUM / BROWSER
# Modo headless (True = sem interface gráfica, False = mostra navegador)
HEADLESS_MODE = os.getenv('HEADLESS_MODE', 'False').lower() == 'true'

# Tempo de espera implícito para elementos (segundos)
IMPLICIT_WAIT = int(os.getenv('IMPLICIT_WAIT', '10'))

# Tempo máximo para carregar página (segundos)
PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))

# Tempo máximo para resolver captcha (segundos)
CAPTCHA_TIMEOUT = int(os.getenv('CAPTCHA_TIMEOUT', '300'))  # 5 minutos

# User Agent customizado (opcional)
USER_AGENT = os.getenv('USER_AGENT', None)

# EXPORTAÇÃO
# Formato padrão de data/hora para nomes de arquivo
DATETIME_FORMAT = "%Y%m%d_%H%M%S"

# Separador CSV
CSV_SEPARATOR = ';'

# Decimal CSV
CSV_DECIMAL = ','

# Encoding dos arquivos
FILE_ENCODING = 'utf-8-sig'  # UTF-8 com BOM (compatível com Excel)

# LOGGING
# Nível de log: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Formato do log
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# SELETORES HTML (ajuste conforme necessário)
# IDs e seletores do site da SEFAZ-SP
# IMPORTANTE: Estes podem mudar se o site for atualizado
SELETORES = {
    'campo_chave_acesso': 'ctl00_ContentPlaceHolder1_txtChaveAcesso',
    'botao_consultar': 'ctl00_ContentPlaceHolder1_btnConsultar',
    'link_detalhes': 'Detalhes',
    'link_produtos': 'Produtos e Serviços',
}

# VALIDAÇÕES
# Tamanho da chave de acesso (dígitos)
TAMANHO_CHAVE_ACESSO = 44

# RETRY / TENTATIVAS
# Número máximo de tentativas para operações que podem falhar
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))

# Tempo de espera entre tentativas (segundos)
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '5'))