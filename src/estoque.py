# src/estoque.py
from src.produto import Produto

class Estoque:
    def __init__(self):
        self.produtos = []  # lista de objetos Produto

    def adicionar(self, produto):
        self.produtos.append(produto)

    def buscar_por_codigo(self, codigo):
        for p in self.produtos:
            if p.codigo == codigo:
                return p
        return None

    def listar_todos(self):
        return self.produtos.copy()