class Produto:
    def __init__(self, codigo, nome, quantidade, quantidade_minima=5, preco_unitario=0.0):
        self.codigo = codigo
        self.nome = nome
        self.quantidade = quantidade
        self.quantidade_minima = quantidade_minima
        self.preco_unitario = preco_unitario

    def __repr__(self):
        return f"Produto({self.codigo}, {self.nome}, estoque: {self.quantidade})"

    def esta_baixo(self):
        return self.quantidade < self.quantidade_minima