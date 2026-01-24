# 🧾 NFe Scraper - Extrator de Cupons Fiscais SEFAZ-SP

Sistema automatizado para extrair dados completos de cupons fiscais eletrônicos (SAT-CF-e) do site da Secretaria da Fazenda de São Paulo.

## 📋 Funcionalidades

- ✅ Leitura de QR Codes de cupons fiscais
- ✅ Validação de chaves de acesso (44 dígitos)
- ✅ Extração completa de dados via web scraping (30 campos)
- ✅ Resolução manual de captcha (seguro e confiável)
- ✅ Exportação para CSV (formato brasileiro)
- ✅ Processamento individual ou em lote
- ✅ Interface CLI interativa
- ✅ Configuração flexível de campos a extrair
- ✅ Arquitetura limpa e modular
- ✅ 70+ testes unitários

## 🏗️ Arquitetura

```
nfe_scraper/
├── src/
│   ├── controllers/       # CupomController - Orquestração
│   ├── services/          # QRCodeService, WebScraperService
│   ├── repositories/      # CSVRepository - Persistência
│   ├── models/            # Emitente, Consumidor, Cupom, Produto, etc
│   └── config/            # settings.py, campos_extracao.py
├── tests/                 # 70+ testes unitários (pytest)
├── output/                # Arquivos CSV gerados
└── main.py                # CLI interativo
```

## 📦 Instalação

### 1. Clone ou baixe o projeto

```bash
cd nfe_scraper
```

### 2. Instale dependências do sistema

**macOS:**
```bash
brew install zbar
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libzbar0
```

**Windows:**
Baixe o instalador do zbar em: https://sourceforge.net/projects/zbar/files/

### 3. Instale o Google Chrome

O projeto usa Selenium com Chrome para web scraping.

**Download:** https://www.google.com/chrome/

**Nota:** O ChromeDriver será instalado automaticamente na primeira execução via `webdriver-manager`.

### 4. Crie um ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 5. Instale as dependências Python

```bash
pip install -r requirements.txt
```

### 6. Configure as variáveis de ambiente (opcional)

## 🚀 Como Usar

### Opção 1: Menu Interativo (Recomendado)

```bash
python main.py
```

O sistema apresentará um menu com 4 opções:

```
1. Processar cupom individual
2. Processar múltiplos cupons (lote)
3. Validar chave de acesso
4. Sair
```

**Exemplo de uso:**
1. Escolha opção `1`
2. Digite ou cole a chave de acesso (pode ter espaços/hífens)
3. Escolha se quer salvar em CSV
4. Resolva o captcha quando o navegador abrir
5. Aguarde a extração
6. Pronto! Arquivo CSV salvo em `output/`

### Opção 2: Uso Programático

```python
from src.controllers.cupom_controller import CupomController

# Cria controller
controller = CupomController()

# Processa um cupom
sucesso, cupom, arquivo, mensagem = controller.processar_cupom(
    entrada="3525 1262 2173 9300 0147 5900 0547 0673 1417 1832 7383",
    salvar_csv=True
)

if sucesso:
    print(f"Arquivo salvo: {arquivo}")
    print(f"Total de produtos: {len(cupom.produtos)}")
```

### Opção 3: Processamento em Lote

**Via CLI:**
```bash
python main.py
# Escolha opção 2
# Opção 1: Digite chaves manualmente
# Opção 2: Leia de arquivo .txt
```

**Via código:**
```python
chaves = [
    "35201214987685002755590004202070561364493478",
    "35251262217393000147590005470673141718327383"
]

resultados = controller.processar_multiplos_cupons(
    chaves,
    salvar_csv=True
)

print(f"Sucesso: {resultados['sucesso']}/{resultados['total']}")
```

## 🔐 Resolução do Captcha

Durante a execução, o navegador Chrome será aberto automaticamente. Quando o captcha aparecer:

1. ⏸️ O script pausará e exibirá uma mensagem
2. 🖱️ Resolva o captcha manualmente no navegador
3. ⏎ Pressione ENTER no terminal para continuar

**Atenção:** O script aguardará até 5 minutos para resolução do captcha.

## 📊 Dados Extraídos

O sistema extrai **30 campos** organizados em 5 categorias:

### 🏢 Emitente (Estabelecimento)
- Nome, CNPJ, IE, IM
- Endereço, Bairro, CEP, UF
- Número do Extrato, Número do SAT

### 👤 Consumidor (Opcional)
- Nome / Razão Social
- CPF/CNPJ (censurado pelo SEFAZ)

### 🧾 Cupom (Dados Gerais)
- Valor Total
- Data e Hora de Emissão
- Forma de Pagamento
- Troco
- Valor Aproximado de Tributos
- Dados do QR Code

### 📦 Local de Entrega (Opcional)
- Endereço completo
- Bairro, Município, UF
- Número da CF-e
- Chave de Acesso

### 🛒 Produtos (Lista Completa)
- **Código NCM** - Nomenclatura Comum do Mercosul (8 dígitos)
- **Descrição** - Nome do produto
- **Quantidade** - Quantidade comercial
- **Valor Líquido** - Valor unitário
- **Valor Total** - Valor total do item
- **Código GTIN** - Código de barras (EAN)

**Configurável:** Você pode escolher quais campos extrair editando `src/config/campos_extracao.py`

## 📁 Formato dos Arquivos

### CSV (Formato Brasileiro)

O arquivo CSV gerado contém **30 colunas** com todos os dados extraídos:

```csv
Emitente_Nome;Emitente_CNPJ;Emitente_IE;...;Produto_NCM;Produto_Descricao;Produto_GTIN
LOJA EXEMPLO;12.345.678/0001-90;123456789;...;12345678;PRODUTO TESTE;7891234567890
```

**Características:**
- Separador: `;` (ponto e vírgula)
- Decimal: `,` (vírgula brasileira)
- Encoding: UTF-8 com BOM (abre corretamente no Excel)
- Uma linha por produto (dados gerais repetidos)
- Nome automático: `cupom_[CNPJ]_[timestamp].csv`

**Localização:** Arquivos salvos em `output/`

**Campos N/A:** Quando um campo não está disponível, aparece como "N/A"

## ⚙️ Configurações

### Settings.py

Edite `src/config/settings.py` para personalizar:

```python
HEADLESS_MODE = False        # True para modo headless (sem interface)
IMPLICIT_WAIT = 10           # Tempo de espera padrão (segundos)
CAPTCHA_TIMEOUT = 300        # Timeout para captcha (segundos)
```

### Campos de Extração

Edite `src/config/campos_extracao.py` para escolher quais campos extrair:

```python
# Emitente (Estabelecimento)
EXTRAIR_EMITENTE = {
    'nome': True,           # Nome do estabelecimento
    'cnpj': True,           # CNPJ
    'ie': True,             # Inscrição Estadual
    'im': True,             # Inscrição Municipal
    'endereco': True,       # Endereço completo
    'bairro': True,         # Bairro
    'cep': True,            # CEP
    'uf': True,             # Estado
    'extrato_numero': False,  # Número do extrato (desabilitado)
    'sat_numero': False       # Número do SAT (desabilitado)
}

# Consumidor (Cliente)
EXTRAIR_CONSUMIDOR = {
    'ativo': True,          # Ativa/desativa extração de consumidor
    'cpf_cnpj': True,       # CPF/CNPJ
    'nome': True            # Nome do consumidor
}

# Cupom (Dados gerais)
EXTRAIR_CUPOM = {
    'total': True,          # Valor total
    'data_hora': True,      # Data e hora de emissão
    'forma_pagamento': True, # Forma de pagamento
    'troco': True,          # Valor do troco
    'tributos': True,       # Valor aproximado de tributos
    'qr_code': True         # Dados do QR Code
}

# Local de Entrega
EXTRAIR_LOCAL_ENTREGA = {
    'ativo': True,          # Ativa/desativa extração
    'endereco': True,
    'bairro': True,
    'municipio': True,
    'uf': True,
    'numero_cfe': True,
    'chave_acesso': True
}

# Produtos
EXTRAIR_PRODUTOS = {
    'ativo': True,          # Ativa/desativa extração
    'ncm': True,            # Código NCM
    'descricao': True,      # Descrição do produto
    'quantidade': True,     # Quantidade
    'valor_liquido': True,  # Valor unitário
    'gtin': True            # Código de barras (GTIN/EAN)
}
```

**Exemplo:** Para extrair apenas dados essenciais, desabilite campos opcionais:

```python
EXTRAIR_EMITENTE = {
    'nome': True,
    'cnpj': True,
    'ie': False,           # Desabilitado
    'im': False,           # Desabilitado
    # ...
}
```

Campos desabilitados aparecerão como "N/A" no CSV.

## 🧪 Testes

```bash
pytest tests/
```

## 🔧 Troubleshooting

### Erro: "Unable to find zbar shared library"

**Causa:** A biblioteca zbar não está instalada no sistema.

**Solução:**

**macOS:**
```bash
brew install zbar
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libzbar0
```

**Windows:**
1. Baixe o instalador: https://sourceforge.net/projects/zbar/files/
2. Instale seguindo o assistente
3. Adicione o diretório de instalação ao PATH

Depois reinstale o pyzbar:
```bash
pip uninstall pyzbar
pip install pyzbar
```

### Erro: Campo não encontrado

Se o script não encontrar elementos na página, pode ser que a estrutura do site mudou. 

**Solução:** Ajuste os seletores em `web_scraper_service.py`:

```python
# Exemplo: alterar ID do campo
campo_chave = self.driver.find_element(
    By.ID, 
    "NOVO_ID_DO_CAMPO"  # Inspecione a página para encontrar
)
```

### ChromeDriver não funciona

**Solução:** Atualize o webdriver-manager:

```bash
pip install --upgrade webdriver-manager
```

### Captcha não aparece

Verifique se está acessando o site correto e se sua conexão está estável.

## 📝 Notas Importantes

- ✅ **Legal:** Este scraper respeita os termos de uso do site público da SEFAZ
- 🔐 **Segurança:** Resolução manual do captcha evita problemas legais
- 🚫 **Limitações:** Não funciona para consultas em massa comerciais
- 📞 **Alternativa:** Para uso empresarial, considere a API oficial da SEFAZ

## 🤝 Contribuindo

Melhorias são bem-vindas! Siga o padrão de código:

- Clean Architecture
- Type hints
- Docstrings em português
- Testes unitários com pytest

## 📄 Licença

Este projeto é fornecido como está, para uso educacional e pessoal.

## 👤 Autor

Desenvolvido seguindo princípios de código limpo e arquitetura modular.

---

**Dúvidas?** Consulte os exemplos em `main.py` ou abra uma issue.