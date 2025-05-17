"""
Scraper específico para sites corporativos.
Responsável por extrair informações de contato e dados adicionais de sites de empresas.
"""

import logging
import time
import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from ...utils.selenium_manager import SeleniumManager

logger = logging.getLogger(__name__)

class CompanySiteScraper(BaseScraper):
    """
    Scraper para extrair informações de sites corporativos.
    """
    
    def __init__(self):
        """Inicializa o scraper de sites corporativos."""
        super().__init__("CompanySite", requires_selenium=True)
    
    def search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Realiza uma busca por sites corporativos com base nos critérios fornecidos.
        
        Args:
            criteria: Critérios de busca
            
        Returns:
            Lista de sites encontrados
        """
        logger.info(f"Iniciando busca por sites corporativos com critérios: {criteria}")
        
        results = []
        
        # Verificar se há uma lista específica de empresas ou domínios
        if 'company_list' in criteria and criteria['company_list']:
            logger.info(f"Usando lista de {len(criteria['company_list'])} empresas fornecida")
            
            # Para cada empresa na lista, buscar site
            for company_name in criteria['company_list']:
                # Buscar site usando Google
                site_info = self._search_site_by_name(company_name)
                if site_info:
                    results.append(site_info)
            
            return results
        
        # Se não houver lista específica, retornar lista vazia
        # (este scraper depende de nomes de empresas ou domínios específicos)
        logger.warning("Nenhuma lista de empresas fornecida para busca de sites corporativos")
        return results
    
    def collect(self, target: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """
        Coleta informações detalhadas de um site corporativo.
        
        Args:
            target: Empresa alvo
            fields: Campos a serem coletados
            
        Returns:
            Dados coletados
        """
        logger.info(f"Coletando dados de site corporativo para: {target.get('name', 'Desconhecido')}")
        
        collected_data = {
            'source': 'company_site',
            'name': target.get('name', '')
        }
        
        # Verificar se há domínio ou website
        domain = target.get('domain', '')
        website = target.get('website', '')
        
        if not domain and not website:
            # Tentar buscar site pelo nome
            if collected_data['name']:
                site_info = self._search_site_by_name(collected_data['name'])
                if site_info and 'website' in site_info:
                    website = site_info['website']
                    
                    # Extrair domínio do site
                    if website:
                        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', website)
                        if domain_match:
                            domain = domain_match.group(1)
            
            if not domain and not website:
                logger.warning("Domínio ou website não fornecido para coleta")
                return collected_data
        
        # Se tiver apenas domínio, construir URL
        if domain and not website:
            website = f"https://{domain}"
        
        # Armazenar website e domínio
        collected_data['website'] = website
        collected_data['domain'] = domain or self._extract_domain(website)
        
        # Usar Selenium para extrair dados
        with SeleniumManager(headless=True) as driver:
            try:
                # Navegar para página inicial
                logger.info(f"Navegando para: {website}")
                driver.get(website)
                time.sleep(5)  # Aguardar carregamento
                
                # Extrair título da página
                try:
                    title = driver.title
                    if title:
                        collected_data['site_title'] = title.strip()
                except Exception as e:
                    logger.warning(f"Erro ao extrair título: {e}")
                
                # Extrair dados de contato da página inicial
                contact_data = self._extract_contact_data(driver)
                collected_data.update(contact_data)
                
                # Procurar e navegar para página de contato
                contact_page = self._find_contact_page(driver, website)
                if contact_page:
                    # Navegar para página de contato
                    logger.info(f"Navegando para página de contato: {contact_page}")
                    driver.get(contact_page)
                    time.sleep(3)
                    
                    # Extrair dados de contato da página de contato
                    contact_data = self._extract_contact_data(driver)
                    
                    # Atualizar dados coletados (priorizar dados da página de contato)
                    for key, value in contact_data.items():
                        if value:  # Só atualizar se o valor não for vazio
                            collected_data[key] = value
                
                # Procurar e navegar para página "sobre"
                about_page = self._find_about_page(driver, website)
                if about_page:
                    # Navegar para página "sobre"
                    logger.info(f"Navegando para página 'sobre': {about_page}")
                    driver.get(about_page)
                    time.sleep(3)
                    
                    # Extrair dados da página "sobre"
                    about_data = self._extract_about_data(driver)
                    
                    # Atualizar dados coletados
                    for key, value in about_data.items():
                        if value and key not in collected_data:  # Só atualizar se o valor não for vazio e o campo não existir
                            collected_data[key] = value
                
                logger.info(f"Coleta concluída para site {collected_data['website']}")
                
            except Exception as e:
                logger.error(f"Erro durante coleta no site corporativo: {e}")
        
        return collected_data
    
    def _search_site_by_name(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Busca site pelo nome da empresa.
        
        Args:
            company_name: Nome da empresa
            
        Returns:
            Informações do site ou None
        """
        logger.info(f"Buscando site para empresa: {company_name}")
        
        # Usar Selenium para buscar no Google
        with SeleniumManager(headless=True) as driver:
            try:
                # Navegar para página de busca
                search_query = f"{company_name} site oficial"
                search_url = f"https://www.google.com/search?q={search_query}"
                driver.get(search_url)
                time.sleep(3)
                
                # Extrair primeiro resultado
                try:
                    result_element = driver.find_element(By.CSS_SELECTOR, "div.g a")
                    if result_element:
                        website = result_element.get_attribute("href")
                        
                        # Verificar se é um resultado válido
                        if website and not any(x in website for x in ["google.com", "youtube.com", "facebook.com", "instagram.com", "linkedin.com"]):
                            # Extrair domínio
                            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', website)
                            domain = domain_match.group(1) if domain_match else ""
                            
                            return {
                                'name': company_name,
                                'website': website,
                                'domain': domain,
                                'source': 'company_site'
                            }
                except NoSuchElementException:
                    logger.warning("Nenhum resultado encontrado")
            
            except Exception as e:
                logger.error(f"Erro ao buscar site para {company_name}: {e}")
        
        return None
    
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
            
            # Remover www. se presente
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except Exception as e:
            logger.error(f"Erro ao extrair domínio de {url}: {e}")
            return ""
    
    def _find_contact_page(self, driver, base_url: str) -> Optional[str]:
        """
        Procura link para página de contato.
        
        Args:
            driver: Driver Selenium
            base_url: URL base do site
            
        Returns:
            URL da página de contato ou None
        """
        # Lista de termos comuns para páginas de contato
        contact_terms = [
            "contato", "fale conosco", "fale-conosco", "contact", "contact us", 
            "contacto", "atendimento", "suporte", "support"
        ]
        
        try:
            # Procurar links que contenham termos de contato
            links = driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                try:
                    href = link.get_attribute("href")
                    text = link.text.lower()
                    
                    if not href:
                        continue
                    
                    # Verificar texto do link
                    if any(term in text for term in contact_terms):
                        return href
                    
                    # Verificar URL do link
                    if any(term in href.lower() for term in contact_terms):
                        return href
                except Exception:
                    continue
            
            # Se não encontrou, tentar construir URLs comuns
            common_paths = ["/contato", "/fale-conosco", "/contact", "/contact-us", "/atendimento"]
            
            for path in common_paths:
                contact_url = urljoin(base_url, path)
                
                # Verificar se a página existe
                try:
                    response = requests.head(contact_url, timeout=5)
                    if response.status_code == 200:
                        return contact_url
                except Exception:
                    continue
            
            return None
        
        except Exception as e:
            logger.error(f"Erro ao procurar página de contato: {e}")
            return None
    
    def _find_about_page(self, driver, base_url: str) -> Optional[str]:
        """
        Procura link para página "sobre".
        
        Args:
            driver: Driver Selenium
            base_url: URL base do site
            
        Returns:
            URL da página "sobre" ou None
        """
        # Lista de termos comuns para páginas "sobre"
        about_terms = [
            "sobre", "quem somos", "quem-somos", "about", "about us", 
            "institucional", "a empresa", "empresa", "company"
        ]
        
        try:
            # Procurar links que contenham termos "sobre"
            links = driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                try:
                    href = link.get_attribute("href")
                    text = link.text.lower()
                    
                    if not href:
                        continue
                    
                    # Verificar texto do link
                    if any(term in text for term in about_terms):
                        return href
                    
                    # Verificar URL do link
                    if any(term in href.lower() for term in about_terms):
                        return href
                except Exception:
                    continue
            
            # Se não encontrou, tentar construir URLs comuns
            common_paths = ["/sobre", "/quem-somos", "/about", "/about-us", "/institucional", "/empresa"]
            
            for path in common_paths:
                about_url = urljoin(base_url, path)
                
                # Verificar se a página existe
                try:
                    response = requests.head(about_url, timeout=5)
                    if response.status_code == 200:
                        return about_url
                except Exception:
                    continue
            
            return None
        
        except Exception as e:
            logger.error(f"Erro ao procurar página 'sobre': {e}")
            return None
    
    def _extract_contact_data(self, driver) -> Dict[str, Any]:
        """
        Extrai dados de contato de uma página.
        
        Args:
            driver: Driver Selenium
            
        Returns:
            Dados de contato extraídos
        """
        contact_data = {}
        
        try:
            # Extrair página completa
            page_source = driver.page_source
            
            # Extrair emails
            emails = self._extract_emails(page_source)
            if emails:
                contact_data['email'] = emails[0]  # Usar primeiro email
            
            # Extrair telefones
            phones = self._extract_phones(page_source)
            if phones:
                contact_data['phone'] = phones[0]  # Usar primeiro telefone
                if len(phones) > 1:
                    contact_data['phone2'] = phones[1]  # Usar segundo telefone
            
            # Extrair endereços
            addresses = self._extract_addresses(page_source)
            if addresses:
                contact_data['address'] = addresses[0]  # Usar primeiro endereço
            
            # Extrair redes sociais
            social_links = self._extract_social_links(driver)
            contact_data.update(social_links)
            
            return contact_data
        
        except Exception as e:
            logger.error(f"Erro ao extrair dados de contato: {e}")
            return contact_data
    
    def _extract_about_data(self, driver) -> Dict[str, Any]:
        """
        Extrai dados da página "sobre".
        
        Args:
            driver: Driver Selenium
            
        Returns:
            Dados extraídos
        """
        about_data = {}
        
        try:
            # Extrair página completa
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extrair descrição da empresa
            # Procurar em parágrafos
            paragraphs = soup.find_all('p')
            if paragraphs:
                # Filtrar parágrafos vazios ou muito curtos
                valid_paragraphs = [p.text.strip() for p in paragraphs if len(p.text.strip()) > 50]
                if valid_paragraphs:
                    about_data['description'] = valid_paragraphs[0]
            
            # Procurar informações sobre tamanho da empresa
            size_patterns = [
                r'(\d+)[+\s]*(?:funcionários|colaboradores|empregados|employees)',
                r'(?:mais de|cerca de|aproximadamente)\s+(\d+)\s+(?:funcionários|colaboradores|empregados|employees)'
            ]
            
            for pattern in size_patterns:
                size_match = re.search(pattern, page_source, re.IGNORECASE)
                if size_match:
                    about_data['employee_count'] = size_match.group(1)
                    about_data['size'] = self._classify_company_size(int(size_match.group(1)))
                    break
            
            # Procurar ano de fundação
            foundation_patterns = [
                r'(?:fundada|criada|estabelecida|founded|established)\s+em\s+(\d{4})',
                r'(?:desde|since)\s+(\d{4})',
                r'(?:fundada|criada|estabelecida|founded|established)(?:\s+\w+){0,3}\s+(\d{4})'
            ]
            
            for pattern in foundation_patterns:
                foundation_match = re.search(pattern, page_source, re.IGNORECASE)
                if foundation_match:
                    about_data['foundation_year'] = foundation_match.group(1)
                    break
            
            return about_data
        
        except Exception as e:
            logger.error(f"Erro ao extrair dados da página 'sobre': {e}")
            return about_data
    
    def _extract_emails(self, text: str) -> List[str]:
        """
        Extrai endereços de email de um texto.
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Lista de emails encontrados
        """
        # Padrão de email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Encontrar todos os emails
        emails = re.findall(email_pattern, text)
        
        # Filtrar emails inválidos
        valid_emails = []
        for email in emails:
            # Verificar se não é um falso positivo
            if not any(x in email for x in ["@example", "@dominio", "@email", "@teste", "@test"]):
                valid_emails.append(email)
        
        return valid_emails
    
    def _extract_phones(self, text: str) -> List[str]:
        """
        Extrai números de telefone de um texto.
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Lista de telefones encontrados
        """
        # Padrões de telefone brasileiros
        phone_patterns = [
            r'\(\d{2}\)\s*\d{4,5}-\d{4}',  # (XX) XXXX-XXXX ou (XX) XXXXX-XXXX
            r'\(\d{2}\)\s*\d{8,9}',        # (XX) XXXXXXXX ou (XX) XXXXXXXXX
            r'\d{2}\s*\d{4,5}-\d{4}',      # XX XXXX-XXXX ou XX XXXXX-XXXX
            r'\d{2}\s*\d{8,9}',            # XX XXXXXXXX ou XX XXXXXXXXX
            r'\+55\s*\d{2}\s*\d{4,5}-\d{4}',  # +55 XX XXXX-XXXX ou +55 XX XXXXX-XXXX
            r'\+55\s*\d{2}\s*\d{8,9}'         # +55 XX XXXXXXXX ou +55 XX XXXXXXXXX
        ]
        
        # Encontrar todos os telefones
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))
        
        return phones
    
    def _extract_addresses(self, text: str) -> List[str]:
        """
        Extrai endereços de um texto.
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Lista de endereços encontrados
        """
        # Padrões de endereço brasileiros
        address_patterns = [
            r'(?:Rua|R\.|Avenida|Av\.|Alameda|Al\.|Praça|Pça\.|Rodovia|Rod\.)\s+[^,\n]+(?:,\s*[^,\n]+){1,3}',
            r'(?:Rua|R\.|Avenida|Av\.|Alameda|Al\.|Praça|Pça\.|Rodovia|Rod\.)\s+[^,\n]+,\s*n[º°]?\s*\d+',
            r'(?:Rua|R\.|Avenida|Av\.|Alameda|Al\.|Praça|Pça\.|Rodovia|Rod\.)\s+[^,\n]+,\s*\d+',
            r'(?:Rua|R\.|Avenida|Av\.|Alameda|Al\.|Praça|Pça\.|Rodovia|Rod\.)\s+[^,\n]+\s*,\s*(?:Bairro|B\.)\s+[^,\n]+'
        ]
        
        # Encontrar todos os endereços
        addresses = []
        for pattern in address_patterns:
            addresses.extend(re.findall(pattern, text, re.IGNORECASE))
        
        # Filtrar endereços muito curtos
        valid_addresses = [addr for addr in addresses if len(addr) > 15]
        
        return valid_addresses
    
    def _extract_social_links(self, driver) -> Dict[str, str]:
        """
        Extrai links para redes sociais.
        
        Args:
            driver: Driver Selenium
            
        Returns:
            Dicionário com links para redes sociais
        """
        social_links = {}
        
        try:
            # Lista de domínios de redes sociais
            social_domains = {
                'facebook.com': 'facebook',
                'instagram.com': 'instagram',
                'twitter.com': 'twitter',
                'linkedin.com': 'linkedin',
                'youtube.com': 'youtube'
            }
            
            # Procurar links
            links = driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                try:
                    href = link.get_attribute("href")
                    
                    if not href:
                        continue
                    
                    # Verificar se é um link de rede social
                    for domain, name in social_domains.items():
                        if domain in href:
                            social_links[f'{name}_url'] = href
                            break
                except Exception:
                    continue
            
            return social_links
        
        except Exception as e:
            logger.error(f"Erro ao extrair links de redes sociais: {e}")
            return social_links
    
    def _classify_company_size(self, employee_count: int) -> str:
        """
        Classifica o tamanho da empresa com base no número de funcionários.
        
        Args:
            employee_count: Número de funcionários
            
        Returns:
            Classificação de tamanho
        """
        if employee_count < 10:
            return "Microempresa"
        elif employee_count < 50:
            return "Pequeno Porte"
        elif employee_count < 250:
            return "Médio Porte"
        else:
            return "Grande Porte"
