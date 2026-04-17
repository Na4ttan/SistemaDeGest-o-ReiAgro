from django.shortcuts import render, redirect
from .models import Cliente, Fornecedor, Produto, Categoria, Venda, ItensVenda
# Create your views here.


def frente_caixa(request):
    if request.method == 'POST':
        # lógica para salvar a venda
        pass
    # Busca os dados reias para o HTML
    clientes = Cliente.objects.all()
    produtos = Produto.objects.all()

    context = {
        'clientes': clientes,
        'produtos': produtos,
    }
    return render(request, 'index.html', context)


def index(request):
    return render(request, 'paginas/index.html')


def cadastro(request):
    return render(request, 'paginas/cadastro.html')


def consulta(request):
    return render(request, 'paginas/consulta.html')


def fechamento(request):
    return render(request, 'paginas/fechamento.html')
