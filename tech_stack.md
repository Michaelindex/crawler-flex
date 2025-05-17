# Tecnologias e Infraestrutura para o Crawler Flexível

Este documento detalha as tecnologias recomendadas e a infraestrutura necessária para implementar o sistema de crawler flexível, considerando os recursos disponíveis e os requisitos de qualidade e completude dos dados.

## Stack Tecnológico

### Linguagem Principal

**Python 3.9+**
- Justificativa: Ecossistema rico em bibliotecas para web scraping, processamento de dados e integração com APIs
- Vantagens: Sintaxe clara, desenvolvimento rápido, excelente suporte para automação web

### Componentes Core

#### 1. Automação Web e Scraping

**Selenium**
- Uso: Navegação interativa em sites dinâmicos (LinkedIn, portais corporativos)
- Configuração: Integração com ChromeDriver na mesma pasta do executável
- Personalização:
  ```python
  from selenium import webdriver
  from selenium.webdriver.chrome.options import Options
  
  chrome_options = Options()
  chrome_options.add_argument(f"user-agent={USER_AGENT}")
  chrome_options.add_argument("--headless")  # Opcional para execução sem interface gráfica
  
  driver = webdriver.Chrome(options=chrome_options)
  ```

**BeautifulSoup4**
- Uso: Parsing e extração de dados de HTML
- Integração com Selenium para processamento do conteúdo renderizado
- Exemplo:
  ```python
  from bs4 import BeautifulSoup
  
  html = driver.page_source
  soup = BeautifulSoup(html, 'html.parser')
  company_name = soup.find('h1', class_='company-name').text.strip()
  ```

**Requests**
- Uso: Requisições HTTP para APIs e páginas estáticas
- Configuração para simular navegador real:
  ```python
  import requests
  
  headers = {'User-Agent': USER_AGENT}
  response = requests.get(url, headers=headers)
  ```

#### 2. Busca e Descoberta

**SearXNG Client**
- Uso: Interface para o motor de busca SearXNG local
- Implementação:
  ```python
  import requests
  import json
  
  def searx_search(query, format="json"):
      url = f"http://124.81.6.163:8092/search?q={query}&format={format}"
      response = requests.get(url)
      return response.json()
  ```

**Scrapy (Opcional)**
- Uso: Para crawling em larga escala quando necessário
- Vantagens: Gerenciamento de requisições, pipelines de processamento

#### 3. Processamento e Enriquecimento de Dados

**Pandas**
- Uso: Manipulação, transformação e exportação de dados
- Funcionalidades principais: DataFrame para estruturação dos dados, operações de filtragem e agregação

**IA Local (Ollama)**
- Uso: Enriquecimento de dados, classificação e validação
- Integração:
  ```python
  import requests
  import json
  
  def query_local_ai(prompt):
      url = "http://124.81.6.163:11434/api/generate"
      data = {
          "model": "llama3.1:8b",
          "prompt": prompt,
          "stream": False
      }
      response = requests.post(url, json=data)
      return response.json()
  ```

#### 4. Armazenamento e Exportação

**Openpyxl**
- Uso: Geração de arquivos Excel formatados
- Funcionalidades: Formatação condicional, estilos personalizados

**CSV**
- Uso: Exportação em formato CSV para compatibilidade universal
- Implementação via Pandas:
  ```python
  import pandas as pd
  
  df = pd.DataFrame(data)
  df.to_csv("empresas_resultado.csv", index=False)
  df.to_excel("empresas_resultado.xlsx", index=False)
  ```

### Estrutura de Diretórios

```
flexible_crawler/
├── config/
│   ├── settings.py           # Configurações globais
│   └── sources.json          # Whitelist de fontes
├── core/
│   ├── controller.py         # Controlador principal
│   ├── criteria_parser.py    # Processador de critérios
│   └── quality_checker.py    # Validador de qualidade
├── modules/
│   ├── scrapers/
│   │   ├── base_scraper.py   # Classe base para scrapers
│   │   ├── linkedin.py       # Scraper específico para LinkedIn
│   │   ├── company_site.py   # Scraper para sites corporativos
│   │   └── directory.py      # Scraper para diretórios empresariais
│   ├── processors/
│   │   ├── data_unifier.py   # Unificação de dados
│   │   └── enricher.py       # Enriquecimento com IA
│   └── exporters/
│       ├── csv_exporter.py   # Exportação para CSV
│       └── excel_exporter.py # Exportação para Excel
├── utils/
│   ├── searx_client.py       # Cliente para SearXNG
│   ├── ai_client.py          # Cliente para IA local
│   └── selenium_manager.py   # Gerenciador de sessões Selenium
├── data/
│   ├── input/                # Arquivos de entrada (critérios)
│   └── output/               # Arquivos de saída (resultados)
├── main.py                   # Ponto de entrada principal
└── requirements.txt          # Dependências do projeto
```

## Requisitos de Infraestrutura

### Para Desenvolvimento e Execução Local

**Hardware Recomendado**
- CPU: 4+ cores
- RAM: 8+ GB
- Armazenamento: 20+ GB SSD
- Conexão Internet: Estável e rápida

**Software Necessário**
- Python 3.9+
- Chrome/Chromium Browser
- ChromeDriver compatível com a versão do Chrome
- Acesso ao SearXNG (http://124.81.6.163:8092/search)
- Acesso à IA local (http://124.81.6.163:11434/api/generate)

### Para Produção (Futuro)

**Opções de Escalabilidade**
- Containerização com Docker para isolamento e portabilidade
- Orquestração com Docker Compose para gerenciamento de serviços
- Banco de dados para armazenamento persistente (PostgreSQL/MongoDB)

## Integração entre Componentes

### Diagrama de Integração

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Interface      │────▶│  Controller     │────▶│  Criteria       │
│  (main.py)      │     │  (core)         │     │  Parser         │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  SearXNG        │◀───▶│  Scraper        │────▶│  Selenium       │
│  Client         │     │  Modules        │     │  Manager        │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  AI             │◀───▶│  Data           │────▶│  Quality        │
│  Client         │     │  Processor      │     │  Checker        │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │                 │
                        │  Exporters      │
                        │  (CSV/Excel)    │
                        │                 │
                        └─────────────────┘
```

### Fluxo de Dados entre Componentes

1. **Interface → Controller**: Recebe critérios de busca e inicia o processo
2. **Controller → Criteria Parser**: Traduz critérios em instruções estruturadas
3. **Controller → Scraper Modules**: Coordena a execução dos módulos de scraping
4. **Scraper Modules ↔ SearXNG Client**: Realiza buscas para descoberta de empresas
5. **Scraper Modules ↔ Selenium Manager**: Navega em sites para coleta de dados
6. **Scraper Modules → Data Processor**: Envia dados brutos coletados
7. **Data Processor ↔ AI Client**: Enriquece e valida dados com auxílio da IA
8. **Data Processor → Quality Checker**: Verifica completude e qualidade
9. **Data Processor → Exporters**: Envia dados processados para exportação

## Considerações de Segurança e Desempenho

### Segurança

- Implementação de delays aleatórios entre requisições para evitar bloqueios
- Rotação de User-Agents para simular diferentes navegadores
- Armazenamento seguro de credenciais (se necessário no futuro)
- Validação de entrada para prevenir injeções

### Desempenho

- Uso de cache para evitar requisições repetidas
- Implementação de paralelismo controlado para múltiplas fontes
- Mecanismo de retry com backoff exponencial para falhas temporárias
- Logging detalhado para monitoramento e diagnóstico

### Escalabilidade

- Arquitetura modular permitindo adição de novas fontes
- Separação clara entre lógica de negócio e implementação técnica
- Configurações externalizadas para fácil ajuste
- Design que permite futura distribuição de carga

## Dependências do Projeto

```
# requirements.txt
requests==2.31.0
beautifulsoup4==4.12.2
selenium==4.15.2
pandas==2.0.3
openpyxl==3.1.2
lxml==4.9.3
python-dotenv==1.0.0
tqdm==4.66.1
retry==0.9.2
```

## Próximos Passos Técnicos

1. Implementação da estrutura base e módulos core
2. Desenvolvimento dos scrapers para fontes prioritárias
3. Integração com SearXNG e IA local
4. Implementação do processador de dados e validador de qualidade
5. Desenvolvimento dos exportadores de dados
6. Testes com diferentes critérios de busca
