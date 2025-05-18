"""
Arquivo de configurações globais para o crawler flexível.
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações gerais
DEBUG = True
LOG_LEVEL = "INFO"
MAX_RETRIES = 5  # Aumentado de 3 para 5
RETRY_DELAY = 3  # Aumentado de 2 para 3 segundos

# Configurações de User-Agent
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
)

# Configurações de APIs externas
SEARX_URL = "http://124.81.6.163:8092/search"
AI_API_URL = "http://124.81.6.163:11434/api/generate"
AI_MODEL = "llama3.1:8b"

# Configurações de timeouts
REQUEST_TIMEOUT = 45  # Aumentado de 30 para 45 segundos
SELENIUM_PAGE_LOAD_TIMEOUT = 45  # Aumentado de 30 para 45 segundos
SELENIUM_IMPLICIT_WAIT = 15  # Aumentado de 10 para 15 segundos

# Configurações de exportação
DEFAULT_OUTPUT_FORMAT = "excel"
DEFAULT_OUTPUT_DIR = "data/output"

# Configurações de qualidade
MIN_QUALITY_SCORE = 0.3  # Reduzido para aceitar dados parciais
REQUIRED_FIELDS = [
    "Company Name (Revised)",  # Apenas nome da empresa como campo obrigatório
]

# Configurações de scraping
EXPORT_PARTIAL_DATA = True  # Exportar dados mesmo que incompletos

# Whitelist de sites para busca prioritária
WHITELIST_SITES = [
    # Sites corporativos
    {"domain": "linkedin.com", "priority": 1, "type": "social"},
    {"domain": "gov.br", "priority": 1, "type": "government"},
    {"domain": "cnpj.biz", "priority": 2, "type": "business"},
    {"domain": "empresascnpj.com", "priority": 2, "type": "business"},
    {"domain": "facebook.com", "priority": 3, "type": "social"},
    {"domain": "instagram.com", "priority": 3, "type": "social"},
    {"domain": "twitter.com", "priority": 3, "type": "social"},
    {"domain": "guiainvest.com.br", "priority": 3, "type": "business"},
    {"domain": "b3.com.br", "priority": 2, "type": "business"},
    {"domain": "reclameaqui.com.br", "priority": 4, "type": "review"},
    
    # Sites de busca
    {"domain": "google.com", "priority": 5, "type": "search"},
    {"domain": "bing.com", "priority": 5, "type": "search"},
    {"domain": "duckduckgo.com", "priority": 5, "type": "search"}
]

# Configurações de navegação
NAVIGATION_DELAY = 10  # Segundos entre ações de navegação
SCROLL_PAUSE_TIME = 3  # Segundos entre rolagens
MAX_SCROLL_ATTEMPTS = 15  # Número máximo de rolagens por página

# Credenciais do LinkedIn (carregadas do arquivo .env)
LINKEDIN_USERNAME = os.getenv("LINKEDIN_USERNAME", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
