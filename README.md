# Aplicação de Geração de Relatórios ADHOC para Banco de Dados

Este projeto consiste em uma aplicação para geração de relatórios ADHOC, permitindo que usuários criem relatórios personalizados a partir de consultas dinâmicas em um banco de dados, sem a necessidade de conhecimento avançado em SQL.

## Estrutura do Projeto

O projeto está dividido em duas partes principais:

1. **Backend**: API RESTful desenvolvida com FastAPI e SQLAlchemy em Python
2. **Frontend**: Interface de usuário desenvolvida com Vue.js 3 e Vuetify

## Configuração do Ambiente

### Requisitos
- Python 3.10+
- Node.js 16+
- PostgreSQL

### Configuração do Backend
1. Instale as dependências:
```bash
cd BD/aplicacao/backend
pip install -r requirements.txt
```

2. Execute o servidor:
```bash
python main.py
```

### Configuração do Frontend
1. Instale as dependências:
```bash
cd BD/aplicacao/vite-project
npm install
```

2. Execute o servidor de desenvolvimento:
```bash
npm run dev
```

## Descrição Detalhada da Aplicação

### Backend (FastAPI + SQLAlchemy)

#### Arquitetura

O backend segue uma arquitetura em camadas:
- **Controller**: Recebe requisições HTTP e coordena operações
- **DAO (Data Access Object)**: Implementa a lógica de acesso ao banco de dados
- **Models**: Define os modelos de dados e mapeia tabelas do banco

#### Componentes Principais e Lógica Detalhada

##### ConsultaController (controller/consultaController.py)

Este controller implementa os endpoints da API usando FastAPI, seguindo padrões RESTful:

- **GET /tables**
  - **Lógica**: Acessa o DAO para obter a lista completa de tabelas disponíveis no banco de dados. Faz a conversão para formato JSON e gerencia o tratamento de erros, retornando códigos HTTP apropriados.
  - **Fluxo de dados**: Controller → DAO → Banco de Dados → DAO → Controller → Cliente

- **GET /tables/{table_name}/relations**
  - **Lógica**: Recebe o nome da tabela como parâmetro de rota, valida a existência da tabela e então solicita ao DAO que identifique todas as tabelas relacionadas através de chaves estrangeiras.
  - **Processamento**: Isola o cliente das complexidades do sistema de banco de dados, encapsulando exceções em mensagens amigáveis.

- **GET /tables/{table_name}/columns**
  - **Lógica**: Solicita ao DAO os metadados das colunas de uma tabela específica e estrutura os resultados para o cliente. Converte tipos complexos do banco de dados para representações legíveis.

- **POST /tables/joined-columns**
  - **Lógica**: Analisa um objeto de requisição que contém uma tabela base e configurações de joins, transforma-o em estruturas compatíveis com o DAO e solicita a lista de colunas disponíveis nas tabelas combinadas.
  - **Transformação de dados**: Converte objetos Pydantic para estruturas Python nativas antes de encaminhar ao DAO.

- **GET /tables/{source_table}/foreign-keys/{target_table}**
  - **Lógica**: Analisa bidireccionalmente as relações entre duas tabelas específicas, identificando colunas que podem ser usadas para criar joins.
  - **Utilidade**: Permite que a interface sugira automaticamente configurações de join com base na estrutura real do banco.

- **POST /report**
  - **Lógica**: Centraliza a construção do relatório dinâmico. Recebe um complexo objeto de configuração que especifica tabela base, atributos desejados, joins, agrupamentos, funções de agregação, ordenação e filtros.
  - **Processamento**: Normaliza e converte estruturas de dados, executa validações preliminares, e delega a construção da consulta ao DAO. Captura, enriquece e relata exceções detalhadas.
  - **Tratamento de falhas**: Implementa captura de exceções com traceback completo para facilitar depuração.

##### Models Pydantic para Validação de Entrada

Os modelos Pydantic definem a estrutura e restrições dos dados que podem ser enviados à API:

- **JoinRequest**: Encapsula a configuração de uma junção entre tabelas, com validação de tipos e presença de campos obrigatórios.

- **AggregateFunction**: Define a estrutura para funções de agregação, garantindo que a função, o atributo e o alias sejam devidamente especificados.

- **OrderByColumn**: Implementa a estrutura para ordenação, com validação e valores padrão para campos opcionais.

- **ReportRequest**: Modelo complexo que combina todos os parâmetros necessários para geração de relatório, aplicando validações em cada componente e definindo valores padrão para parâmetros opcionais.

##### ConsultaDAO (dao/consultaDAO.py)

Esta classe implementa a lógica complexa de acesso e manipulação de dados:

- **__init__()**
  - **Lógica**: Inicializa a conexão com o banco de dados, estabelecendo um ponto único de acesso à engine SQLAlchemy que será reutilizado por todos os métodos.
  - **Padrão aplicado**: Singleton para a engine de banco de dados, otimizando o uso de recursos.

- **getAllTables()**
  - **Lógica**: Utiliza reflexão de banco de dados para descobrir dinamicamente todas as tabelas disponíveis no schema público.
  - **Algorítmo**: Acessa os metadados do banco via inspetor SQLAlchemy, evitando a necessidade de conhecimento prévio da estrutura.
  - **Tratamento de erros**: Implementa captura e log de exceções, com propagação para a camada superior com contexto enriquecido.

- **getTableRelations(table_name)**
  - **Lógica**: Identifica relações entre tabelas analisando metadados de chaves estrangeiras em duas direções.
  - **Algoritmo**:
    1. Descobre chaves onde a tabela especificada referencia outras tabelas
    2. Descobre chaves onde outras tabelas referenciam a tabela especificada
    3. Combina os resultados, elimina duplicatas e retorna uma lista ordenada
  - **Complexidade**: Proporcional ao número de tabelas no banco e suas relações

- **getTableColumns(table_name)**
  - **Lógica**: Extrai e formata metadados completos de colunas, incluindo nome, tipo, restrições e outras propriedades.
  - **Processamento**: Converte tipos de dados complexos do SQLAlchemy para representações textuais padronizadas.
  - **Estrutura resultante**: Lista de dicionários com informações detalhadas sobre cada coluna.

- **getJoinedTablesColumns(base_table, joins)**
  - **Lógica**: Agrega colunas de múltiplas tabelas relacionadas, qualificando-as para evitar ambiguidades.
  - **Algoritmo**:
    1. Obtém e processa colunas da tabela base
    2. Para cada join configurado, obtém e processa colunas da tabela alvo
    3. Qualifica todas as colunas com o nome da tabela (table.column) para identificação única
    4. Evita processamento redundante rastreando tabelas já processadas
  - **Otimização**: Implementa verificação de duplicação para evitar processar a mesma tabela múltiplas vezes.

- **getForeignKeyRelations(source_table, target_table)**
  - **Lógica**: Analisa em profundidade as relações de chave estrangeira entre duas tabelas específicas.
  - **Processamento bidirecional**:
    1. Identifica colunas da tabela origem que referenciam a tabela destino
    2. Identifica colunas da tabela destino que referenciam a tabela origem
    3. Para cada relação, registra as colunas envolvidas e a direção da referência
  - **Aplicação**: Fornece informações essenciais para sugestão automática de joins na interface.

- **generateAdhocReport(base_table, attributes, joins, group_by_attributes, aggregate_functions, order_by_columns, filters, limit)**
  - Esta função é o coração da aplicação, implementando um motor de consulta SQL dinâmico. A lógica detalhada inclui:
  
  - **Mapeamento Dinâmico de Modelos**:
    - Utiliza reflexão Python para descobrir todas as classes de modelo disponíveis
    - Cria um mapeamento entre nomes de tabela e classes ORM correspondentes
    - Valida a existência da tabela base antes de prosseguir
    - Implementa gerenciamento de aliases para evitar conflitos em consultas complexas
  
  - **Resolução Inteligente de Colunas**:
    - Implementa uma lógica centralizada para localizar e validar colunas
    - Resolve ambiguidades quando o mesmo nome de coluna existe em múltiplas tabelas
    - Gerencia automaticamente a criação e reutilização de aliases de tabela
    - Implementa validação rigorosa para garantir que tabelas e colunas solicitadas existam
  
  - **Construção Dinâmica da Cláusula SELECT**:
    - Processa atributos qualificados (table.column) e não qualificados (column)
    - Para atributos não qualificados, implementa busca inteligente em todas as tabelas disponíveis
    - Gerencia aliases para colunas com nomes duplicados em tabelas diferentes
    - Aplica um sistema de contagem para controlar e resolver duplicações
  
  - **Processamento de Funções de Agregação**:
    - Traduz funções de agregação solicitadas (COUNT, SUM, AVG, etc.) para operações SQLAlchemy
    - Resolve dinamicamente a coluna alvo para cada função de agregação
    - Implementa validação de funções de agregação suportadas
    - Aplica aliases personalizados para os resultados de cada agregação
  
  - **Construção Dinâmica de JOINs**:
    - Processa configurações de join com suporte a INNER, LEFT e RIGHT joins
    - Resolve atributos de junção em ambos os lados, com suporte a qualificação de tabela
    - Constrói condições de igualdade para os joins baseadas nos atributos especificados
    - Implementa simulação de RIGHT JOIN para compensar limitações do SQLAlchemy
  
  - **Aplicação de Filtros (WHERE)**:
    - Suporta ampla variedade de operadores de comparação (=, !=, >, <, >=, <=)
    - Implementa operadores de texto (LIKE, ILIKE) com suporte a padrões
    - Processa operadores de conjunto (IN, NOT IN) com suporte a múltiplos formatos de entrada
    - Combina múltiplas condições de filtro usando AND lógico
  
  - **Implementação de GROUP BY**:
    - Processa atributos de agrupamento qualificados e não qualificados
    - Garante que todas as colunas não agregadas na seleção estejam no GROUP BY
    - Implementa busca inteligente de colunas em todas as tabelas disponíveis
    - Valida a consistência entre colunas selecionadas e agrupamento
  
  - **Configuração de ORDER BY**:
    - Suporta ordenação por múltiplas colunas com direções independentes
    - Implementa direções ASC (ascendente) e DESC (descendente)
    - Processa especificações de ordenação com flexibilidade de formato
    - Aplica a ordenação na sequência especificada para resultados consistentes
  
  - **Execução e Formatação de Resultados**:
    - Aplica limitação de resultados para controle de volume de dados
    - Gera representação textual da consulta SQL para depuração e transparência
    - Executa a consulta dentro de uma sessão transacional
    - Converte resultados para formato amigável a JSON para uso pela API
    - Gerencia recursos de banco de dados com práticas de fechamento adequado

  - **Considerações de Performance e Segurança**:
    - Implementa detecção e prevenção de injeção SQL através de parametrização
    - Otimiza a construção de consulta para minimizar operações redundantes
    - Implementa validação rigorosa para prevenir erros em tempo de execução
    - Gerencia recursos de banco de dados com controle apropriado de sessão

##### Database (dao/database.py)

A configuração do banco de dados implementa os seguintes conceitos:

- **Conexão Configurável**: Utiliza string de conexão parametrizada para facilitar configuração em diferentes ambientes.
- **Pool de Conexões**: Implementa gerenciamento avançado de pool para otimizar recursos, definindo tamanho de pool, overflow máximo e timeout.
- **Sessões Transacionais**: Configura fábrica de sessões com parâmetros específicos para controle transacional e comportamento de flush.
- **Base Declarativa**: Estabelece uma classe base comum para todos os modelos ORM, garantindo consistência no mapeamento objeto-relacional.
- **Acesso Global**: Implementa função de acesso à engine para permitir reuso consistente em diferentes partes da aplicação.

##### Models (models/models.py)

Os modelos ORM implementam os seguintes conceitos:

- **Mapeamento Objeto-Relacional**: Define classes Python que espelham a estrutura das tabelas do banco.
- **Definição de Metadados**: Especifica tipos de colunas, restrições, chaves primárias e estrangeiras.
- **Relacionamentos Bidirecionais**: Configura referências entre tabelas que permitem navegação em ambas direções.
- **Validação Estrutural**: Implementa restrições como not-null, tamanho máximo e outras validações.
- **Integração com ORM**: Herda da Base declarativa para integração com o sistema SQLAlchemy.

### Frontend (Vue.js + Vuetify)

#### Componentes Principais

##### AdhocReport.vue

Componente principal que atua como orquestrador central de toda a aplicação, implementando uma arquitetura baseada em estado compartilhado e comunicação de eventos. Este componente encapsula a lógica de negócio fundamental para a criação dinâmica de relatórios:

**Gerenciamento de Estado**:
- Implementa um modelo de estado centralizado usando a API de reatividade do Vue.js
- Mantém o estado de todas as configurações do relatório em estruturas reativas
- Implementa estratégia de cache para otimizar a experiência do usuário
- Gerencia dependências entre diferentes aspectos do relatório (atributos disponíveis dependem da tabela base e joins)

**Ciclo de Vida e Inicialização**:
- Utiliza o hook `onMounted()` para iniciar a carga assíncrona de dados iniciais
- Implementa estratégia de carregamento progressivo para minimizar o tempo de resposta inicial
- Estabelece listeners de eventos para reagir a mudanças em subcomponentes
- Configura sistemas de validação para garantir integridade dos dados em cada etapa

**Fluxo de Carregamento de Dados**:
- Implementa uma sequência estratégica de chamadas à API:
  1. Carrega tabelas disponíveis no início
  2. Ao selecionar uma tabela base, carrega seus atributos e tabelas relacionadas
  3. Ao configurar joins, recalcula dinamicamente atributos disponíveis
  4. Gerencia dependências entre atributos, agrupamentos e ordenação

**Gerenciamento de Comunicação**:
- Implementa comunicação unidirecional para subcomponentes via props
- Recebe atualizações dos subcomponentes via eventos personalizados
- Centraliza chamadas à API do backend, abstraindo complexidade dos componentes filhos
- Implementa sistema de propagação de erros para tratamento unificado

**Lógica de Geração de Relatórios**:
- O método `generateReport()` orquestra o processo completo:
  1. Valida integridade da configuração antes de submeter
  2. Constrói uma representação normalizada do relatório compatível com a API
  3. Implementa tratamento de erros com feedback contextual
  4. Processa e formata os resultados para renderização
  5. Gerencia estado de carregamento para feedback visual ao usuário

**Otimizações e Performance**:
- Implementa debouncing em operações custosas para evitar chamadas excessivas
- Utiliza computed properties para derivar dados sem recálculos desnecessários
- Implementa estratégia de memoização para consultas frequentes
- Gerencia ciclo de vida de recursos para evitar vazamentos de memória

**Tratamento de Casos Especiais**:
- Implementa lógica específica para lidar com atributos duplicados entre tabelas
- Gerencia conflitos de tipos de dados para agregações
- Controla dependências entre agrupamento e funções de agregação
- Implementa validações contextuais baseadas no estado atual da configuração

**Algoritmos Principais**:

1. **Processo de Montagem de Configuração de Relatório**:
   - Inicializa estruturas de dados vazias para cada aspecto do relatório
   - Estabelece validadores para cada tipo de configuração
   - Implementa sistema de dependências para atualizações em cascata
   - Mantém histórico de alterações para recursos de desfazer/refazer

2. **Resolução de Atributos Qualificados**:
   - Para cada atributo selecionado, verifica se já está qualificado (table.column)
   - Se não estiver qualificado, determina a tabela de origem baseada em contexto
   - Para atributos ambíguos (mesmo nome em múltiplas tabelas), implementa heurística de resolução
   - Mantém mapeamento interno entre representações qualificadas e não qualificadas

3. **Coordenação de Joins**:
   - Rastreia dependências entre joins para determinar ordem de execução
   - Implementa validação de integridade referencial baseada em metadados
   - Gerencia tabelas transitivas (joins indiretos)
   - Otimiza configuração para evitar joins redundantes ou desnecessários

##### TableSelector.vue

Permite a seleção da tabela base para o relatório:
- Exibe a lista de tabelas disponíveis
- Emite eventos quando uma tabela é selecionada

##### AttributeSelector.vue

Gerencia a seleção de atributos (colunas) para o relatório:
- Exibe atributos disponíveis com seus tipos
- Permite selecionar múltiplos atributos
- Suporta atributos qualificados (table.column) para joins
- Funções para selecionar todos ou limpar seleção

##### JoinTables.vue

Permite a configuração de junções entre tabelas:
- Seleciona a tabela alvo para o join
- Define o tipo de join (INNER, LEFT, RIGHT)
- Configura os atributos de junção
- Sugere automaticamente as colunas para join com base em chaves estrangeiras
- Gerencia uma lista de joins configurados

Principais funções:
- `fetchJoinSuggestions()`: Busca sugestões de colunas para join baseadas em FKs
- `addJoin()`: Adiciona uma nova junção à lista
- `removeJoin()`: Remove uma junção existente

##### GroupBy.vue

Configura agrupamentos e funções de agregação:
- Permite selecionar atributos para agrupar
- Suporta funções de agregação (COUNT, SUM, AVG, MIN, MAX)
- Gerencia aliases para as funções de agregação

Principais funções:
- `addAggregateFunction()`: Adiciona uma função de agregação
- `removeAggregateFunction()`: Remove uma função de agregação

##### OrderBy.vue

Configura a ordenação dos resultados:
- Seleciona atributos para ordenação
- Define a direção (ASC/DESC)
- Permite múltiplas colunas de ordenação com prioridade

Principais funções:
- `addOrderBy()`: Adiciona uma coluna de ordenação
- `removeOrderBy()`: Remove uma coluna de ordenação
- `moveUp()/moveDown()`: Altera a prioridade de ordenação

##### ReportViewer.vue

Exibe os resultados do relatório:
- Renderiza uma tabela dinâmica com os dados
- Gerencia estados de carregamento e erros
- Exibe mensagens informativas
- Suporta paginação de resultados grandes

## Fluxo de Funcionamento

1. O usuário seleciona uma tabela base
2. O sistema carrega os atributos disponíveis para essa tabela
3. O usuário seleciona os atributos desejados
4. Opcionalmente, o usuário configura:
   - Junções com outras tabelas
   - Agrupamentos e funções de agregação
   - Ordenação dos resultados
5. O usuário clica em "Gerar Relatório"
6. O frontend envia a configuração para o backend
7. O backend:
   - Constrói a consulta SQL dinâmica
   - Executa a consulta no banco de dados
   - Retorna os resultados e a SQL gerada
8. O frontend exibe os resultados na tabela

## Aspectos Técnicos Importantes

### Backend

- **Reflexão de Banco de Dados**: Utiliza o inspetor do SQLAlchemy para obter metadados do banco dinamicamente
- **Consultas Dinâmicas**: Constrói consultas SQL complexas em tempo de execução com base nas escolhas do usuário
- **Tratamento de Ambiguidades**: Qualifica nomes de colunas (table.column) para evitar conflitos em joins
- **Validação de Entrada**: Verifica se as tabelas e colunas solicitadas existem antes de construir a consulta

### Frontend

- **Reatividade**: Utiliza o sistema de reatividade do Vue.js para atualizar a interface conforme as escolhas do usuário
- **v-model Bidirecional**: Implementa comunicação bidirecional entre componentes
- **Lazy Loading**: Carrega dados sob demanda para melhor performance
- **Feedback Visual**: Fornece feedback claro sobre operações e erros

## Tratamento de Casos Especiais

- **Joins Múltiplos**: Suporta encadeamento de múltiplas tabelas com relações diversas
- **Atributos Duplicados**: Trata nomes de colunas duplicados em diferentes tabelas através de qualificação
- **Validação de GROUP BY**: Garante que todas as colunas não agregadas estejam na cláusula GROUP BY
- **Sugestão de Joins**: Analisa chaves estrangeiras para sugerir automaticamente colunas para join

## Conclusão

Esta aplicação fornece uma interface intuitiva para construção de relatórios dinâmicos sem conhecimento de SQL, democratizando o acesso a dados e análises para usuários de todos os níveis técnicos.