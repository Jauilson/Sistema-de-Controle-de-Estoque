# src/produto.py
class Produto:
    def __init__(self, codigo, nome, quantidade, quantidade_minima=5):
        self.codigo = codigo
        self.nome = nome
        self.quantidade = quantidade
        self.quantidade_minima = quantidade_minima

    def __repr__(self):
        return f"Produto({self.codigo}, {self.nome}, estoque: {self.quantidade})"

    def esta_baixo(self):
        """Retorna True se estoque está abaixo do mínimo"""
        return self.quantidade < self.quantidade_minima