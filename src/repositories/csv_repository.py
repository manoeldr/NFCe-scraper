"""
Repositório para salvar dados em formato CSV
"""
import csv
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.config import settings
from src.models.cupom_completo import CupomCompleto


class CSVRepository:
    """
    Repositório para salvar cupons fiscais em formato CSV
    
    Gera arquivo CSV com todos os dados do cupom:
    - Emitente
    - Consumidor  
    - Cupom
    - Local de Entrega
    - Produtos (uma linha por produto)
    """
    
    def __init__(self, diretorio: Optional[Path] = None):
        """
        Inicializa o repositório CSV
        
        Args:
            diretorio: Diretório onde salvar os arquivos (padrão: settings.OUTPUT_DIR)
        """
        self.diretorio = diretorio or settings.OUTPUT_DIR
        self.diretorio.mkdir(exist_ok=True, parents=True)
    
    def salvar(self, cupom: CupomCompleto, nome_arquivo: Optional[str] = None) -> Path:
        """
        Salva um cupom completo em arquivo CSV
        
        Args:
            cupom: Objeto CupomCompleto com todos os dados
            nome_arquivo: Nome customizado do arquivo (opcional)
        
        Returns:
            Path do arquivo salvo
        """
        # Gera nome do arquivo se não fornecido
        if not nome_arquivo:
            timestamp = datetime.now().strftime(settings.DATETIME_FORMAT)
            cnpj_limpo = cupom.emitente.cnpj.replace('.', '').replace('/', '').replace('-', '') if cupom.emitente.cnpj else 'sem_cnpj'
            nome_arquivo = f"cupom_{cnpj_limpo}_{timestamp}.csv"
        
        # Garante extensão .csv
        if not nome_arquivo.endswith('.csv'):
            nome_arquivo += '.csv'
        
        caminho = self.diretorio / nome_arquivo
        
        # Escreve o CSV
        with open(caminho, 'w', newline='', encoding=settings.FILE_ENCODING) as arquivo:
            writer = csv.writer(
                arquivo, 
                delimiter=settings.CSV_SEPARATOR,
                quoting=csv.QUOTE_MINIMAL
            )
            
            # Cabeçalho
            writer.writerow(self._gerar_cabecalho())
            
            # Dados
            for linha in self._gerar_linhas(cupom):
                writer.writerow(linha)
        
        print(f"SUCESSO: Arquivo CSV salvo em {caminho}")
        return caminho
    
    def _gerar_cabecalho(self) -> list:
        """
        Gera o cabeçalho do CSV
        
        Returns:
            Lista com nomes das colunas
        """
        return [
            # Emitente
            'Emitente_Nome',
            'Emitente_CNPJ',
            'Emitente_IE',
            'Emitente_IM',
            'Emitente_Endereco',
            'Emitente_Bairro',
            'Emitente_CEP',
            'Emitente_UF',
            'Emitente_Extrato_Numero',
            'Emitente_SAT_Numero',
            
            # Consumidor
            'Consumidor_Nome',
            'Consumidor_CPF_CNPJ',
            
            # Cupom
            'Cupom_Total',
            'Cupom_Data_Hora',
            'Cupom_Forma_Pagamento',
            'Cupom_Troco',
            'Cupom_Tributos',
            'Cupom_QR_Code',
            
            # Local de Entrega
            'Entrega_Endereco',
            'Entrega_Bairro',
            'Entrega_Municipio',
            'Entrega_UF',
            'Entrega_Numero_CFe',
            'Entrega_Chave_Acesso',
            
            # Produto
            'Produto_Descricao',
            'Produto_NCM',
            'Produto_Quantidade',
            'Produto_Valor_Liquido',
            'Produto_Valor_Total',
            'Produto_Cod_GTIN',
        ]
    
    def _gerar_linhas(self, cupom: CupomCompleto) -> list:
        """
        Gera as linhas de dados do CSV
        
        Cada produto gera uma linha, repetindo dados de emitente/consumidor/cupom
        
        Args:
            cupom: Objeto CupomCompleto
        
        Returns:
            Lista de listas (cada sublista é uma linha)
        """
        linhas = []
        
        # Se não tem produtos, gera uma linha só com dados gerais
        if not cupom.produtos:
            linhas.append(self._gerar_linha_base(cupom, None))
            return linhas
        
        # Uma linha por produto
        for produto in cupom.produtos:
            linha = self._gerar_linha_base(cupom, produto)
            linhas.append(linha)
        
        return linhas
    
    def _gerar_linha_base(self, cupom: CupomCompleto, produto=None) -> list:
        """
        Gera uma linha base com todos os dados
        
        Args:
            cupom: CupomCompleto
            produto: Produto individual (opcional)
        
        Returns:
            Lista com valores da linha
        """
        # Emitente
        linha = [
            cupom.emitente.nome or 'N/A',
            cupom.emitente.cnpj or 'N/A',
            cupom.emitente.ie or 'N/A',
            cupom.emitente.im or 'N/A',
            cupom.emitente.endereco or 'N/A',
            cupom.emitente.bairro or 'N/A',
            cupom.emitente.cep or 'N/A',
            cupom.emitente.uf or 'N/A',
            cupom.emitente.extrato_numero or 'N/A',
            cupom.emitente.sat_numero or 'N/A',
        ]
        
        # Consumidor
        if cupom.consumidor and cupom.consumidor.esta_presente():
            linha.extend([
                cupom.consumidor.nome or 'N/A',
                cupom.consumidor.cpf_cnpj or 'N/A',
            ])
        else:
            linha.extend(['N/A', 'N/A'])
        
        # Cupom
        linha.extend([
            cupom.cupom.total or 'N/A',
            cupom.cupom.data_hora or 'N/A',
            cupom.cupom.forma_pagamento or 'N/A',
            cupom.cupom.troco or 'N/A',
            cupom.cupom.tributos or 'N/A',
            cupom.cupom.qr_code or 'N/A',
        ])
        
        # Local de Entrega
        if cupom.local_entrega and cupom.local_entrega.esta_presente():
            linha.extend([
                cupom.local_entrega.endereco or 'N/A',
                cupom.local_entrega.bairro or 'N/A',
                cupom.local_entrega.municipio or 'N/A',
                cupom.local_entrega.uf or 'N/A',
                cupom.local_entrega.numero_cfe or 'N/A',
                cupom.local_entrega.chave_acesso or 'N/A',
            ])
        else:
            linha.extend(['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'])
        
        # Produto
        if produto:
            linha.extend([
                produto.descricao or 'N/A',
                produto.codigo_ncm or 'N/A',
                produto.quantidade or 'N/A',
                produto.valor_liquido or 'N/A',
                produto.valor_total or 'N/A',
                produto.cod_gtin or 'N/A',
            ])
        else:
            linha.extend(['N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'])
        
        return linha