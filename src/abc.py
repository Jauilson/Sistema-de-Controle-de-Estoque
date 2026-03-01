import pandas as pd

def classificar_abc(produtos):
    """
    produtos: lista de objetos Produto
    retorna: DataFrame com colunas: Nome, ValorTotal, Percentual, Acumulado, Classe
    """
    if not produtos:
        return pd.DataFrame()
    
    # Calcular valor total em estoque para cada produto
    dados = []
    for p in produtos:
        valor_total = p.quantidade * p.preco_unitario
        dados.append({
            "Nome": p.nome,
            "Código": p.codigo,
            "Valor Total (R$)": valor_total
        })
    
    df = pd.DataFrame(dados)
    df = df.sort_values("Valor Total (R$)", ascending=False).reset_index(drop=True)
    
    total_geral = df["Valor Total (R$)"].sum()
    df["Percentual"] = (df["Valor Total (R$)"] / total_geral) * 100
    df["Acumulado"] = df["Percentual"].cumsum()
    
    # Classificar
    condicoes = [
        df["Acumulado"] <= 70,
        df["Acumulado"] <= 90,
        df["Acumulado"] > 90
    ]
    classes = ["A", "B", "C"]
    df["Classe"] = pd.Series(pd.cut(df.index, bins=[-1, len(df[condicoes[0]]), len(df[condicoes[0]])+len(df[condicoes[1]]), len(df)], labels=classes)).astype(str)
    # Mais simples: usar o acumulado para definir
    df["Classe"] = "C"
    df.loc[df["Acumulado"] <= 90, "Classe"] = "B"
    df.loc[df["Acumulado"] <= 70, "Classe"] = "A"
    
    return df