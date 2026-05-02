from decimal import Decimal
import json
from django.http import JsonResponse, request
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Cliente, Fornecedor, Produto, Categoria, Venda, ItensVenda, FechamentoCaixa, Sangria
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required
def frente_caixa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            itens = data.get('itens')
            cliente_nome = data.get('cliente')
            forma_pagamento = data.get('forma_pagamento')
            total_enviado = data.get('total_venda', 0)

            cliente_id = data.get('cliente')
            if cliente_id:
                try:
                    cliente_obj = Cliente.objects.get(id=cliente_id)
                    nome_para_venda = cliente_obj.nome
                except (Cliente.DoesNotExist, ValueError):
                    nome_para_venda = "Consumidor (Venda Geral)"
            else:
                nome_para_venda = "Consumidor (Venda Geral)"

            nova_venda = Venda.objects.create(
                cliente=nome_para_venda,
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
                <p>Cliente: {nome_para_venda}</p>
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
                'recibo_html': recibo_html 
            })
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400)

    # Busca os dados reias para o HTML
    produtos = Produto.objects.all().order_by('data_validade', 'nome_produto')

    # 2. BUSCA TODOS OS CLIENTES 
    clientes = Cliente.objects.all()

    # 3. Coloca os clientes no dicionário de contexto
    context = {
        'produtos': produtos,
        'clientes': clientes,
    }

    return render(request, 'paginas/index.html', context)


@login_required
def cadastro(request):
    if request.method == 'POST':
        # Verifica qual formulário foi enviado.
        
        #cadastro de cliente
        if 'cpf' in request.POST:
            nome = request.POST.get('nome')
            cpf = request.POST.get('cpf')
            telefone = request.POST.get('telefone_cliente')
            email = request.POST.get('email_cliente')

            Cliente.objects.update_or_create(
                cpf=cpf,
                defaults={
                    'nome': nome,
                    'telefone': telefone,
                    'email': email
                }
            )
            from django.urls import reverse

            url_destino = reverse('home') + f'?cpf_novo={cpf}'
            #podemos pedir uma mensagem de sucesso aqui dps
            return redirect(url_destino)

        # --- Cadastro de produto ---
        elif 'nome_produto' in request.POST:
            # 1. Captura de dados comuns
            nome_produto = request.POST.get('nome_produto')
            barcode = request.POST.get('barcode')
            data_val = request.POST.get('data_validade') or None
            id_cat = request.POST.get('id_categoria')
            id_forn = request.POST.get('id_fornecedor')
            
            # 2. Lógica para diferenciar os formulários
            is_granel = request.POST.get('venda_granel_especifica') == 'true'

            if is_granel:
                # Se for ração, o preço de venda vem do campo 'preco_venda_saco'
                preco_v = request.POST.get('preco_venda_saco').replace(',', '.')
                preco_c = request.POST.get('preco_custo', '0').replace(',', '.') 
                
                # Pega o peso (ex: 15) e transforma em fator de conversão (15000)
                peso_informado = request.POST.get('peso_pacote').replace(',', '.')
                fator_decimal = Decimal(peso_informado) * Decimal('1000.000')
                
                unidade_medida = 'PA' # Força ser Pacote
                quantia = request.POST.get('quantia')
            else:
                # Lógica original para produtos normais
                preco_c = request.POST.get('preco_custo').replace(',', '.')
                preco_v = request.POST.get('preco_venda').replace(',', '.')
                unidade_medida = request.POST.get('unidade_medida')
                quantia = request.POST.get('quantia')
                fator_decimal = Decimal('1.000')

            # 3. Conversão de valores para Decimal
            preco_custo_decimal = Decimal(preco_c)
            preco_venda_decimal = Decimal(preco_v)
            
            if not quantia or quantia.strip() == "":
                quantia_decimal = Decimal('0.000')
            else:
                quantia_decimal = Decimal(quantia.replace(',', '.'))

            # 4. Busca instâncias de Categoria e Fornecedor
            categoria_instancia = Categoria.objects.get(id=id_cat)
            fornecedor_instancia = Fornecedor.objects.get(id=id_forn)

            # 5. GARANTIR A EXISTÊNCIA DO PRODUTO (Sem erro de variável local)
            # Criamos com estoque zero para não violar a restrição de NOT NULL
            produto, criado = Produto.objects.get_or_create(
                codigo_barras=barcode,
                data_validade=data_val,
                defaults={
                    'nome_produto': nome_produto,
                    'categoria': categoria_instancia,
                    'fornecedor': fornecedor_instancia,
                    'preco_custo': preco_custo_decimal,
                    'preco_venda': preco_venda_decimal,
                    'unidade_medida': unidade_medida,
                    'fator_conversao': fator_decimal,
                    'quantidade_estoque': Decimal('0.000')
                }
            )

            # 6. ATUALIZAÇÃO FINAL DOS DADOS E ESTOQUE
            if not criado:
                # Se o produto já existia, atualizamos os preços e somamos o estoque
                produto.nome_produto = nome_produto
                produto.categoria = categoria_instancia
                produto.fornecedor = fornecedor_instancia
                produto.preco_custo = preco_custo_decimal
                produto.preco_venda = preco_venda_decimal
                produto.unidade_medida = unidade_medida
                produto.fator_conversao = fator_decimal
                produto.quantidade_estoque += quantia_decimal
            else:
                # Se for novo, apenas definimos a quantidade vinda do formulário
                produto.quantidade_estoque = quantia_decimal

            produto.save()
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
    todos_produtos = Produto.objects.filter(unidade_medida='PA')

    context = {
    'fornecedores':fornecedores,
    'categorias': categorias,
    'todos_produtos': todos_produtos,
    }
            
    return render(request, 'paginas/cadastro.html', context)

@login_required
def consulta(request):
    
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
        if tipo_filtro == 'codigo_barras':
            produtos_lista = produtos_lista.filter(codigo_barras__icontains=valor_busca)
        elif tipo_filtro == 'nome_produto':
            produtos_lista = produtos_lista.filter(nome_produto__icontains=valor_busca)
        elif tipo_filtro == 'fornecedor':
            produtos_lista = produtos_lista.filter(fornecedor__nome_fantasia__icontains=valor_busca)
        

    filtros = ['categoria', 'unidade_medida', 'valor_busca', 'tipo_filtro']
    consulta_feita = any(request.GET.get(f) for f in filtros)
    
    context = {
        'categorias' : Categorias,
        "produtos_lista" : produtos_lista,
        'consulta_feita' : consulta_feita,
    }


    return render(request, 'paginas/consulta.html', context)

@login_required
def relatorios(request):
    hoje = timezone.now().date()
    trinta_dias = hoje + timedelta(days=30) # Define o intervalo de 1 mês[cite: 12]
    # Filtra produtos da categoria específica
    # Certifique-se de que o nome no banco seja exatamente este
    produtos_nutricao = Produto.objects.filter(
        categoria__nome_categoria__icontains='Nutrição Animal',
        quantidade_estoque__gt=0  # Filtra apenas estoque maior que zero[cite: 12]
    )

    # inicializa os contadores
    dados_grafico = {
        'vencidos': 0,      # Vermelho
        'critico': 0,       # laranja (Até 30 dias)
        'alerta': 0,        # Laranja-vermelho (31-60 dias)
        'atencao': 0,       # Amarelo (61-90 dias)
        'seguro': 0         # Verde (> 90 dias)
    }

    for p in produtos_nutricao:
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

    produtos_vencidos = produtos_nutricao.filter(data_validade__lt=hoje).order_by('data_validade')

    produtos_proximos = produtos_nutricao.filter(
        data_validade__gte=hoje, 
        data_validade__lte=trinta_dias
    ).order_by('data_validade')

    context = {
        'dados_grafico': dados_grafico,
        'produtos_vencidos': produtos_vencidos,
        'produtos_proximos': produtos_proximos,
    }
    return render(request, 'paginas/relatorios.html', context)

@login_required
def fechamento(request):
    # Busca o último fechamento realizado no banco de dados
    ultimo_fechamento = FechamentoCaixa.objects.order_by('-data_criacao').first()
    
    # Se existir um fechamento anterior, pegamos o valor que foi deixado
    fundo_abertura_anterior = ultimo_fechamento.fundo_reserva_proximo_dia if ultimo_fechamento else 0
    
    context = {
        'fundo_abertura_anterior': fundo_abertura_anterior,
        # ... outros dados de vendas ...
    }
    return render(request, 'paginas/fechamento.html', context)

@login_required
def buscar_cliente_cpf(request):
    cpf = request.GET.get('cpf')
    try:
        cliente = Cliente.objects.get(cpf=cpf)
        return JsonResponse({'status': 'sucesso', 'nome': cliente.nome, 'id': cliente.id})
    except Cliente.DoesNotExist:
        return JsonResponse({'status': 'erro', 'mensagem': 'Cliente não encontrado'}, status=404)


@login_required
def desmembrar_produto(request, produto_id):
    # O produto_id aqui deve ser o do produto GRANEL (o que recebe o estoque)
    produto_granel = get_object_or_404(Produto, id=produto_id)
    
    if not producto_granel.produto_pai:
        messages.error(request, "Este produto não possui um pacote vinculado para desmembramento.")
        return redirect('consulta')

    produto_pacote = producto_granel.produto_pai

    if producto_pacote.quantidade_estoque >= 1:
        # 1. Diminui 1 unidade do pacote fechado
        producto_pacote.quantidade_estoque -= 1
        producto_pacote.save()

        # 2. Aumenta o estoque do granel com base no fator de conversão
        # Ex: Se o fator for 15, adiciona 15kg ao estoque granel
        producto_granel.quantidade_estoque += producto_granel.fator_conversao
        producto_granel.save()

        messages.success(request, f"Sucesso! 1 unidade de {producto_pacote.nome} foi convertida em {producto_granel.fator_conversao} {producto_granel.forma_medida}.")
    else:
        messages.error(request, f"Estoque insuficiente de {producto_pacote.nome} para desmembrar.")

    return redirect('estoque')