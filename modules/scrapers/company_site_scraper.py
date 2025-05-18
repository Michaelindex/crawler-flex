"""
Scraper especializado para sites corporativos.
Responsável por extrair informações diretamente dos sites das empresas.
"""

import logging
import time
import re
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urljoin

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
        self.cnpj_pattern = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}')
        
        # Páginas comuns para informações de contato
        self.contact_pages = [
            '/contato', '/contact', '/fale-conosco', '/about', '/sobre', 
            '/quem-somos', '/institucional', '/empresa', '/a-empresa',
            '/sobre-nos', '/about-us', '/contatos', '/contacts'
        ]
        
        # Termos para busca de informações específicas
        self.terms = {
            'fantasy_name': ['nome fantasia', 'fantasy name', 'marca', 'brand', 'trade name'],
            'employees': ['funcionários', 'employees', 'colaboradores', 'equipe', 'team', 'pessoas', 'people'],
            'size': ['tamanho', 'size', 'porte', 'scale'],
            'cnpj': ['cnpj', 'cadastro nacional', 'inscrição']
        }
    
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
            search_results = self.searx_client.search(search_query, max_results=10)
            
            if not search_results:
                logger.warning(f"Nenhum resultado de busca encontrado para {company_name}")
                # Tentar busca alternativa
                search_query = f"{company_name} website"
                search_results = self.searx_client.search(search_query, max_results=10)
                if not search_results:
                    return company_data
            
            # Filtrar resultados para encontrar o site oficial
            official_site = None
            for result in search_results:
                # Verificar se o resultado é um dicionário ou uma string
                if isinstance(result, dict):
                    url = result.get('url', '')
                    title = result.get('title', '')
                elif isinstance(result, str):
                    # Se for string, assumir que é a URL
                    url = result
                    title = ""
                else:
                    continue
                
                # Verificar se o título ou URL contém o nome da empresa
                if self._is_likely_official_site(url, title, company_name):
                    official_site = url
                    break
            
            if not official_site:
                # Tentar busca direta pelo domínio
                company_domain = self._guess_domain(company_name)
                if company_domain:
                    official_site = f"https://{company_domain}"
                    logger.info(f"Tentando domínio direto: {official_site}")
                else:
                    logger.warning(f"Site oficial não encontrado para {company_name}")
                    return company_data
            
            logger.info(f"Site oficial encontrado para {company_name}: {official_site}")
            company_data['domain'] = self._extract_domain(official_site)
            company_data['website'] = official_site
            
            # Extrair informações do site oficial
            with SeleniumManager() as driver:
                if not driver:
                    logger.error("Falha ao inicializar o driver Selenium")
                    return company_data
                
                # Navegar para o site oficial
                logger.info(f"Navegando para: {official_site}")
                try:
                    driver.get(official_site)
                    time.sleep(settings.NAVIGATION_DELAY)
                except Exception as e:
                    logger.error(f"Falha ao navegar para {official_site}: {e}")
                    return company_data
                
                # Extrair informações da página inicial
                self._extract_contact_info(driver, company_data)
                self._extract_company_info(driver, company_data, company_name)
                
                # Verificar páginas de contato
                for contact_page in self.contact_pages:
                    try:
                        contact_url = urljoin(official_site, contact_page)
                        logger.info(f"Verificando página de contato: {contact_url}")
                        
                        driver.get(contact_url)
                        time.sleep(settings.NAVIGATION_DELAY)
                        
                        # Extrair informações da página de contato
                        self._extract_contact_info(driver, company_data)
                        self._extract_company_info(driver, company_data, company_name)
                        
                        # Se encontrou informações suficientes, parar
                        if self._has_sufficient_info(company_data):
                            break
                    
                    except Exception as e:
                        logger.warning(f"Erro ao acessar página de contato {contact_page}: {e}")
                        continue
                
                # Buscar página "Sobre" ou "Quem Somos" se ainda faltam informações
                if not self._has_sufficient_info(company_data):
                    self._find_and_navigate_about_page(driver, company_data, company_name)
                
                # Buscar informações específicas que ainda estão faltando
                self._search_for_missing_info(driver, company_data, company_name)
        
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
            if 'phone' not in company_data or 'phone2' not in company_data:
                phones = self.phone_pattern.findall(page_text)
                if phones:
                    # Formatar telefones encontrados
                    formatted_phones = []
                    for phone_parts in phones:
                        formatted_phone = ''
                        
                        if phone_parts[0]:  # DDD
                            formatted_phone += phone_parts[0].replace('(', '').replace(')', '').strip()
                        
                        if phone_parts[1] and phone_parts[2]:  # Número
                            if formatted_phone:
                                formatted_phone += ' '
                            formatted_phone += f"{phone_parts[1].strip()}-{phone_parts[2].strip()}"
                        
                        if formatted_phone and formatted_phone not in formatted_phones:
                            formatted_phones.append(formatted_phone)
                    
                    # Atribuir telefones
                    if formatted_phones and 'phone' not in company_data:
                        company_data['phone'] = formatted_phones[0]
                    
                    if len(formatted_phones) > 1 and 'phone2' not in company_data:
                        company_data['phone2'] = formatted_phones[1]
            
            # Extrair CNPJ
            if 'cnpj' not in company_data:
                cnpjs = self.cnpj_pattern.findall(page_text)
                if cnpjs:
                    company_data['cnpj'] = cnpjs[0]
            
            # Extrair endereço
            if 'address' not in company_data:
                # Procurar por elementos que possam conter endereços
                address_candidates = driver.find_elements(By.XPATH, "//*[contains(text(), 'Endereço') or contains(text(), 'endereço') or contains(text(), 'Localização') or contains(text(), 'localização') or contains(text(), 'Address')]")
                
                for candidate in address_candidates:
                    try:
                        # Verificar o texto do elemento pai ou próximo irmão
                        parent = candidate.find_element(By.XPATH, "./..")
                        address_text = parent.text
                        
                        # Se o texto parece um endereço (contém número, CEP, etc.)
                        if re.search(r'\d+.*(?:CEP|cep).*\d+', address_text) or re.search(r'\d+.*(?:Bairro|bairro)', address_text):
                            company_data['address'] = address_text
                            
                            # Tentar extrair cidade e estado
                            city_state_match = re.search(r'([A-Za-zÀ-ÿ\s]+)\s*[-,]\s*([A-Z]{2})', address_text)
                            if city_state_match:
                                company_data['city'] = city_state_match.group(1).strip()
                                company_data['state'] = city_state_match.group(2).strip()
                            
                            break
                    except (NoSuchElementException, StaleElementReferenceException):
                        continue
        
        except Exception as e:
            logger.error(f"Erro ao extrair informações de contato: {e}")
    
    def _extract_company_info(self, driver, company_data: Dict[str, Any], company_name: str) -> None:
        """
        Extrai informações gerais da empresa.
        
        Args:
            driver: Driver Selenium
            company_data: Dicionário para armazenar os dados extraídos
            company_name: Nome da empresa
        """
        try:
            # Extrair nome fantasia
            if 'fantasy_name' not in company_data:
                # Procurar por elementos que possam conter o nome fantasia
                for term in self.terms['fantasy_name']:
                    try:
                        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{term}')]")
                        for element in elements:
                            try:
                                parent = element.find_element(By.XPATH, "./..")
                                text = parent.text
                                
                                # Procurar por padrões como "Nome Fantasia: XYZ"
                                match = re.search(f"{term}[:\s]+([^\n]+)", text, re.IGNORECASE)
                                if match:
                                    company_data['fantasy_name'] = match.group(1).strip()
                                    break
                            except (NoSuchElementException, StaleElementReferenceException):
                                continue
                        
                        if 'fantasy_name' in company_data:
                            break
                    except Exception:
                        continue
                
                # Se não encontrou, usar o nome da empresa como fallback
                if 'fantasy_name' not in company_data:
                    # Tentar encontrar o nome da empresa em destaque na página
                    try:
                        # Procurar em h1, h2, logo alt text, etc.
                        headers = driver.find_elements(By.CSS_SELECTOR, "h1, h2, img[alt*='logo']")
                        for header in headers:
                            text = header.text if header.tag_name in ['h1', 'h2'] else header.get_attribute('alt')
                            if text and company_name.lower() in text.lower():
                                company_data['fantasy_name'] = text.strip()
                                break
                    except Exception:
                        pass
            
            # Extrair tamanho da empresa (número de funcionários)
            if 'size' not in company_data:
                for term in self.terms['employees']:
                    try:
                        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{term}')]")
                        for element in elements:
                            try:
                                text = element.text
                                # Procurar por padrões como "X funcionários" ou "equipe de X pessoas"
                                size_match = re.search(r'(\d+[\d.]*)\s*(?:' + term + ')', text, re.IGNORECASE)
                                if size_match:
                                    company_data['size'] = f"{size_match.group(1)} {term}"
                                    break
                            except (StaleElementReferenceException):
                                continue
                        
                        if 'size' in company_data:
                            break
                    except Exception:
                        continue
            
            # Extrair CNPJ se ainda não tiver
            if 'cnpj' not in company_data:
                for term in self.terms['cnpj']:
                    try:
                        elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{term}')]")
                        for element in elements:
                            try:
                                parent = element.find_element(By.XPATH, "./..")
                                text = parent.text
                                
                                # Procurar por CNPJ no formato XX.XXX.XXX/XXXX-XX
                                cnpj_match = re.search(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', text)
                                if cnpj_match:
                                    company_data['cnpj'] = cnpj_match.group(0)
                                    break
                            except (NoSuchElementException, StaleElementReferenceException):
                                continue
                        
                        if 'cnpj' in company_data:
                            break
                    except Exception:
                        continue
        
        except Exception as e:
            logger.error(f"Erro ao extrair informações da empresa: {e}")
    
    def _find_and_navigate_about_page(self, driver, company_data: Dict[str, Any], company_name: str) -> None:
        """
        Encontra e navega para a página "Sobre" ou "Quem Somos".
        
        Args:
            driver: Driver Selenium
            company_data: Dicionário para armazenar os dados extraídos
            company_name: Nome da empresa
        """
        try:
            # Lista de termos para procurar links de "Sobre"
            about_terms = ['sobre', 'about', 'quem somos', 'who we are', 'a empresa', 'the company', 'institucional']
            
            # Procurar links que contenham esses termos
            for term in about_terms:
                try:
                    links = driver.find_elements(By.XPATH, f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{term}')]")
                    
                    if not links:
                        # Tentar encontrar por href
                        links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{term}')]")
                    
                    if links:
                        for link in links:
                            try:
                                href = link.get_attribute('href')
                                if href:
                                    logger.info(f"Navegando para página 'Sobre': {href}")
                                    driver.get(href)
                                    time.sleep(settings.NAVIGATION_DELAY)
                                    
                                    # Extrair informações
                                    self._extract_contact_info(driver, company_data)
                                    self._extract_company_info(driver, company_data, company_name)
                                    
                                    # Se encontrou informações suficientes, parar
                                    if self._has_sufficient_info(company_data):
                                        return
                            except Exception:
                                continue
                except Exception:
                    continue
        
        except Exception as e:
            logger.error(f"Erro ao procurar página 'Sobre': {e}")
    
    def _search_for_missing_info(self, driver, company_data: Dict[str, Any], company_name: str) -> None:
        """
        Busca informações específicas que ainda estão faltando.
        
        Args:
            driver: Driver Selenium
            company_data: Dicionário para armazenar os dados extraídos
            company_name: Nome da empresa
        """
        try:
            current_url = driver.current_url
            base_url = '/'.join(current_url.split('/')[:3])  # http(s)://domain.com
            
            # Lista de informações faltantes e termos de busca
            missing_info = []
            
            if 'fantasy_name' not in company_data:
                missing_info.append(('fantasy_name', 'nome fantasia'))
            
            if 'size' not in company_data:
                missing_info.append(('size', 'número de funcionários'))
            
            if 'cnpj' not in company_data:
                missing_info.append(('cnpj', 'cnpj'))
            
            # Buscar cada informação faltante
            for info_key, search_term in missing_info:
                try:
                    # Tentar usar a busca interna do site
                    search_elements = driver.find_elements(By.XPATH, "//input[@type='search' or contains(@class, 'search') or @placeholder='Buscar' or @placeholder='Search']")
                    
                    if search_elements:
                        search_input = search_elements[0]
                        search_input.clear()
                        search_input.send_keys(search_term)
                        search_input.send_keys(Keys.RETURN)
                        time.sleep(settings.NAVIGATION_DELAY)
                        
                        # Extrair informações da página de resultados
                        self._extract_contact_info(driver, company_data)
                        self._extract_company_info(driver, company_data, company_name)
                        
                        # Voltar para a página anterior
                        driver.back()
                        time.sleep(settings.NAVIGATION_DELAY)
                except Exception:
                    pass
            
            # Se ainda faltam informações, tentar buscar em páginas específicas
            if not self._has_sufficient_info(company_data):
                specific_pages = [
                    '/legal', '/juridico', '/termos', '/terms', 
                    '/privacidade', '/privacy', '/politica-de-privacidade',
                    '/dados-da-empresa', '/company-data'
                ]
                
                for page in specific_pages:
                    try:
                        page_url = urljoin(base_url, page)
                        logger.info(f"Verificando página específica: {page_url}")
                        
                        driver.get(page_url)
                        time.sleep(settings.NAVIGATION_DELAY)
                        
                        # Extrair informações
                        self._extract_contact_info(driver, company_data)
                        self._extract_company_info(driver, company_data, company_name)
                        
                        # Se encontrou informações suficientes, parar
                        if self._has_sufficient_info(company_data):
                            break
                    except Exception:
                        continue
        
        except Exception as e:
            logger.error(f"Erro ao buscar informações faltantes: {e}")
    
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
        title_contains_name = company_name.lower() in title.lower() if title else False
        
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
    
    def _guess_domain(self, company_name: str) -> str:
        """
        Tenta adivinhar o domínio da empresa com base no nome.
        
        Args:
            company_name: Nome da empresa
            
        Returns:
            Domínio adivinhado ou None
        """
        # Simplificar o nome da empresa
        simplified = company_name.lower()
        
        # Remover termos comuns
        for term in ['s.a.', 's/a', 'sa', 'ltda', 'eireli', 'mei', 'me', 'epp', 'corporation', 'inc', 'corp']:
            simplified = simplified.replace(term, '')
        
        # Remover pontuação e espaços
        simplified = re.sub(r'[^\w\s]', '', simplified)
        simplified = simplified.strip()
        
        # Substituir espaços por vazio
        simplified = simplified.replace(' ', '')
        
        # Tentar domínios comuns
        domains = [
            f"{simplified}.com.br",
            f"{simplified}.com",
            f"{simplified}.net.br",
            f"{simplified}.net",
            f"{simplified}.org.br",
            f"{simplified}.org"
        ]
        
        # Se o nome for composto, tentar variações com hífen
        if ' ' in company_name:
            hyphenated = company_name.lower().replace(' ', '-')
            hyphenated = re.sub(r'[^\w\-]', '', hyphenated)
            
            domains.extend([
                f"{hyphenated}.com.br",
                f"{hyphenated}.com"
            ])
        
        return domains[0] if domains else None
    
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
        # Lista de campos importantes
        important_fields = ['fantasy_name', 'domain', 'email', 'phone', 'size', 'cnpj']
        
        # Contar quantos campos importantes estão preenchidos
        filled_fields = sum(1 for field in important_fields if field in company_data and company_data[field])
        
        # Considerar suficiente se pelo menos 4 campos importantes estiverem preenchidos
        return filled_fields >= 4
