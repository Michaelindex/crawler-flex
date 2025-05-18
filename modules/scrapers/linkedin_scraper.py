"""
Scraper especializado para LinkedIn.
Responsável por extrair informações de perfis de empresas no LinkedIn.
"""

import logging
import time
import re
import json
from typing import Dict, Any, List, Optional
from urllib.parse import quote

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from modules.scrapers.base_scraper import BaseScraper
from utils.selenium_manager import SeleniumManager
from utils.searx_client import SearxClient
from config import settings

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    """
    Scraper especializado para LinkedIn.
    """
    
    def __init__(self):
        """Inicializa o scraper do LinkedIn."""
        super().__init__("linkedin")
        self.searx_client = SearxClient()
        self.base_url = "https://www.linkedin.com"
        self.search_url = "https://www.linkedin.com/search/results/companies/?keywords="
        self.is_logged_in = False
    
    def search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Busca empresas no LinkedIn com base nos critérios.
        
        Args:
            criteria: Critérios de busca
            
        Returns:
            Lista de resultados da busca
        """
        logger.info(f"Iniciando busca no LinkedIn com critérios: {criteria}")
        
        results = []
        
        try:
            # Verificar se há uma lista específica de empresas
            if 'companies' in criteria and criteria['companies']:
                for company in criteria['companies']:
                    company_name = company.get('name', '')
                    if company_name:
                        logger.info(f"Buscando no LinkedIn: {company_name}")
                        company_data = self._search_company(company_name)
                        if company_data:
                            results.append({
                                'name': company_name,
                                'data': company_data,
                                'source': 'linkedin'
                            })
            elif 'sector' in criteria:
                # Buscar por setor
                sector = criteria.get('sector', {}).get('main', '')
                location = criteria.get('location', '')
                
                if sector:
                    search_query = sector
                    if location:
                        search_query += f" {location}"
                    
                    logger.info(f"Buscando empresas no LinkedIn por setor: {search_query}")
                    
                    # Limitar o número de resultados
                    max_results = criteria.get('output', {}).get('max_results', 5)
                    
                    # Buscar empresas
                    companies = self._search_companies_by_criteria(search_query, max_results)
                    
                    for company_name in companies:
                        company_data = self._search_company(company_name)
                        if company_data:
                            results.append({
                                'name': company_name,
                                'data': company_data,
                                'source': 'linkedin'
                            })
        
        except Exception as e:
            logger.error(f"Erro durante busca no LinkedIn: {e}")
        
        logger.info(f"Busca no LinkedIn encontrou {len(results)} resultados")
        return results
    
    def collect(self, company_name: str) -> Dict[str, Any]:
        """
        Coleta dados detalhados de uma empresa específica no LinkedIn.
        
        Args:
            company_name: Nome da empresa
            
        Returns:
            Dados coletados
        """
        logger.info(f"Coletando dados do LinkedIn para: {company_name}")
        
        try:
            return self._search_company(company_name)
        except Exception as e:
            logger.error(f"Erro ao coletar dados do LinkedIn para {company_name}: {e}")
            return {}
    
    def _login(self, driver) -> bool:
        """
        Realiza login no LinkedIn.
        
        Args:
            driver: Driver Selenium
            
        Returns:
            True se o login foi bem-sucedido, False caso contrário
        """
        if self.is_logged_in:
            return True
        
        username = settings.LINKEDIN_USERNAME
        password = settings.LINKEDIN_PASSWORD
        
        if not username or not password:
            logger.warning("Credenciais do LinkedIn não configuradas. Continuando sem login.")
            return False
        
        try:
            logger.info("Tentando fazer login no LinkedIn...")
            
            # Navegar para a página de login
            driver.get("https://www.linkedin.com/login")
            time.sleep(settings.NAVIGATION_DELAY)
            
            # Verificar se já está logado
            if "feed" in driver.current_url:
                logger.info("Já está logado no LinkedIn")
                self.is_logged_in = True
                return True
            
            # Preencher formulário de login
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.clear()
            username_field.send_keys(username)
            
            password_field = driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Clicar no botão de login
            login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Aguardar redirecionamento
            time.sleep(settings.NAVIGATION_DELAY * 2)
            
            # Verificar se o login foi bem-sucedido
            if "feed" in driver.current_url or "checkpoint" in driver.current_url:
                logger.info("Login no LinkedIn bem-sucedido")
                self.is_logged_in = True
                return True
            else:
                logger.warning("Falha no login do LinkedIn")
                return False
        
        except Exception as e:
            logger.error(f"Erro durante login no LinkedIn: {e}")
            return False
    
    def _search_company(self, company_name: str) -> Dict[str, Any]:
        """
        Busca e extrai informações de uma empresa específica no LinkedIn.
        
        Args:
            company_name: Nome da empresa
            
        Returns:
            Dados da empresa
        """
        company_data = {}
        
        try:
            # Primeiro, tentar encontrar a URL do perfil da empresa
            company_url = self._find_company_profile_url(company_name)
            
            if not company_url:
                logger.warning(f"Perfil do LinkedIn não encontrado para {company_name}")
                return company_data
            
            logger.info(f"Perfil do LinkedIn encontrado para {company_name}: {company_url}")
            
            # Extrair informações do perfil
            with SeleniumManager() as driver:
                if not driver:
                    logger.error("Falha ao inicializar o driver Selenium")
                    return company_data
                
                # Tentar fazer login (opcional, mas melhora os resultados)
                self._login(driver)
                
                # Navegar para o perfil da empresa
                logger.info(f"Navegando para: {company_url}")
                driver.get(company_url)
                time.sleep(settings.NAVIGATION_DELAY)
                
                # Extrair informações básicas
                company_data.update(self._extract_basic_info(driver))
                
                # Extrair informações de contato
                company_data.update(self._extract_contact_info(driver))
                
                # Extrair informações sobre tamanho da empresa
                company_data.update(self._extract_company_size(driver))
                
                # Extrair informações sobre localização
                company_data.update(self._extract_location(driver))
                
                # Extrair informações sobre funcionários
                company_data.update(self._extract_employees_info(driver))
                
                # Adicionar URL do LinkedIn
                company_data['linkedin'] = company_url
        
        except Exception as e:
            logger.error(f"Erro ao buscar empresa no LinkedIn: {e}")
        
        return company_data
    
    def _find_company_profile_url(self, company_name: str) -> Optional[str]:
        """
        Encontra a URL do perfil da empresa no LinkedIn.
        
        Args:
            company_name: Nome da empresa
            
        Returns:
            URL do perfil ou None se não encontrado
        """
        try:
            # Método 1: Buscar diretamente no LinkedIn
            with SeleniumManager() as driver:
                if not driver:
                    logger.error("Falha ao inicializar o driver Selenium")
                    return None
                
                # Tentar fazer login (opcional, mas melhora os resultados)
                self._login(driver)
                
                # Construir URL de busca
                search_query = quote(company_name)
                url = f"{self.search_url}{search_query}"
                
                logger.info(f"Buscando empresa no LinkedIn: {url}")
                driver.get(url)
                time.sleep(settings.NAVIGATION_DELAY)
                
                # Procurar resultados
                try:
                    company_links = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/company/')]"))
                    )
                    
                    for link in company_links:
                        href = link.get_attribute('href')
                        if href and '/company/' in href:
                            # Verificar se o nome da empresa está no texto do link
                            link_text = link.text.lower()
                            company_name_lower = company_name.lower()
                            
                            # Simplificar nomes para comparação
                            link_text_simple = re.sub(r'[^\w\s]', '', link_text).lower()
                            company_name_simple = re.sub(r'[^\w\s]', '', company_name_lower).lower()
                            
                            # Verificar correspondência
                            if (company_name_simple in link_text_simple or 
                                link_text_simple in company_name_simple):
                                return href
                except Exception as e:
                    logger.warning(f"Erro ao buscar links de empresa: {e}")
            
            # Método 2: Usar SearX para encontrar o perfil
            search_query = f"{company_name} linkedin company"
            search_results = self.searx_client.search(search_query, max_results=5)
            
            if search_results:
                for result in search_results:
                    # Verificar se o resultado é um dicionário ou uma string
                    if isinstance(result, dict):
                        url = result.get('url', '')
                    elif isinstance(result, str):
                        url = result
                    else:
                        continue
                    
                    # Verificar se é um perfil de empresa do LinkedIn
                    if '/company/' in url and 'linkedin.com' in url:
                        return url
            
            # Método 3: Tentar URL direta com slug do nome da empresa
            company_slug = company_name.lower().replace(' ', '-').replace('.', '').replace(',', '')
            direct_url = f"https://www.linkedin.com/company/{company_slug}/"
            
            return None
        
        except Exception as e:
            logger.error(f"Erro ao buscar perfil do LinkedIn para {company_name}: {e}")
            return None
    
    def _extract_basic_info(self, driver) -> Dict[str, Any]:
        """
        Extrai informações básicas do perfil da empresa.
        
        Args:
            driver: Driver Selenium
            
        Returns:
            Informações básicas extraídas
        """
        info = {}
        
        try:
            # Extrair nome da empresa
            try:
                name_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//h1"))
                )
                info['fantasy_name'] = name_element.text.strip()
            except Exception as e:
                logger.warning(f"Erro ao extrair nome da empresa: {e}")
            
            # Extrair descrição/sobre
            try:
                about_elements = driver.find_elements(By.XPATH, "//section[contains(@class, 'about')]//p")
                if about_elements:
                    info['description'] = about_elements[0].text.strip()
            except Exception as e:
                logger.warning(f"Erro ao extrair descrição da empresa: {e}")
            
            # Extrair setor/indústria
            try:
                industry_elements = driver.find_elements(By.XPATH, "//div[contains(text(), 'setor') or contains(text(), 'Setor') or contains(text(), 'industry') or contains(text(), 'Industry')]/following-sibling::div")
                if industry_elements:
                    info['industry'] = industry_elements[0].text.strip()
            except Exception as e:
                logger.warning(f"Erro ao extrair setor da empresa: {e}")
            
            # Extrair site
            try:
                website_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'http') and not(contains(@href, 'linkedin.com'))]")
                for element in website_elements:
                    href = element.get_attribute('href')
                    if href and not href.startswith('https://www.linkedin.com'):
                        info['domain'] = href
                        break
            except Exception as e:
                logger.warning(f"Erro ao extrair site da empresa: {e}")
        
        except Exception as e:
            logger.error(f"Erro ao extrair informações básicas: {e}")
        
        return info
    
    def _extract_contact_info(self, driver) -> Dict[str, Any]:
        """
        Extrai informações de contato do perfil da empresa.
        
        Args:
            driver: Driver Selenium
            
        Returns:
            Informações de contato extraídas
        """
        info = {}
        
        try:
            # Verificar se há uma seção de contato
            contact_sections = driver.find_elements(By.XPATH, "//section[contains(@class, 'contact')]")
            
            if contact_sections:
                # Extrair telefone
                try:
                    phone_elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'Telefone') or contains(text(), 'Phone')]/following-sibling::span")
                    if phone_elements:
                        info['phone'] = phone_elements[0].text.strip()
                except Exception as e:
                    logger.warning(f"Erro ao extrair telefone: {e}")
                
                # Extrair email
                try:
                    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
                    page_text = driver.page_source
                    emails = email_pattern.findall(page_text)
                    
                    if emails:
                        # Filtrar emails genéricos
                        valid_emails = [email for email in emails if not self._is_generic_email(email)]
                        if valid_emails:
                            info['email'] = valid_emails[0]
                except Exception as e:
                    logger.warning(f"Erro ao extrair email: {e}")
            
            # Se não encontrou na seção de contato, tentar na página "Sobre"
            if not info.get('phone') or not info.get('email'):
                # Verificar se já estamos na página "Sobre"
                if "about" not in driver.current_url:
                    # Procurar link para a página "Sobre"
                    about_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/about/')]")
                    
                    if about_links:
                        about_url = about_links[0].get_attribute('href')
                        logger.info(f"Navegando para página 'Sobre': {about_url}")
                        
                        driver.get(about_url)
                        time.sleep(settings.NAVIGATION_DELAY)
                        
                        # Tentar extrair informações novamente
                        if not info.get('phone'):
                            try:
                                phone_elements = driver.find_elements(By.XPATH, "//span[contains(text(), 'Telefone') or contains(text(), 'Phone')]/following-sibling::span")
                                if phone_elements:
                                    info['phone'] = phone_elements[0].text.strip()
                            except Exception:
                                pass
                        
                        if not info.get('email'):
                            try:
                                email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
                                page_text = driver.page_source
                                emails = email_pattern.findall(page_text)
                                
                                if emails:
                                    # Filtrar emails genéricos
                                    valid_emails = [email for email in emails if not self._is_generic_email(email)]
                                    if valid_emails:
                                        info['email'] = valid_emails[0]
                            except Exception:
                                pass
        
        except Exception as e:
            logger.error(f"Erro ao extrair informações de contato: {e}")
        
        return info
    
    def _extract_company_size(self, driver) -> Dict[str, Any]:
        """
        Extrai informações sobre o tamanho da empresa.
        
        Args:
            driver: Driver Selenium
            
        Returns:
            Informações sobre tamanho extraídas
        """
        info = {}
        
        try:
            # Procurar por elementos que contenham informações sobre tamanho
            size_elements = driver.find_elements(By.XPATH, "//div[contains(text(), 'funcionários') or contains(text(), 'employees') or contains(text(), 'Tamanho da empresa') or contains(text(), 'Company size')]/following-sibling::div")
            
            if size_elements:
                size_text = size_elements[0].text.strip()
                
                # Extrair números do texto
                numbers = re.findall(r'\d+(?:[\s.-]\d+)*', size_text)
                if numbers:
                    # Formatar o tamanho
                    size_range = numbers[0]
                    info['size'] = f"{size_range} funcionários"
        
        except Exception as e:
            logger.error(f"Erro ao extrair tamanho da empresa: {e}")
        
        return info
    
    def _extract_location(self, driver) -> Dict[str, Any]:
        """
        Extrai informações sobre localização da empresa.
        
        Args:
            driver: Driver Selenium
            
        Returns:
            Informações sobre localização extraídas
        """
        info = {}
        
        try:
            # Procurar por elementos que contenham informações sobre localização
            location_elements = driver.find_elements(By.XPATH, "//div[contains(text(), 'Sede') or contains(text(), 'Headquarters') or contains(text(), 'Local') or contains(text(), 'Location')]/following-sibling::div")
            
            if location_elements:
                location_text = location_elements[0].text.strip()
                info['location'] = location_text
                
                # Tentar extrair cidade e estado
                location_parts = location_text.split(',')
                if len(location_parts) >= 2:
                    info['city'] = location_parts[0].strip()
                    info['state'] = location_parts[1].strip()
        
        except Exception as e:
            logger.error(f"Erro ao extrair localização da empresa: {e}")
        
        return info
    
    def _extract_employees_info(self, driver) -> Dict[str, Any]:
        """
        Extrai informações sobre funcionários da empresa.
        
        Args:
            driver: Driver Selenium
            
        Returns:
            Informações sobre funcionários extraídas
        """
        info = {}
        
        try:
            # Verificar se há uma seção de funcionários
            employee_sections = driver.find_elements(By.XPATH, "//section[contains(@class, 'employee') or contains(@class, 'people')]")
            
            if employee_sections:
                # Procurar por funcionários listados
                employee_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'employee-card') or contains(@class, 'people-card')]")
                
                if employee_elements:
                    # Extrair informações do primeiro funcionário (geralmente um executivo)
                    first_employee = employee_elements[0]
                    
                    try:
                        name_element = first_employee.find_element(By.XPATH, ".//span[contains(@class, 'name') or contains(@class, 'title')]")
                        position_element = first_employee.find_element(By.XPATH, ".//span[contains(@class, 'position') or contains(@class, 'subtitle')]")
                        
                        if name_element and position_element:
                            full_name = name_element.text.strip()
                            position = position_element.text.strip()
                            
                            # Dividir nome em primeiro e segundo
                            name_parts = full_name.split(' ', 1)
                            if len(name_parts) >= 2:
                                info['first_name'] = name_parts[0]
                                info['second_name'] = name_parts[1]
                            else:
                                info['first_name'] = full_name
                            
                            info['office'] = position
                    except Exception as e:
                        logger.warning(f"Erro ao extrair informações de funcionário: {e}")
        
        except Exception as e:
            logger.error(f"Erro ao extrair informações de funcionários: {e}")
        
        return info
    
    def _search_companies_by_criteria(self, search_query: str, max_results: int = 5) -> List[str]:
        """
        Busca empresas no LinkedIn com base em critérios.
        
        Args:
            search_query: Consulta de busca
            max_results: Número máximo de resultados
            
        Returns:
            Lista de nomes de empresas encontradas
        """
        companies = []
        
        try:
            with SeleniumManager() as driver:
                if not driver:
                    logger.error("Falha ao inicializar o driver Selenium")
                    return companies
                
                # Tentar fazer login (opcional, mas melhora os resultados)
                self._login(driver)
                
                # Construir URL de busca
                encoded_query = quote(search_query)
                url = f"{self.search_url}{encoded_query}"
                
                logger.info(f"Buscando empresas no LinkedIn: {url}")
                driver.get(url)
                time.sleep(settings.NAVIGATION_DELAY)
                
                # Procurar resultados
                company_elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'entity-result__title-text')]")
                
                for i, element in enumerate(company_elements):
                    if i >= max_results:
                        break
                    
                    try:
                        company_name = element.text.strip()
                        if company_name:
                            companies.append(company_name)
                    except Exception:
                        continue
                
                # Se não encontrou resultados suficientes, tentar rolar a página
                if len(companies) < max_results:
                    for _ in range(3):  # Tentar rolar até 3 vezes
                        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                        time.sleep(settings.SCROLL_PAUSE_TIME)
                        
                        # Procurar mais resultados
                        company_elements = driver.find_elements(By.XPATH, "//span[contains(@class, 'entity-result__title-text')]")
                        
                        for i, element in enumerate(company_elements):
                            if len(companies) >= max_results:
                                break
                            
                            try:
                                company_name = element.text.strip()
                                if company_name and company_name not in companies:
                                    companies.append(company_name)
                            except Exception:
                                continue
                        
                        if len(companies) >= max_results:
                            break
        
        except Exception as e:
            logger.error(f"Erro ao buscar empresas por critérios: {e}")
        
        return companies
    
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
