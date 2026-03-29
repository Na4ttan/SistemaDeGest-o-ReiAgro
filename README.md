# Sistema de gestão Rei Agro
Como o foco é CRUD, Framework Web, Banco de Dados e Controle de Versão, aqui está uma proposta estruturada e profissional para o repositório da Rei Agro:

Projeto Integrador I - Sistema de Gerenciamento Rei Agro
Este repositório contém o software desenvolvido para o Projeto Integrador I do curso de Bacharelado em Tecnologia da Informação da UNIVESP. O sistema foi concebido para atender às necessidades da Rei Agro, uma pet shop e loja de produtos agropecuários, focando na organização de dados e automação de processos básicos.

🎯 Objetivo do Projeto
O objetivo principal é aplicar conceitos de desenvolvimento web para criar uma ferramenta que permita o gerenciamento completo (CRUD) de itens essenciais ao negócio, como produtos, clientes ou agendamentos, garantindo a integridade dos dados e a facilidade de uso.

🚀 Requisitos e Funcionalidades
Seguindo as diretrizes da disciplina, o projeto implementa um CRUD (Create, Read, Update, Delete) que permite:

Cadastro: Inclusão de novos registros no banco de dados.

Consulta: Visualização e listagem dos dados armazenados.

Edição: Atualização de informações existentes.

Exclusão: Remoção de registros de forma segura.

🛠️ Tecnologias Utilizadas
Para cumprir os requisitos de framework web e persistência de dados, utilizamos:

Linguagem: Python

Framework Web: Flask (ou Django, conforme sua implementação)

Banco de Dados: SQLite (persistência de dados local)

Controle de Versão: Git e GitHub

Frontend: HTML5, CSS3 e Jinja2 (template engine)

📂 Estrutura do Banco de Dados
Para atender aos requisitos de persistência e organização de dados, o sistema utiliza um banco de dados relacional com as seguintes tabelas principais, garantindo a integridade referencial do sistema da Rei Agro:

Categoria: Organização dos produtos (ex: rações, medicamentos, acessórios).

Fornecedor: Cadastro das empresas parceiras que fornecem os insumos.

Produto: Gestão do estoque com vínculo à categoria e ao fornecedor.

Cliente: Cadastro completo para controle de atendimento e histórico.

Venda: Registro das transações realizadas na loja.

Itens_venda: Tabela de relacionamento que detalha cada produto inserido em uma venda específica.

O sistema permite a gestão completa (CRUD) de todas as entidades mencionadas, assegurando que o usuário possa cadastrar, visualizar, atualizar e remover registros conforme a necessidade do negócio
