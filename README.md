# Crawler Flexível para Coleta de Dados Empresariais

Este projeto implementa um sistema de crawler/scraping flexível para coletar dados de empresas com base em diferentes critérios de busca, garantindo alta qualidade e completude das informações.

## Visão Geral

O Crawler Flexível foi projetado para atender à necessidade de coletar dados empresariais completos a partir de critérios variáveis, como:
- Empresas de um setor específico (ex: tecnologia, saúde)
- Empresas com determinado número de funcionários
- Empresas com faturamento específico
- Empresas em determinadas localizações
- Contatos específicos dentro das empresas

O sistema utiliza uma arquitetura modular que permite fácil expansão e adaptação a novos requisitos.

## Estrutura do Projeto

```
flexible_crawler/
├── config/                  # Configurações do sistema
│   ├── settings.py          # Configurações globais
│   └── sources.json         # Whitelist de fontes
├── core/                    # Componentes principais
│   ├── controller.py        # Controlador principal
│   ├── criteria_parser.py   # Parser de critérios
│   └── quality_checker.py   # Verificador de qualidade
├── modules/                 # Módulos funcionais
│   ├── scrapers/            # Módulos de scraping
│   │   └── base_scraper.py  # Classe base para scrapers
│   ├── processors/          # Processadores de dados
│   │   └── data_processor.py # Processador principal
│   └── exporters/           # Exportadores de dados
│       └── excel_exporter.py # Exportador para Excel
├── utils/                   # Utilitários
│   ├── searx_client.py      # Cliente SearXNG
│   ├── ai_client.py         # Cliente para IA local
│   └── selenium_manager.py  # Gerenciador Selenium
├── data/                    # Diretórios de dados
│   ├── input/               # Arquivos de entrada
│   └── output/              # Arquivos de saída
├── main.py                  # Script principal
├── setup.sh                 # Script de instalação
└── requirements.txt         # Dependências
```

## Instalação

### Pré-requisitos

- Python 3.6 ou superior
- pip (gerenciador de pacotes Python)
- Google Chrome ou Chromium (para Selenium)
- Acesso à internet

### Instalação Automática

1. Descompacte o arquivo zip em um diretório de sua escolha
2. Abra um terminal e navegue até o diretório do projeto
3. Execute o script de instalação:

```bash
chmod +x setup.sh  # Apenas em sistemas Unix/Linux
./setup.sh
```

### Instalação Manual

1. Descompacte o arquivo zip em um diretório de sua escolha
2. Abra um terminal e navegue até o diretório do projeto
3. Crie e ative um ambiente virtual:

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Ativar ambiente virtual (Linux/Mac)
source venv/bin/activate
```

4. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Uso

### Executando com Arquivo de Critérios

O modo mais flexível de usar o crawler é através de arquivos JSON com critérios de busca:

```bash
python main.py --criteria data/input/exemplo_tecnologia_sp.json
```

### Executando com Parâmetros Diretos

Para buscas mais simples, você pode usar parâmetros diretos na linha de comando:

```bash
python main.py --sector "tecnologia" --location "São Paulo" --min-employees 50 --max-employees 500
```

### Parâmetros Disponíveis

- `--criteria`: Caminho para arquivo JSON com critérios de busca
- `--sector`: Setor principal da empresa
- `--location`: Localização (país, estado ou cidade)
- `--min-employees`: Número mínimo de funcionários
- `--max-employees`: Número máximo de funcionários
- `--min-revenue`: Faturamento mínimo
- `--output`: Caminho para arquivo de saída
- `--format`: Formato de saída (excel, csv)
- `--max-results`: Número máximo de resultados

## Exemplos de Critérios

### Exemplo 1: Empresas de Tecnologia em São Paulo

```json
{
  "sector": {
    "main": "tecnologia",
    "sub_sectors": ["software", "hardware", "serviços de TI"]
  },
  "location": {
    "country": "Brasil",
    "states": ["SP"],
    "cities": ["São Paulo"]
  },
  "size": {
    "employees": {
      "min": 50,
      "max": 500
    }
  },
  "output": {
    "format": "excel",
    "max_results": 10
  }
}
```

### Exemplo 2: Empresas de Saúde com Faturamento Bilionário

```json
{
  "sector": {
    "main": "saúde",
    "sub_sectors": ["hospitais", "clínicas", "laboratórios"]
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
    "max_results": 5
  }
}
```

## Configuração de APIs Externas

O sistema está configurado para usar as seguintes APIs externas:

- SearXNG: `http://124.81.6.163:8092/search`
- IA local: `http://124.81.6.163:11434/api/generate`

Estas configurações podem ser alteradas no arquivo `config/settings.py`.

## Personalização e Extensão

### Adicionando Novos Scrapers

1. Crie um novo arquivo em `modules/scrapers/`
2. Implemente uma classe que herde de `BaseScraper`
3. Implemente os métodos `search` e `collect`
4. Registre o scraper no controlador

### Adicionando Novos Exportadores

1. Crie um novo arquivo em `modules/exporters/`
2. Implemente uma classe com método `export`
3. Registre o exportador no controlador

## Solução de Problemas

### Problemas com Selenium

Se encontrar problemas com o Selenium:

1. Verifique se o Chrome/Chromium está instalado
2. Verifique se o chromedriver está no PATH ou no diretório do projeto
3. Tente executar em modo não-headless para depuração

### Problemas de Conexão

Se encontrar problemas de conexão com APIs externas:

1. Verifique sua conexão com a internet
2. Verifique se as URLs das APIs estão corretas em `config/settings.py`
3. Verifique se as APIs estão acessíveis a partir de sua rede

## Limitações Atuais

- O sistema está em fase de protótipo, com implementações simplificadas
- Alguns componentes retornam dados simulados para demonstração
- A integração com IA local requer ajustes para uso em produção
- O sistema não implementa rotação de proxies ou user-agents para evitar bloqueios

## Próximos Passos

Para evoluir este protótipo para um sistema completo:

1. Implementar scrapers específicos para cada fonte na whitelist
2. Melhorar a detecção e prevenção de bloqueios
3. Implementar cache para requisições
4. Adicionar interface web para configuração e monitoramento
5. Implementar armazenamento persistente em banco de dados

## Licença

Este projeto é fornecido como está, sem garantias expressas ou implícitas.
