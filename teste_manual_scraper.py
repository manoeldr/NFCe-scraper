"""
Teste manual INTERATIVO do Web Scraper Service

Execute este arquivo para testar o scraper com uma chave REAL:
    python teste_manual_scraper.py

IMPORTANTE: Este não é um teste automatizado!
Você precisará resolver o captcha manualmente.
"""
from src.services.web_scraper_service import WebScraperService
from src.services.qrcode_service import QRCodeService
from src.repositories.csv_repository import CSVRepository


def main():
    print("=" * 70)
    print("TESTE MANUAL DO WEB SCRAPER - SEFAZ-SP")
    print("=" * 70)
    print()
    
    # Pede a chave ao usuário
    print("Digite a chave de acesso do cupom fiscal:")
    print("(Pode ser com espaços, hífens, etc - será limpa automaticamente)")
    entrada = input("Chave: ").strip()
    
    if not entrada:
        print("ERRO: Nenhuma chave fornecida")
        return
    
    # Processa e valida a chave
    qrcode_service = QRCodeService()
    chave = qrcode_service.processar_entrada(entrada)
    
    if not chave:
        print("ERRO: Chave inválida")
        return
    
    print(f"\nChave validada: {chave}")
    print()
    
    # Pergunta se quer continuar
    confirmar = input("Deseja iniciar o scraping? (s/n): ").lower()
    
    if confirmar != 's':
        print("Operação cancelada")
        return
    
    print("\nIniciando web scraper...")
    print("O Chrome será aberto automaticamente...")
    print()
    
    # Cria o scraper (headless=False para ver o navegador)
    scraper = WebScraperService(headless=False)
    
    # Executa o fluxo completo
    cupom_completo = scraper.extrair_dados_cupom(chave)
    
    # Exibe os resultados
    print("\n" + "=" * 70)
    print("RESULTADOS DA EXTRAÇÃO")
    print("=" * 70)
    
    if cupom_completo:
        print("\nSUCESSO! Dados extraídos com sucesso!\n")
        
        # Emitente
        print("ESTABELECIMENTO:")
        print(f"   Nome: {cupom_completo.emitente.nome}")
        print(f"   CNPJ: {cupom_completo.emitente.cnpj}")
        print(f"   Endereço: {cupom_completo.emitente.endereco}")
        print(f"   Bairro: {cupom_completo.emitente.bairro}")
        print(f"   CEP: {cupom_completo.emitente.cep}")
        print(f"   UF: {cupom_completo.emitente.uf}")
        print(f"   IE: {cupom_completo.emitente.ie}")
        print(f"   IM: {cupom_completo.emitente.im}")
        print()
        
        # Consumidor
        if cupom_completo.consumidor and cupom_completo.consumidor.esta_presente():
            print("CONSUMIDOR:")
            print(f"   Nome: {cupom_completo.consumidor.nome}")
            print(f"   CPF/CNPJ: {cupom_completo.consumidor.cpf_cnpj}")
            print()
        else:
            print("CONSUMIDOR: Não identificado")
            print()
        
        # Cupom
        print("CUPOM:")
        print(f"   Total: R$ {cupom_completo.cupom.total}")
        print(f"   Data/Hora: {cupom_completo.cupom.data_hora}")
        print(f"   Forma Pagamento: {cupom_completo.cupom.forma_pagamento}")
        print(f"   Troco: {cupom_completo.cupom.troco}")
        print(f"   Tributos: {cupom_completo.cupom.tributos}")
        print()
        
        # Local de Entrega
        if cupom_completo.local_entrega and cupom_completo.local_entrega.esta_presente():
            print("LOCAL DE ENTREGA:")
            print(f"   Endereço: {cupom_completo.local_entrega.endereco}")
            print(f"   Bairro: {cupom_completo.local_entrega.bairro}")
            print(f"   Município: {cupom_completo.local_entrega.municipio}")
            print(f"   UF: {cupom_completo.local_entrega.uf}")
            print()
        else:
            print("LOCAL DE ENTREGA: Não informado")
            print()
        
        # Produtos
        print(f"PRODUTOS ({len(cupom_completo.produtos)} itens):")
        for idx, produto in enumerate(cupom_completo.produtos, 1):
            print(f"\n   {idx}. {produto.descricao}")
            print(f"      NCM: {produto.codigo_ncm}")
            print(f"      Quantidade: {produto.quantidade}")
            print(f"      Valor: R$ {produto.valor_liquido}")
            if produto.cod_gtin:
                print(f"      GTIN: {produto.cod_gtin}")
        
        print("\n" + "=" * 70)
        
        # Pergunta se quer salvar
        print("\n")
        salvar = input("Deseja salvar os dados em CSV? (s/n): ").lower()
        
        if salvar == 's':
            print("\nSalvando dados em CSV...")
            
            # Cria repositório e salva
            csv_repo = CSVRepository()
            arquivo_salvo = csv_repo.salvar(cupom_completo)
            
            print(f"Arquivo salvo com sucesso!")
            print(f"Localização: {arquivo_salvo}")
            print(f"\nAbra o arquivo no Excel ou LibreOffice para visualizar.")
    else:
        print("\nERRO: Nenhum dado foi extraído")
        print("\nVerifique se:")
        print("- A chave está correta")
        print("- Você resolveu o captcha")
        print("- O site está acessível")
        print("- Os campos estão configurados em campos_extracao.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAVISO: Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n\nERRO inesperado: {str(e)}")
        import traceback
        traceback.print_exc()