# src/relatorios.py
import os
from datetime import datetime
from fpdf import FPDF
import pandas as pd

from src.persistencia import carregar, carregar_historico

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Sistema de Controle de Estoque', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, title, 0, 1, 'L', 1)
        self.ln(4)

    def table_from_dataframe(self, df, col_widths=None):
        """Desenha uma tabela com os dados do DataFrame."""
        if df.empty:
            self.cell(0, 5, "Nenhum dado disponível.", ln=1)
            return
        if col_widths is None:
            col_widths = [self.epw / len(df.columns)] * len(df.columns)
        # Cabeçalho
        self.set_font('Arial', 'B', 10)
        for i, col in enumerate(df.columns):
            self.cell(col_widths[i], 7, str(col), border=1, align='C')
        self.ln()
        # Linhas
        self.set_font('Arial', '', 9)
        for _, row in df.iterrows():
            for i, col in enumerate(df.columns):
                value = str(row[col]) if pd.notna(row[col]) else ""
                self.cell(col_widths[i], 6, value, border=1, align='C')
            self.ln()
        self.ln()

def gerar_relatorio_pdf(nome_empresa="Minha Empresa", periodo="", responsavel="Sistema", caminho_saida=None):
    """Gera um PDF com relatório completo do sistema."""
    # Define caminho de saída com timestamp
    if caminho_saida is None:
        os.makedirs("relatorios", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_saida = os.path.join("relatorios", f"relatorio_estoque_{timestamp}.pdf")

    estoque = carregar()
    historico = carregar_historico()
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    pdf = PDF()
    pdf.add_page()

    # Cabeçalho da empresa
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 8, nome_empresa, ln=1, align='C')
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, "Relatório de Posição de Estoque", ln=1, align='C')
    pdf.ln(4)

    # Informações do relatório
    pdf.set_font('Arial', '', 10)
    pdf.cell(95, 5, f"Data de emissão: {data_geracao}", border=0, ln=0)
    pdf.cell(95, 5, f"Responsável: {responsavel}", border=0, ln=1)
    if periodo:
        pdf.cell(0, 5, f"Período: {periodo}", ln=1)
    pdf.ln(5)

    # 1. Estoque atual
    pdf.chapter_title("Estoque Atual")
    if estoque.listar_todos():
        dados_estoque = []
        for p in estoque.listar_todos():
            valor_total = p.quantidade * p.preco_unitario if hasattr(p, 'preco_unitario') else 0
            dados_estoque.append({
                "Código": p.codigo,
                "Produto": p.nome,
                "Mínimo": p.quantidade_minima,
                "Estoque": p.quantidade,
                "Custo Unit.": f"R$ {p.preco_unitario:.2f}" if hasattr(p, 'preco_unitario') else "-",
                "Valor Total": f"R$ {valor_total:.2f}"
            })
        df_estoque = pd.DataFrame(dados_estoque)
        # Ajustar larguras (em mm)
        pdf.table_from_dataframe(df_estoque, col_widths=[25, 45, 20, 20, 30, 30])
    else:
        pdf.cell(0, 5, "Nenhum produto cadastrado.", ln=1)

    # 2. Produtos com estoque baixo
    pdf.chapter_title("Produtos com Estoque Baixo")
    baixos = [p for p in estoque.listar_todos() if p.esta_baixo()]
    if baixos:
        dados_baixos = []
        for p in baixos:
            dados_baixos.append({
                "Código": p.codigo,
                "Produto": p.nome,
                "Estoque": p.quantidade,
                "Mínimo": p.quantidade_minima
            })
        df_baixos = pd.DataFrame(dados_baixos)
        pdf.table_from_dataframe(df_baixos, col_widths=[30, 60, 25, 25])
    else:
        pdf.cell(0, 5, "Nenhum produto com estoque baixo.", ln=1)

    # 3. Últimas movimentações
    pdf.chapter_title("Movimentações Recentes")
    if not historico.empty:
        historico_recente = historico.sort_values("data_hora", ascending=False).head(20)
        df_hist = historico_recente[["data_hora", "nome_produto", "tipo", "quantidade"]].copy()
        df_hist.columns = ["Data/Hora", "Produto", "Tipo", "Qtd"]
        pdf.table_from_dataframe(df_hist, col_widths=[35, 60, 20, 15])
    else:
        pdf.cell(0, 5, "Nenhuma movimentação registrada.", ln=1)

    pdf.output(caminho_saida)
    return caminho_saida

    # 4. Curva ABC
    pdf.add_page()
    pdf.chapter_title("Classificação ABC")
    from .relatorios import classificar_abc  # import dentro da função para evitar circular
    classificacao = classificar_abc(estoque.listar_todos())
    if classificacao:
        dados_abc = []
        for item in classificacao:
            dados_abc.append({
                "Produto": item["nome"],
                "Valor (R$)": f"{item['valor_total']:.2f}",
                "%": f"{item['percentual']:.1f}%",
                "Classe": item["classe"]
            })
        df_abc = pd.DataFrame(dados_abc)
        pdf.table_from_dataframe(df_abc, col_widths=[60, 30, 20, 15])
    else:
        pdf.cell(0, 5, "Nenhum produto com valor positivo.", ln=1)

def classificar_abc(produtos):
    """
    Classifica produtos em A, B, C com base no valor total em estoque.
    Retorna uma lista de dicionários com os produtos e suas classificações.
    """
    if not produtos:
        return []
    
    # Calcular valor total e ordenar decrescente
    dados = []
    for p in produtos:
        valor_total = p.quantidade * p.preco_unitario
        dados.append({
            "codigo": p.codigo,
            "nome": p.nome,
            "quantidade": p.quantidade,
            "preco_unitario": p.preco_unitario,
            "valor_total": valor_total
        })
    # Ordenar por valor_total decrescente
    dados.sort(key=lambda x: x["valor_total"], reverse=True)
    
    # Calcular valor total geral
    total_geral = sum(item["valor_total"] for item in dados)
    if total_geral == 0:
        return dados  # todos com valor zero
    
    # Calcular percentual acumulado
    acumulado = 0
    for item in dados:
        acumulado += item["valor_total"]
        item["percentual"] = (item["valor_total"] / total_geral) * 100
        item["percentual_acumulado"] = (acumulado / total_geral) * 100
        
        # Classificação
        if item["percentual_acumulado"] <= 70:
            item["classe"] = "A"
        elif item["percentual_acumulado"] <= 90:
            item["classe"] = "B"
        else:
            item["classe"] = "C"
    return dados