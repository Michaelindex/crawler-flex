"""
Cliente para interação com o motor de busca SearXNG.
"""

import logging
import urllib.parse
import requests
from typing import Dict, Any, List, Optional

from ..config import settings

logger = logging.getLogger(__name__)

class SearxClient:
    """
    Cliente para realizar buscas no motor SearXNG.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Inicializa o cliente SearXNG.
        
        Args:
            base_url: URL base do SearXNG (opcional)
        """
        self.base_url = base_url or settings.SEARX_URL
        self.headers = {
            'User-Agent': settings.USER_AGENT
        }
    
    def search(self, query: str, format: str = "json", **kwargs) -> Dict[str, Any]:
        """
        Realiza uma busca no SearXNG.
        
        Args:
            query: Consulta de busca
            format: Formato de resposta (json, html, etc.)
            **kwargs: Parâmetros adicionais de busca
            
        Returns:
            Resultados da busca
        """
        logger.info(f"Realizando busca SearXNG: {query}")
        
        # Construir URL de busca
        encoded_query = urllib.parse.quote(query)
        url = f"{self.base_url}?q={encoded_query}&format={format}"
        
        # Adicionar parâmetros adicionais
        for key, value in kwargs.items():
            url += f"&{key}={value}"
        
        # Realizar requisição
        try:
            response = requests.get(url, headers=self.headers, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            if format == "json":
                return response.json()
            else:
                return {"content": response.text}
            
        except Exception as e:
            logger.error(f"Erro na busca SearXNG: {e}")
            return {"error": str(e), "results": []}
    
    def get_company_info(self, company_name: str, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Busca informações sobre uma empresa específica.
        
        Args:
            company_name: Nome da empresa
            location: Localização da empresa (opcional)
            
        Returns:
            Lista de resultados relevantes
        """
        # Construir query
        query = company_name
        if location:
            query += f" {location}"
        
        # Realizar busca
        results = self.search(query)
        
        # Filtrar e processar resultados
        processed_results = []
        
        if "results" in results:
            for result in results["results"]:
                processed_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "source": result.get("engine", "")
                })
        
        return processed_results
    
    def discover_companies(self, criteria: Dict[str, Any], max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Descobre empresas com base em critérios.
        
        Args:
            criteria: Critérios de busca
            max_results: Número máximo de resultados
            
        Returns:
            Lista de empresas descobertas
        """
        # Construir query com base nos critérios
        query_parts = []
        
        # Adicionar setor
        if "sector" in criteria:
            sector = criteria["sector"]
            if "main" in sector:
                query_parts.append(sector["main"])
            
            if "sub_sectors" in sector and sector["sub_sectors"]:
                query_parts.append(sector["sub_sectors"][0])  # Usar primeiro sub-setor
        
        # Adicionar localização
        if "location" in criteria:
            location = criteria["location"]
            if "country" in location:
                query_parts.append(location["country"])
            
            if "states" in location and location["states"]:
                query_parts.append(location["states"][0])  # Usar primeiro estado
        
        # Adicionar palavras-chave adicionais
        if "additional" in criteria and "keywords" in criteria["additional"]:
            keywords = criteria["additional"]["keywords"]
            if keywords:
                query_parts.append(keywords[0])  # Usar primeira palavra-chave
        
        # Adicionar termos específicos para empresas
        query_parts.append("empresa OR companhia OR corporação")
        
        # Construir query final
        query = " ".join(query_parts)
        
        # Realizar busca
        results = self.search(query, pages=2)
        
        # Processar resultados
        companies = []
        
        if "results" in results:
            for result in results["results"][:max_results]:
                # Extrair informações básicas
                company = {
                    "name": result.get("title", "").split(" - ")[0].strip(),
                    "url": result.get("url", ""),
                    "description": result.get("content", ""),
                    "source": "searx"
                }
                
                # Adicionar à lista se parecer uma empresa
                if self._looks_like_company(company):
                    companies.append(company)
        
        return companies
    
    def _looks_like_company(self, result: Dict[str, Any]) -> bool:
        """
        Verifica se um resultado parece ser uma empresa.
        
        Args:
            result: Resultado da busca
            
        Returns:
            True se parecer uma empresa, False caso contrário
        """
        # Implementação simplificada para o protótipo
        # Na versão completa, usaria heurísticas mais sofisticadas
        
        # Verificar se o título contém termos comuns de não-empresas
        negative_terms = ["wikipedia", "dicionário", "significado", "o que é", "definição"]
        for term in negative_terms:
            if term.lower() in result["name"].lower():
                return False
        
        # Verificar se a URL parece ser de uma empresa
        if "url" in result:
            url = result["url"].lower()
            if any(domain in url for domain in [".gov.", ".edu.", "wikipedia", "dicionario"]):
                return False
        
        return True
