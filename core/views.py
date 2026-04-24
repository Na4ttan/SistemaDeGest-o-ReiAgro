import json
from django.http import JsonResponse, request
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



def cadastro(request):
    if request.method == 'POST':
        # Verifica qual formulário foi enviado.
        
        #cadastro de cliente
        if 'cpf' in request.POST:
            nome = request.POST.get('nome')
            cpf = request.POST.get('cpf')
            telefone = request.POST.get('telefone_cliente')
            email = request.POST.get('email_cliente')

            Cliente.objects.create(
                nome=nome,
                cpf=cpf,
                telefone=telefone,
                email=email
            )
            #podemos pedir uma mensagem de sucesso aqui dps
            return redirect('cadastro')

        #Cadastro de produto
        elif 'nome_produto' in request.POST:
            nome_produto = request.POST.get('nome_produto')
            categoria = request.POST.get('id_categoria')
            fornecedor = request.POST.get('id_fornecedor')
            preco_custo = request.POST.get('preco_custo').replace(',', '.')
            preco_venda = request.POST.get('preco_venda').replace(',', '.')
            quantia = request.POST.get('quantia')
            unidade_medida = request.POST.get('unidade_medida')

            id_cat = request.POST.get('id_categoria')
            id_forn = request.POST.get('id_fornecedor')

            #busca instâncias reais
            categoria_instancia = Categoria.objects.get(id=id_cat)
            fornecedor_instancia = Fornecedor.objects.get(id=id_forn)

            #salvando as instâncias
            Produto.objects.create(
                nome_produto=nome_produto,
                categoria=categoria_instancia,
                fornecedor=fornecedor_instancia,
                preco_custo=preco_custo,
                preco_venda=preco_venda,
                quantidade_estoque=quantia,
                unidade_medida=unidade_medida
                )
            
            #podemos pedir uma mensagem de sucesso aqui dps
            return redirect('cadastro')

        #cadastro de fornecedor
        elif "nome_fantasia" in request.POST:
            nome_fantasia = request.POST.get('nome_fantasia')
            cnpj = request.POST.get('cnpj')
            telefone = request.POST.get('telefone_forn')
            email = request.POST.get('email_forn')

            Fornecedor.objects.create(
                nome_fantasia=nome_fantasia,
                cnpj=cnpj,
                telefone=telefone,
                email=email
            )
            #podemos pedir uma mensagem de sucesso aqui dps
            return redirect('cadastro')
    #busca os dados reais para preencher os selects do formulário
    fornecedores = Fornecedor.objects.all()
    categorias = Categoria.objects.all()

    context = {
    'fornecedores':fornecedores,
    'categorias': categorias,
    }
            
    return render(request, 'paginas/cadastro.html', context)


def consulta(request):
    return render(request, 'paginas/consulta.html')


def fechamento(request):
    return render(request, 'paginas/fechamento.html')
