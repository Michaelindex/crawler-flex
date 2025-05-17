"""
Parser de critérios para o crawler flexível.
Responsável por validar e processar os critérios de busca.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class CriteriaParser:
    """
    Parser para validar e processar critérios de busca.
    """
    
    def __init__(self):
        """Inicializa o parser de critérios."""
        pass
    
    def parse(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida e processa os critérios de busca.
        
        Args:
            criteria: Dicionário com os critérios de busca
            
        Returns:
            Dicionário com os critérios processados
        """
        logger.info(f"Processando critérios: {criteria}")
        
        # Validar critérios
        self._validate_criteria(criteria)
        
        # Processar critérios específicos
        processed = {}
        
        # Processar critérios de setor
        if 'sector' in criteria:
            processed['sector'] = self._process_sector(criteria['sector'])
        
        # Processar critérios de tamanho
        if 'size' in criteria:
            processed['size'] = self._process_size(criteria['size'])
        
        # Processar critérios de localização
        if 'location' in criteria:
            processed['location'] = self._process_location(criteria['location'])
        
        # Processar critérios de contatos
        if 'contacts' in criteria:
            processed['contacts'] = self._process_contacts(criteria['contacts'])
        
        # Processar critérios adicionais
        if 'additional' in criteria:
            processed['additional'] = self._process_additional(criteria['additional'])
        
        # Processar lista de empresas (se fornecida)
        if 'company_list' in criteria:
            processed['company_list'] = self._process_company_list(criteria['company_list'])
        
        # Processar configurações de saída
        if 'output' in criteria:
            processed['output'] = self._process_output(criteria['output'])
        else:
            processed['output'] = {'format': 'excel'}
        
        logger.info(f"Critérios processados: {processed}")
        return processed
    
    def _validate_criteria(self, criteria: Dict[str, Any]) -> None:
        """
        Valida os critérios de busca.
        
        Args:
            criteria: Dicionário com os critérios de busca
            
        Raises:
            ValueError: Se os critérios forem inválidos
        """
        # Verificar se pelo menos um critério de busca foi fornecido
        if not criteria:
            raise ValueError("Nenhum critério de busca fornecido")
        
        # Verificar se há critérios de busca ou lista de empresas
        has_search_criteria = any(key in criteria for key in ['sector', 'size', 'location', 'contacts', 'additional'])
        has_company_list = 'company_list' in criteria
        
        if not has_search_criteria and not has_company_list:
            raise ValueError("É necessário fornecer critérios de busca ou uma lista de empresas")
    
    def _process_sector(self, sector: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa critérios de setor.
        
        Args:
            sector: Critérios de setor
            
        Returns:
            Critérios de setor processados
        """
        processed = {}
        
        if 'main' in sector:
            processed['main'] = sector['main']
        
        if 'sub_sectors' in sector and isinstance(sector['sub_sectors'], list):
            processed['sub_sectors'] = sector['sub_sectors']
        
        return processed
    
    def _process_size(self, size: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa critérios de tamanho.
        
        Args:
            size: Critérios de tamanho
            
        Returns:
            Critérios de tamanho processados
        """
        processed = {}
        
        if 'employees' in size:
            employees = size['employees']
            processed_employees = {}
            
            if 'min' in employees:
                processed_employees['min'] = int(employees['min'])
            
            if 'max' in employees:
                processed_employees['max'] = int(employees['max'])
            
            processed['employees'] = processed_employees
        
        if 'revenue' in size:
            revenue = size['revenue']
            processed_revenue = {}
            
            if 'min' in revenue:
                processed_revenue['min'] = int(revenue['min'])
            
            if 'max' in revenue and revenue['max']:
                processed_revenue['max'] = int(revenue['max'])
            
            if 'currency' in revenue:
                processed_revenue['currency'] = revenue['currency']
            else:
                processed_revenue['currency'] = 'BRL'
            
            processed['revenue'] = processed_revenue
        
        return processed
    
    def _process_location(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa critérios de localização.
        
        Args:
            location: Critérios de localização
            
        Returns:
            Critérios de localização processados
        """
        processed = {}
        
        if 'country' in location:
            processed['country'] = location['country']
        
        if 'states' in location and isinstance(location['states'], list):
            processed['states'] = location['states']
        
        if 'cities' in location and isinstance(location['cities'], list):
            processed['cities'] = location['cities']
        
        return processed
    
    def _process_contacts(self, contacts: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa critérios de contatos.
        
        Args:
            contacts: Critérios de contatos
            
        Returns:
            Critérios de contatos processados
        """
        processed = {}
        
        if 'departments' in contacts and isinstance(contacts['departments'], list):
            processed['departments'] = contacts['departments']
        
        if 'positions' in contacts and isinstance(contacts['positions'], list):
            processed['positions'] = contacts['positions']
        
        return processed
    
    def _process_additional(self, additional: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa critérios adicionais.
        
        Args:
            additional: Critérios adicionais
            
        Returns:
            Critérios adicionais processados
        """
        processed = {}
        
        if 'founded_after' in additional:
            processed['founded_after'] = int(additional['founded_after'])
        
        if 'founded_before' in additional:
            processed['founded_before'] = int(additional['founded_before'])
        
        if 'has_international_presence' in additional:
            processed['has_international_presence'] = bool(additional['has_international_presence'])
        
        if 'keywords' in additional and isinstance(additional['keywords'], list):
            processed['keywords'] = additional['keywords']
        
        return processed
    
    def _process_company_list(self, company_list: List[str]) -> List[str]:
        """
        Processa lista de empresas.
        
        Args:
            company_list: Lista de nomes de empresas
            
        Returns:
            Lista de empresas processada
        """
        # Remover duplicatas e valores vazios
        return list(set(filter(None, company_list)))
    
    def _process_output(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa configurações de saída.
        
        Args:
            output: Configurações de saída
            
        Returns:
            Configurações de saída processadas
        """
        processed = {}
        
        if 'format' in output:
            format_value = output['format'].lower()
            if format_value in ['excel', 'csv', 'json']:
                processed['format'] = format_value
            else:
                processed['format'] = 'excel'
        else:
            processed['format'] = 'excel'
        
        if 'max_results' in output:
            try:
                processed['max_results'] = int(output['max_results'])
            except (ValueError, TypeError):
                processed['max_results'] = 100
        else:
            processed['max_results'] = 100
        
        return processed
