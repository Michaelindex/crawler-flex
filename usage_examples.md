# Exemplos de Uso do Crawler Flexível com Critérios Variáveis

Este documento apresenta exemplos práticos de como configurar e utilizar o crawler flexível para diferentes cenários de busca, demonstrando a adaptabilidade do sistema a diversos critérios.

## Formato de Entrada de Critérios

Os critérios de busca são fornecidos em formato JSON estruturado, permitindo combinações complexas de parâmetros:

```json
{
  "sector": {
    "main": "string",
    "sub_sectors": ["string"]
  },
  "size": {
    "employees": {
      "min": int,
      "max": int
    },
    "revenue": {
      "min": int,
      "max": int,
      "currency": "string"
    }
  },
  "location": {
    "country": "string",
    "states": ["string"],
    "cities": ["string"]
  },
  "contacts": {
    "departments": ["string"],
    "positions": ["string"]
  },
  "additional": {
    "founded_after": int,
    "founded_before": int,
    "has_international_presence": boolean,
    "keywords": ["string"]
  },
  "output": {
    "format": "string",
    "max_results": int
  }
}
```

## Exemplo 1: Empresas de Saúde com Alto Faturamento e Tamanho Médio

**Cenário**: Buscar empresas do setor de saúde que faturam mais de 1 bilhão e possuem entre 100 e 200 funcionários.

### Entrada de Critérios:

```json
{
  "sector": {
    "main": "saúde",
    "sub_sectors": ["hospitais", "clínicas", "laboratórios", "farmacêuticas"]
  },
  "size": {
    "employees": {
      "min": 100,
      "max": 200
    },
    "revenue": {
      "min": 1000000000,
      "currency": "BRL"
    }
  },
  "location": {
    "country": "Brasil"
  },
  "output": {
    "format": "excel",
    "max_results": 50
  }
}
```

### Fluxo de Execução:

1. **Planejamento**: O sistema identifica que deve priorizar fontes com dados financeiros e de tamanho de empresas no setor de saúde.

2. **Descoberta**: 
   - Busca no SearXNG: `"empresas saúde Brasil faturamento bilhão"`
   - Consulta diretórios especializados do setor de saúde
   - Filtra resultados iniciais por tamanho (100-200 funcionários)

3. **Coleta Aprofundada**:
   - Para cada empresa candidata, coleta dados do LinkedIn para confirmar número de funcionários
   - Busca em relatórios financeiros e rankings para validar faturamento
   - Extrai informações detalhadas de sites corporativos

4. **Validação e Enriquecimento**:
   - Cruza dados de múltiplas fontes para confirmar faturamento
   - Utiliza IA para estimar número de funcionários quando não explícito
   - Prioriza empresas com dados mais completos e confiáveis

5. **Resultado**: Planilha Excel com até 50 empresas de saúde que atendem aos critérios, com todos os campos preenchidos.

### Código de Execução:

```python
from flexible_crawler.core.controller import CrawlerController

# Carregar critérios do arquivo JSON
criteria = {
  "sector": {
    "main": "saúde",
    "sub_sectors": ["hospitais", "clínicas", "laboratórios", "farmacêuticas"]
  },
  "size": {
    "employees": {
      "min": 100,
      "max": 200
    },
    "revenue": {
      "min": 1000000000,
      "currency": "BRL"
    }
  },
  "location": {
    "country": "Brasil"
  },
  "output": {
    "format": "excel",
    "max_results": 50
  }
}

# Iniciar o crawler com os critérios
controller = CrawlerController()
result = controller.execute(criteria)

print(f"Busca concluída. {len(result.companies)} empresas encontradas.")
print(f"Arquivo gerado: {result.output_file}")
```

## Exemplo 2: Empresas de Tecnologia em São Paulo com Contatos de TI

**Cenário**: Buscar empresas de tecnologia localizadas em São Paulo, coletando especificamente contatos de coordenadores e gerentes de TI.

### Entrada de Critérios:

```json
{
  "sector": {
    "main": "tecnologia",
    "sub_sectors": ["software", "hardware", "serviços de TI", "telecomunicações"]
  },
  "location": {
    "country": "Brasil",
    "states": ["SP"],
    "cities": ["São Paulo"]
  },
  "contacts": {
    "departments": ["TI", "Tecnologia", "Infraestrutura"],
    "positions": ["Coordenador", "Gerente", "Diretor"]
  },
  "output": {
    "format": "csv",
    "max_results": 100
  }
}
```

### Fluxo de Execução:

1. **Planejamento**: O sistema identifica que deve priorizar fontes ricas em informações de contato e filtrar geograficamente.

2. **Descoberta**: 
   - Busca no SearXNG: `"empresas tecnologia São Paulo"`
   - Consulta LinkedIn para empresas do setor em São Paulo
   - Filtra resultados iniciais por localização exata

3. **Coleta Aprofundada**:
   - Para cada empresa, busca perfis de funcionários no LinkedIn com cargos específicos
   - Analisa páginas "Equipe" e "Contato" nos sites corporativos
   - Busca em diretórios profissionais e plataformas de networking

4. **Validação e Enriquecimento**:
   - Verifica se os contatos encontrados realmente trabalham nas empresas
   - Utiliza IA para inferir emails corporativos com base em padrões
   - Valida números de telefone e departamentos

5. **Resultado**: Arquivo CSV com até 100 empresas de tecnologia em São Paulo, incluindo contatos específicos de TI.

### Código de Execução:

```python
from flexible_crawler.core.controller import CrawlerController

# Carregar critérios
criteria = {
  "sector": {
    "main": "tecnologia",
    "sub_sectors": ["software", "hardware", "serviços de TI", "telecomunicações"]
  },
  "location": {
    "country": "Brasil",
    "states": ["SP"],
    "cities": ["São Paulo"]
  },
  "contacts": {
    "departments": ["TI", "Tecnologia", "Infraestrutura"],
    "positions": ["Coordenador", "Gerente", "Diretor"]
  },
  "output": {
    "format": "csv",
    "max_results": 100
  }
}

# Iniciar o crawler com os critérios
controller = CrawlerController()
result = controller.execute(criteria)

print(f"Busca concluída. {len(result.companies)} empresas encontradas.")
print(f"Arquivo gerado: {result.output_file}")
```

## Exemplo 3: Empresas de Varejo com Presença Internacional

**Cenário**: Buscar empresas brasileiras do setor de varejo que possuem operações internacionais.

### Entrada de Critérios:

```json
{
  "sector": {
    "main": "varejo",
    "sub_sectors": ["moda", "eletrônicos", "alimentos", "e-commerce"]
  },
  "location": {
    "country": "Brasil"
  },
  "additional": {
    "has_international_presence": true,
    "keywords": ["global", "internacional", "exportação", "filiais"]
  },
  "output": {
    "format": "excel",
    "max_results": 30
  }
}
```

### Fluxo de Execução:

1. **Planejamento**: O sistema identifica que deve buscar empresas de varejo e verificar presença internacional.

2. **Descoberta**: 
   - Busca no SearXNG: `"empresas brasileiras varejo internacional global"`
   - Consulta rankings de internacionalização de empresas
   - Filtra resultados iniciais por setor de varejo

3. **Coleta Aprofundada**:
   - Para cada empresa, analisa seções "Sobre" e "Onde Estamos" nos sites corporativos
   - Busca notícias sobre expansão internacional
   - Verifica relatórios anuais para menções de operações globais

4. **Validação e Enriquecimento**:
   - Confirma presença internacional com múltiplas fontes
   - Utiliza IA para analisar textos e identificar menções a operações globais
   - Complementa com dados de contato e tamanho

5. **Resultado**: Planilha Excel com até 30 empresas brasileiras de varejo com presença internacional confirmada.

## Exemplo 4: Startups de Fintech Fundadas nos Últimos 5 Anos

**Cenário**: Buscar startups brasileiras do setor financeiro (fintechs) fundadas nos últimos 5 anos.

### Entrada de Critérios:

```json
{
  "sector": {
    "main": "financeiro",
    "sub_sectors": ["fintech", "pagamentos", "crédito", "investimentos"]
  },
  "location": {
    "country": "Brasil"
  },
  "additional": {
    "founded_after": 2020,
    "keywords": ["startup", "fintech", "inovação"]
  },
  "size": {
    "employees": {
      "max": 100
    }
  },
  "output": {
    "format": "excel",
    "max_results": 50
  }
}
```

### Fluxo de Execução:

1. **Planejamento**: O sistema identifica que deve focar em empresas recentes do setor financeiro.

2. **Descoberta**: 
   - Busca no SearXNG: `"startups fintech Brasil fundadas após 2020"`
   - Consulta plataformas de startups e aceleradoras
   - Filtra resultados por data de fundação

3. **Coleta Aprofundada**:
   - Para cada startup, verifica data de fundação em registros oficiais
   - Coleta informações sobre fundadores e equipe
   - Busca dados sobre rodadas de investimento e tecnologias

4. **Validação e Enriquecimento**:
   - Confirma data de fundação com múltiplas fontes
   - Utiliza IA para classificar precisamente o sub-setor dentro de fintech
   - Complementa com dados de contato e tamanho atual

5. **Resultado**: Planilha Excel com até 50 startups de fintech brasileiras fundadas após 2020.

## Exemplo 5: Empresas de Qualquer Setor a partir de Lista de Nomes

**Cenário**: Buscar informações completas para uma lista específica de empresas fornecida pelo usuário.

### Entrada de Critérios:

```json
{
  "company_list": [
    "Empresa A",
    "Empresa B",
    "Empresa C",
    "Empresa D",
    "Empresa E"
  ],
  "output": {
    "format": "excel"
  }
}
```

### Fluxo de Execução:

1. **Planejamento**: O sistema identifica que deve buscar informações específicas para empresas já conhecidas.

2. **Descoberta**: 
   - Pula a fase de descoberta, pois as empresas já estão definidas
   - Valida a existência de cada empresa na lista

3. **Coleta Aprofundada**:
   - Para cada empresa na lista, busca todos os dados requeridos
   - Prioriza fontes oficiais como site corporativo e LinkedIn
   - Coleta dados cadastrais, contatos e informações estruturais

4. **Validação e Enriquecimento**:
   - Unifica dados de múltiplas fontes para cada empresa
   - Utiliza IA para preencher lacunas com base em informações correlatas
   - Garante completude de todos os campos requeridos

5. **Resultado**: Planilha Excel com informações completas para todas as empresas da lista.

## Interface de Linha de Comando

O sistema pode ser executado via linha de comando, facilitando a automação:

```bash
# Executar com arquivo de critérios
python -m flexible_crawler --criteria criteria.json --output empresas_resultado.xlsx

# Executar com parâmetros diretos
python -m flexible_crawler --sector "tecnologia" --location "São Paulo" --min-employees 100 --output empresas_resultado.csv
```

## Interface Web Simples (Futura)

Uma interface web simples permitirá definir critérios através de formulários:

1. **Página de Critérios**: Formulário para definir setor, tamanho, localização e outros parâmetros
2. **Página de Execução**: Monitoramento em tempo real do progresso da busca
3. **Página de Resultados**: Visualização e download dos dados coletados

## Adaptação a Novos Critérios

O sistema foi projetado para facilmente incorporar novos tipos de critérios:

1. **Adicionar novo critério**: Atualizar o schema de critérios no módulo `criteria_parser.py`
2. **Implementar lógica de busca**: Adicionar handlers específicos nos módulos de scraping
3. **Atualizar validação**: Incluir regras de validação para o novo critério
4. **Documentar**: Adicionar exemplos de uso do novo critério

Esta flexibilidade permite que o sistema evolua conforme as necessidades de busca se tornam mais complexas ou específicas.
