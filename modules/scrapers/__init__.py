"""
Módulo de inicialização do pacote scrapers.
Importa e registra todos os scrapers disponíveis.
"""

from .base_scraper import BaseScraper
from .linkedin_scraper import LinkedInScraper
from .cnpj_scraper import CNPJScraper
from .company_site_scraper import CompanySiteScraper

# Registrar scrapers disponíveis
AVAILABLE_SCRAPERS = {
    'linkedin': LinkedInScraper,
    'cnpj': CNPJScraper,
    'company_site': CompanySiteScraper
}

def get_scraper(name: str) -> BaseScraper:
    """
    Obtém uma instância de scraper pelo nome.
    
    Args:
        name: Nome do scraper
        
    Returns:
        Instância do scraper
        
    Raises:
        ValueError: Se o scraper não existir
    """
    if name not in AVAILABLE_SCRAPERS:
        raise ValueError(f"Scraper não encontrado: {name}")
    
    return AVAILABLE_SCRAPERS[name]()

def get_all_scrapers() -> dict:
    """
    Obtém todas as classes de scrapers disponíveis.
    
    Returns:
        Dicionário com nome e classe de cada scraper
    """
    return AVAILABLE_SCRAPERS
