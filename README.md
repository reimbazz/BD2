# 📊 Sistema de Relatórios ADHOC

## 📋 Visão Geral

O **Sistema de Relatórios ADHOC** é uma aplicação web moderna e intuitiva que permite aos usuários criar relatórios dinâmicos e consultas personalizadas sem necessidade de conhecimento técnico em SQL. O sistema oferece uma interface visual para selecionar tabelas, configurar relacionamentos, aplicar filtros e gerar relatórios em tempo real.

## 🎯 Objetivo do Projeto

**Democratizar o acesso aos dados** através de uma ferramenta que:

- **Elimina a barreira técnica**: Usuários não precisam conhecer SQL para criar consultas complexas
- **Acelera a tomada de decisão**: Relatórios em tempo real com interface intuitiva
- **Reduz dependência de TI**: Analistas e gestores podem criar seus próprios relatórios
- **Garante qualidade dos dados**: Validações automáticas previnem erros nas consultas
- **Oferece flexibilidade total**: Suporte a joins, agregações, filtros e ordenações complexas

## 🛠️ Stack Tecnológica

### Frontend
- **Vue 3** - Framework reativo para interface de usuário
- **TypeScript** - Tipagem estática para maior robustez
- **Vuetify 3** - Biblioteca de componentes Material Design
- **Vite** - Build tool moderna e rápida
- **Axios** - Cliente HTTP para comunicação com a API

### Backend
- **FastAPI** - Framework Python moderno e performático
- **SQLAlchemy** - ORM poderoso para abstração do banco de dados
- **Pydantic** - Validação de dados e serialização
- **PostgreSQL** - Banco de dados relacional robusto
- **Uvicorn** - Servidor ASGI de alta performance

## 🏗️ Organização do Projeto

```
BD/
├── aplicacao/
│   ├── backend/                 # API em FastAPI
│   │   ├── main.py             # Ponto de entrada da aplicação
│   │   ├── controller/         # Controladores da API REST
│   │   ├── dao/               # Camada de acesso aos dados
│   │   ├── models/            # Modelos do banco de dados
│   │   └── requirements.txt   # Dependências Python
│   └── vite-project/          # Frontend em Vue 3
│       ├── src/
│       │   ├── components/    # Componentes reutilizáveis
│       │   │   └── adhoc/    # Componentes específicos do ADHOC
│       │   ├── services/     # Serviços de comunicação com API
│       │   ├── types/        # Definições de tipos TypeScript
│       │   ├── utils/        # Utilitários e funções auxiliares
│       │   └── config/       # Configurações da aplicação
│       └── package.json      # Dependências Node.js
└── carga_cidades_sem_populacao.py # Scripts de carga de dados
```

## 🎮 Funcionalidades Principais

### 1. **Seleção Inteligente de Tabelas**
- Listagem automática de todas as tabelas disponíveis no banco
- Detecção automática de relacionamentos entre tabelas
- Sugestões de joins baseadas em chaves estrangeiras
- Visualização clara da estrutura de relacionamentos

### 2. **Construção Visual de Relacionamentos (Joins)**
- Interface drag-and-drop para configurar joins
- Suporte a diferentes tipos de join (INNER, LEFT, RIGHT, FULL)
- Detecção automática de chaves de relacionamento
- Validação de integridade dos relacionamentos em tempo real

### 3. **Seleção Flexível de Atributos**
- Visualização de todas as colunas disponíveis das tabelas selecionadas
- Informações detalhadas sobre tipos de dados
- Aplicação de funções SQL (UPPER, LOWER, LENGTH, etc.)
- Seleção múltipla com botões "Selecionar Todos" e "Limpar"

### 4. **Sistema de Filtros Avançado**
- Filtros dinâmicos baseados no tipo de dados da coluna
- Operadores inteligentes (=, !=, LIKE, IN, BETWEEN, etc.)
- Validação de entrada em tempo real

### 5. **Agrupamento e Agregação**
- Suporte a funções de agregação (COUNT, SUM, AVG, MIN, MAX)
- Agrupamento por múltiplas colunas
- Geração automática de aliases descritivos
- Validação das regras de GROUP BY do SQL

### 6. **Ordenação Hierárquica**
- Ordenação por múltiplas colunas
- Direção ascendente ou descendente
- Reordenação por prioridade
- Compatibilidade com colunas agregadas

### 7. **Visualização e Exportação**
- Exibição tabular dos resultados
- Paginação automática para grandes volumes
- Visualização da query SQL gerada
- Opções de exportação (CSV, Excel, PDF)

## 🧩 Componentes do Frontend

### **AdhocReport.vue** - Componente Orquestrador
**Função**: Componente principal que gerencia todo o fluxo da aplicação
**Lógica**: 
- Centraliza o estado global da aplicação (tabelas, atributos, joins, filtros)
- Coordena a comunicação entre todos os componentes filhos
- Gerencia o ciclo de vida dos dados (carregamento, validação, envio)
- Implementa watchers para sincronização automática entre componentes
- Executa validações antes de gerar o relatório final

### **TableSelector.vue** - Seletor de Tabelas
**Função**: Permite ao usuário escolher a tabela principal para o relatório
**Lógica**:
- Carrega lista de tabelas disponíveis do banco de dados
- Emite eventos quando uma tabela é selecionada
- Atualiza automaticamente as opções de join disponíveis
- Limpa seleções dependentes quando a tabela muda

### **AttributeSelector.vue** - Seletor de Atributos
**Função**: Interface para seleção das colunas que aparecerão no relatório
**Lógica**:
- Recebe lista de atributos disponíveis das tabelas selecionadas
- Implementa seleção múltipla com checkboxes
- Mantém sincronia entre estado local e estado pai
- Oferece funcionalidades de "Selecionar Todos" e "Limpar Seleção"
- Evita loops de reatividade através de validações de mudança

### **JoinTables.vue** - Configurador de Relacionamentos
**Função**: Interface para configurar joins entre tabelas
**Lógica**:
- Busca automaticamente relacionamentos possíveis via foreign keys
- Valida a integridade dos relacionamentos configurados
- Suporta joins transitivos (através de tabelas intermediárias)
- Atualiza atributos disponíveis conforme joins são adicionados

### **Filters.vue** - Sistema de Filtros
**Função**: Criação de condições WHERE dinâmicas
**Lógica**:
- Adapta operadores disponíveis baseado no tipo de dados
- Implementa validação de entrada específica por tipo
- Suporta múltiplos filtros com lógica AND/OR
- Oferece interface intuitiva para valores (input, select, date picker)
- Gera automaticamente parâmetros seguros para evitar SQL injection

### **GroupBy.vue** - Agrupamento e Agregação
**Função**: Configuração de agrupamentos e funções de agregação
**Lógica**:
- Detecta automaticamente funções compatíveis com cada tipo de dados
- Gera aliases automáticos para funções de agregação
- Valida regras do SQL (colunas não agregadas devem estar no GROUP BY)
- Permite múltiplas funções de agregação simultâneas
- Sincroniza com outros componentes para manter consistência

### **OrderBy.vue** - Ordenação de Resultados
**Função**: Configuração da ordenação dos resultados
**Lógica**:
- Suporta ordenação por múltiplas colunas em ordem de prioridade
- Inclui colunas originais e colunas agregadas
- Permite alteração da direção (ASC/DESC) individual
- Implementa reordenação de prioridades
- Valida se as colunas selecionadas estão disponíveis

### **ReportViewer.vue** - Visualizador de Resultados
**Função**: Exibição dos dados do relatório gerado
**Lógica**:
- Renderiza dados em formato tabular responsivo
- Implementa paginação automática para performance
- Mostra indicadores de carregamento e tratamento de erros
- Oferece visualização da query SQL gerada
- Integra funcionalidades de exportação

## 🔄 Fluxo de Funcionamento

### 1. **Inicialização**
Ao carregar a aplicação, o sistema busca automaticamente todas as tabelas disponíveis no banco de dados e apresenta na interface de seleção.

### 2. **Seleção de Tabela Base**
O usuário escolhe uma tabela principal. O sistema automaticamente:
- Carrega todos os atributos da tabela
- Busca relacionamentos possíveis com outras tabelas
- Atualiza as opções de join disponíveis

### 3. **Configuração de Relacionamentos**
Se necessário, o usuário pode adicionar outras tabelas através de joins:
- O sistema sugere relacionamentos baseados em foreign keys
- Atributos de todas as tabelas joineadas ficam disponíveis

### 4. **Seleção de Atributos**
O usuário escolhe quais colunas aparecerão no relatório:
- Lista mostra todas as colunas disponíveis das tabelas selecionadas
- Informações de tipo de dados ajudam na seleção
- Funções SQL podem ser aplicadas aos atributos

### 5. **Aplicação de Filtros**
O usuário pode adicionar condições para filtrar os dados:
- Interface adapta-se ao tipo de dados da coluna
- Múltiplos filtros podem ser combinados com lógica AND/OR
- Validação previne erros de entrada

### 6. **Configuração de Agrupamento**
Para relatórios analíticos, o usuário pode:
- Agrupar por uma ou mais colunas
- Aplicar funções de agregação (COUNT, SUM, AVG, etc.)
- Sistema valida automaticamente as regras do GROUP BY

### 7. **Definição de Ordenação**
O usuário define como os resultados serão ordenados:
- Múltiplas colunas em ordem de prioridade
- Direção ascendente ou descendente para cada coluna
- Compatibilidade com colunas agregadas

### 8. **Geração e Visualização**
O sistema gera a query SQL e executa:
- Validação final da estrutura da consulta
- Execução segura usando prepared statements
- Apresentação dos resultados em formato tabular
- Opções para visualizar a query SQL gerada

## 🔐 Segurança e Performance

### **Segurança**
- **Prepared Statements**: Prevenção automática contra SQL injection
- **Validação de Entrada**: Todos os dados são validados antes do processamento
- **Controle de Acesso**: Sistema preparado para integração com autenticação
- **Sanitização**: Limpeza automática de dados de entrada

### **Performance**
- **Connection Pooling**: Pool de conexões otimizado para o banco
- **Paginação Automática**: Limitação de resultados para evitar sobrecarga
- **Otimização de Queries**: Ordem otimizada de joins para melhor performance
- **Cache de Metadados**: Cache dos esquemas de tabelas para reduzir consultas

## 🚀 Como Executar

### **Pré-requisitos**
- Python 3.8+ instalado
- Node.js 16+ instalado
- PostgreSQL configurado
- Git para clonar o repositório

### **Backend**
```bash
cd BD/aplicacao/backend
pip install -r requirements.txt
python main.py
```

### **Frontend**
```bash
cd BD/aplicacao/vite-project
yarn install
yarn run dev
```

### **Acesso**
- Frontend: http://localhost:5173
- API Documentation: http://localhost:8000/docs
- API Base URL: http://localhost:8000/api/db

## 🎨 Características da Interface

### **Design Responsivo**
- Interface adaptável para desktop, tablet e mobile
- Componentes Material Design através do Vuetify
- Tema consistente com paleta de cores profissional

### **Experiência do Usuário**
- Fluxo intuitivo e progressivo
- Feedback visual em tempo real
- Indicadores de carregamento e progresso
- Mensagens de erro claras e acionáveis
- Tooltips e ajuda contextual

### **Acessibilidade**
- Suporte a navegação por teclado
- Contraste adequado para legibilidade
- Componentes semânticos HTML
- Compatibilidade com leitores de tela

## 📈 Benefícios Técnicos

### **Manutenibilidade**
- Código modular e bem estruturado
- Tipagem forte reduz bugs em produção
- Padrões de projeto facilitam evolução
- Documentação abrangente do código

### **Escalabilidade**
- Arquitetura desacoplada permite crescimento
- API RESTful facilita integrações
- Frontend componentizado para reutilização
- Banco de dados otimizado para consultas complexas

### **Confiabilidade**
- Tratamento robusto de erros
- Validações em múltiplas camadas
- Logs detalhados para debugging
- Testes automatizados (em desenvolvimento)


---

**Desenvolvido com ❤️ para democratizar o acesso aos dados**
