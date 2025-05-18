"""
Scraper especializado para sites corporativos.
Responsável por extrair informações diretamente dos sites das empresas.
"""

import logging
import time
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from modules.scrapers.base_scraper import BaseScraper
from utils.selenium_manager import SeleniumManager
from utils.searx_client import SearxClient
from config import settings

logger = logging.getLogger(__name__)

class CompanySiteScraper(BaseScraper):
    """
    Scraper especializado para sites corporativos.
    """
    
    def __init__(self):
        """Inicializa o scraper de sites corporativos."""
        super().__init__("company_site")
        self.searx_client = SearxClient()
        
        # Padrões para identificação de informações
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        self.phone_pattern = re.compile(r'(\(?\d{2,3}\)?[-.\s]?)?(\d{4,5})[-.\s]?(\d{4})')
        
        # Páginas comuns para informações de contato
        self.contact_pages = [
            '/contato', '/contact', '/fale-conosco', '/about', '/sobre', 
            '/quem-somos', '/institucional', '/empresa'
        ]
    
    def search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca empresas com base nos critérios.
        
        Args:
            criteria: Critérios de busca
            
        Returns:
            Lista de resultados da busca
        """
        logger.info(f"Iniciando busca por sites corporativos com critérios: {criteria}")
        
        results = []
        
        # Verificar se há uma lista específica de empresas
        if 'companies' in criteria and criteria['companies']:
            for company in criteria['companies']:
                company_name = company.get('name', '')
                if company_name:
                    logger.info(f"Buscando site corporativo para: {company_name}")
                    company_data = self._find_company_site(company_name)
                    if company_data:
                        results.append({
                            'name': company_name,
                            'data': company_data,
                            'source': 'company_site'
                        })
        else:
            logger.warning("Nenhuma lista de empresas fornecida para busca de sites corporativos")
        
        logger.info(f"Busca com company_site encontrou {len(results)} resultados")
        return results
    
    def collect(self, company_name: str) -> Dict[str, Any]:
        """
        Coleta dados detalhados de uma empresa específica.
        
        Args:
            company_name: Nome da empresa
            
        Returns:
            Dados coletados
        """
        logger.info(f"Coletando dados do site corporativo para: {company_name}")
        
        try:
            return self._find_company_site(company_name)
        except Exception as e:
            logger.error(f"Erro ao coletar dados do site corporativo para {company_name}: {e}")
            return {}
    
    def _find_company_site(self, company_name: str) -> Dict[str, Any]:
        """
        Encontra e extrai informações do site corporativo de uma empresa.
        
        Args:
            company_name: Nome da empresa
            
        Returns:
            Dados extraídos do site corporativo
        """
        company_data = {}
        
        try:
            # Buscar site oficial da empresa usando SearX
            search_query = f"{company_name} site oficial"
            search_results = self.searx_client.search(search_query, max_results=5)
            
            if not search_results:
                logger.warning(f"Nenhum resultado de busca encontrado para {company_name}")
                return company_data
            
            # Filtrar resultados para encontrar o site oficial
            official_site = None
            for result in search_results:
                url = result.get('url', '')
                title = result.get('title', '')
                
                # Verificar se o título contém o nome da empresa
                if self._is_likely_official_site(url, title, company_name):
                    official_site = url
                    break
            
            if not official_site:
                logger.warning(f"Site oficial não encontrado para {company_name}")
                return company_data
            
            logger.info(f"Site oficial encontrado para {company_name}: {official_site}")
            company_data['domain'] = self._extract_domain(official_site)
            
            # Extrair informações do site oficial
            with SeleniumManager() as driver:
                if not driver:
                    logger.error("Falha ao inicializar o driver Selenium")
                    return company_data
                
                # Navegar para o site oficial
                logger.info(f"Navegando para: {official_site}")
                if not driver.get(official_site):
                    logger.error(f"Falha ao navegar para {official_site}")
                    return company_data
                
                time.sleep(settings.NAVIGATION_DELAY)
                
                # Extrair informações da página inicial
                self._extract_contact_info(driver, company_data)
                
                # Verificar páginas de contato
                for contact_page in self.contact_pages:
                    contact_url = official_site.rstrip('/') + contact_page
                    logger.info(f"Verificando página de contato: {contact_url}")
                    
                    try:
                        driver.get(contact_url)
                        time.sleep(settings.NAVIGATION_DELAY)
                        
                        # Extrair informações da página de contato
                        self._extract_contact_info(driver, company_data)
                        
                        # Se encontrou informações suficientes, parar
                        if self._has_sufficient_info(company_data):
                            break
                    
                    except Exception as e:
                        logger.warning(f"Erro ao acessar página de contato {contact_url}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Erro ao buscar site corporativo para {company_name}: {e}")
        
        return company_data
    
    def _extract_contact_info(self, driver, company_data: Dict[str, Any]) -> None:
        """
        Extrai informações de contato de uma página.
        
        Args:
            driver: Driver Selenium
            company_data: Dicionário para armazenar os dados extraídos
        """
        try:
            # Extrair todo o texto da página
            page_text = driver.page_source
            
            # Extrair emails
            if 'email' not in company_data:
                emails = self.email_pattern.findall(page_text)
                if emails:
                    # Filtrar emails genéricos
                    valid_emails = [email for email in emails if not self._is_generic_email(email)]
                    if valid_emails:
                        company_data['email'] = valid_emails[0]
            
            # Extrair telefones
            if 'phone' not in company_data:
                phones = self.phone_pattern.findall(page_text)
                if phones:
                    # Formatar o primeiro telefone encontrado
                    phone_parts = phones[0]
                    formatted_phone = ''
                    
                    if phone_parts[0]:  # DDD
                        formatted_phone += phone_parts[0].replace('(', '').replace(')', '').strip()
                    
                    if phone_parts[1] and phone_parts[2]:  # Número
                        if formatted_phone:
                            formatted_phone += ' '
                        formatted_phone += f"{phone_parts[1].strip()}-{phone_parts[2].strip()}"
                    
                    company_data['phone'] = formatted_phone
            
            # Extrair endereço
            if 'address' not in company_data:
                # Procurar por elementos que possam conter endereços
                address_candidates = driver.find_elements(By.XPATH, "//*[contains(text(), 'Endereço') or contains(text(), 'endereço') or contains(text(), 'Localização') or contains(text(), 'localização')]")
                
                for candidate in address_candidates:
                    # Verificar o texto do elemento pai ou próximo irmão
                    parent = candidate.find_element(By.XPATH, "./..")
                    address_text = parent.text
                    
                    # Se o texto parece um endereço (contém número, CEP, etc.)
                    if re.search(r'\d+.*(?:CEP|cep).*\d+', address_text) or re.search(r'\d+.*(?:Bairro|bairro)', address_text):
                        company_data['address'] = address_text
                        break
            
            # Extrair tamanho da empresa (número de funcionários)
            if 'size' not in company_data:
                size_candidates = driver.find_elements(By.XPATH, "//*[contains(text(), 'funcionários') or contains(text(), 'colaboradores') or contains(text(), 'equipe')]")
                
                for candidate in size_candidates:
                    size_text = candidate.text
                    # Procurar por padrões como "X funcionários" ou "equipe de X pessoas"
                    size_match = re.search(r'(\d+[\d.]*)\s*(?:funcionários|colaboradores|pessoas)', size_text)
                    if size_match:
                        company_data['size'] = size_match.group(0)
                        break
        
        except Exception as e:
            logger.error(f"Erro ao extrair informações de contato: {e}")
    
    def _is_likely_official_site(self, url: str, title: str, company_name: str) -> bool:
        """
        Verifica se uma URL é provavelmente o site oficial da empresa.
        
        Args:
            url: URL do site
            title: Título da página
            company_name: Nome da empresa
            
        Returns:
            True se for provavelmente o site oficial, False caso contrário
        """
        # Verificar se o domínio contém o nome da empresa
        domain = self._extract_domain(url)
        company_name_simplified = company_name.lower().replace(' ', '').replace('.', '').replace('-', '')
        
        # Remover termos comuns do nome da empresa para comparação
        for term in ['sa', 'ltda', 'eireli', 'mei', 'me', 'epp', 'corporation', 'inc', 'corp']:
            company_name_simplified = company_name_simplified.replace(term, '')
        
        # Verificar se o domínio contém parte significativa do nome da empresa
        domain_contains_name = False
        if len(company_name_simplified) > 3:
            for i in range(3, len(company_name_simplified) + 1):
                if company_name_simplified[:i] in domain:
                    domain_contains_name = True
                    break
        
        # Verificar se o título contém o nome da empresa
        title_contains_name = company_name.lower() in title.lower()
        
        # Verificar se é um site de rede social ou plataforma conhecida
        is_social_media = any(platform in domain for platform in [
            'facebook', 'linkedin', 'twitter', 'instagram', 'youtube',
            'wikipedia', 'cnpj', 'receita', 'gov.br'
        ])
        
        return (domain_contains_name or title_contains_name) and not is_social_media
    
    def _extract_domain(self, url: str) -> str:
        """
        Extrai o domínio de uma URL.
        
        Args:
            url: URL completa
            
        Returns:
            Domínio extraído
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Remover 'www.' se presente
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except:
            return url
    
    def _is_generic_email(self, email: str) -> bool:
        """
        Verifica se um email é genérico (não específico da empresa).
        
        Args:
            email: Endereço de email
            
        Returns:
            True se for um email genérico, False caso contrário
        """
        generic_patterns = [
            'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com',
            'example.com', 'test.com', 'mail.com', 'email.com'
        ]
        
        generic_prefixes = [
            'info@', 'contact@', 'example@', 'test@', 'user@',
            'admin@', 'webmaster@', 'postmaster@', 'hostmaster@'
        ]
        
        # Verificar domínio genérico
        for pattern in generic_patterns:
            if email.lower().endswith(pattern):
                return True
        
        # Verificar prefixo genérico
        for prefix in generic_prefixes:
            if email.lower().startswith(prefix):
                return True
        
        return False
    
    def _has_sufficient_info(self, company_data: Dict[str, Any]) -> bool:
        """
        Verifica se já foram coletadas informações suficientes.
        
        Args:
            company_data: Dados coletados
            
        Returns:
            True se houver informações suficientes, False caso contrário
        """
        # Verificar se tem pelo menos email e telefone
        return 'email' in company_data and 'phone' in company_data
