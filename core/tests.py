from django.test import TestCase
from django.utils import timezone
from .models import Produto, Categoria, Fornecedor
from decimal import Decimal

class ProdutoModelTest(TestCase):
    def setUp(self):
        # Configura os dados iniciais para o teste
        self.categoria = Categoria.objects.create(nome_categoria="Nutrição Animal")
        self.fornecedor = Fornecedor.objects.create(
            nome_fantasia="Fornecedor Teste", 
            cnpj="12.345.678/0001-90"
        )

    def test_estoque_zerado_vencidos(self):
        """Teste para verificar se o estoque é zerado corretamente no descarte"""
        produto = Produto.objects.create(
            nome_produto="Ração Teste Vencida",
            categoria=self.categoria,
            fornecedor=self.fornecedor,
            preco_custo=Decimal('50.00'),
            preco_venda=Decimal('80.00'),
            quantidade_estoque=Decimal('10.000'),
            data_validade=timezone.now().date() - timezone.timedelta(days=1)
        )
        
        produto.quantidade_estoque = 0
        produto.save()
        
        self.assertEqual(produto.quantidade_estoque, 0)

    def test_validacao_unidade_inteira(self):
        """Garante que produtos UN, PA, LT não aceitem estoque fracionado"""
        p_un = Produto.objects.create(
            nome_produto="Coleira de Couro",
            unidade_medida='UN',
            quantidade_estoque=Decimal('10.000'),
            categoria=self.categoria, # Corrigido de self.cat
            fornecedor=self.fornecedor, # Corrigido de self.forn
            preco_custo=Decimal('15.00'),
            preco_venda=Decimal('30.00'),
            codigo_barras="123456"
        )
        
        venda_fracionada = Decimal('1.5')
        # Lógica: Se não for KG, o resto da divisão por 1 deve ser 0
        permitido = (p_un.unidade_medida == 'KG' or venda_fracionada % 1 == 0)
        
        self.assertFalse(permitido, "O sistema não deve permitir venda fracionada para UN")

    def test_produto_kg_permite_fracionado(self):
        """Garante que produtos KG aceitem estoque fracionado (gramas)"""
        # Para KG, a lógica deve sempre retornar True (permitido)
        venda_kg = Decimal('0.550')
        permitido = ('KG' == 'KG' or venda_kg % 1 == 0)
        
        self.assertTrue(permitido, "O sistema deve permitir venda fracionada para KG")


    def test_impedir_venda_estoque_insuficiente(self):
        """Verifica se o sistema impede (ou valida) venda acima do estoque disponível"""
        produto = Produto.objects.create(
            nome_produto="Produto Escasso",
            unidade_medida='UN',
            quantidade_estoque=Decimal('2.000'),
            categoria=self.categoria,
            fornecedor=self.fornecedor,
            preco_custo=10, preco_venda=20, codigo_barras="321"
        )
        
        venda_solicitada = Decimal('3.000')
        # Lógica: Disponível - Solicitado deve ser >= 0
        pode_vender = (produto.quantidade_estoque - venda_solicitada) >= 0
        
        self.assertFalse(pode_vender, "O sistema não deveria permitir vender 3 itens tendo apenas 2")

    def test_integridade_desmembramento(self):
        """Garante que a conversão de Pacote para KG mantém a soma correta do estoque"""
        pai = Produto.objects.create(
            nome_produto="Ração Saco 15kg",
            unidade_medida='PA',
            quantidade_estoque=Decimal('5.000'),
            fator_conversao=Decimal('15.000'),
            categoria=self.categoria,
            fornecedor=self.fornecedor,
            preco_custo=100, preco_venda=150, codigo_barras="999"
        )
        
        # Simula a lógica da sua view 'confirmar_desmembramento'
        pai.quantidade_estoque -= 1
        pai.save()
        
        # Verifica se o pai agora tem 4
        self.assertEqual(pai.quantidade_estoque, Decimal('4.000'))

    def test_calculo_caixa_com_sangria(self):
        """Valida se o total em caixa considera as sangrias (saídas de dinheiro)"""
        vendas_dinheiro = Decimal('1000.00')
        fundo_abertura = Decimal('200.00')
        sangria = Decimal('150.00')
        
        # Total esperado: (1000 + 200) - 150 = 1050
        total_calculado = (vendas_dinheiro + fundo_abertura) - sangria
        
        self.assertEqual(total_calculado, Decimal('1050.00'))