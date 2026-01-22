# 🧾 NFe Scraper - Extrator de Cupons Fiscais SEFAZ-SP

Sistema automatizado para extrair dados de cupons fiscais eletrônicos (SAT) do site da Secretaria da Fazenda de São Paulo.

## 📋 Funcionalidades

- ✅ Leitura de QR Codes de cupons fiscais
- ✅ Extração automática de dados via web scraping
- ✅ Resolução manual de captcha (seguro e confiável)
- ✅ Exportação para CSV e XML
- ✅ Processamento de múltiplos cupons
- ✅ Arquitetura limpa e modular

## 🏗️ Arquitetura

```
nfe_scraper/
├── src/
│   ├── controllers/       # Orquestração do fluxo
│   ├── services/          # Lógica de negócio
│   ├── repositories/      # Persistência de dados
│   ├── models/            # Modelos de dados
│   └── config/            # Configurações
├── tests/                 # Testes unitários
├── output/                # Arquivos gerados (CSV/XML)
└── main.py               # Script principal
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

### Opção 1: Menu Interativo

```bash
python main.py
```

Siga as instruções no menu para escolher o modo de processamento.

### Opção 2: Por QR Code

```python
from src.controllers.scraper_controller import ScraperController

controller = ScraperController()
produtos = controller.processar_cupom_por_qrcode(
    caminho_imagem="qrcode.png",
    salvar_csv=True,
    salvar_xml=True
)
```

### Opção 3: Por Chave de Acesso

```python
controller = ScraperController()
produtos = controller.processar_cupom_por_chave(
    chave_acesso="12345678901234567890123456789012345678901234",
    salvar_csv=True,
    salvar_xml=True
)
```

### Opção 4: Múltiplos Cupons

```python
chaves = [
    "chave1_44digitos",
    "chave2_44digitos",
    "chave3_44digitos"
]

resultados = controller.processar_multiplos_cupons(
    chaves,
    salvar_csv=True,
    salvar_xml=True
)
```

## 🔐 Resolução do Captcha

Durante a execução, o navegador Chrome será aberto automaticamente. Quando o captcha aparecer:

1. ⏸️ O script pausará e exibirá uma mensagem
2. 🖱️ Resolva o captcha manualmente no navegador
3. ⏎ Pressione ENTER no terminal para continuar

**Atenção:** O script aguardará até 5 minutos para resolução do captcha.

## 📊 Dados Extraídos

Para cada produto do cupom fiscal, são extraídos:

- **Código NCM** - Nomenclatura Comum do Mercosul
- **Valor Líquido** - Valor sem impostos
- **Código do Produto** - Identificador interno
- **Código GTIN** - Código de barras internacional
- **Valor Total** - Valor final com impostos

## 📁 Formato dos Arquivos

### CSV

```csv
Codigo_NCM;Valor_Liquido;Cod_Produto;Cod_GTIN;Valor_Total
12345678;10,50;PROD001;7891234567890;12,00
```

- Separador: `;` (ponto e vírgula)
- Decimal: `,` (vírgula)
- Encoding: UTF-8 com BOM (compatível com Excel)

### XML

```xml
<?xml version='1.0' encoding='UTF-8'?>
<CupomFiscal>
  <Metadados>
    <ChaveAcesso>12345...</ChaveAcesso>
    <DataExtracao>2026-01-19T20:30:00</DataExtracao>
  </Metadados>
  <Produtos>
    <Produto id="1">
      <CodigoNCM>12345678</CodigoNCM>
      <ValorLiquido>10.50</ValorLiquido>
      <CodigoProduto>PROD001</CodigoProduto>
      <CodigoGTIN>7891234567890</CodigoGTIN>
      <ValorTotal>12.00</ValorTotal>
    </Produto>
  </Produtos>
</CupomFiscal>
```

## ⚙️ Configurações

Edite `src/config/settings.py` para personalizar:

```python
HEADLESS_MODE = False        # True para modo headless (sem interface)
IMPLICIT_WAIT = 10           # Tempo de espera padrão (segundos)
CAPTCHA_TIMEOUT = 300        # Timeout para captcha (segundos)
```

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