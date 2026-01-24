"""
Configuração de quais campos extrair do cupom fiscal

Altere True/False para ativar/desativar a extração de cada campo.
Campos desativados retornarão "N/A" ou None.
"""

# ============================================================
# EMITENTE (Estabelecimento comercial)
# ============================================================
EXTRAIR_EMITENTE = {
    'ie': True,                    # Inscrição Estadual
    'im': True,                    # Inscrição Municipal
    'extrato_numero': True,        # Número do extrato
    'sat_numero': True,            # Número do SAT
    'nome': True,                  # Nome do estabelecimento
    'cnpj': True,                  # CNPJ
    'endereco': True,              # Endereço completo
    'bairro': True,                # Bairro
    'cep': True,                   # CEP
    'uf': True,                    # UF (estado)
}

# ============================================================
# CONSUMIDOR (Destinatário / Cliente)
# ============================================================
EXTRAIR_CONSUMIDOR = {
    'ativo': True,                 # Se False, ignora toda extração de consumidor
    'cpf_cnpj': True,              # CPF ou CNPJ do consumidor
    'nome': True,                  # Nome / Razão Social
}

# ============================================================
# CUPOM (Dados gerais da venda)
# ============================================================
EXTRAIR_CUPOM = {
    'total': True,                 # Valor total da compra
    'forma_pagamento': True,       # Forma de pagamento
    'troco': True,                 # Valor do troco
    'tributos': True,              # Valor aproximado de tributos
    'data_hora': True,             # Data e hora da emissão
    'qr_code': True,               # Dados do QR Code
}

# ============================================================
# LOCAL DE ENTREGA (Opcional - nem sempre existe)
# ============================================================
EXTRAIR_LOCAL_ENTREGA = {
    'ativo': True,                 # Se False, não tenta nem abrir a aba
    'endereco': True,              # Endereço de entrega
    'bairro': True,                # Bairro / Distrito
    'municipio': True,             # Município
    'uf': True,                    # UF (estado)
    'numero_cfe': True,            # Número da CF-e
    'chave_acesso': True,          # Chave de acesso
}

# ============================================================
# PRODUTOS (Lista de itens comprados)
# ============================================================
EXTRAIR_PRODUTOS = {
    'ativo': True,                 # Se False, não extrai produtos
    'ncm': True,                   # Código NCM
    'descricao': True,             # Descrição do produto
    'quantidade': True,            # Quantidade comercial
    'valor_liquido': True,         # Valor líquido do item
}