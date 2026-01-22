"""
Teste manual INTERATIVO do Web Scraper Service

Execute este arquivo para testar o scraper com uma chave REAL:
    python teste_manual_scraper.py

IMPORTANTE: Este não é um teste automatizado. Precisará resolver o captcha manualmente.
"""
from src.services.web_scraper_service import WebScraperService
from src.services.qrcode_service import QRCodeService


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
    produtos = scraper.extrair_dados_cupom(chave)
    
    # Exibe os resultados
    print("\n" + "=" * 70)
    print("RESULTADOS")
    print("=" * 70)
    
    if produtos:
        print(f"\nSUCESSO: {len(produtos)} produtos extraídos!\n")
        
        for idx, produto in enumerate(produtos, 1):
            print(f"{idx}. {produto.descricao}")
            print(f"   Código: {produto.cod_produto}")
            print(f"   Quantidade: {produto.quantidade}")
            print(f"   Valor: R$ {produto.valor_liquido}")
            print()
        
        # Pergunta se quer salvar
        salvar = input("Deseja salvar os dados em CSV? (s/n): ").lower()
        
        if salvar == 's':
            print("\nTODO: Implementar salvamento em CSV")
            print("(Será feito no próximo passo)")
    else:
        print("\nERRO: Nenhum produto foi extraído")
        print("\nVerifique se:")
        print("- A chave está correta")
        print("- Você resolveu o captcha")
        print("- O site está acessível")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário")
    except Exception as e:
        print(f"\n\nERRO inesperado: {str(e)}")
        import traceback
        traceback.print_exc()