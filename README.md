# 🐾 Sistema de Gestão Rei Agro

**Projeto Integrador I - Bacharelado em Tecnologia da Informação (UNIVESP)**

O **Rei Agro** é um ecossistema de gerenciamento desenvolvido especificamente para o setor de pet shop e produtos agropecuários. O sistema vai além do CRUD tradicional, incorporando inteligência de estoque, controle rigoroso de sanidade de produtos e automação de comunicação com o cliente.

## 🚀 Diferenciais do Projeto

Diferente de sistemas genéricos, esta aplicação foca na **prevenção de perdas** e na **agilidade do PDV**:

* **Gestão de Validade Inteligente:** Monitoramento automático de produtos vencidos ou próximos ao vencimento, com alertas visuais no dashboard.
* **Controle de Estoque Crítico:** Notificação de itens com baixo volume em estoque para otimização de compras.
* **Descarte Sustentável:** Funcionalidade para exclusão lógica e registro de produtos vencidos descartados pela loja.
* **Desmembramento de Produtos:** Permite a conversão de itens de atacado para varejo (fracionamento).
* **PDV com Recibo Digital:** Finalização de venda com envio automático de recibo em HTML via e-mail (SMTP), reduzindo o uso de papel.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.13
* **Framework Web:** Django 6.x
* **Banco de Dados:** SQLite (Desenvolvimento)
* **Segurança:** Variáveis de ambiente (`python-dotenv`) para proteção de credenciais.
* **Frontend:** HTML5, CSS3, JavaScript (ES6) e Bootstrap 5.
* **Ferramentas:** Git, GitHub, e leitor de código de barras via câmera (HTML5-QR Code).

## 📊 Estrutura de Dados (Modelagem)

A arquitetura do banco de dados foi projetada para garantir integridade referencial e histórico de transações:

* **Categoria & Fornecedor:** Estruturas de classificação e rastreabilidade de origem.
* **Produto:** Armazena dados críticos como preço de venda, unidade de medida (un/kg), data de validade e saldo em estoque.
* **Cliente:** Cadastro com identificação por CPF e canal de comunicação (e-mail) para envio de recibos.
* **Venda & ItensVenda:** Registro de transações financeiras, desdobrando múltiplos produtos em uma única venda e atualizando o estoque em tempo real.

## ⚙️ Funcionalidades Principais

1. **Dashboard de Alertas:** Listagem prioritária de produtos que exigem atenção (vencimento e estoque).
2. **Frente de Caixa (PDV):** Interface rápida com busca por código de barras, cálculo de troco e envio de e-mail.
3. **Gestão de Descarte:** Módulo para remoção de produtos impróprios para consumo, mantendo a conformidade do inventário.
4. **Operações de Fracionamento:** Lógica para desmembrar produtos e ajustar quantidades de acordo com a unidade de medida.

---

### 🔧 Como rodar o projeto

1. Clone o repositório.
2. Crie e ative seu ambiente virtual (`venv`).
3. Instale as dependências: `pip install -r requirements.txt`.
4. Crie o arquivo `.env` com suas credenciais de e-mail conforme o `settings.py`.
5. Execute as migrações: `python manage.py migrate`.
6. Inicie o servidor: `python manage.py runserver`.

---

🌐 Acesso Online (Deploy)
O sistema está hospedado e pode ser acessado pelo link abaixo:
👉 https://na4ttan.pythonanywhere.com/

Como você mencionou o **desmembramento** e a **exclusão de vencidos**, essa estrutura mostra para os professores da UNIVESP que você pensou em um problema real do comércio (perder produtos por data e precisar vender fracionado). Ficou muito bom!
