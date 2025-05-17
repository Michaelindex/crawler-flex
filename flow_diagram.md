# Fluxo de Funcionamento Personalizado do Crawler Flexível

Este documento detalha o fluxo de funcionamento do sistema de crawler flexível, mostrando como ele se adapta a diferentes critérios de busca e garante a qualidade e completude dos dados.

## Diagrama de Fluxo Principal

```
┌─────────────────┐
│                 │
│  Definição de   │
│  Critérios      │
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│                 │
│  Planejamento   │
│  de Busca       │
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│                 │
│  Descoberta     │
│  de Empresas    │
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│                 │
│  Coleta         │
│  Aprofundada    │
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│                 │
│  Validação e    │
│  Enriquecimento │
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│                 │
│  Exportação     │
│  de Dados       │
│                 │
└─────────────────┘
```

## Detalhamento das Etapas

### 1. Definição de Critérios

**Entrada**: Parâmetros definidos pelo usuário
**Saída**: Objeto de critérios estruturado

Nesta etapa, o sistema recebe e processa os critérios de busca, que podem incluir:

- **Critérios de Setor**: Área de atuação da empresa (ex: saúde, tecnologia)
- **Critérios Financeiros**: Faturamento, capital social
- **Critérios de Tamanho**: Número de funcionários
- **Critérios Geográficos**: Localização, região
- **Critérios de Contato**: Cargos específicos, departamentos
- **Critérios Adicionais**: Tempo de mercado, presença internacional, etc.

O sistema converte esses critérios em um objeto estruturado que guiará todas as etapas seguintes.

### 2. Planejamento de Busca

**Entrada**: Objeto de critérios
**Saída**: Plano de execução com fontes priorizadas

Com base nos critérios, o sistema:

1. Determina quais fontes são mais relevantes para cada tipo de informação
2. Estabelece a ordem de consulta às fontes
3. Define estratégias específicas para cada fonte
4. Estima o tempo e recursos necessários
5. Prepara os parâmetros de busca para cada módulo

Por exemplo, para empresas de saúde com alto faturamento, o sistema pode priorizar associações setoriais de saúde e rankings financeiros específicos.

### 3. Descoberta de Empresas

**Entrada**: Plano de execução
**Saída**: Lista inicial de empresas candidatas

Nesta fase, o sistema:

1. Utiliza o SearXNG para buscar empresas que correspondam aos critérios básicos
2. Consulta diretórios empresariais específicos do setor
3. Analisa rankings e listas relevantes
4. Filtra resultados preliminares com base nos critérios
5. Cria uma lista priorizada de empresas para investigação aprofundada

O sistema mantém um registro de confiança para cada fonte de descoberta, ajustando dinamicamente a prioridade com base em resultados anteriores.

### 4. Coleta Aprofundada

**Entrada**: Lista de empresas candidatas
**Saída**: Dados brutos coletados de múltiplas fontes

Para cada empresa na lista, o sistema executa:

1. **Coleta em Camadas**:
   - **Camada 1**: Informações básicas (nome, site, localização)
   - **Camada 2**: Perfil detalhado (tamanho, setor, descrição)
   - **Camada 3**: Dados financeiros e estruturais
   - **Camada 4**: Informações de contato específicas

2. **Estratégias por Fonte**:
   - **LinkedIn**: Navegação com Selenium para extrair perfil da empresa
   - **Sites Corporativos**: Análise de páginas "Sobre", "Contato", "Equipe"
   - **Diretórios Empresariais**: Extração estruturada de dados cadastrais
   - **Redes Sociais**: Coleta de informações complementares

3. **Adaptação Dinâmica**:
   - Se uma fonte falhar, o sistema tenta fontes alternativas
   - Se dados específicos estiverem faltando, intensifica a busca nessa área

### 5. Validação e Enriquecimento

**Entrada**: Dados brutos coletados
**Saída**: Registros de empresas validados e completos

Nesta etapa crítica, o sistema:

1. **Unifica dados** de múltiplas fontes em um registro coerente
2. **Resolve conflitos** quando fontes diferentes fornecem informações contraditórias
3. **Identifica lacunas** nos dados coletados
4. **Enriquece dados** utilizando:
   - Inferência baseada em informações correlatas
   - Consulta à IA local para análise e preenchimento inteligente
   - Buscas adicionais direcionadas para campos específicos
5. **Valida a qualidade** dos dados com verificações cruzadas

O sistema aplica regras de negócio específicas para cada campo, garantindo que todos os dados atendam aos padrões de qualidade.

### 6. Exportação de Dados

**Entrada**: Registros validados e completos
**Saída**: Arquivo CSV/Excel formatado

Finalmente, o sistema:

1. Formata os dados conforme a estrutura de colunas requerida
2. Aplica formatação específica para cada tipo de dado
3. Gera o arquivo no formato solicitado (CSV/Excel)
4. Produz um relatório de qualidade dos dados
5. Armazena metadados sobre a execução para referência futura

## Adaptação a Diferentes Critérios

O sistema se adapta a diferentes cenários de busca:

### Cenário 1: Busca por Setor Específico
- Prioriza fontes especializadas no setor
- Utiliza terminologia e classificações específicas do setor
- Adapta estratégias de validação para padrões do setor

### Cenário 2: Busca por Tamanho de Empresa
- Foca em fontes que fornecem dados sobre número de funcionários
- Utiliza indicadores indiretos para estimar tamanho (faturamento, presença física)
- Cruza informações de múltiplas fontes para maior precisão

### Cenário 3: Busca por Contatos Específicos
- Prioriza fontes ricas em informações de contato (LinkedIn, sites corporativos)
- Utiliza técnicas específicas para identificação de cargos e departamentos
- Implementa validação adicional para confirmar dados de contato

### Cenário 4: Busca por Região Geográfica
- Utiliza filtros geográficos nas buscas iniciais
- Prioriza fontes locais e regionais
- Valida localização com múltiplas referências

## Mecanismos de Controle de Qualidade

Para garantir a máxima qualidade e completude dos dados, o sistema implementa:

1. **Verificação de Completude**: Garante que todos os campos obrigatórios estejam preenchidos
2. **Validação de Formato**: Verifica se os dados estão no formato correto (emails, telefones, CNPJs)
3. **Verificação de Consistência**: Confirma que os dados são coerentes entre si
4. **Controle de Fontes**: Rastreia a origem de cada informação para avaliação de confiabilidade
5. **Feedback Loop**: Aprende com execuções anteriores para melhorar a qualidade das buscas futuras

## Extensibilidade do Fluxo

O sistema foi projetado para ser facilmente estendido:

1. **Novas Fontes**: Podem ser adicionadas sem modificar o fluxo principal
2. **Novos Critérios**: O mecanismo de planejamento adapta-se a novos tipos de critérios
3. **Novos Campos**: A estrutura de dados pode ser expandida para incluir informações adicionais
4. **Novas Estratégias**: Técnicas de coleta podem ser atualizadas ou substituídas
5. **Novos Formatos**: Suporte a formatos adicionais de exportação pode ser implementado
