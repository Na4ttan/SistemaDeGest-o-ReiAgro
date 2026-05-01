let itensVenda = [];
let html5QrCode;

document.addEventListener('DOMContentLoaded', function () {

    // --- FUNCIONALIDADE 1: MENU DE NAVEGAÇÃO ---
    const menuLateral = document.getElementById('menuLateral');
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

    const inputCpf = document.getElementById('input-cpf');
    
    // Função que dispara a busca (refatorada para ser reutilizável)
    function dispararBuscaCpf() {
        if (inputCpf.value.length >= 11) {
            inputCpf.dispatchEvent(new Event('blur'));
        }
    }

    if (inputCpf && inputCpf.value !== "") {
        dispararBuscaCpf();
    }


    const selectProduto = document.getElementById('select-produto');
    const inputPreco = document.getElementById('input-preco');
    const inputQuantidade = document.getElementById('input-quantidade');
    const inputScan = document.getElementById('input-scan');

    if (selectProduto) {
        selectProduto.addEventListener('change', function () {
            const option = this.options[this.selectedIndex];
            const preco = option.getAttribute('data-preco');
            const unidade = option.getAttribute('data-unidade');

            if (preco) {
                const valor = parseFloat(preco);
                inputPreco.value = valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
                inputPreco.setAttribute('data-valor-puro', preco);
            }

            if (unidade === 'KG') {
                inputQuantidade.step = "0.001";
            } else {
                inputQuantidade.step = "1";
                inputQuantidade.value = Math.round(inputQuantidade.value) || 1;
            }
        });

        if (inputScan) {
            inputScan.addEventListener('keypress', function (e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const codigoBipado = this.value.trim();

                    if (codigoBipado === "") return;

                    let produtoEncontrado = false;

                    Array.from(selectProduto.options).forEach(option => {
                        const codigoNoBanco = option.getAttribute('data-codigo');

                        if (codigoNoBanco && codigoNoBanco.trim() === codigoBipado) {
                            selectProduto.value = option.value;
                            selectProduto.dispatchEvent(new Event('change'));
                            window.adicionarItem();
                            produtoEncontrado = true;
                        }
                    });

                    if (!produtoEncontrado) {
                        alert("Produto não encontrado!");
                    }

                    this.value = '';
                    this.focus();
                }
            });
        }
    }

    // Função Global para adicionar item
    window.adicionarItem = function () {
        if (!selectProduto || !inputPreco) return;

        const option = selectProduto.options[selectProduto.selectedIndex];
        const produtoId = selectProduto.value;
        const nomeExibicao = option.text;
        const unidadeMedida = option.getAttribute('data-unidade');
        const precoPuro = inputPreco.getAttribute('data-valor-puro');

        const qtdString = inputQuantidade.value.replace(',', '.');
        const qtd = parseFloat(qtdString);

        if (!produtoId || !precoPuro) {
            alert("Por favor, selecione um produto primeiro!");
            return;
        }

        if (qtd <= 0 || isNaN(qtd)) {
            alert("A quantidade deve ser maior que zero!");
            return;
        }

        if (unidadeMedida !== 'KG' && qtd % 1 !== 0) {
            alert("Produtos com unidade '" + unidadeMedida + "' só podem ser vendidos em quantidades inteiras!");
            return;
        }

        itensVenda.push({
            id: produtoId,
            produto: nomeExibicao,
            unidade: unidadeMedida,
            quantidade: qtd,
            preco: parseFloat(precoPuro),
            subtotal: parseFloat(precoPuro) * qtd
        });

        atualizarResumo();

        selectProduto.value = "";
        inputPreco.value = "";
        inputQuantidade.value = 1;
        inputQuantidade.step = "1";
    };

    window.removerItem = function (index) {
        itensVenda.splice(index, 1);
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

        if (typeof calcularTroco === "function") calcularTroco();
    }

    window.finalizarVenda = function () {
        const formaPagamento = document.getElementById('select-pagamento').value;
        const clienteId = document.getElementById('id-cliente-venda').value;
        
        if (itensVenda.length === 0) {
            alert("Adicione pelo menos um produto!");
            return;
        }

        const dadosVenda = {
            cliente: clienteId,
            forma_pagamento: formaPagamento,
            itens: itensVenda,
            total_venda : parseFloat(document.getElementById('valor-total-exibicao').innerText.replace('R$', '').replace(',', '.'))
        };

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
                const janelaRecibo = window.open('', '_blank');
                janelaRecibo.document.write(data.recibo_html);
                janelaRecibo.document.close();
                janelaRecibo.print();
                location.reload();
            } else {
                alert("Erro ao salvar: " + data.mensagem);
            }
        });
    };

    // --- LÓGICA DE TROCO ---
    const selectPagamento = document.getElementById('select-pagamento');
    const secaoTroco = document.getElementById('secao-troco');
    const inputRecebido = document.getElementById('input-valor-recebido');
    const displayTroco = document.getElementById('valor-troco');

    function calcularTroco() {
        // Captura o total atual da venda removendo o "R$" e formatando para número
        const totalVendaStr = document.getElementById('valor-total-exibicao').innerText
            .replace('R$', '').replace('.', '').replace(',', '.').trim();
        const totalVenda = parseFloat(totalVendaStr) || 0;
        
        const valorRecebido = parseFloat(inputRecebido.value) || 0;
        const troco = valorRecebido - totalVenda;

        if (troco > 0) {
            displayTroco.innerText = `R$ ${troco.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
            displayTroco.classList.replace('text-danger', 'text-success');
        } else if (troco < 0) {
            displayTroco.innerText = `Faltam R$ ${Math.abs(troco).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
            displayTroco.classList.replace('text-success', 'text-danger');
        } else {
            displayTroco.innerText = "R$ 0,00";
            displayTroco.classList.add('text-success');
        }
    }

    // Evento para mostrar/esconder campo de troco
    selectPagamento.addEventListener('change', function() {
        if (this.value === 'Dinheiro') {
            secaoTroco.style.display = 'block';
        } else {
            secaoTroco.style.display = 'none';
            inputRecebido.value = ''; // Limpa o campo se mudar de ideia
        }
    });

    // Evento para calcular enquanto o usuário digita
    inputRecebido.addEventListener('input', calcularTroco);

}); // 

// --- FUNÇÕES DA CÂMERA 

window.alternarCamera = function () {
    const readerDiv = document.getElementById('reader');
    const btnCamera = document.querySelector('button[onclick="alternarCamera()"]');
    const icone = document.getElementById('icone-camera');

    if (readerDiv.style.display === 'none' || readerDiv.style.display === '') {
        readerDiv.style.display = 'block';
        icone.className = 'bi bi-camera-video-off';
        btnCamera.classList.replace('btn-outline-rei', 'btn-danger');
        startScanner();
    } else {
        stopScanner();
        readerDiv.style.display = 'none';
        icone.className = 'bi bi-camera';
        btnCamera.classList.replace('btn-danger', 'btn-outline-rei');
    }
};

function startScanner() {
    if (html5QrCode) {
        html5QrCode.clear();
    }

    html5QrCode = new Html5Qrcode("reader");

    // Configuração básica de leitura
    const config = { 
        fps: 10, // Menos FPS exige menos processamento
        qrbox: { width: 250, height: 150 },
        aspectRatio: 1.0
    };

    // APENAS o essencial: Câmera traseira. Sem forçar resolução ou zoom por enquanto.
    html5QrCode.start(
        { facingMode: "environment" }, 
        config,
        (decodedText) => {
            const inputScan = document.getElementById('input-scan');
            inputScan.value = decodedText;
            inputScan.dispatchEvent(new KeyboardEvent('keypress', { key: 'Enter', bubbles: true }));
            if (navigator.vibrate) navigator.vibrate(100);
        }
    ).catch(err => {
        console.error("Erro ao iniciar:", err);
        alert("Erro: " + err); // Isso vai nos mostrar se o erro é 'Permission denied' ou 'NotFound'
    });
}

function stopScanner() {
    if (html5QrCode && html5QrCode.isScanning) {
        html5QrCode.stop()
            .then(() => {
                html5QrCode.clear();
            })
            .catch(err => console.error("Erro ao parar câmera:", err));
    }
}

document.getElementById('input-cpf').addEventListener('blur', function() {
    const cpf = this.value;
    const displayNome = document.getElementById('nome-cliente-cpf');
    const inputIdOculto = document.getElementById('id-cliente-venda');
    
    if (cpf.length >= 11) {
        fetch(`/buscar-cliente-cpf/?cpf=${cpf}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'sucesso') {
                    // Armazena o ID no input oculto e mostra o nome[cite: 5]
                    inputIdOculto.value = data.id;
                    displayNome.textContent = "Cliente: " + data.nome;
                    displayNome.className = "form-text text-success fw-bold mt-1";
                    displayNome.style.display = 'block';
                } else {
                    inputIdOculto.value = "";
                    displayNome.textContent = "Cliente não encontrado.";
                    displayNome.className = "form-text text-danger mt-1";
                    displayNome.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                inputIdOculto.value = "";
                displayNome.style.display = 'none';
            });
    } else {
        inputIdOculto.value = "";
        displayNome.style.display = 'none';
    }
});