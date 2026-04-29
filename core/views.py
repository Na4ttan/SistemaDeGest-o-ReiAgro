from decimal import Decimal
import json
from django.http import JsonResponse, request
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from .models import Cliente, Fornecedor, Produto, Categoria, Venda, ItensVenda
# Create your views here.


def frente_caixa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            itens = data.get('itens')
            cliente_nome = data.get('cliente')
            forma_pagamento = data.get('forma_pagamento')
            # Captura o total enviado pelo JS (usaremos o nome 'total_venda')
            total_enviado = data.get('total_venda', 0)

            nova_venda = Venda.objects.create(
                cliente=cliente_nome,
                forma_de_pagamento=forma_pagamento,
                produto="Múltiplos Itens",
                quantidade=1,
                valorTotal=Decimal(str(total_enviado))
            )

            total_venda_calculado = 0

            # percorrendo os itens
            for item in itens:
                produto_obj = Produto.objects.get(id=item['id'])
                qtd_decimal = Decimal(str(item['quantidade']))
                preco_unit = Decimal(str(item['preco']))

                #salvando na tabela itensvenda
                ItensVenda.objects.create(
                    venda=nova_venda, # Aqui vinculamos ao ID da venda única
                    produto=produto_obj,
                    quantidade=qtd_decimal,
                    preco_unitario=preco_unit
                )

                # subitraindo a quantidade vendida para atualizar o estoque
                produto_obj.quantidade_estoque -= qtd_decimal

                # salva a alteração no banco
                produto_obj.save()

                total_venda_calculado += float(item['subtotal'])

            recibo_html = f"""
            <html>
            <head><style>
                body {{ font-family: monospace; width: 300px; }}
                .text-center {{ text-align: center; }}
                .separador {{ border-top: 1px dashed #000; margin: 10px 0; }}
            </style></head>
            <body>
                <h2 class="text-center">REI AGRO</h2>
                <p class="text-center">Loja 02 - JD. Colina I<br>Fone: 19 989900845</p>

                <p class="text-center">Recibo de Venda</p>
                <p>Cliente: {cliente_nome}</p>
                <div class="separador"></div>
                <table>
                    <thead><tr><th>Prod</th><th>Qtd</th><th>Total</th></tr></thead>
                    <tbody>
            """
            for item in itens:
                recibo_html += f"<tr><td>{item['produto']}</td><td>{item['quantidade']} {item['unidade']}</td><td>R$ {item['subtotal']:.2f}</td></tr>"

            recibo_html += f"""
                    </tbody>
                </table>
                <div class="separador"></div>
                <p><strong>TOTAL: R$ {total_venda_calculado:.2f}</strong></p>
                <p>Pagamento: {forma_pagamento}</p>
                <p class="text-center">Obrigado pela preferência!</p>
            </body>
            </html>
            """

            return JsonResponse({
                'status': 'sucesso', 
                'mensagem': 'Venda salva!',
                'recibo_html': recibo_html # Enviamos o HTML pronto para o JS
            })
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400)

    # Busca os dados reias para o HTML
    produtos = Produto.objects.all().order_by('data_validade', 'nome_produto')

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
            if not quantia or quantia.strip() == "":
                quantia_dedimal = Decimal('0')
            else:
                quantia_dedimal = Decimal(quantia.replace(',', '.'))
            unidade_medida = request.POST.get('unidade_medida')
            data_val = request.POST.get('data_validade')

            id_cat = request.POST.get('id_categoria')
            id_forn = request.POST.get('id_fornecedor')
            if not data_val:
                data_val = None

            #busca instâncias reais
            categoria_instancia = Categoria.objects.get(id=id_cat)
            fornecedor_instancia = Fornecedor.objects.get(id=id_forn)

            #buscando produto com as mesmas características
            #se não existir, o Django cria. Se existir, ele apenas recupera em 'produto'
            produto, criado = Produto.objects.get_or_create(
                nome_produto=nome_produto,
                categoria=categoria_instancia,
                fornecedor=fornecedor_instancia,
                preco_custo=preco_custo,
                preco_venda=preco_venda,
                quantidade_estoque=quantia,
                unidade_medida=unidade_medida,
                data_validade=data_val,
                defaults = {
                'preco_custo' : preco_custo,
                'preco_venda' : preco_venda,
                'quantidade_estoque' : 0
                }
            )

            # Agora somamos a nova quantidade à que já existe
            produto.quantidade_estoque += quantia_dedimal
            produto.save()

            # Se o produto já existia, talvez seja necessário mudar o valor
            produto.preco_custo = preco_custo
            produto.preco_venda = preco_venda

            produto.save()
            
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
    hoje = timezone.now().date()
    # Filtra produtos da categoria específica
    # Certifique-se de que o nome no banco seja exatamente este
    produtos = Produto.objects.filter(categoria__nome_categoria__icontains='Nutrição Animal')

    #inicializa inicializa os contadores
    dados_grafico = {
        'vencidos': 0,      # Vermelho
        'critico': 0,       # laranja (Até 30 dias)
        'alerta': 0,        # Laranja-vermelho (31-60 dias)
        'atencao': 0,       # Amarelo (61-90 dias)
        'seguro': 0         # Verde (> 90 dias)
    }

    for p in produtos:
        if not p.data_validade:
            continue

        dias_para_vencer = (p.data_validade - hoje).days

        if dias_para_vencer < 0:
            dados_grafico['vencidos'] += 1
        elif dias_para_vencer <= 30:
            dados_grafico['critico'] += 1
        elif dias_para_vencer <= 60:
            dados_grafico['alerta'] += 1
        elif dias_para_vencer <= 90:
            dados_grafico['atencao'] += 1
        else:
            dados_grafico['seguro'] += 1

    Categorias = Categoria.objects.all()

    # Captura os dados do formulário
    categoria_id = request.GET.get('categoria')
    unidade = request.GET.get('unidade_medida')
    tipo_filtro = request.GET.get('tipo_filtro')
    valor_busca = request.GET.get('valor_busca')

    produtos_lista = Produto.objects.all().order_by('nome_produto')

    # Filtra por Categoria se selecionada
    if categoria_id:
        produtos_lista = produtos_lista.filter(categoria_id=categoria_id)
    
    if unidade:
        produtos_lista = produtos_lista.filter(unidade_medida=unidade)

    # Filtra pelo Atributo escolhido
    if valor_busca:
        if tipo_filtro == 'id':
            produtos_lista = produtos_lista.filter(id=valor_busca)
        elif tipo_filtro == 'nome_produto':
            produtos_lista = produtos_lista.filter(nome_produto__icontains=valor_busca)
        elif tipo_filtro == 'preco_venda':
            produtos_lista = produtos_lista.filter(preco_venda__gte=valor_busca)
    

    filtros = ['categoria', 'unidade_medida', 'valor_busca', 'tipo_filtro']
    consulta_feita = any(request.GET.get(f) for f in filtros)
    
    context = {
        'dados_grafico': dados_grafico,
        'categorias' : Categorias,
        "produtos_lista" : produtos_lista,
        'consulta_feita' : consulta_feita,
    }


    return render(request, 'paginas/consulta.html', context)


def fechamento(request):
    return render(request, 'paginas/fechamento.html')
