# Controle de Suprimentos e Manutenção

Este é um sistema robusto desenvolvido em **Django** para gestão de suprimentos e controle técnico de manutenção de equipamentos (Computadores, Impressoras e Periféricos).

## 🚀 Funcionalidades Principais

### 1. Gestão de Suprimentos
- Cadastro de **Projetos** e **Unidades**.
- Controle de estoque de suprimentos.
- Registro de **Entregas de Suprimentos** por setor e unidade.

### 2. Inventário de Equipamentos
- Registro detalhado de máquinas (Patrimônio, Marca, Modelo, Tipo).
- Integração com dados de sistema operacional e hardware.

### 3. Módulo de Manutenção (Tickets)
Este é o módulo mais avançado do sistema, focado no suporte técnico.
- **Abertura de Tickets**: Interface dinâmica que se adapta ao tipo de equipamento.
    - **Desktops**: Permite detalhar estado de Processador, Placa-Mãe, Memória RAM (por pente), Fonte, Cooler e Armazenamento.
    - **Periféricos/Impressoras**: Foca no estado geral e marca/modelo específicos.
- **Diagnóstico Automático**: O sistema gera um texto técnico consolidado baseado nos estados dos componentes selecionados ("Bom", "Ruim", "Não contém").
- **Edição Persistente**: O formulário de edição recupera todos os estados de hardware e diagnóstico previamente salvos.

### 4. Relatórios e Exportação
- **Dashboard de Tickets**: Visualização em cards com status coloridos (Aberto, Aguardando Peças, Finalizado, Condenado, etc.).
- **Resumo de Peças Defeituosas**: Página dedicada que agrupa todos os componentes que precisam ser repostos.
- **Exportação Excel Premium**: Gera um arquivo `.xlsx` organizado em 3 abas:
    - **Aba 1: Peças Necessárias**: Agrupa por componente, especificando a quantidade e os chamados vinculados. **Filtro**: Exclui tickets `FINALIZADO` e `CONDENADO`.
    - **Aba 2: Todos os Tickets**: Lista todos os tickets (exceto "FINALIZADO") com data, ID, técnico, status, modelo, a nova coluna de **Peças Defeituosas/Faltantes** e a de **Observações**.
    - **Aba 3: Equipamentos Condenados**: Seção exclusiva com os descartes (status `CONDENADO`), incluindo a coluna de **Peças Defeituosas/Faltantes** e a de **Observação**.

## 🛠️ Tecnologias Utilizadas
- **Backend**: Python 3.11+ / Django 4.2+
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção).
- **Frontend**: HTML5, Vanilla CSS, JavaScript (ES6+), Bootstrap 5.
- **Bibliotecas**:
    - `openpyxl`: Geração e formatação de relatórios Excel.
    - `Bootstrap Icons`: Ícones da interface.

## 📂 Estrutura do Projeto (App: `cltsupri`)
- `models.py`: Define `TicketManutencao` com campos JSON para detalhes de memória RAM e diagnósticos automáticos.
- `views.py`: Contém a lógica complexa de exportação Excel e agregação de defeitos.
- `templates/`:
    - `novo_ticket.html`: Formulário dinâmico com lógica JS para diagnósticos em tempo real.
    - `relatorio_tickets.html`: Histórico de chamados.
- `admin.py`: Customização completa do painel administrativo para o modelo de manutenção.

## 📝 Notas para Desenvolvimento Futuro
- **Lógica de RAM**: O campo `ram_pentes_detalhes` é armazenado como JSON. Ao editar, o JavaScript lê esse JSON para reconstruir a lista de pentes na tela.
- **Exportação**: Ao adicionar novos campos ao relatório Excel, certifique-se de atualizar a lógica de `get_column_letter` para evitar erros em células mescladas.
- **Filtros**: A exportação Excel possui regras específicas por aba:
    - **Aba 1 (Peças)**: Exclui tickets com status `FINALIZADO` e `CONDENADO` (lista apenas o que realmente precisa ser comprado).
    - **Demais Abas**: Excluem apenas tickets `FINALIZADO`.

---
*Mantido por Gleison Medeiros*
