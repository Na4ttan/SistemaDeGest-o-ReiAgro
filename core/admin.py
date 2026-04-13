from django.contrib import admin
from .models import Categoria, Fornecedor, Produto, Cliente, Venda, ItensVenda

admin.site.register(Categoria)
admin.site.register(Fornecedor)
admin.site.register(Produto)
admin.site.register(Cliente)
admin.site.register(Venda)
admin.site.register(ItensVenda)