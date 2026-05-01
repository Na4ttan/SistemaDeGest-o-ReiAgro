from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    nome_categoria = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome_categoria


class Fornecedor(models.Model):
    nome_fantasia = models.CharField(max_length=30)
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
    codigo_barras = models.CharField(max_length=13, verbose_name="Código de Barras")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.CASCADE)
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade_estoque = models.DecimalField(max_digits=10, decimal_places=3)
    unidade_medida = models.CharField(
        max_length=2, choices=UNIDADES_CHOICES, default='UN')
    data_validade = models.DateField(blank=True, null=True, verbose_name="Data de Validade")

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
    quantidade = models.DecimalField(
        max_digits=10, decimal_places=3, default=1.000)
    valorTotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    data_venda = models.DateTimeField(auto_now_add=True)
    forma_de_pagamento = models.CharField(max_length=8, default="Dinheiro")

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

class FechamentoCaixa(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    operador = models.ForeignKey(User, on_delete=models.PROTECT)
    
    # Valores do Sistema (O que o sistema calculou)
    vendas_dinheiro_sistema = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Valores Declarados (O que o usuário contou na mão)
    dinheiro_em_caixa = models.DecimalField(max_digits=10, decimal_places=2) 
    
    # Destino do Dinheiro
    fundo_reserva_proximo_dia = models.DecimalField(max_digits=10, decimal_places=2)
    valor_recolhido = models.DecimalField(max_digits=10, decimal_places=2)
    
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Fechamento {self.data_criacao.strftime('%d/%m/%Y')} - {self.operador}"

class Sangria(models.Model):
    fechamento = models.ForeignKey(FechamentoCaixa, related_name='sangrias', on_delete=models.CASCADE)
    motivo = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    hora = models.DateTimeField(auto_now_add=True)