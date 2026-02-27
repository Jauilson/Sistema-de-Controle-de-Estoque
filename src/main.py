# src/main.py
from produto import Produto
from estoque import Estoque

def exibir_menu():
    print("\n=== SISTEMA DE CONTROLE DE ESTOQUE ===")
    print("1 - Cadastrar produto")
    print("2 - Listar produtos")
    print("3 - Entrada de estoque")
    print("4 - Saída de estoque")
    print("5 - Relatório de estoque baixo")
    print("0 - Sair")
    return input("Escolha uma opção: ")

def main():
    from persistencia import carregar, salvar
    estoque = carregar()

    while True:
        opcao = exibir_menu()

        if opcao == "1":
            codigo = input("Código: ")
            nome = input("Nome: ")
            qtd = int(input("Quantidade inicial: "))
            qtd_min = int(input("Quantidade mínima (padrão 5): ") or "5")
            p = Produto(codigo, nome, qtd, qtd_min)
            estoque.adicionar(p)
            salvar(estoque)
            print("Produto cadastrado com sucesso!")

        elif opcao == "2":
            produtos = estoque.listar_todos()
            if not produtos:
                print("Nenhum produto cadastrado.")
            else:
                for p in produtos:
                    print(p)

        elif opcao == "3":
            codigo = input("Código do produto: ")
            p = estoque.buscar_por_codigo(codigo)
            if p:
                qtd = int(input("Quantidade a adicionar: "))
                p.quantidade += qtd
                print(f"Estoque atualizado. Novo estoque: {p.quantidade}")
            else:
                print("Produto não encontrado.")

        elif opcao == "4":
            codigo = input("Código do produto: ")
            p = estoque.buscar_por_codigo(codigo)
            if p:
                qtd = int(input("Quantidade a retirar: "))
                if qtd <= p.quantidade:
                    p.quantidade -= qtd
                    print(f"Retirada realizada. Novo estoque: {p.quantidade}")
                    if p.esta_baixo():
                        print(f"⚠️  ALERTA: Estoque do produto {p.nome} está baixo!")
                else:
                    print("Quantidade indisponível em estoque.")
            else:
                print("Produto não encontrado.")

        elif opcao == "5":
            baixos = [p for p in estoque.listar_todos() if p.esta_baixo()]
            if baixos:
                print("Produtos com estoque baixo:")
                for p in baixos:
                    print(f"- {p.nome} (código {p.codigo}): {p.quantidade} unidades (mínimo {p.quantidade_minima})")
            else:
                print("Nenhum produto com estoque baixo.")

        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main()