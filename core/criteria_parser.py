"""
Parser de critérios para o crawler flexível.
Responsável por interpretar e validar os critérios de busca.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class CriteriaParser:
    """
    Parser de critérios para o crawler flexível.
    """
    
    def __init__(self):
        """Inicializa o parser de critérios."""
        pass
    
    def parse(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa e valida os critérios de busca.
        
        Args:
            criteria: Critérios de busca
            
        Returns:
            Critérios validados e normalizados
            
        Raises:
            ValueError: Se os critérios forem inválidos
        """
        logger.info(f"Processando critérios: {criteria}")
        
        # Verificar se há critérios
        if not criteria:
            raise ValueError("Critérios de busca não fornecidos")
        
        # Verificar se há uma lista de empresas específicas
        has_companies = 'companies' in criteria and isinstance(criteria['companies'], list) and len(criteria['companies']) > 0
        
        # Verificar se há critérios de setor
        has_sector = 'sector' in criteria and criteria['sector'].get('main')
        
        # Verificar se há critérios de localização
        has_location = 'location' in criteria and (
            criteria['location'].get('country') or 
            criteria['location'].get('states') or 
            criteria['location'].get('cities')
        )
        
        # Verificar se há critérios de tamanho
        has_size = 'size' in criteria and (
            'employees' in criteria['size'] or 
            'revenue' in criteria['size']
        )
        
        # Verificar se há critérios de busca válidos
        if not (has_companies or has_sector or has_location or has_size):
            raise ValueError("É necessário fornecer critérios de busca ou uma lista de empresas")
        
        # Normalizar critérios
        normalized = self._normalize_criteria(criteria)
        
        return normalized
    
    def _normalize_criteria(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza os critérios de busca.
        
        Args:
            criteria: Critérios de busca
            
        Returns:
            Critérios normalizados
        """
        normalized = criteria.copy()
        
        # Normalizar lista de empresas
        if 'companies' in normalized:
            companies = []
            for company in normalized['companies']:
                if isinstance(company, str):
                    companies.append({'name': company})
                elif isinstance(company, dict) and 'name' in company:
                    companies.append(company)
            
            normalized['companies'] = companies
        
        # Normalizar setor
        if 'sector' in normalized and isinstance(normalized['sector'], str):
            normalized['sector'] = {'main': normalized['sector']}
        
        # Normalizar localização
        if 'location' in normalized:
            location = normalized['location']
            
            # Converter string única em país
            if isinstance(location, str):
                normalized['location'] = {'country': location}
            
            # Garantir que listas sejam listas
            for field in ['states', 'cities']:
                if field in normalized['location'] and isinstance(normalized['location'][field], str):
                    normalized['location'][field] = [normalized['location'][field]]
        
        # Normalizar tamanho
        if 'size' in normalized:
            size = normalized['size']
            
            # Converter número único em funcionários
            if isinstance(size, int):
                normalized['size'] = {'employees': {'min': size}}
            
            # Normalizar funcionários
            if 'employees' in size and isinstance(size['employees'], int):
                normalized['size']['employees'] = {'min': size['employees']}
            
            # Normalizar faturamento
            if 'revenue' in size and isinstance(size['revenue'], (int, float)):
                normalized['size']['revenue'] = {'min': size['revenue'], 'currency': 'BRL'}
        
        # Normalizar saída
        if 'output' not in normalized:
            normalized['output'] = {}
        
        if 'format' not in normalized['output']:
            normalized['output']['format'] = 'excel'
        
        if 'max_results' not in normalized['output']:
            normalized['output']['max_results'] = 5
        
        return normalized
    
    def get_company_names(self, criteria: Dict[str, Any]) -> List[str]:
        """
        Extrai nomes de empresas dos critérios.
        
        Args:
            criteria: Critérios de busca
            
        Returns:
            Lista de nomes de empresas
        """
        companies = []
        
        if 'companies' in criteria and criteria['companies']:
            for company in criteria['companies']:
                if isinstance(company, dict) and 'name' in company:
                    companies.append(company['name'])
                elif isinstance(company, str):
                    companies.append(company)
        
        return companies
    
    def get_max_results(self, criteria: Dict[str, Any]) -> int:
        """
        Obtém o número máximo de resultados.
        
        Args:
            criteria: Critérios de busca
            
        Returns:
            Número máximo de resultados
        """
        if 'output' in criteria and 'max_results' in criteria['output']:
            return criteria['output']['max_results']
        
        return 5
