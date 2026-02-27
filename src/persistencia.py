# src/persistencia.py
import pandas as pd
from produto import Produto

ARQUIVO_EXCEL = "../data/estoque.xlsx"

def salvar(estoque):
    """Salva a lista de produtos em Excel"""
    dados = []
    for p in estoque.listar_todos():
        dados.append({
            "Código": p.codigo,
            "Nome": p.nome,
            "Quantidade": p.quantidade,
            "Quantidade Mínima": p.quantidade_minima
        })
    df = pd.DataFrame(dados)
    df.to_excel(ARQUIVO_EXCEL, index=False)
    print(f"Dados salvos em {ARQUIVO_EXCEL}")

def carregar():
    """Carrega produtos do Excel, retorna um objeto Estoque"""
    from estoque import Estoque
    try:
        df = pd.read_excel(ARQUIVO_EXCEL)
        estoque = Estoque()
        for _, row in df.iterrows():
            p = Produto(
                codigo=row["Código"],
                nome=row["Nome"],
                quantidade=row["Quantidade"],
                quantidade_minima=row["Quantidade Mínima"]
            )
            estoque.adicionar(p)
        return estoque
    except FileNotFoundError:
        # Se arquivo não existe, retorna estoque vazio
        return Estoque()