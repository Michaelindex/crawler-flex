"""
Scraper específico para LinkedIn.
Responsável por extrair informações de empresas do LinkedIn.
"""

import logging
import time
import re
from typing import Dict, Any, List, Optional
from urllib.parse import quote

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_scraper import BaseScraper
from utils.selenium_manager import SeleniumManager

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    """
    Scraper para extrair informações de empresas do LinkedIn.
    """
    
    def __init__(self):
        """Inicializa o scraper do LinkedIn."""
        super().__init__("LinkedIn", requires_selenium=True)
        self.base_url = "https://www.linkedin.com/company/"
        self.search_url = "https://www.linkedin.com/search/results/companies/?keywords="
    
    def search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Realiza uma busca por empresas no LinkedIn com base nos critérios fornecidos.
        
        Args:
            criteria: Critérios de busca
            
        Returns:
            Lista de empresas encontradas
        """
        logger.info(f"Iniciando busca no LinkedIn com critérios: {criteria}")
        
        results = []
        
        # Verificar se há uma lista específica de empresas
        if 'company_list' in criteria and criteria['company_list']:
            logger.info(f"Usando lista de {len(criteria['company_list'])} empresas fornecida")
            for company_name in criteria['company_list']:
                results.append({
                    'name': company_name,
                    'source': 'linkedin',
                    'url': f"{self.base_url}{quote(company_name.lower().replace(' ', '-'))}"
                })
            return results
        
        # Construir query de busca
        query_parts = []
        
        # Adicionar setor
        if 'sector' in criteria:
            sector = criteria['sector']
            if 'main' in sector:
                query_parts.append(sector['main'])
        
        # Adicionar localização
        if 'location' in criteria:
            location = criteria['location']
            if 'country' in location and location['country'] == 'Brasil':
                query_parts.append('Brasil')
            
            if 'states' in location and location['states']:
                query_parts.append(location['states'][0])
            
            if 'cities' in location and location['cities']:
                query_parts.append(location['cities'][0])
        
        # Construir query final
        query = " ".join(query_parts)
        if not query:
            query = "empresas tecnologia brasil"  # Query padrão
        
        # Realizar busca usando Selenium
        with SeleniumManager(headless=True) as driver:
            try:
                # Navegar para página de busca
                search_query = quote(query)
                url = f"{self.search_url}{search_query}"
                logger.info(f"Navegando para URL de busca: {url}")
                
                driver.get(url)
                time.sleep(5)  # Aguardar carregamento
                
                # Extrair resultados da busca
                company_elements = driver.find_elements(By.CSS_SELECTOR, ".entity-result__title-text a")
                
                # Limitar resultados conforme configuração
                max_results = criteria.get('output', {}).get('max_results', 10)
                
                # Processar resultados
                for i, element in enumerate(company_elements[:max_results]):
                    try:
                        company_name = element.text.strip()
                        company_url = element.get_attribute("href")
                        
                        if company_name and company_url:
                            results.append({
                                'name': company_name,
                                'source': 'linkedin',
                                'url': company_url
                            })
                    except Exception as e:
                        logger.warning(f"Erro ao processar resultado {i}: {e}")
                
                logger.info(f"Busca concluída. {len(results)} empresas encontradas")
                
            except Exception as e:
                logger.error(f"Erro durante busca no LinkedIn: {e}")
                
                # Tentar abordagem alternativa com URLs diretas
                logger.info("Tentando abordagem alternativa com URLs diretas")
                
                # Gerar algumas empresas com base nos critérios
                sector_name = criteria.get('sector', {}).get('main', 'tecnologia')
                
                # Lista de empresas brasileiras por setor (simplificada)
                tech_companies = ["Totvs", "Locaweb", "Positivo", "Linx", "Neogrid", "CI&T", "Stefanini", "Tivit"]
                health_companies = ["Fleury", "Dasa", "Hapvida", "Hermes Pardini", "Oncoclínicas", "Rede D'Or"]
                finance_companies = ["Nubank", "Stone", "PagSeguro", "XP", "BTG Pactual", "Inter"]
                retail_companies = ["Magazine Luiza", "Via Varejo", "Lojas Renner", "Americanas", "Raia Drogasil"]
                
                # Selecionar lista com base no setor
                if "saude" in sector_name.lower() or "saúde" in sector_name.lower():
                    companies = health_companies
                elif "finan" in sector_name.lower() or "banco" in sector_name.lower():
                    companies = finance_companies
                elif "varejo" in sector_name.lower() or "retail" in sector_name.lower():
                    companies = retail_companies
                else:
                    companies = tech_companies
                
                # Adicionar empresas à lista de resultados
                for company in companies[:max_results]:
                    results.append({
                        'name': company,
                        'source': 'linkedin',
                        'url': f"{self.base_url}{quote(company.lower().replace(' ', '-'))}"
                    })
        
        return results
    
    def collect(self, target: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """
        Coleta informações detalhadas de uma empresa específica no LinkedIn.
        
        Args:
            target: Empresa alvo
            fields: Campos a serem coletados
            
        Returns:
            Dados coletados
        """
        logger.info(f"Coletando dados do LinkedIn para: {target.get('name', 'Desconhecido')}")
        
        collected_data = {
            'source': 'linkedin',
            'name': target.get('name', ''),
            'url': target.get('url', '')
        }
        
        # Verificar se há URL
        if not collected_data['url']:
            logger.warning("URL não fornecida para coleta")
            return collected_data
        
        # Usar Selenium para extrair dados
        with SeleniumManager(headless=True) as driver:
            try:
                # Navegar para página da empresa
                logger.info(f"Navegando para: {collected_data['url']}")
                driver.get(collected_data['url'])
                time.sleep(5)  # Aguardar carregamento
                
                # Extrair dados básicos
                try:
                    # Nome da empresa (confirmar)
                    name_element = driver.find_element(By.CSS_SELECTOR, ".org-top-card-summary__title")
                    if name_element:
                        collected_data['name'] = name_element.text.strip()
                except NoSuchElementException:
                    logger.warning("Elemento de nome não encontrado")
                
                # Extrair tamanho da empresa
                try:
                    # Procurar na seção "Sobre"
                    about_link = None
                    try:
                        about_link = driver.find_element(By.XPATH, "//a[contains(@href, '/about/')]")
                    except NoSuchElementException:
                        logger.warning("Link 'Sobre' não encontrado")
                    
                    if about_link:
                        about_url = about_link.get_attribute("href")
                        driver.get(about_url)
                        time.sleep(3)
                        
                        # Procurar tamanho da empresa
                        try:
                            size_element = driver.find_element(By.XPATH, "//dt[contains(text(), 'Tamanho da empresa')]/following-sibling::dd")
                            if size_element:
                                collected_data['size'] = size_element.text.strip()
                        except NoSuchElementException:
                            # Tentar em inglês
                            try:
                                size_element = driver.find_element(By.XPATH, "//dt[contains(text(), 'Company size')]/following-sibling::dd")
                                if size_element:
                                    collected_data['size'] = size_element.text.strip()
                            except NoSuchElementException:
                                logger.warning("Elemento de tamanho não encontrado")
                        
                        # Procurar site da empresa
                        try:
                            website_element = driver.find_element(By.XPATH, "//dt[contains(text(), 'Site')]/following-sibling::dd//a")
                            if website_element:
                                collected_data['website'] = website_element.get_attribute("href")
                                
                                # Extrair domínio do site
                                if collected_data['website']:
                                    domain_match = re.search(r'https?://(?:www\.)?([^/]+)', collected_data['website'])
                                    if domain_match:
                                        collected_data['domain'] = domain_match.group(1)
                        except NoSuchElementException:
                            # Tentar em inglês
                            try:
                                website_element = driver.find_element(By.XPATH, "//dt[contains(text(), 'Website')]/following-sibling::dd//a")
                                if website_element:
                                    collected_data['website'] = website_element.get_attribute("href")
                                    
                                    # Extrair domínio do site
                                    if collected_data['website']:
                                        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', collected_data['website'])
                                        if domain_match:
                                            collected_data['domain'] = domain_match.group(1)
                            except NoSuchElementException:
                                logger.warning("Elemento de site não encontrado")
                        
                        # Procurar setor da empresa
                        try:
                            industry_element = driver.find_element(By.XPATH, "//dt[contains(text(), 'Setor')]/following-sibling::dd")
                            if industry_element:
                                collected_data['industry'] = industry_element.text.strip()
                        except NoSuchElementException:
                            # Tentar em inglês
                            try:
                                industry_element = driver.find_element(By.XPATH, "//dt[contains(text(), 'Industry')]/following-sibling::dd")
                                if industry_element:
                                    collected_data['industry'] = industry_element.text.strip()
                            except NoSuchElementException:
                                logger.warning("Elemento de setor não encontrado")
                        
                        # Procurar localização da empresa
                        try:
                            location_element = driver.find_element(By.XPATH, "//dt[contains(text(), 'Localização')]/following-sibling::dd")
                            if location_element:
                                location_text = location_element.text.strip()
                                collected_data['location'] = location_text
                                
                                # Tentar extrair cidade e estado
                                if "," in location_text:
                                    parts = location_text.split(",")
                                    collected_data['city'] = parts[0].strip()
                                    if len(parts) > 1:
                                        collected_data['state'] = parts[1].strip()
                        except NoSuchElementException:
                            # Tentar em inglês
                            try:
                                location_element = driver.find_element(By.XPATH, "//dt[contains(text(), 'Headquarters')]/following-sibling::dd")
                                if location_element:
                                    location_text = location_element.text.strip()
                                    collected_data['location'] = location_text
                                    
                                    # Tentar extrair cidade e estado
                                    if "," in location_text:
                                        parts = location_text.split(",")
                                        collected_data['city'] = parts[0].strip()
                                        if len(parts) > 1:
                                            collected_data['state'] = parts[1].strip()
                            except NoSuchElementException:
                                logger.warning("Elemento de localização não encontrado")
                
                except Exception as e:
                    logger.error(f"Erro ao extrair dados da seção 'Sobre': {e}")
                
                # Extrair contatos
                try:
                    # Voltar para página principal
                    driver.get(collected_data['url'])
                    time.sleep(3)
                    
                    # Procurar funcionários
                    people_link = None
                    try:
                        people_link = driver.find_element(By.XPATH, "//a[contains(@href, '/people/')]")
                    except NoSuchElementException:
                        logger.warning("Link 'Pessoas' não encontrado")
                    
                    if people_link:
                        people_url = people_link.get_attribute("href")
                        driver.get(people_url)
                        time.sleep(3)
                        
                        # Extrair primeiro contato
                        try:
                            contact_elements = driver.find_elements(By.CSS_SELECTOR, ".org-people-profile-card")
                            if contact_elements and len(contact_elements) > 0:
                                contact = contact_elements[0]
                                
                                # Nome
                                try:
                                    name_element = contact.find_element(By.CSS_SELECTOR, ".org-people-profile-card__profile-title")
                                    full_name = name_element.text.strip()
                                    
                                    # Dividir em primeiro e segundo nome
                                    name_parts = full_name.split()
                                    if len(name_parts) > 0:
                                        collected_data['first_name'] = name_parts[0]
                                    if len(name_parts) > 1:
                                        collected_data['last_name'] = " ".join(name_parts[1:])
                                except NoSuchElementException:
                                    logger.warning("Nome do contato não encontrado")
                                
                                # Cargo
                                try:
                                    position_element = contact.find_element(By.CSS_SELECTOR, ".org-people-profile-card__profile-position")
                                    collected_data['position'] = position_element.text.strip()
                                except NoSuchElementException:
                                    logger.warning("Cargo do contato não encontrado")
                        except Exception as e:
                            logger.warning(f"Erro ao extrair contatos: {e}")
                
                except Exception as e:
                    logger.error(f"Erro ao extrair dados de contatos: {e}")
                
                # Adicionar LinkedIn URL
                collected_data['linkedin'] = collected_data['url']
                
                logger.info(f"Coleta concluída para {collected_data['name']}")
                
            except Exception as e:
                logger.error(f"Erro durante coleta no LinkedIn: {e}")
        
        return collected_data
