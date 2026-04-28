let itensVenda = [];

document.addEventListener('DOMContentLoaded', function () {

  // --- FUNCIONALIDADE 1: MENU DE NAVEGAÇÃO ---
  const menuLateral = document.getElementById('menuLateral');
  // Adicionamos uma verificação 'if' para evitar erros em páginas que não têm o menu
  if (menuLateral) {
    const bsOffcanvas = new bootstrap.Offcanvas(menuLateral);
    const links = menuLateral.querySelectorAll('.nav-link');

    links.forEach(link => {
      link.addEventListener('click', () => {
        if (menuLateral.classList.contains('show')) {
          bsOffcanvas.hide();
        }
      });
    });
  }

  // --- FUNCIONALIDADE 2: PDV (VENDA) ---
  const selectProduto = document.getElementById('select-produto');
  const inputPreco = document.getElementById('input-preco');
  const inputQuantidade = document.getElementById('input-quantidade');

  // Verifica se estamos na página de venda antes de rodar a lógica
  if (selectProduto) {
  selectProduto.addEventListener('change', function () {
    const option = this.options[this.selectedIndex];
    const preco = option.getAttribute('data-preco');
    const unidade = option.getAttribute('data-unidade'); // Pegando a unidade

    if (preco) {
      const valor = parseFloat(preco);
      inputPreco.value = valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
      inputPreco.setAttribute('data-valor-puro', preco);
    }

    // REGRA DE GRANEL:
    if (unidade === 'KG') {
      inputQuantidade.step = "0.001"; // Permite 3 casas decimais
    } else {
      inputQuantidade.step = "1";     // Bloqueia as setas do teclado para inteiros
      inputQuantidade.value = Math.round(inputQuantidade.value) || 1; // Arredonda se já houver valor
    }
  });
}
  

  // Função Global para adicionar item
// Função Global para adicionar item
window.adicionarItem = function () {
  if (!selectProduto || !inputPreco) return;

  const option = selectProduto.options[selectProduto.selectedIndex];
  const produtoId = selectProduto.value; // Adicionado
  const nomeExibicao = option.text; // Adicionado
  const unidadeMedida = option.getAttribute('data-unidade');
  const precoPuro = inputPreco.getAttribute('data-valor-puro'); // Adicionado
  
  const qtdString = inputQuantidade.value.replace(',', '.');
  const qtd = parseFloat(qtdString);

  // 1. Validação de seleção
  if (!produtoId || !precoPuro) {
    alert("Por favor, selecione um produto primeiro!");
    return;
  }

  // 2. Validação de quantidade zero ou negativa
  if (qtd <= 0 || isNaN(qtd)) {
    alert("A quantidade deve ser maior que zero!");
    return;
  }

  // 3. VALIDAÇÃO DE FRAÇÃO
  // Se não for KG e a quantidade tiver casas decimais
  if (unidadeMedida !== 'KG' && qtd % 1 !== 0) {
    alert("Produtos com unidade '" + unidadeMedida + "' só podem ser vendidos em quantidades inteiras!");
    return;
  }

  // 4. Adiciona ao array
  itensVenda.push({
    id: produtoId,
    produto: nomeExibicao,
    unidade: unidadeMedida,
    quantidade: qtd,
    preco: parseFloat(precoPuro),
    subtotal: parseFloat(precoPuro) * qtd
  });

  // 5. Atualiza a tela e limpa os campos
  atualizarResumo();

  selectProduto.value = "";
  inputPreco.value = "";
  inputQuantidade.value = 1;
  inputQuantidade.step = "1"; // Reseta o step para o padrão
};

  window.removerItem = function (index) {
    // Remove 1 elemento na posição 'index'
    itensVenda.splice(index, 1);

    // Chama a função que já existe para redesenhar a lista e o total
    atualizarResumo();
  };

  function atualizarResumo() {
    const lista = document.getElementById('lista-itens-venda');
    const totalExibicao = document.getElementById('valor-total-exibicao');
    const contador = document.getElementById('contador-itens');

    if (!lista) return;

    let totalGeral = 0;
    lista.innerHTML = '';

    itensVenda.forEach((item, index) => {
      totalGeral += item.subtotal;
      lista.innerHTML += `
    <div class="sale-item d-flex justify-content-between align-items-center">
        <div>
            <strong>${item.produto}</strong>
            <small class="d-block">${item.quantidade} ${item.unidade.toLowerCase()}</small>
        </div>
        <div class="d-flex align-items-center">
            <span class="me-3">R$ ${item.subtotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
            <button type="button" onclick="removerItem(${index})" class="btn btn-sm btn-outline-danger border-0">
                <i class="bi bi-x-circle"></i>
            </button>
        </div>
    </div>`;
    });

    if (totalExibicao) totalExibicao.innerText = `R$ ${totalGeral.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    if (contador) contador.innerText = `${itensVenda.length} item(ns)`;
  }
});

window.finalizarVenda = function () {
  const formaPagamento = document.getElementById('select-pagamento').value;
  const clienteSelect = document.getElementById('select-cliente');
  const clienteNome = clienteSelect.options[clienteSelect.selectedIndex].text;

  if (itensVenda.length === 0) {
    alert("Adicione pelo menos um produto!");
    return;
  }

  // Dados que vamos enviar
  const dadosVenda = {
    cliente: clienteNome,
    forma_pagamento: formaPagamento,
    itens: itensVenda
  };

  // Enviando para o Django
  fetch('', { // O '' significa que envia para a mesma URL atual
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
    },
    body: JSON.stringify(dadosVenda)
  })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'sucesso') {
        alert("Venda realizada com sucesso!");
        location.reload(); // Recarrega a página para limpar tudo
      } else {
        alert("Erro ao salvar: " + data.mensagem);
      }
    });
};