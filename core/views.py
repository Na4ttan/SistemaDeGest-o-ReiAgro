import json
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Cliente, Fornecedor, Produto, Categoria, Venda, ItensVenda
# Create your views here.


def frente_caixa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            itens = data.get('itens')
            cliente_nome = data.get('cliente')
            forma_pagamento = data.get('forma_pagamento')

            # Para cada item na lista do JS, criamos uma Venda no banco
            for item in itens:
                produto_obj = Produto.objects.get(nome_produto=item['produto'])
                Venda.objects.create(
                    cliente=cliente_nome,
                    produto=item['produto'],
                    quantidade=item['quantidade'],
                    preco=item['preco'],
                    forma_de_pagamento=forma_pagamento
                )

                # subitraindo a quantidade vendida para atualizar o estoque
                produto_obj.quantidade_estoque -= item['quantidade']

                # salva a alteração no banco
                produto_obj.save()

            return JsonResponse({'status': 'sucesso', 'mensagem': 'Venda salva com sucesso!'})
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400)
    # Busca os dados reias para o HTML
    produtos = Produto.objects.all()

    # 2. BUSCA TODOS OS CLIENTES (A linha que estava faltando!)
    clientes = Cliente.objects.all()

    # 3. Coloca os clientes no dicionário de contexto
    context = {
        'produtos': produtos,
        'clientes': clientes,
    }

    return render(request, 'paginas/index.html', context)


def index(request):
    return render(request, 'paginas/index.html')


def cadastro(request):
    return render(request, 'paginas/cadastro.html')


def consulta(request):
    return render(request, 'paginas/consulta.html')


def fechamento(request):
    return render(request, 'paginas/fechamento.html')
