# src/persistencia.py
import os
import pandas as pd
from src.produto import Produto
from src.estoque import Estoque

ARQUIVO_EXCEL = os.path.join("data", "estoque.xlsx")

def salvar(estoque):
    """Salva a lista de produtos em Excel"""
    dados = []
    for p in estoque.listar_todos():
        dados.append({
            "Código": p.codigo,
            "Nome": p.nome,
            "Quantidade": p.quantidade,
            "Quantidade Mínima": p.quantidade_minima,
            "Preço Unitário": p.preco_unitario
        })
    df = pd.DataFrame(dados)
    df.to_excel(ARQUIVO_EXCEL, index=False)
    print(f"Dados salvos em {ARQUIVO_EXCEL}")

def carregar():
    """Carrega produtos do Excel, retorna um objeto Estoque"""
    from src.estoque import Estoque
    try:
        df = pd.read_excel(ARQUIVO_EXCEL)
        estoque = Estoque()
        for _, row in df.iterrows():
            p = Produto(
                codigo=row["Código"],
                nome=row["Nome"],
                quantidade=row["Quantidade"],
                quantidade_minima=row["Quantidade Mínima"],
                preco_unitario=row.get("Preço Unitário", 0.0)
            )
            estoque.adicionar(p)
        return estoque
    except FileNotFoundError:
        # Se arquivo não existe, retorna estoque vazio
        return Estoque()
    
# ===== HISTÓRICO DE MOVIMENTAÇÕES =====
ARQUIVO_HISTORICO = os.path.join("data", "historico.xlsx")

def registrar_movimentacao(codigo, nome, tipo, quantidade, responsavel="sistema"):
    """Registra uma movimentação no histórico."""
    from datetime import datetime
    nova_mov = {
        "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "codigo_produto": codigo,
        "nome_produto": nome,
        "tipo": tipo,
        "quantidade": quantidade,
        "responsavel": responsavel
    }
    try:
        df = pd.read_excel(ARQUIVO_HISTORICO)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["data_hora", "codigo_produto", "nome_produto", "tipo", "quantidade", "responsavel"])
    
    df = pd.concat([df, pd.DataFrame([nova_mov])], ignore_index=True)
    df.to_excel(ARQUIVO_HISTORICO, index=False)

def carregar_historico():
    """Retorna DataFrame com todo o histórico."""
    try:
        return pd.read_excel(ARQUIVO_HISTORICO)
    except FileNotFoundError:
        return pd.DataFrame(columns=["data_hora", "codigo_produto", "nome_produto", "tipo", "quantidade", "responsavel"])