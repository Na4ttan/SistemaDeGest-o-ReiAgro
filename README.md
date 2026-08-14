# 🐾 Sistema de Gestão Rei Agro

![Status](https://img.shields.io/badge/status-conclu%C3%ADdo-brightgreen)
![Django](https://img.shields.io/badge/Django-6.x-092E20)
![Python](https://img.shields.io/badge/Python-3.13-blue)

**Projeto Integrador I - Bacharelado em Tecnologia da Informação (UNIVESP)**

O **Rei Agro** é um ecossistema de gerenciamento desenvolvido especificamente para o setor de pet shop e produtos agropecuários. O sistema vai além do CRUD tradicional, incorporando inteligência de estoque, controle rigoroso de sanidade de produtos e automação de comunicação com o cliente.

---

## 🚀 Diferenciais do Projeto

Diferente de sistemas genéricos, esta aplicação foca na **prevenção de perdas** e na **agilidade do PDV**:

- **Gestão de Validade Inteligente:** Monitoramento automático de produtos vencidos ou próximos ao vencimento, com alertas visuais no dashboard.
- **Controle de Estoque Crítico:** Notificação de itens com baixo volume em estoque para otimização de compras.
- **Descarte Sustentável:** Funcionalidade para exclusão lógica e registro de produtos vencidos descartados pela loja.
- **Desmembramento de Produtos:** Permite a conversão de itens de atacado para varejo (fracionamento).
- **PDV com Recibo Digital:** Finalização de venda com envio automático de recibo em HTML via e-mail (SMTP), reduzindo o uso de papel.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.13
- **Framework Web:** Django 6.x
- **Banco de Dados:** SQLite (Desenvolvimento)
- **Segurança:** Variáveis de ambiente (`python-dotenv`) para proteção de credenciais.
- **Frontend:** HTML5, CSS3, JavaScript (ES6) e Bootstrap 5.
- **Ferramentas:** Git, GitHub, e leitor de código de barras via câmera (HTML5-QR Code).

---

## 📊 Estrutura de Dados (Modelagem)

A arquitetura do banco de dados foi projetada para garantir integridade referencial e histórico de transações:

- **Categoria & Fornecedor:** Estruturas de classificação e rastreabilidade de origem.
- **Produto:** Armazena dados críticos como preço de venda, unidade de medida (un/kg), data de validade e saldo em estoque.
- **Cliente:** Cadastro com identificação por CPF e canal de comunicação (e-mail) para envio de recibos.
- **Venda & ItensVenda:** Registro de transações financeiras, desdobrando múltiplos produtos em uma única venda e atualizando o estoque em tempo real.

---

## ⚙️ Funcionalidades Principais

1. **Dashboard de Alertas:** Listagem prioritária de produtos que exigem atenção (vencimento e estoque).
2. **Frente de Caixa (PDV):** Interface rápida com busca por código de barras, cálculo de troco e envio de e-mail.
3. **Gestão de Descarte:** Módulo para remoção de produtos impróprios para consumo, mantendo a conformidade do inventário.
4. **Operações de Fracionamento:** Lógica para desmembrar produtos e ajustar quantidades de acordo com a unidade de medida.

---

## 📸 Screenshots

<img width="899" height="640" alt="Imagem colada" src="https://github.com/user-attachments/assets/a8d05a21-51eb-4652-9e82-7af8dfc2dc37" />
<img width="1366" height="768" alt="Imagem colada (3)" src="https://github.com/user-attachments/assets/954d6187-9028-47d9-9af4-1da5b175aa00" />
<img width="899" height="679" alt="Imagem colada (2)" src="https://github.com/user-attachments/assets/4b64a126-3ff9-4b74-a526-07030d46232d" />
<img width="233" height="683" alt="Screenshot_20260514_114505_Brave" src="https://github.com/user-attachments/assets/bef7a37e-97e6-49cc-8b63-85b6cd1dd426" />
<img width="315" height="683" alt="Screenshot_20260514_114425_Brave" src="https://github.com/user-attachments/assets/ba0ca435-3e9f-4305-b18a-e43106ce5650" />

---

## 🔧 Como rodar o projeto

1. Clone o repositório:
   ```bash
   git clone https://github.com/Na4ttan/SistemaDeGest-o-ReiAgro.git
   cd SistemaDeGest-o-ReiAgro
   
2. Crie e ative o ambiente virtual:
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

3. Instale as dependências:
   pip install -r requirements.txt

4. Insira o email de envio de rebibo na linha 145 de settings.py, na variável 'EMAIL_HOST_USER' (⚠️ Use uma conta do Gmail)

5. Crie o arquivo .env na raiz do projeto com a seguinte variável:
   EMAIL_HOST_PASSWORD=sua_senha_de_app

6. Execute as migrações:
   python manage.py migrate

7. Inicie o servidor:
   python manage.py runserver

8. Acesse: http://127.0.0.1:8000

🧠 Desafios superados e aprendizados
Primeiro projeto Django: Aprendi na prática sobre ORM, views, autenticação e signals.

Lógica de desmembramento: Implementei conversão de pacote para KG controlando estoque e validade.

Segurança: Refatorei o transporte de CPF de URL para sessão (LGPD).

Trabalho solo: O projeto era para 8 pessoas; assumi a liderança e entreguei sozinho o sistema completo.

🌐 Acesso Online (Deploy)
O sistema está hospedado e pode ser acessado pelo link abaixo:
👉 https://na4ttan.pythonanywhere.com/

📄 Licença
Este projeto é acadêmico e não possui uma licença definida. Entre em contato para mais informações.
