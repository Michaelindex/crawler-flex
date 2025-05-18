"""
Arquivo de configurações globais para o crawler flexível.
"""

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
MIN_QUALITY_SCORE = 0.3  # Reduzido de 0.5 para 0.3
REQUIRED_FIELDS = [
    "Company Name (Revised)",  # Apenas nome da empresa como campo obrigatório
]

# Configurações de scraping
RECEITAWS_DELAY = 10  # Aumentado de 5 para 10 segundos entre requisições
USE_ALTERNATIVE_SOURCES = True  # Usar fontes alternativas quando ReceitaWS falhar
USE_FALLBACK_DATA = True  # Usar dados de fallback quando scraping falhar
EXPORT_PARTIAL_DATA = True  # Exportar dados mesmo que incompletos
