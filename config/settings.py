"""
Arquivo de configurações globais para o crawler flexível.
"""

# Configurações gerais
DEBUG = True
LOG_LEVEL = "INFO"
MAX_RETRIES = 3
RETRY_DELAY = 2  # segundos

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
REQUEST_TIMEOUT = 30  # segundos
SELENIUM_PAGE_LOAD_TIMEOUT = 30  # segundos
SELENIUM_IMPLICIT_WAIT = 10  # segundos

# Configurações de exportação
DEFAULT_OUTPUT_FORMAT = "excel"
DEFAULT_OUTPUT_DIR = "data/output"

# Configurações de qualidade
MIN_QUALITY_SCORE = 0.7  # Score mínimo para considerar dados válidos
REQUIRED_FIELDS = [
    "Company Name (Revised)",
    "CNPJ",
    "Fantasy name",
    "Domain",
    "Location",
    "City",
    "State",
    "E-mail",
    "Telephone"
]
