# app.py
import os
os.makedirs("data", exist_ok=True)
import streamlit as st
import pandas as pd
from src.estoque import Estoque
from src.produto import Produto
from src.persistencia import carregar, salvar
from src.persistencia import registrar_movimentacao
from src.persistencia import carregar, salvar, registrar_movimentacao, carregar_historico
from src.relatorios import gerar_relatorio_pdf
from src.relatorios import classificar_abc

# Configuração da página
st.set_page_config(page_title="Controle de Estoque", layout="wide")
st.title("📦 Sistema de Controle de Estoque")

# Inicializa o estoque na sessão (mantém dados entre interações)
if "estoque" not in st.session_state:
    st.session_state.estoque = carregar()

estoque = st.session_state.estoque

# Menu lateral
menu = st.sidebar.selectbox("Menu", ["Cadastrar Produto", "Listar Produtos", "Movimentação", "Histórico", "Relatórios", "Dashboard", "Gerar PDF"])

if menu == "Cadastrar Produto":
    st.header("➕ Cadastrar Novo Produto")
    with st.form("cadastro"):
        codigo = st.text_input("Código")
        nome = st.text_input("Nome")
        qtd = st.number_input("Quantidade inicial", min_value=0, step=1)
        qtd_min = st.number_input("Quantidade mínima", min_value=0, value=5, step=1)
        preco = st.number_input("Preço unitário (R$)", min_value=0.0, step=0.01, format="%.2f")
        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            # Verificar se código já existe
            if any(p.codigo == codigo for p in estoque.listar_todos()):
                st.error("Já existe um produto com este código. Use um código único.")
            else:
                produto = Produto(codigo, nome, qtd, qtd_min, preco)
                estoque.adicionar(produto)
                salvar(estoque)
                st.success("Produto cadastrado com sucesso!")

elif menu == "Listar Produtos":
    st.header("📋 Produtos em Estoque")
    produtos = estoque.listar_todos()
    if not produtos:
        st.info("Nenhum produto cadastrado.")
    else:
        # Cabeçalho
        cols = st.columns([2, 3, 2, 2, 2, 2, 1])
        cols[0].markdown("**Código**")
        cols[1].markdown("**Nome**")
        cols[2].markdown("**Qtd**")
        cols[3].markdown("**Mínimo**")
        cols[4].markdown("**Preço**")
        cols[5].markdown("**Status**")
        cols[6].markdown("**Ação**")

        for idx, p in enumerate(produtos):
            cols = st.columns([2, 3, 2, 2, 2, 2, 1])
            cols[0].write(p.codigo)
            cols[1].write(p.nome)
            cols[2].write(p.quantidade)
            cols[3].write(p.quantidade_minima)
            cols[4].write(f"R$ {p.preco_unitario:.2f}")
            cols[5].write("⚠️" if p.esta_baixo() else "✅")
            # Chave única usando código + índice
            if cols[6].button("🗑️", key=f"del_{p.codigo}_{idx}"):
                estoque.produtos.pop(p)
                salvar(estoque)
                st.rerun()

elif menu == "Movimentação":
    st.header("📦 Registrar Movimentação")
    produtos = estoque.listar_todos()
    if not produtos:
        st.warning("Cadastre um produto primeiro.")
    else:
        # Criar dicionário para seleção
        opcoes = {f"{p.codigo} - {p.nome}": p for p in produtos}
        escolha = st.selectbox("Selecione o produto", list(opcoes.keys()))
        produto = opcoes[escolha]

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Entrada"):
                quantidade = st.number_input("Quantidade", min_value=1, step=1, key="entrada")
                produto.quantidade += quantidade
                salvar(estoque)
                registrar_movimentacao(produto.codigo, produto.nome, "entrada", quantidade)
                st.success(f"Entrada registrada! Novo estoque: {produto.quantidade}")
        with col2:
            if st.button("➖ Saída"):
                quantidade = st.number_input("Quantidade", min_value=1, step=1, key="saida")
                if quantidade <= produto.quantidade:
                    produto.quantidade -= quantidade
                    salvar(estoque)
                    registrar_movimentacao(produto.codigo, produto.nome, "saida", quantidade)
                    st.success(f"Saída registrada! Novo estoque: {produto.quantidade}")
                    if produto.esta_baixo():
                        st.warning(f"⚠️ Estoque do produto {produto.nome} está baixo!")
                else:
                    st.error("Quantidade insuficiente em estoque.")

elif menu == "Histórico":
    st.header("📜 Histórico de Movimentações")
    df_hist = carregar_historico()
    if df_hist.empty:
        st.info("Nenhuma movimentação registrada ainda.")
    else:
        # Mostra as últimas 100, ordenadas da mais recente para a mais antiga
        df_hist = df_hist.sort_values("data_hora", ascending=False)
        st.dataframe(df_hist, use_container_width=True)
        
        # Opcional: filtros simples
        with st.expander("Filtros"):
            produtos_unicos = df_hist["nome_produto"].unique()
            produto_filtro = st.multiselect("Produto", produtos_unicos)
            if produto_filtro:
                df_hist = df_hist[df_hist["nome_produto"].isin(produto_filtro)]
            
            tipo_filtro = st.multiselect("Tipo", ["entrada", "saida"])
            if tipo_filtro:
                df_hist = df_hist[df_hist["tipo"].isin(tipo_filtro)]
            
            st.dataframe(df_hist)

elif menu == "Relatórios":
    st.header("📉 Relatório de Estoque Baixo")
    baixos = [p for p in estoque.listar_todos() if p.esta_baixo()]
    if baixos:
        dados = []
        for p in baixos:
            dados.append({
                "Código": p.codigo,
                "Nome": p.nome,
                "Quantidade": p.quantidade,
                "Mínimo": p.quantidade_minima
            })
        df = pd.DataFrame(dados)
        st.dataframe(df)
    else:
        st.success("Nenhum produto com estoque baixo.")

elif menu == "Dashboard":
    st.header("📈 Visão Geral")
    produtos = estoque.listar_todos()
    if not produtos:
        st.info("Nenhum dado para exibir.")
    else:
        # Métricas básicas
        total_itens = sum(p.quantidade for p in produtos)
        st.metric("Total de itens em estoque", total_itens)
        
        # Gráfico de barras
        df = pd.DataFrame([
            {"Produto": p.nome, "Quantidade": p.quantidade, "Mínimo": p.quantidade_minima}
            for p in produtos
        ])
        st.bar_chart(df.set_index("Produto")[["Quantidade", "Mínimo"]])

        # Curva ABC
        st.subheader("📊 Classificação ABC (por valor em estoque)")
        classificacao = classificar_abc(produtos)
        if classificacao:
            df_abc = pd.DataFrame(classificacao)
            # Gráfico de pizza
            st.plotly_chart(
                {
                    "data": [{
                        "values": df_abc["valor_total"],
                        "labels": df_abc["nome"] + " (" + df_abc["classe"] + ")",
                        "type": "pie",
                        "hole": 0.3,
                        "name": "Valor em Estoque"
                    }],
                    "layout": {"title": "Distribuição de Valor por Produto"}
                },
                use_container_width=True
            )
            # Tabela com classificação
            st.dataframe(df_abc[["nome", "valor_total", "percentual", "classe"]])

elif menu == "Gerar PDF":
    st.header("📄 Gerar Relatório em PDF")
    st.markdown("Preencha as informações abaixo e clique em **Gerar PDF**.")

    with st.form("form_relatorio"):
        nome_empresa = st.text_input("Nome da empresa", value="Minha Empresa")
        periodo = st.text_input("Período de referência (ex: 01/01/2026 a 31/01/2026)", value="")
        responsavel = st.text_input("Responsável", value="Admin")
        submitted = st.form_submit_button("📥 Gerar PDF")

    if submitted:
        with st.spinner("Gerando relatório..."):
            from src.relatorios import gerar_relatorio_pdf
            caminho = gerar_relatorio_pdf(
                nome_empresa=nome_empresa,
                periodo=periodo,
                responsavel=responsavel
            )
            st.session_state["ultimo_pdf"] = caminho
            st.success("Relatório gerado com sucesso!")

    # Botão de download fora do formulário e fora do if submitted
    if "ultimo_pdf" in st.session_state:
        with open(st.session_state["ultimo_pdf"], "rb") as f:
            st.download_button(
                label="📥 Clique aqui para baixar o PDF",
                data=f,
                file_name=os.path.basename(st.session_state["ultimo_pdf"]),
                mime="application/pdf"
            )

