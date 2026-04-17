from django.db import models


class Categoria(models.Model):
    nome_categoria = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome_categoria


class Fornecedor(models.Model):
    nome_fantasia = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True)
    telefone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.nome_fantasia


class Produto(models.Model):

    # Definindo as constantes para as opções
    UNIDADES_CHOICES = [
        ('KG', 'Quilograma'),
        ('UN', 'Unidade'),
        ('LT', 'Litro'),
        ('MT', 'Metro'),
        ('PA', 'Pacote'),
    ]
    nome_produto = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_estoque = models.DecimalField(max_digits=10, decimal_places=3)
    unidade_medida = models.CharField(
        max_length=2, choices=UNIDADES_CHOICES, default='UN')  # Ex: KG, UN, SACA

    def __str__(self):
        return self.nome_produto


class Cliente(models.Model):
    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return self.nome


class Venda(models.Model):
    cliente = models.CharField(max_length=200, default='Consumidor')
    produto = models.CharField(max_length=200, default='Geral')
    quantidade = models.IntegerField(default=1)
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    data_venda = models.DateTimeField(auto_now_add=True)

    def __calculo_total(self):
        return self.quantidade * self.preco

    def __str__(self):
        return f"{self.cliente} - {self.produto}"


class ItensVenda(models.Model):
    venda = models.ForeignKey(
        Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.DecimalField(max_digits=10, decimal_places=3)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade} x {self.produto.nome_produto}"
