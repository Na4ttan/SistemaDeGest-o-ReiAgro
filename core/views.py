from decimal import Decimal
import json
from django.http import JsonResponse, request
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import Cliente, Fornecedor, Produto, Categoria, Venda, ItensVenda, FechamentoCaixa, Sangria
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
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

            cor_primaria = "#2f6f3e" # Verde Rei Agro

            recibo_html = f"""
            <html>
            <head><style>
                body {{ font-family: monospace; width: 300px; color: #333; }}
                .text-center {{ text-align: center; }}
                .separador {{ border-top: 1px dashed #000; margin: 10px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th {{ text-align: left; border-bottom: 1px solid #ddd; }}
                td {{ padding: 5px 0; }}
            </style></head>
            <body>
                <h2 class="text-center" style="color: #2f6f3e;">REI AGRO</h2>
                <p class="text-center">Loja 02 - JD. Colina I<br>Fone: 19 989900845</p>
                <p class="text-center"><strong>Recibo de Compra</strong></p>
                <p>Cliente: {nome_para_venda}</p>
                <div class="separador"></div>
                <table>
                    <thead>
                        <tr><th>Item</th><th>Qtd</th><th>Total</th></tr>
                    </thead>
                    <tbody>
            """

            for item in itens:
                # Acessamos os dados diretamente do dicionário 'item' que vem do JavaScript
                nome_prod = item.get('produto', 'Produto')
                quantidade = item.get('quantidade', 0)
                unidade = item.get('unidade', '').lower()
                # Garantimos que o subtotal seja formatado como número
                subtotal = float(item.get('subtotal', 0))

                recibo_html += f"<tr><td>{nome_prod}</td><td>{quantidade} {unidade}</td><td>R$ {subtotal:.2f}</td></tr>"

            recibo_html += f"""
                    </tbody>
                </table>
                <div class="separador"></div>
                <p style="font-size: 1.2rem;"><strong>TOTAL: R$ {total_venda_calculado:.2f}</strong></p>
                <p>Forma de Pagamento: {forma_pagamento}</p>
                <div class="separador"></div>
                <p class="text-center">Agradecemos a preferência!<br>Volte sempre.</p>
            </body>
            </html>
            """

            # === NOVA FUNCIONALIDADE: ENVIO DE EMAIL ===
            try:
                if 'cliente_obj' in locals() and cliente_obj.email:
                    email_venda = EmailMessage(
                        subject=f'Recibo de Compra - Rei Agro - Pedido #{nova_venda.id}',
                        body=recibo_html,
                        from_email=None,  
                        to=[cliente_obj.email],
                    )
                    email_venda.content_subtype = "html"
                    email_venda.send()
            except Exception as mail_error:
                print(f"Erro ao enviar recibo por e-mail: {mail_error}")

            # RETORNO ÚNICO DE SUCESSO PARA O SCRIPT.JS
            return JsonResponse({
                'status': 'sucesso', 
                'mensagem': 'Venda salva com sucesso!',
                'recibo_html': recibo_html 
            })

        except Exception as e:
            # RETORNO ÚNICO DE ERRO
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400)

    # FORA DO POST: Busca os dados para renderizar a página inicial
    produtos = Produto.objects.all().order_by('data_validade', 'nome_produto')
    clientes = Cliente.objects.all()

    cpf_para_preencher = request.session.pop('cpf_novo', '')

    context = {
        'produtos': produtos,
        'clientes': clientes,
        'cpf_auto' : cpf_para_preencher,
    }

    return render(request, 'paginas/index.html', context)

@login_required
def buscar_produto_por_codigo(request):
    barcode = request.GET.get('barcode')
    # Buscamos todos os produtos que tenham esse código e estoque
    produtos = Produto.objects.filter(
        Q(codigo_barras=barcode) | Q(codigo_barras=f"G-{barcode}"),
        quantidade_estoque__gt=0
    ).order_by('-unidade_medida')

    if produtos.count() > 1:
        lista_produtos = []
        for p in produtos:
            lista_produtos.append({
                'id': p.id,
                'nome': p.nome_produto,
                'preco': str(p.preco_venda),
                'unidade': p.unidade_medida,
                'validade': p.data_validade.strftime('%d/%m/%Y') if p.data_validade else "N/A"
            })
        return JsonResponse({'status': 'multiplos', 'produtos': lista_produtos})
    
    elif produtos.count() == 1:
        p = produtos.first()
        return JsonResponse({
            'status': 'sucesso', 
            'id': p.id, 
            'nome': p.nome_produto, 
            'preco': str(p.preco_venda),
            'unidade': p.unidade_medida
        })
    
    return JsonResponse({'status': 'erro', 'mensagem': 'Produto não encontrado ou sem estoque.'})


@login_required
def buscar_cliente_cpf(request):
    cpf = request.GET.get('cpf')
    try:
        cliente = Cliente.objects.get(cpf=cpf)
        return JsonResponse({
            'status': 'sucesso', 
            'nome': cliente.nome, 
            'id': cliente.id,
            'tem_email': bool(cliente.email) # Retorna True se houver e-mail cadastrado
        })
    except Cliente.DoesNotExist:
        return JsonResponse({'status': 'erro', 'mensagem': 'Cliente não encontrado'}, status=404)

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
            
            # Salva o CPF na sessão do navegador de forma segura
            request.session['cpf_novo'] = cpf
            
            messages.success(request, "Cliente cadastrado com sucesso!")
            return redirect('home') 

        # --- Cadastro de produto ---
        elif 'nome_produto' in request.POST:
            nome_produto = request.POST.get('nome_produto')
            barcode = request.POST.get('barcode')
            data_val = request.POST.get('data_validade') or None
            id_cat = request.POST.get('id_categoria')
            id_forn = request.POST.get('id_fornecedor')
            
            # Identifica se é Nutrição Animal e se foi marcado para vender a granel
            is_granel = request.POST.get('venda_granel_especifica') == 'true'

            # TRATAMENTO DE VALORES (Preços e Quantidades)
            if is_granel:
                preco_v = request.POST.get('preco_venda_saco', '0').replace(',', '.')
                preco_c = request.POST.get('preco_custo', '0').replace(',', '.') 
                peso_informado = request.POST.get('peso_pacote', '0').replace(',', '.')
                # Fator de conversão é o peso do saco (ex: 20)
                fator_decimal = Decimal(peso_informado) 
                unidade_medida = 'PA' 
            else:
                preco_c = request.POST.get('preco_custo', '0').replace(',', '.')
                preco_v = request.POST.get('preco_venda', '0').replace(',', '.')
                unidade_medida = request.POST.get('unidade_medida')
                fator_decimal = Decimal('1.000')

            preco_custo_decimal = Decimal(preco_c)
            preco_venda_decimal = Decimal(preco_v)
            quantia = request.POST.get('quantia', '0')
            quantia_decimal = Decimal(quantia.replace(',', '.') or '0')

            categoria_instancia = Categoria.objects.get(id=id_cat)
            fornecedor_instancia = Fornecedor.objects.get(id=id_forn)

            # SALVAR O PRODUTO PRINCIPAL (PACOTE OU NORMAL)
            produto, criado = Produto.objects.get_or_create(
                codigo_barras=barcode,
                data_validade=data_val, # Importante: diferencia lotes no estoque
                defaults={
                    'nome_produto': nome_produto,
                    'categoria': categoria_instancia,
                    'fornecedor': fornecedor_instancia,
                    'preco_custo': preco_custo_decimal,
                    'preco_venda': preco_venda_decimal,
                    'unidade_medida': unidade_medida,
                    'fator_conversao': fator_decimal,
                    'quantidade_estoque': quantia_decimal,
                }
            )

            if not criado:
                produto.quantidade_estoque += quantia_decimal
                produto.preco_venda = preco_venda_decimal
                produto.save()

            # AUTOMAÇÃO DO VÍNCULO (Cria o item em KG se for granel)
            if is_granel:
                # O código do filho será sempre "G-" + código original
                barcode_filho = f"G-{barcode}"
                
                # BUSCA POR: Código de Barras (G-...) + Validade + Unidade KG
                produto_kg, filho_criado = Produto.objects.get_or_create(
                    codigo_barras=barcode_filho,
                    data_validade=data_val,
                    unidade_medida='KG',
                    defaults={
                        'nome_produto': f"{nome_produto} (A Granel)",
                        'categoria': categoria_instancia,
                        'fornecedor': fornecedor_instancia,
                        'produto_pai': produto, # Vincula ao lote/pacote específico
                        'preco_custo': preco_custo_decimal / (fator_decimal if fator_decimal > 0 else 1),
                        'preco_venda': Decimal(request.POST.get('preco_venda_kg', '0').replace(',', '.')),
                        'quantidade_estoque': Decimal('0.000'),
                        'fator_conversao': fator_decimal 
                    }
                )

                # Se o produto filho já existia (mesmo código e validade), 
                # garantimos que o vínculo com o pai atual esteja correto
                if not filho_criado:
                    produto_kg.produto_pai = produto
                    produto_kg.fator_conversao = fator_decimal
                    produto_kg.save()

            messages.success(request, "Produto cadastrado com sucesso!")
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
    trinta_dias = hoje + timedelta(days=30) # Define o intervalo de 1 mês
    # Filtra produtos da categoria específica
    # Certifique-se de que o nome no banco seja exatamente este
    produtos_nutricao = Produto.objects.filter(
        categoria__nome_categoria__icontains='Nutrição Animal',
        quantidade_estoque__gt=0  # Filtra apenas estoque maior que zero
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

    produtos_baixo_estoque = produtos_nutricao.filter(
        Q(unidade_medida='KG', quantidade_estoque__lt=15) | 
        Q(unidade_medida__in=['UN', 'PA', 'LT', 'MT'], quantidade_estoque__lt=5)
    ).order_by('quantidade_estoque')

    context = {
        'dados_grafico': dados_grafico,
        'produtos_vencidos': produtos_vencidos,
        'produtos_proximos': produtos_proximos,
        'produtos_baixo_estoque': produtos_baixo_estoque,
    }
    return render(request, 'paginas/relatorios.html', context)

@login_required
def fechamento(request):
    hoje = timezone.now().date()
    
    # Busca vendas do dia
    vendas_dia = Venda.objects.filter(data_venda__date=hoje)

    # Agrupa valores por forma de pagamento
    resumo_pagamentos = {
        'Dinheiro': vendas_dia.filter(forma_de_pagamento='Dinheiro').aggregate(Sum('valorTotal'))['valorTotal__sum'] or 0,
        'PIX': vendas_dia.filter(forma_de_pagamento='PIX').aggregate(Sum('valorTotal'))['valorTotal__sum'] or 0,
        'Crédito': vendas_dia.filter(forma_de_pagamento='Crédito').aggregate(Sum('valorTotal'))['valorTotal__sum'] or 0,
        'Débito': vendas_dia.filter(forma_de_pagamento='Débito').aggregate(Sum('valorTotal'))['valorTotal__sum'] or 0,
    }

    total_vendido = sum(resumo_pagamentos.values())
    
    # Busca fundo de abertura anterior (seu código existente)
    ultimo_fechamento = FechamentoCaixa.objects.order_by('-data_criacao').first()
    fundo_abertura_anterior = ultimo_fechamento.fundo_reserva_proximo_dia if ultimo_fechamento else 0
    
    context = {
        'resumo': resumo_pagamentos,
        'total_vendido': total_vendido,
        'vendas_dinheiro': resumo_pagamentos['Dinheiro'],
        'fundo_abertura_anterior': fundo_abertura_anterior,
    }
    return render(request, 'paginas/fechamento.html', context)

@login_required
def processar_fechamento(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            fechamento = FechamentoCaixa.objects.create(
                operador=request.user,
                vendas_dinheiro_sistema=Decimal(str(data.get('vendas_sistema'))),
                dinheiro_em_caixa=Decimal(str(data.get('total_em_caixa'))),
                fundo_reserva_proximo_dia=Decimal(str(data.get('fundo_caixa'))),
                valor_recolhido=Decimal(str(data.get('recolhimento'))),
            )

            sangrias_enviadas = data.get('sangrias', [])
            for s in sangrias_enviadas:
                Sangria.objects.create(
                    fechamento=fechamento,
                    motivo=s['motivo'],
                    valor=Decimal(str(s['valor']))
                )

            return JsonResponse({'status': 'sucesso', 'mensagem': 'Caixa fechado com sucesso!'})
        except Exception as e:
            return JsonResponse({'status': 'erro', 'mensagem': str(e)}, status=400)
    
    return JsonResponse({'status': 'erro', 'mensagem': 'Método inválido'}, status=405)


@login_required
def desmembrar(request, produto_id):
    if request.method == 'POST':
        #  Pega o PACOTE
        produto_pacote = get_object_or_404(Produto, id=produto_id)

        # Busca o KG que tenha o mesmo PAI e a MESMA VALIDADE
        produto_granel = Produto.objects.filter(
            produto_pai=produto_pacote, 
            unidade_medida='KG',
            data_validade=produto_pacote.data_validade 
        ).first()

        # Tenta buscar pelo código G- caso o vínculo de ID falhe
        if not produto_granel:
            barcode_filho = f"G-{produto_pacote.codigo_barras}"
            produto_granel = Produto.objects.filter(
                codigo_barras=barcode_filho,
                data_validade=produto_pacote.data_validade,
                unidade_medida='KG'
            ).first()

        if not produto_granel:
            # Mensagem detalhada para te ajudar a debugar
            msg = f"Vínculo não encontrado! Não existe um produto KG com a validade {produto_pacote.data_validade} associado ao pacote {produto_pacote.nome_produto}."
            messages.error(request, msg)
            return redirect('operacao')

        # Executa a conversão de estoque
        peso_informado = request.POST.get('peso_manual')
        try:
            peso_decimal = Decimal(peso_informado.replace(',', '.'))
            
            if produto_pacote.quantidade_estoque >= 1:
                produto_pacote.quantidade_estoque -= 1
                produto_pacote.save() 

                produto_granel.quantidade_estoque += peso_decimal
                produto_granel.save() 

                messages.success(request, f"Concluído! 1 pacote de {produto_pacote.nome_produto} virou {peso_decimal}kg.")
            else:
                messages.error(request, "Estoque de pacotes insuficiente.")
                
        except (ValueError, TypeError, AttributeError):
            messages.error(request, "Peso inválido informado.")

    return redirect('operacao')


@login_required
def operacao(request):
    query = request.GET.get('codigo_barras')
    pacotes = []
    if query:
        # Busca pacotes que tenham o código de barras informado
        pacotes = Produto.objects.filter(codigo_barras=query, unidade_medida='PA')
    
    # --- NOVA LÓGICA PARA PRODUTOS VENCIDOS ---
    hoje = timezone.now().date()
    vencidos_nutricao = Produto.objects.filter(
        categoria__nome_categoria__icontains='Nutrição Animal',
        data_validade__lt=hoje,
        quantidade_estoque__gt=0
    ).order_by('data_validade')

    # Busca categorias e fornecedores para o formulário de "Edição/Cadastro" do Granel
    categorias = Categoria.objects.all()
    fornecedores = Fornecedor.objects.all()
    
    return render(request, 'paginas/operacao.html', {
        'pacotes': pacotes,
        'categorias': categorias,
        'fornecedores': fornecedores,
        'query': query,
        'vencidos_nutricao': vencidos_nutricao, # Adicionado ao contexto
    })

@login_required
def confirmar_desmembramento(request):
    if request.method == 'POST':
        id_pai = request.POST.get('id_pai')
        pacote_pai = get_object_or_404(Produto, id=id_pai)
        
        nome = request.POST.get('nome_produto')
        preco_venda = request.POST.get('preco_venda').replace(',', '.')
        estoque_input = request.POST.get('estoque_inicial', '').strip().replace(',', '.')
        validade = request.POST.get('data_validade')

        # VALIDAÇÃO: Se o peso estiver vazio, interrompe o erro
        if not estoque_input:
            messages.error(request, "O campo 'Peso p/ adicionar' é obrigatório!")
            return redirect('operacao')

        try:
            estoque_decimal = Decimal(estoque_input)
            preco_venda_decimal = Decimal(preco_venda)
            
            if pacote_pai.quantidade_estoque >= 1:
                # 1. Tira do pacote
                pacote_pai.quantidade_estoque -= 1
                pacote_pai.save()
                
                # 2. Custo proporcional
                fator = pacote_pai.fator_conversao if pacote_pai.fator_conversao > 0 else 1
                preco_custo_kg = pacote_pai.preco_custo / fator

                # 3. Busca ou Cria Granel
                produto_granel, created = Produto.objects.get_or_create(
                    produto_pai=pacote_pai,
                    data_validade=validade,
                    unidade_medida='KG',
                    defaults={
                        'nome_produto': nome,
                        'preco_venda': preco_venda_decimal,
                        'preco_custo': preco_custo_kg,
                        'quantidade_estoque': 0,
                        'categoria': pacote_pai.categoria,
                        'fornecedor': pacote_pai.fornecedor,
                        'codigo_barras': f"G-{pacote_pai.codigo_barras}",
                        'fator_conversao': 1
                    }
                )
                
                # 4. Atualiza estoque e preço
                produto_granel.quantidade_estoque += estoque_decimal
                produto_granel.preco_venda = preco_venda_decimal
                produto_granel.save()
                
                messages.success(request, f"Sucesso! Foram adicionados {estoque_decimal}kg ao estoque.")
            else:
                messages.error(request, "Estoque de pacotes insuficiente.")
                
        except (InvalidOperation, ValueError):
            messages.error(request, "Valor de peso ou preço inválido!")
            
    return redirect('operacao')


@login_required
def excluir_produto_vencido(request, produto_id):
    if request.method == 'POST':
        produto = get_object_or_404(Produto, id=produto_id)
        nome = produto.nome_produto
        
        # Zera o estoque do produto selecionado
        produto.quantidade_estoque = 0
        produto.save()
        
        # Se for um produto pai, também zera o estoque dos filhos (granel)
        filhos = Produto.objects.filter(produto_pai=produto)
        if filhos.exists():
            filhos.update(quantidade_estoque=0)
            
        messages.warning(request, f"O estoque de '{nome}' e seus derivados foi zerado devido ao descarte.")
    
    return redirect('operacao')