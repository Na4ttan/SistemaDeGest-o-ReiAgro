from django.contrib import admin
from .models import Categoria, Fornecedor, Produto, Cliente, Venda, ItensVenda, FechamentoCaixa, Sangria

admin.site.register(Categoria)
admin.site.register(Fornecedor)
admin.site.register(Produto)
admin.site.register(Cliente)
admin.site.register(Venda)
admin.site.register(ItensVenda)

@admin.register(FechamentoCaixa)
class FechamentoCaixaAdmin(admin.ModelAdmin):
    list_display = ('data_criacao', 'operador', 'valor_recolhido')
    list_filter = ('data_criacao', 'operador') 

@admin.register(Sangria)
class SangriaAdmin(admin.ModelAdmin):
    list_display = ('fechamento', 'motivo', 'valor', 'hora') 
    list_filter = ('hora',)