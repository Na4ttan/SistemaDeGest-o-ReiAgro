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

  const inputScan = document.getElementById('input-scan');

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
  if (inputScan) {
    inputScan.addEventListener('keypress', function (e) {
      if (e.key === 'Enter') {
        e.preventDefault(); // Evita que o formulário seja enviado acidentalmente
        const codigoBipado = this.value.trim();

        if (codigoBipado === "") return;

        let produtoEncontrado = false;

        // Procura o código nos atributos do select
        Array.from(selectProduto.options).forEach(option => {
          if (option.getAttribute('data-codigo') === codigoBipado) {
            // Seleciona o produto e dispara o 'change' para carregar preço/unidade
            selectProduto.value = option.value;
            selectProduto.dispatchEvent(new Event('change'));
            
            // Chama a função de adicionar que já existe
            window.adicionarItem();
            
            produtoEncontrado = true;
          }
        });

        if (!produtoEncontrado) {
          alert("Produto não encontrado!");
        }

        this.value = ''; // Limpa para o próximo bipe
        this.focus();    // Garante que o foco continue no campo de scan
      }
    });
  
}
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
  fetch('', {
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
        
        // NOVO: Abre uma nova janela para impressão do recibo
        const janelaRecibo = window.open('', '_blank');
        janelaRecibo.document.write(data.recibo_html);
        janelaRecibo.document.close();
        janelaRecibo.print(); // Opcional: abre a caixa de impressão automaticamente

        location.reload();
      } else {
        alert("Erro ao salvar: " + data.mensagem);
      }
    });
};

let html5QrCode;

window.alternarCamera = function() {
    const readerDiv = document.getElementById('reader');
    const btnCamera = document.querySelector('button[onclick="alternarCamera()"]'); // Seleciona o botão
    
    if (readerDiv.style.display === 'none' || readerDiv.style.display === '') {
        // PREPARAÇÃO PARA ABRIR
        readerDiv.style.display = 'block';
        btnCamera.innerHTML = '<i class="bi bi-camera-video-off"></i> Fechar Câmera'; // Altera ícone e texto
        btnCamera.classList.replace('btn-outline-rei', 'btn-danger'); // Opcional: muda a cor para vermelho
        startScanner();
    } else {
        // PREPARAÇÃO PARA FECHAR
        stopScanner();
        readerDiv.style.display = 'none';
        btnCamera.innerHTML = '<i class="bi bi-camera"></i> Abrir Câmera'; // Volta ao original
        btnCamera.classList.replace('btn-danger', 'btn-outline-rei'); // Volta a cor original
    }
}

function startScanner() {
    // Garante que se já houver uma instância rodando, ela seja limpa antes
    if (html5QrCode) {
        html5QrCode.clear();
    }

    html5QrCode = new Html5Qrcode("reader");

    // Configurações otimizadas para leitura de códigos de barras (que são mais largos)
    const config = { 
        fps: 15, // Aumentei um pouco o FPS para ficar mais fluido
        qrbox: { width: 300, height: 180 }, // Caixa retangular é melhor para código de barras de fábrica
        aspectRatio: 1.0 // Garante proporção quadrada no preview
    };

    // A preferência pela câmera traseira é dada pelo 'facingMode: environment'
    html5QrCode.start(
        { facingMode: { exact: "environment" } }, // 'exact' força a traseira, se falhar ele cai no catch
        config,
        (decodedText) => {
            const inputScan = document.getElementById('input-scan');
            inputScan.value = decodedText;
            
            // Dispara o evento de busca que já criamos
            const event = new KeyboardEvent('keypress', { 
                key: 'Enter',
                bubbles: true // Garante que o evento suba na árvore do DOM
            });
            inputScan.dispatchEvent(event);

            // Feedback tátil para o celular (vibração curta ao ler com sucesso)
            if (navigator.vibrate) {
                navigator.vibrate(100);
            }
        },
        (errorMessage) => { /* Ignora erros de frame para não poluir o console */ }
    ).catch(err => {
        // Se 'exact: environment' falhar (ex: PC sem câmera traseira), tenta o modo normal
        console.warn("Câmera traseira exata não encontrada, tentando modo padrão...");
        html5QrCode.start({ facingMode: "environment" }, config, (decodedText) => {
            document.getElementById('input-scan').value = decodedText;
            document.getElementById('input-scan').dispatchEvent(new KeyboardEvent('keypress', { key: 'Enter' }));
        }).catch(err2 => {
            alert("Erro crítico ao acessar câmera: " + err2);
            alternarCamera(); // Fecha o leitor se der erro total
        });
    });
}

function stopScanner() {
    if (html5QrCode && html5QrCode.isScanning) {
        html5QrCode.stop()
            .then(() => {
                html5QrCode.clear();
                console.log("Câmera desligada.");
            })
            .catch(err => console.error("Erro ao parar câmera:", err));
    }
}