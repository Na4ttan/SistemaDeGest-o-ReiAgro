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
  let itensVenda = [];
  const selectProduto = document.getElementById('select-produto');
  const inputPreco = document.getElementById('input-preco');
  const inputQuantidade = document.getElementById('input-quantidade');

  // Verifica se estamos na página de venda antes de rodar a lógica
  if (selectProduto) {
    selectProduto.addEventListener('change', function () {
      const option = this.options[this.selectedIndex];
      const preco = option.getAttribute('data-preco');

      if (preco) {
        const valor = parseFloat(preco);
        inputPreco.value = valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
        inputPreco.setAttribute('data-valor-puro', preco);
      }
    });
  }

  // Função Global para adicionar item
  window.adicionarItem = function () {
    if (!selectProduto || !inputPreco) return;

    const clienteSelecionado = document.getElementById('select-cliente').value;

    const nome = selectProduto.value;
    const precoPuro = inputPreco.getAttribute('data-valor-puro');
    const qtd = parseInt(inputQuantidade.value);

    if (!nome || !precoPuro) {
      alert("Por favor, selecione um produto primeiro!");
      return;
    }

    itensVenda.push({
      produto: nome,
      quantidade: qtd,
      preco: parseFloat(precoPuro),
      subtotal: parseFloat(precoPuro) * qtd
    });

    atualizarResumo();

    // Limpa campos
    selectProduto.value = "";
    inputPreco.value = "";
    inputQuantidade.value = 1;
  };

  function atualizarResumo() {
    const lista = document.getElementById('lista-itens-venda');
    const totalExibicao = document.getElementById('valor-total-exibicao');
    const contador = document.getElementById('contador-itens');

    if (!lista) return;

    let totalGeral = 0;
    lista.innerHTML = '';

    itensVenda.forEach(item => {
      totalGeral += item.subtotal;
      lista.innerHTML += `
        <div class="sale-item">
            <div>
                <strong>${item.produto}</strong>
                <small>${item.quantidade} un.</small>
            </div>
            <span>R$ ${item.subtotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
        </div>`;
    });

    if (totalExibicao) totalExibicao.innerText = `R$ ${totalGeral.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    if (contador) contador.innerText = `${itensVenda.length} item(ns)`;
  }
});