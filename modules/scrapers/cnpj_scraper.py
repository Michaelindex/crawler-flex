"""
Scraper específico para dados de CNPJ.
Responsável por extrair informações fiscais e cadastrais de empresas.
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
import requests
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from utils.selenium_manager import SeleniumManager

logger = logging.getLogger(__name__)

class CNPJScraper(BaseScraper):
    """
    Scraper para extrair informações fiscais e cadastrais de empresas.
    """
    
    def __init__(self):
        """Inicializa o scraper de CNPJ."""
        super().__init__("CNPJ", requires_selenium=True)
        self.cnpj_biz_url = "https://cnpj.biz/"
        self.receita_ws_url = "https://receitaws.com.br/v1/cnpj/"
    
    def search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Realiza uma busca por CNPJs com base nos critérios fornecidos.
        
        Args:
            criteria: Critérios de busca
            
        Returns:
            Lista de empresas encontradas
        """
        logger.info(f"Iniciando busca de CNPJ com critérios: {criteria}")
        
        results = []
        
        # Verificar se há uma lista específica de empresas
        if 'company_list' in criteria and criteria['company_list']:
            logger.info(f"Usando lista de {len(criteria['company_list'])} empresas fornecida")
            
            # Para cada empresa na lista, buscar CNPJ
            for company_name in criteria['company_list']:
                # Buscar CNPJ usando Selenium
                cnpj_info = self._search_cnpj_by_name(company_name)
                if cnpj_info:
                    results.append(cnpj_info)
            
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
        
        # Buscar empresas usando SearXNG ou outra fonte
        # (Implementação simplificada - na versão completa, usaria uma API de busca)
        
        # Lista de CNPJs de exemplo por setor (simplificada)
        tech_cnpjs = [
            {"name": "TOTVS S.A.", "cnpj": "53113791000122"},
            {"name": "LOCAWEB SERVIÇOS DE INTERNET S.A.", "cnpj": "02351877000152"},
            {"name": "POSITIVO TECNOLOGIA S.A.", "cnpj": "81243735000148"},
            {"name": "LINX S.A.", "cnpj": "06948969000175"},
            {"name": "CI&T SOFTWARE S.A.", "cnpj": "00609634000146"}
        ]
        
        health_cnpjs = [
            {"name": "FLEURY S.A.", "cnpj": "60840055000131"},
            {"name": "DIAGNÓSTICOS DA AMÉRICA S.A.", "cnpj": "61486650000183"},
            {"name": "HAPVIDA ASSISTÊNCIA MÉDICA LTDA", "cnpj": "63554067000198"},
            {"name": "INSTITUTO HERMES PARDINI S.A.", "cnpj": "19378769000176"},
            {"name": "REDE D'OR SÃO LUIZ S.A.", "cnpj": "06047087000139"}
        ]
        
        finance_cnpjs = [
            {"name": "NU PAGAMENTOS S.A.", "cnpj": "18236120000158"},
            {"name": "STONE PAGAMENTOS S.A.", "cnpj": "16501555000157"},
            {"name": "PAGSEGURO INTERNET S.A.", "cnpj": "08561701000101"},
            {"name": "XP INVESTIMENTOS S.A.", "cnpj": "02332886000104"},
            {"name": "BANCO INTER S.A.", "cnpj": "00416968000101"}
        ]
        
        retail_cnpjs = [
            {"name": "MAGAZINE LUIZA S.A.", "cnpj": "47960950000121"},
            {"name": "VIA VAREJO S.A.", "cnpj": "33041260065290"},
            {"name": "LOJAS RENNER S.A.", "cnpj": "92754738000162"},
            {"name": "AMERICANAS S.A.", "cnpj": "00776574000156"},
            {"name": "RAIA DROGASIL S.A.", "cnpj": "61585865000151"}
        ]
        
        # Selecionar lista com base no setor
        sector_name = criteria.get('sector', {}).get('main', '').lower()
        if "saude" in sector_name or "saúde" in sector_name:
            cnpjs_list = health_cnpjs
        elif "finan" in sector_name or "banco" in sector_name:
            cnpjs_list = finance_cnpjs
        elif "varejo" in sector_name or "retail" in sector_name:
            cnpjs_list = retail_cnpjs
        else:
            cnpjs_list = tech_cnpjs
        
        # Limitar resultados conforme configuração
        max_results = criteria.get('output', {}).get('max_results', 5)
        
        # Adicionar CNPJs à lista de resultados
        for cnpj_info in cnpjs_list[:max_results]:
            results.append({
                'name': cnpj_info["name"],
                'cnpj': cnpj_info["cnpj"],
                'source': 'cnpj',
                'url': f"{self.cnpj_biz_url}{cnpj_info['cnpj']}"
            })
        
        return results
    
    def collect(self, target: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """
        Coleta informações detalhadas de CNPJ para uma empresa específica.
        
        Args:
            target: Empresa alvo
            fields: Campos a serem coletados
            
        Returns:
            Dados coletados
        """
        logger.info(f"Coletando dados de CNPJ para: {target.get('name', 'Desconhecido')}")
        
        collected_data = {
            'source': 'cnpj',
            'name': target.get('name', ''),
            'cnpj': target.get('cnpj', '')
        }
        
        # Verificar se há CNPJ
        if not collected_data['cnpj']:
            # Tentar buscar CNPJ pelo nome
            if collected_data['name']:
                cnpj_info = self._search_cnpj_by_name(collected_data['name'])
                if cnpj_info and 'cnpj' in cnpj_info:
                    collected_data['cnpj'] = cnpj_info['cnpj']
            
            if not collected_data['cnpj']:
                logger.warning("CNPJ não fornecido para coleta")
                return collected_data
        
        # Normalizar CNPJ (remover caracteres especiais)
        cnpj = ''.join(filter(str.isdigit, collected_data['cnpj']))
        
        # Tentar primeiro com ReceitaWS (mais confiável, mas com limites)
        try:
            receita_data = self._collect_from_receitaws(cnpj)
            if receita_data:
                collected_data.update(receita_data)
                logger.info(f"Dados coletados com sucesso da ReceitaWS para CNPJ {cnpj}")
                return collected_data
        except Exception as e:
            logger.warning(f"Erro ao coletar dados da ReceitaWS: {e}")
        
        # Se falhar, tentar com CNPJ.biz usando Selenium
        try:
            cnpj_biz_data = self._collect_from_cnpjbiz(cnpj)
            if cnpj_biz_data:
                collected_data.update(cnpj_biz_data)
                logger.info(f"Dados coletados com sucesso do CNPJ.biz para CNPJ {cnpj}")
                return collected_data
        except Exception as e:
            logger.error(f"Erro ao coletar dados do CNPJ.biz: {e}")
        
        return collected_data
    
    def _search_cnpj_by_name(self, company_name: str) -> Optional[Dict[str, Any]]:
        """
        Busca CNPJ pelo nome da empresa.
        
        Args:
            company_name: Nome da empresa
            
        Returns:
            Informações do CNPJ ou None
        """
        logger.info(f"Buscando CNPJ para empresa: {company_name}")
        
        # Usar Selenium para buscar no CNPJ.biz
        with SeleniumManager(headless=True) as driver:
            try:
                # Navegar para página de busca
                search_url = f"https://www.google.com/search?q={quote(company_name)}+cnpj"
                driver.get(search_url)
                time.sleep(3)
                
                # Procurar padrões de CNPJ nos resultados
                page_source = driver.page_source
                
                # Padrão de CNPJ: XX.XXX.XXX/XXXX-XX
                cnpj_pattern = r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}'
                cnpj_matches = re.findall(cnpj_pattern, page_source)
                
                if cnpj_matches:
                    # Pegar o primeiro CNPJ encontrado
                    cnpj = cnpj_matches[0]
                    # Remover caracteres especiais
                    cnpj_clean = ''.join(filter(str.isdigit, cnpj))
                    
                    return {
                        'name': company_name,
                        'cnpj': cnpj_clean,
                        'cnpj_formatted': cnpj,
                        'source': 'cnpj',
                        'url': f"{self.cnpj_biz_url}{cnpj_clean}"
                    }
                
                # Se não encontrou, tentar buscar diretamente no CNPJ.biz
                search_url = f"{self.cnpj_biz_url}?q={quote(company_name)}"
                driver.get(search_url)
                time.sleep(3)
                
                # Procurar resultados
                try:
                    result_links = driver.find_elements(By.CSS_SELECTOR, "a.empresa")
                    if result_links and len(result_links) > 0:
                        # Clicar no primeiro resultado
                        result_links[0].click()
                        time.sleep(3)
                        
                        # Extrair CNPJ da URL
                        current_url = driver.current_url
                        cnpj_clean = current_url.split("/")[-1]
                        
                        # Extrair nome da empresa
                        try:
                            name_element = driver.find_element(By.CSS_SELECTOR, "h1")
                            if name_element:
                                company_name = name_element.text.strip()
                        except NoSuchElementException:
                            pass
                        
                        return {
                            'name': company_name,
                            'cnpj': cnpj_clean,
                            'source': 'cnpj',
                            'url': current_url
                        }
                except Exception as e:
                    logger.warning(f"Erro ao buscar resultados no CNPJ.biz: {e}")
            
            except Exception as e:
                logger.error(f"Erro ao buscar CNPJ para {company_name}: {e}")
        
        return None
    
    def _collect_from_receitaws(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Coleta dados da API ReceitaWS.
        
        Args:
            cnpj: CNPJ da empresa
            
        Returns:
            Dados coletados ou None
        """
        try:
            url = f"{self.receita_ws_url}{cnpj}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'ERROR':
                    logger.warning(f"Erro na API ReceitaWS: {data.get('message')}")
                    return None
                
                # Extrair dados relevantes
                result = {}
                
                # Nome e fantasia
                result['name'] = data.get('nome', '')
                result['fantasy_name'] = data.get('fantasia', '')
                
                # Localização
                result['address'] = data.get('logradouro', '')
                if data.get('numero'):
                    result['address'] += f", {data.get('numero')}"
                if data.get('complemento'):
                    result['address'] += f" - {data.get('complemento')}"
                
                result['city'] = data.get('municipio', '')
                result['state'] = data.get('uf', '')
                result['zip_code'] = data.get('cep', '')
                result['location'] = f"{result['address']}, {result['city']} - {result['state']}, {result['zip_code']}"
                
                # Contato
                result['phone'] = data.get('telefone', '')
                result['email'] = data.get('email', '')
                
                # Informações adicionais
                result['cnpj_formatted'] = data.get('cnpj', '')
                result['opening_date'] = data.get('abertura', '')
                result['legal_nature'] = data.get('natureza_juridica', '')
                result['status'] = data.get('situacao', '')
                result['last_update'] = data.get('ultima_atualizacao', '')
                result['type'] = data.get('tipo', '')
                result['capital'] = data.get('capital_social', '')
                
                # Atividades
                if 'atividade_principal' in data and data['atividade_principal']:
                    result['main_activity'] = data['atividade_principal'][0].get('text', '')
                    result['main_activity_code'] = data['atividade_principal'][0].get('code', '')
                
                return result
            else:
                logger.warning(f"Erro ao acessar ReceitaWS: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao coletar dados da ReceitaWS: {e}")
            return None
    
    def _collect_from_cnpjbiz(self, cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Coleta dados do site CNPJ.biz usando Selenium.
        
        Args:
            cnpj: CNPJ da empresa
            
        Returns:
            Dados coletados ou None
        """
        with SeleniumManager(headless=True) as driver:
            try:
                # Navegar para página da empresa
                url = f"{self.cnpj_biz_url}{cnpj}"
                logger.info(f"Navegando para: {url}")
                driver.get(url)
                time.sleep(5)  # Aguardar carregamento
                
                # Extrair dados
                result = {}
                
                # Nome e fantasia
                try:
                    name_element = driver.find_element(By.CSS_SELECTOR, "h1")
                    if name_element:
                        result['name'] = name_element.text.strip()
                except NoSuchElementException:
                    logger.warning("Elemento de nome não encontrado")
                
                try:
                    fantasy_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Nome Fantasia')]/following-sibling::td")
                    if fantasy_element:
                        result['fantasy_name'] = fantasy_element.text.strip()
                except NoSuchElementException:
                    logger.warning("Elemento de nome fantasia não encontrado")
                
                # CNPJ formatado
                try:
                    cnpj_element = driver.find_element(By.XPATH, "//th[contains(text(), 'CNPJ')]/following-sibling::td")
                    if cnpj_element:
                        result['cnpj_formatted'] = cnpj_element.text.strip()
                except NoSuchElementException:
                    logger.warning("Elemento de CNPJ não encontrado")
                
                # Localização
                try:
                    address_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Endereço')]/following-sibling::td")
                    if address_element:
                        result['address'] = address_element.text.strip()
                except NoSuchElementException:
                    logger.warning("Elemento de endereço não encontrado")
                
                try:
                    city_state_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Município')]/following-sibling::td")
                    if city_state_element:
                        city_state = city_state_element.text.strip()
                        if " / " in city_state:
                            city, state = city_state.split(" / ", 1)
                            result['city'] = city.strip()
                            result['state'] = state.strip()
                except NoSuchElementException:
                    logger.warning("Elemento de município/estado não encontrado")
                
                try:
                    zip_element = driver.find_element(By.XPATH, "//th[contains(text(), 'CEP')]/following-sibling::td")
                    if zip_element:
                        result['zip_code'] = zip_element.text.strip()
                except NoSuchElementException:
                    logger.warning("Elemento de CEP não encontrado")
                
                # Contato
                try:
                    phone_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Telefone')]/following-sibling::td")
                    if phone_element:
                        result['phone'] = phone_element.text.strip()
                except NoSuchElementException:
                    logger.warning("Elemento de telefone não encontrado")
                
                try:
                    email_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Email')]/following-sibling::td")
                    if email_element:
                        result['email'] = email_element.text.strip()
                except NoSuchElementException:
                    logger.warning("Elemento de email não encontrado")
                
                # Informações adicionais
                try:
                    opening_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Data de Abertura')]/following-sibling::td")
                    if opening_element:
                        result['opening_date'] = opening_element.text.strip()
                except NoSuchElementException:
                    logger.warning("Elemento de data de abertura não encontrado")
                
                try:
                    status_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Situação')]/following-sibling::td")
                    if status_element:
                        result['status'] = status_element.text.strip()
                except NoSuchElementException:
                    logger.warning("Elemento de situação não encontrado")
                
                try:
                    capital_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Capital Social')]/following-sibling::td")
                    if capital_element:
                        result['capital'] = capital_element.text.strip()
                except NoSuchElementException:
                    logger.warning("Elemento de capital social não encontrado")
                
                # Atividade principal
                try:
                    activity_element = driver.find_element(By.XPATH, "//th[contains(text(), 'Atividade Principal')]/following-sibling::td")
                    if activity_element:
                        activity_text = activity_element.text.strip()
                        
                        # Tentar extrair código e descrição
                        activity_match = re.match(r'(\d+\.\d+-\d+-\d+) - (.+)', activity_text)
                        if activity_match:
                            result['main_activity_code'] = activity_match.group(1)
                            result['main_activity'] = activity_match.group(2)
                        else:
                            result['main_activity'] = activity_text
                except NoSuchElementException:
                    logger.warning("Elemento de atividade principal não encontrado")
                
                # Montar localização completa
                if 'address' in result and 'city' in result and 'state' in result:
                    result['location'] = f"{result['address']}, {result['city']} - {result['state']}"
                    if 'zip_code' in result:
                        result['location'] += f", {result['zip_code']}"
                
                return result
                
            except Exception as e:
                logger.error(f"Erro durante coleta no CNPJ.biz: {e}")
                return None
