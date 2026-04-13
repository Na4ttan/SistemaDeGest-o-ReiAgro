from django.shortcuts import render
from .models import Cliente, Fornecedor, Produto, Categoria, Venda, ItensVenda
# Create your views here.


def home(request):
    return render(request, 'index.html')
