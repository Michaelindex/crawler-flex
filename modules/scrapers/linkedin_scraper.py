"""
Scraper especializado para LinkedIn.
Responsável por extrair informações de empresas do LinkedIn.
"""

import logging
import time
import re
from typing import Dict, Any, List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from modules.scrapers.base_scraper import BaseScraper
from utils.selenium_manager import SeleniumManager
from config import settings

logger = logging.getLogger(__name__)

class LinkedInScraper(BaseScraper):
    """
    Scraper especializado para LinkedIn.
    """
    
    def __init__(self):
        """Inicializa o scraper do LinkedIn."""
        super().__init__("linkedin")
        self.base_url = "https://www.linkedin.com"
        self.search_url = "https://www.linkedin.com/search/results/companies/"
        self.logged_in = False
    
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
        
        # Verificar se há uma lista específica de empresas
        if 'companies' in criteria and criteria['companies']:
            for company in criteria['companies']:
                company_name = company.get('name', '')
                if company_name:
                    logger.info(f"Buscando empresa específica no LinkedIn: {company_name}")
                    company_data = self._search_company(company_name)
                    if company_data:
                        results.append({
                            'name': company_name,
                            'data': company_data,
                            'source': 'linkedin'
                        })
        
        # Busca por setor
        elif 'sector' in criteria and criteria['sector'].get('main'):
            sector = criteria['sector']['main']
            logger.info(f"Buscando empresas por setor no LinkedIn: {sector}")
            
            # Limitar número de resultados
            max_results = criteria.get('output', {}).get('max_results', 5)
            
            # Buscar empresas por setor
            sector_results = self._search_by_sector(sector, max_results)
            results.extend(sector_results)
        
        logger.info(f"Busca no LinkedIn encontrou {len(results)} resultados")
        return results
    
    def collect(self, company_name: str) -> Dict[str, Any]:
        """
        Coleta dados detalhados de uma empresa específica.
        
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
    
    def _search_company(self, company_name: str) -> Dict[str, Any]:
        """
        Busca uma empresa específica no LinkedIn.
        
        Args:
            company_name: Nome da empresa
            
        Returns:
            Dados da empresa
        """
        company_data = {}
        
        try:
            with SeleniumManager() as driver:
                if not driver:
                    logger.error("Falha ao inicializar o driver Selenium")
                    return company_data
                
                # Tentar login se configurado
                if not self.logged_in and hasattr(settings, 'LINKEDIN_USERNAME') and hasattr(settings, 'LINKEDIN_PASSWORD'):
                    self._login(driver)
                
                # Construir URL de busca
                search_query = company_name.replace(' ', '%20')
                url = f"{self.search_url}?keywords={search_query}"
                
                logger.info(f"Navegando para URL de busca: {url}")
                if not driver.get(url):
                    logger.error(f"Falha ao navegar para {url}")
                    return company_data
                
                time.sleep(settings.NAVIGATION_DELAY)
                
                # Verificar se há resultados
                try:
                    results = driver.find_elements(By.CSS_SELECTOR, ".search-result__info")
                    if not results:
                        logger.warning(f"Nenhum resultado encontrado para {company_name}")
                        return company_data
                    
                    # Clicar no primeiro resultado
                    results[0].click()
                    time.sleep(settings.NAVIGATION_DELAY)
                    
                    # Extrair dados da página da empresa
                    company_data = self._extract_company_data(driver)
                    company_data['name'] = company_name
                    
                except NoSuchElementException:
                    logger.warning(f"Elementos de resultado não encontrados para {company_name}")
                except Exception as e:
                    logger.error(f"Erro ao processar resultados de busca para {company_name}: {e}")
        
        except Exception as e:
            logger.error(f"Erro durante busca no LinkedIn: {e}")
        
        return company_data
    
    def _search_by_sector(self, sector: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Busca empresas por setor no LinkedIn.
        
        Args:
            sector: Setor de interesse
            max_results: Número máximo de resultados
            
        Returns:
            Lista de resultados da busca
        """
        results = []
        
        try:
            with SeleniumManager() as driver:
                if not driver:
                    logger.error("Falha ao inicializar o driver Selenium")
                    return results
                
                # Tentar login se configurado
                if not self.logged_in and hasattr(settings, 'LINKEDIN_USERNAME') and hasattr(settings, 'LINKEDIN_PASSWORD'):
                    self._login(driver)
                
                # Construir URL de busca
                search_query = sector.replace(' ', '%20')
                url = f"{self.search_url}?keywords={search_query}"
                
                logger.info(f"Navegando para URL de busca por setor: {url}")
                if not driver.get(url):
                    logger.error(f"Falha ao navegar para {url}")
                    return results
                
                time.sleep(settings.NAVIGATION_DELAY)
                
                # Extrair resultados da página
                try:
                    company_elements = driver.find_elements(By.CSS_SELECTOR, ".search-result__info")
                    
                    # Limitar ao número máximo de resultados
                    for i, element in enumerate(company_elements[:max_results]):
                        try:
                            company_name = element.find_element(By.CSS_SELECTOR, ".search-result__title").text.strip()
                            logger.info(f"Encontrada empresa: {company_name}")
                            
                            # Clicar no resultado para ver detalhes
                            element.click()
                            time.sleep(settings.NAVIGATION_DELAY * 2)
                            
                            # Extrair dados da página da empresa
                            company_data = self._extract_company_data(driver)
                            company_data['name'] = company_name
                            
                            results.append({
                                'name': company_name,
                                'data': company_data,
                                'source': 'linkedin'
                            })
                            
                            # Voltar para a página de resultados
                            driver.back()
                            time.sleep(settings.NAVIGATION_DELAY)
                            
                        except Exception as e:
                            logger.error(f"Erro ao processar empresa #{i+1}: {e}")
                            continue
                
                except NoSuchElementException:
                    logger.warning(f"Elementos de resultado não encontrados para setor {sector}")
                except Exception as e:
                    logger.error(f"Erro ao processar resultados de busca por setor {sector}: {e}")
        
        except Exception as e:
            logger.error(f"Erro durante busca por setor no LinkedIn: {e}")
        
        return results
    
    def _extract_company_data(self, driver) -> Dict[str, Any]:
        """
        Extrai dados da página de uma empresa no LinkedIn.
        
        Args:
            driver: Driver Selenium
            
        Returns:
            Dados extraídos da empresa
        """
        company_data = {}
        
        try:
            # Extrair nome da empresa (redundante, mas útil para verificação)
            try:
                company_data['name'] = driver.find_element(By.CSS_SELECTOR, ".org-top-card-summary__title").text.strip()
            except NoSuchElementException:
                logger.warning("Nome da empresa não encontrado na página")
            
            # Extrair tamanho da empresa
            try:
                company_info = driver.find_elements(By.CSS_SELECTOR, ".org-top-card-summary-info-list__info-item")
                for info in company_info:
                    if "funcionários" in info.text.lower():
                        company_data['size'] = info.text.strip()
                        break
            except NoSuchElementException:
                logger.warning("Tamanho da empresa não encontrado")
            
            # Extrair localização
            try:
                location = driver.find_element(By.CSS_SELECTOR, ".org-top-card-summary__headquarter").text.strip()
                company_data['location'] = location
                
                # Tentar extrair cidade e estado
                location_parts = location.split(',')
                if len(location_parts) >= 2:
                    company_data['city'] = location_parts[0].strip()
                    company_data['state'] = location_parts[1].strip()
            except NoSuchElementException:
                logger.warning("Localização da empresa não encontrada")
            
            # Extrair site
            try:
                website = driver.find_element(By.CSS_SELECTOR, ".org-top-card-primary-actions__action a").get_attribute("href")
                company_data['website'] = website
            except NoSuchElementException:
                logger.warning("Site da empresa não encontrado")
            
            # Extrair URL do LinkedIn
            company_data['linkedin'] = driver.current_url
            
            # Rolar para ver mais informações
            driver.execute_script("window.scrollTo(0, 500)")
            time.sleep(settings.SCROLL_PAUSE_TIME)
            
            # Extrair informações de contato (se disponíveis)
            try:
                # Clicar em "Ver informações de contato" se existir
                contact_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Ver informações de contato')]")
                contact_button.click()
                time.sleep(settings.NAVIGATION_DELAY)
                
                # Extrair email
                try:
                    email = driver.find_element(By.CSS_SELECTOR, ".org-contact-info__email").text.strip()
                    company_data['email'] = email
                except NoSuchElementException:
                    logger.warning("Email não encontrado nas informações de contato")
                
                # Extrair telefone
                try:
                    phone = driver.find_element(By.CSS_SELECTOR, ".org-contact-info__phone").text.strip()
                    company_data['phone'] = phone
                except NoSuchElementException:
                    logger.warning("Telefone não encontrado nas informações de contato")
                
                # Fechar modal
                try:
                    close_button = driver.find_element(By.CSS_SELECTOR, ".artdeco-modal__dismiss")
                    close_button.click()
                    time.sleep(1)
                except:
                    pass
                
            except NoSuchElementException:
                logger.warning("Botão de informações de contato não encontrado")
            
            # Extrair informações sobre funcionários
            try:
                # Tentar encontrar algum funcionário listado
                employees = driver.find_elements(By.CSS_SELECTOR, ".org-people-profile-card__profile-info")
                if employees and len(employees) > 0:
                    employee = employees[0]
                    name_element = employee.find_element(By.CSS_SELECTOR, ".org-people-profile-card__profile-title")
                    full_name = name_element.text.strip()
                    
                    # Dividir em primeiro e segundo nome
                    name_parts = full_name.split(' ', 1)
                    if len(name_parts) >= 2:
                        company_data['first_name'] = name_parts[0]
                        company_data['last_name'] = name_parts[1]
                    else:
                        company_data['first_name'] = full_name
                    
                    # Extrair cargo
                    try:
                        position = employee.find_element(By.CSS_SELECTOR, ".org-people-profile-card__profile-position").text.strip()
                        company_data['position'] = position
                    except:
                        pass
            except:
                logger.warning("Não foi possível extrair informações de funcionários")
        
        except Exception as e:
            logger.error(f"Erro ao extrair dados da empresa: {e}")
        
        return company_data
    
    def _login(self, driver) -> bool:
        """
        Realiza login no LinkedIn.
        
        Args:
            driver: Driver Selenium
            
        Returns:
            True se o login for bem-sucedido, False caso contrário
        """
        try:
            logger.info("Tentando login no LinkedIn")
            
            # Navegar para página de login
            driver.get("https://www.linkedin.com/login")
            time.sleep(settings.NAVIGATION_DELAY)
            
            # Preencher credenciais
            username_field = driver.find_element(By.ID, "username")
            password_field = driver.find_element(By.ID, "password")
            
            username_field.send_keys(settings.LINKEDIN_USERNAME)
            password_field.send_keys(settings.LINKEDIN_PASSWORD)
            
            # Clicar no botão de login
            login_button = driver.find_element(By.CSS_SELECTOR, ".login__form_action_container button")
            login_button.click()
            
            time.sleep(settings.NAVIGATION_DELAY * 2)
            
            # Verificar se o login foi bem-sucedido
            if "feed" in driver.current_url or "checkpoint" in driver.current_url:
                logger.info("Login no LinkedIn bem-sucedido")
                self.logged_in = True
                return True
            else:
                logger.warning("Login no LinkedIn falhou")
                return False
        
        except Exception as e:
            logger.error(f"Erro durante login no LinkedIn: {e}")
            return False
