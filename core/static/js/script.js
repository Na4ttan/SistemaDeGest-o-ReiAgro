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

                    // Nova lógica: Em vez de percorrer o select aqui, perguntamos ao servidor
                    fetch(`/buscar-produto-codigo/?barcode=${codigoBipado}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.status === 'multiplos') {
                                // Abre a modal para o usuário escolher o lote/validade
                                abrirModalEscolha(data.produtos);
                            } 
                            else if (data.status === 'sucesso') {
                                // Se achou só um, seleciona no select e dispara a adição
                                selectProduto.value = data.id;
                                selectProduto.dispatchEvent(new Event('change'));
                                window.adicionarItem();
                            } 
                            else {
                                alert("Produto não encontrado ou sem estoque!");
                            }
                        })
                        .catch(err => console.error("Erro na busca:", err));

                    this.value = '';
                    this.focus();
                }
            });
        }
    }

    // Função para preencher e mostrar a Modal
    function abrirModalEscolha(produtos) {
        const container = document.getElementById('container-escolha-produtos');
        container.innerHTML = ''; 

        produtos.forEach(p => {
            const btn = document.createElement('button');
            // Estilização compatível com o tema Rei Agro
            btn.className = 'btn btn-outline-primary text-start p-3 mb-2 d-flex justify-content-between align-items-center w-100';
            btn.innerHTML = `
                <div>
                    <strong>${p.nome}</strong><br>
                    <small class="text-muted">Validade: ${p.validade} | Un: ${p.unidade}</small>
                </div>
                <span class="badge bg-success">R$ ${parseFloat(p.preco).toLocaleString('pt-BR', {minimumFractionDigits: 2})}</span>
            `;
            
            btn.onclick = () => {
                // Vincula a escolha à estrutura existente do PDV
                selectProduto.value = p.id;
                selectProduto.dispatchEvent(new Event('change'));
                window.adicionarItem();
                
                // Fecha a modal do Bootstrap
                const modalElement = document.getElementById('modalEscolhaProduto');
                const modalInstance = bootstrap.Modal.getOrCreateInstance(modalElement);
                modalInstance.hide();
            };
            container.appendChild(btn);
        });

        const modalExibir = new bootstrap.Modal(document.getElementById('modalEscolhaProduto'));
        modalExibir.show();
    }

    // Função Global para adicionar item
    window.adicionarItem = function () {
    const codigoBipado = inputScan.value.trim();
    const produtoIdSelecionado = selectProduto.value;

    // 1. Lógica para quando o usuário clica no botão "Adicionar" manualmente
    // mas não selecionou nada no menu, apenas digitou/bipou o código.
    if (!produtoIdSelecionado && codigoBipado !== "") {
        fetch(`/buscar-produto-codigo/?barcode=${codigoBipado}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'multiplos') {
                    // Abre a modal se houver mais de um lote/tipo (PA ou KG)
                    abrirModalEscolha(data.produtos); 
                } 
                else if (data.status === 'sucesso') {
                    // Se só houver um, seleciona ele no select e chama a função novamente
                    selectProduto.value = data.id;
                    selectProduto.dispatchEvent(new Event('change'));
                    window.adicionarItem(); 
                } 
                else {
                    alert("Produto não encontrado ou sem estoque!");
                    inputScan.value = "";
                }
            })
            .catch(err => console.error("Erro na busca:", err));
        return; // Interrompe a execução para aguardar a resposta ou a escolha na modal
    }

    // 2. Lógica Original de Inserção (Executa quando já temos um ID selecionado)
    if (!selectProduto || !inputPreco) return;

    const produtoId = selectProduto.value;
    const option = selectProduto.options[selectProduto.selectedIndex];

    // Se o select continuar vazio após a verificação acima, não faz nada
    if (!produtoId) {
        return; 
    }

    const precoPuro = inputPreco.getAttribute('data-valor-puro');
    const unidadeMedida = option ? option.getAttribute('data-unidade') : '';
    const nomeExibicao = option ? option.text : '';
    const qtd = parseFloat(inputQuantidade.value.replace(',', '.'));

    if (qtd <= 0 || isNaN(qtd)) {
        alert("A quantidade deve ser maior que zero!");
        return;
    }

    if (unidadeMedida !== 'KG' && qtd % 1 !== 0) {
        alert("Produtos com unidade '" + unidadeMedida + "' só podem ser vendidos em quantidades inteiras!");
        return;
    }

    // Adiciona à lista de vendas
    itensVenda.push({
        id: produtoId,
        produto: nomeExibicao,
        unidade: unidadeMedida,
        quantidade: qtd,
        preco: parseFloat(precoPuro),
        subtotal: parseFloat(precoPuro) * qtd
    });

    atualizarResumo();

    // Limpa os campos para o próximo item
    selectProduto.value = "";
    inputPreco.value = "";
    inputScan.value = "";
    inputQuantidade.value = 1;
    inputQuantidade.step = "1";
    inputScan.focus();
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

    // Função global para remover item do array e atualizar a tela
    window.removerItem = function (index) {
        // Remove 1 item do array itensVenda na posição 'index'
        itensVenda.splice(index, 1);
        
        // Redesenha a lista e recalcula o total
        atualizarResumo();
    };

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
                // --- NOVA LÓGICA DE DECISÃO ---
                const inputIdOculto = document.getElementById('id-cliente-venda');
                const temEmail = inputIdOculto.getAttribute('data-tem-email') === 'true';

                if (!temEmail) {
                    // SE NÃO TEM EMAIL: Injeta o HTML e abre o modal para WhatsApp
                    const containerRecibo = document.getElementById('conteudo-recibo-a6');
                    if (containerRecibo) {
                        containerRecibo.innerHTML = data.recibo_html;
                    }

                    const elementoModal = document.getElementById('modalRecibo');
                    if (elementoModal) {
                        const modalInstancia = new bootstrap.Modal(elementoModal);
                        modalInstancia.show();
                    }
                } else {
                    // SE TEM EMAIL: Apenas avisa que já foi enviado
                    alert("Venda concluída! O recibo foi enviado para o e-mail do cliente.");
                }

                // --- LIMPEZA DOS DADOS ---
                itensVenda = [];
                atualizarResumo();
                document.getElementById('valor-total-exibicao').textContent = "R$ 0,00";
                document.getElementById('input-cpf').value = "";
                document.getElementById('nome-cliente-cpf').style.display = 'none';
                
                // Reseta a etiqueta de e-mail para a próxima venda
                inputIdOculto.setAttribute('data-tem-email', 'false');

            } else {
                alert('Erro ao finalizar venda: ' + data.mensagem);
            }
        });
    };

    // --- LÓGICA DE TROCO ---
    const selectPagamento = document.getElementById('select-pagamento');
    const secaoTroco = document.getElementById('secao-troco');
    const inputRecebido = document.getElementById('input-valor-recebido');
    const displayTroco = document.getElementById('valor-troco');

    function calcularTroco() {
       
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
let processandoLeitura = false;
let travaLeituraAtiva = false;

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

    const modalReciboElement = document.getElementById('modalRecibo');
    if (modalReciboElement) {
        modalReciboElement.addEventListener('hidden.bs.modal', function () {
            // Limpa as travas de layout do Bootstrap
            document.body.classList.remove('modal-open');
            document.body.removeAttribute('style');
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(b => b.remove());
        });
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
            if (processandoLeitura) return;

            processandoLeitura = true;

            const inputScan = document.getElementById('input-scan');
            const inputBarcode = document.getElementById('barcode');

            if (inputScan) {
                inputScan.value = decodedText;
                
                // Em vez de simular o Enter, chama a função de adicionar direto para ser mais robusto
                if (typeof window.adicionarItem === "function") {
                    window.adicionarItem();
                }

                if (navigator.vibrate) navigator.vibrate(100);

                // Libera para o próximo "bip" após 2 segundos
                setTimeout(() => {
                    processandoLeitura = false;
                }, 2000);

            } else if (inputBarcode) {
                inputBarcode.value = decodedText;
                if (navigator.vibrate) navigator.vibrate(100);

                // No cadastro, fecha a câmera após ler e reseta a trava
                window.alternarCamera(); 
                processandoLeitura = false;
            }
       
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
                    inputIdOculto.value = data.id;
                    
                    // AQUI ESTÁ A ALTERAÇÃO: Guardamos se o cliente tem e-mail
                    inputIdOculto.setAttribute('data-tem-email', data.tem_email); 
                    
                    displayNome.textContent = "Cliente: " + data.nome;
                    displayNome.className = "form-text text-success fw-bold mt-1";
                    displayNome.style.display = 'block';
                } else {
                    inputIdOculto.value = "";
                    // Se não encontrou o cliente, resetamos a etiqueta de e-mail
                    inputIdOculto.setAttribute('data-tem-email', 'false');
                    
                    displayNome.textContent = "Cliente não encontrado.";
                    displayNome.className = "form-text text-danger mt-1";
                    displayNome.style.display = 'block';
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                inputIdOculto.value = "";
                inputIdOculto.setAttribute('data-tem-email', 'false');
                displayNome.style.display = 'none';
            });
    } else {
        inputIdOculto.value = "";
        inputIdOculto.setAttribute('data-tem-email', 'false');
        displayNome.style.display = 'none';
    }
});

window.compartilharRecibo = async function() {
    if (!window.jspdf || !window.html2canvas) {
        alert("Carregando componentes... Tente novamente.");
        return;
    }

    const { jsPDF } = window.jspdf;
    const elemento = document.getElementById('conteudo-recibo-a6');

    try {
        // Escala 3 mantém a nitidez da fonte pequena
        const canvas = await html2canvas(elemento, { 
            scale: 3,
            useCORS: true
        });
        const imgData = canvas.toDataURL('image/png');

        // Largura de 80mm é ideal para leitura em celular
        const larguraPdf = 80; 
        const alturaPdf = (canvas.height * larguraPdf) / canvas.width;

        const pdf = new jsPDF({
            orientation: 'p',
            unit: 'mm',
            format: [larguraPdf, alturaPdf + 5] 
        });

        // Adiciona a imagem ocupando a largura total disponível
        pdf.addImage(imgData, 'PNG', 0, 2, larguraPdf, alturaPdf);
        
        const pdfBlob = pdf.output('blob');
        const arquivo = new File([pdfBlob], "recibo_rei_agro.pdf", { type: "application/pdf" });

        if (navigator.canShare && navigator.canShare({ files: [arquivo] })) {
            await navigator.share({ files: [arquivo], title: 'Recibo Rei Agro' });
        } else {
            pdf.save("recibo_rei_agro.pdf");
        }
    } catch (err) {
        console.error("Erro na geração do PDF:", err);
    }
};