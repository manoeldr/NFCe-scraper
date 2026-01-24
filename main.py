"""
Script principal CLI para extração de dados de cupons fiscais

Execute:
    python main.py
"""
import sys
from pathlib import Path

from src.controller.cupom_controller import CupomController


def exibir_menu():
    """Exibe menu principal"""
    print("\n" + "="*70)
    print("SISTEMA DE EXTRAÇÃO DE CUPONS FISCAIS - SEFAZ-SP")
    print("="*70)
    print("\nOpções:")
    print("1. Processar cupom individual")
    print("2. Processar múltiplos cupons (lote)")
    print("3. Validar chave de acesso")
    print("4. Sair")
    print("\n" + "="*70)


def processar_cupom_individual(controller):
    """Processa um único cupom"""
    print("\n" + "="*70)
    print("PROCESSAR CUPOM INDIVIDUAL")
    print("="*70)
    
    # Solicita chave
    print("\nDigite a chave de acesso do cupom:")
    entrada = input("Chave: ").strip()
    
    if not entrada:
        print("\nERRO: Nenhuma chave fornecida")
        return
    
    # Pergunta se quer salvar CSV
    salvar = input("\nDeseja salvar em CSV? (s/n): ").lower().strip()
    salvar_csv = salvar == 's'
    
    # Processa
    print("\nProcessando...")
    sucesso, cupom, arquivo, mensagem = controller.processar_cupom(
        entrada,
        salvar_csv=salvar_csv,
        nome_arquivo=None
    )
    
    # Resultado
    if sucesso:
        print("\nSUCESSO: Cupom processado")
        
        if arquivo:
            print(f"Arquivo salvo: {arquivo}")
    else:
        print(f"\nERRO: {mensagem}")
    
    input("\nPressione ENTER para continuar...")


def processar_lote(controller):
    """Processa múltiplos cupons"""
    print("\n" + "="*70)
    print("PROCESSAR LOTE DE CUPONS")
    print("="*70)
    
    print("\nOpções de entrada:")
    print("1. Digitar chaves manualmente")
    print("2. Ler de arquivo (uma chave por linha)")
    
    opcao = input("\nEscolha (1-2): ").strip()
    
    chaves = []
    
    if opcao == '1':
        print("\nDigite as chaves (uma por linha)")
        print("Digite uma linha vazia para finalizar:")
        
        while True:
            chave = input("Chave: ").strip()
            if not chave:
                break
            chaves.append(chave)
    
    elif opcao == '2':
        caminho = input("\nCaminho do arquivo: ").strip()
        
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                chaves = [linha.strip() for linha in f if linha.strip()]
        except FileNotFoundError:
            print(f"\nERRO: Arquivo não encontrado: {caminho}")
            input("\nPressione ENTER para continuar...")
            return
        except Exception as e:
            print(f"\nERRO ao ler arquivo: {str(e)}")
            input("\nPressione ENTER para continuar...")
            return
    else:
        print("\nOpção inválida")
        input("\nPressione ENTER para continuar...")
        return
    
    if not chaves:
        print("\nNenhuma chave fornecida")
        input("\nPressione ENTER para continuar...")
        return
    
    print(f"\nTotal de chaves: {len(chaves)}")
    
    # Pergunta se quer salvar CSV
    salvar = input("Deseja salvar em CSV? (s/n): ").lower().strip()
    salvar_csv = salvar == 's'
    
    # Confirmação
    confirmar = input(f"\nProcessar {len(chaves)} cupons? (s/n): ").lower().strip()
    
    if confirmar != 's':
        print("\nOperação cancelada")
        input("\nPressione ENTER para continuar...")
        return
    
    # Processa lote
    print("\nProcessando lote...")
    resultados = controller.processar_multiplos_cupons(chaves, salvar_csv=salvar_csv)
    
    # Exibe resumo
    print("\n" + "="*70)
    print("RESUMO")
    print("="*70)
    print(f"Total: {resultados['total']}")
    print(f"Sucesso: {resultados['sucesso']}")
    print(f"Erro: {resultados['erro']}")
    
    input("\nPressione ENTER para continuar...")


def validar_chave(controller):
    """Valida uma chave sem processar"""
    print("\n" + "="*70)
    print("VALIDAR CHAVE DE ACESSO")
    print("="*70)
    
    entrada = input("\nDigite a chave: ").strip()
    
    if not entrada:
        print("\nNenhuma chave fornecida")
        input("\nPressione ENTER para continuar...")
        return
    
    valido, chave, mensagem = controller.validar_chave(entrada)
    
    if valido:
        print(f"\nVALIDA: {chave}")
    else:
        print(f"\nINVALIDA: {mensagem}")
    
    input("\nPressione ENTER para continuar...")


def main():
    """Função principal"""
    print("\nInicializando sistema...")
    
    # Cria controller
    controller = CupomController(headless=False)
    
    while True:
        exibir_menu()
        
        opcao = input("\nEscolha uma opção (1-4): ").strip()
        
        if opcao == '1':
            processar_cupom_individual(controller)
        
        elif opcao == '2':
            processar_lote(controller)
        
        elif opcao == '3':
            validar_chave(controller)
        
        elif opcao == '4':
            print("\nEncerrando sistema...")
            print("Até logo!")
            sys.exit(0)
        
        else:
            print("\nOpção inválida! Escolha entre 1 e 4.")
            input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário")
        print("Até logo!")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nERRO INESPERADO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)