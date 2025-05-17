"""
Processador de dados para unificar e enriquecer informações coletadas.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Processador para unificar e enriquecer dados coletados de múltiplas fontes.
    """
    
    def __init__(self, ai_client=None):
        """
        Inicializa o processador de dados.
        
        Args:
            ai_client: Cliente para IA local (opcional)
        """
        self.ai_client = ai_client
    
    def process(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa dados brutos coletados de múltiplas fontes.
        
        Args:
            raw_data: Lista de dados brutos coletados
            
        Returns:
            Lista de dados processados e unificados
        """
        logger.info(f"Processando {len(raw_data)} registros de dados brutos")
        
        # Agrupar dados por empresa
        grouped_data = self._group_by_company(raw_data)
        logger.info(f"Dados agrupados em {len(grouped_data)} empresas")
        
        # Processar cada grupo
        processed_data = []
        for company_id, company_data in grouped_data.items():
            processed = self._process_company(company_id, company_data)
            processed_data.append(processed)
        
        logger.info(f"Processamento concluído. {len(processed_data)} empresas processadas")
        return processed_data
    
    def _group_by_company(self, raw_data: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Agrupa dados brutos por empresa.
        
        Args:
            raw_data: Lista de dados brutos
            
        Returns:
            Dicionário com dados agrupados por empresa
        """
        grouped = {}
        
        for item in raw_data:
            # Identificar a empresa (por CNPJ, domínio ou nome)
            company_id = self._get_company_id(item)
            
            if company_id not in grouped:
                grouped[company_id] = []
            
            grouped[company_id].append(item)
        
        return grouped
    
    def _get_company_id(self, item: Dict[str, Any]) -> str:
        """
        Obtém um identificador único para a empresa.
        
        Args:
            item: Dados da empresa
            
        Returns:
            Identificador único da empresa
        """
        # Tentar usar CNPJ como identificador
        if 'cnpj' in item and item['cnpj']:
            return f"cnpj:{self._normalize_cnpj(item['cnpj'])}"
        
        # Tentar usar domínio como identificador
        if 'domain' in item and item['domain']:
            return f"domain:{item['domain'].lower()}"
        
        # Usar nome como identificador (menos confiável)
        if 'name' in item and item['name']:
            return f"name:{item['name'].lower()}"
        
        # Fallback para um hash dos dados
        import hashlib
        import json
        data_str = json.dumps(item, sort_keys=True)
        return f"hash:{hashlib.md5(data_str.encode()).hexdigest()}"
    
    def _normalize_cnpj(self, cnpj: str) -> str:
        """
        Normaliza um CNPJ removendo caracteres não numéricos.
        
        Args:
            cnpj: CNPJ a ser normalizado
            
        Returns:
            CNPJ normalizado
        """
        return ''.join(c for c in cnpj if c.isdigit())
    
    def _process_company(self, company_id: str, company_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processa dados de uma empresa específica.
        
        Args:
            company_id: Identificador da empresa
            company_data: Lista de dados da empresa de diferentes fontes
            
        Returns:
            Dados processados e unificados da empresa
        """
        logger.debug(f"Processando empresa {company_id} com {len(company_data)} fontes de dados")
        
        # Inicializar dados unificados
        unified = {}
        
        # Unificar dados básicos
        unified = self._unify_basic_data(company_data, unified)
        
        # Unificar dados de contato
        unified = self._unify_contact_data(company_data, unified)
        
        # Unificar dados de localização
        unified = self._unify_location_data(company_data, unified)
        
        # Enriquecer dados com IA (se disponível)
        if self.ai_client:
            unified = self._enrich_with_ai(unified)
        
        # Transformar para formato de saída
        output = self._transform_to_output_format(unified)
        
        return output
    
    def _unify_basic_data(self, company_data: List[Dict[str, Any]], unified: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unifica dados básicos da empresa.
        
        Args:
            company_data: Lista de dados da empresa
            unified: Dados unificados atuais
            
        Returns:
            Dados unificados atualizados
        """
        # Implementação simplificada para o protótipo
        # Na versão completa, implementaria lógica de resolução de conflitos
        # e priorização de fontes
        
        for item in company_data:
            # Nome da empresa
            if 'name' in item and item['name'] and 'name' not in unified:
                unified['name'] = item['name']
            
            # CNPJ
            if 'cnpj' in item and item['cnpj'] and 'cnpj' not in unified:
                unified['cnpj'] = item['cnpj']
            
            # Nome fantasia
            if 'fantasy_name' in item and item['fantasy_name'] and 'fantasy_name' not in unified:
                unified['fantasy_name'] = item['fantasy_name']
            
            # Domínio
            if 'domain' in item and item['domain'] and 'domain' not in unified:
                unified['domain'] = item['domain']
            
            # Tamanho
            if 'size' in item and item['size'] and 'size' not in unified:
                unified['size'] = item['size']
        
        return unified
    
    def _unify_contact_data(self, company_data: List[Dict[str, Any]], unified: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unifica dados de contato da empresa.
        
        Args:
            company_data: Lista de dados da empresa
            unified: Dados unificados atuais
            
        Returns:
            Dados unificados atualizados
        """
        # Implementação simplificada para o protótipo
        
        for item in company_data:
            # Email
            if 'email' in item and item['email'] and 'email' not in unified:
                unified['email'] = item['email']
            
            # Telefone principal
            if 'phone' in item and item['phone'] and 'phone' not in unified:
                unified['phone'] = item['phone']
            
            # Telefone secundário
            if 'phone2' in item and item['phone2'] and 'phone2' not in unified:
                unified['phone2'] = item['phone2']
            
            # LinkedIn
            if 'linkedin' in item and item['linkedin'] and 'linkedin' not in unified:
                unified['linkedin'] = item['linkedin']
            
            # Contatos específicos
            if 'contacts' in item and item['contacts'] and 'contacts' not in unified:
                unified['contacts'] = item['contacts']
        
        return unified
    
    def _unify_location_data(self, company_data: List[Dict[str, Any]], unified: Dict[str, Any]) -> Dict[str, Any]:
        """
        Unifica dados de localização da empresa.
        
        Args:
            company_data: Lista de dados da empresa
            unified: Dados unificados atuais
            
        Returns:
            Dados unificados atualizados
        """
        # Implementação simplificada para o protótipo
        
        for item in company_data:
            # Endereço completo
            if 'address' in item and item['address'] and 'address' not in unified:
                unified['address'] = item['address']
            
            # Cidade
            if 'city' in item and item['city'] and 'city' not in unified:
                unified['city'] = item['city']
            
            # Estado
            if 'state' in item and item['state'] and 'state' not in unified:
                unified['state'] = item['state']
        
        return unified
    
    def _enrich_with_ai(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriquece dados usando IA local.
        
        Args:
            data: Dados a serem enriquecidos
            
        Returns:
            Dados enriquecidos
        """
        # Implementação simplificada para o protótipo
        # Na versão completa, usaria a IA para inferir dados faltantes
        # e melhorar a qualidade dos dados existentes
        
        return data
    
    def _transform_to_output_format(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforma dados unificados para o formato de saída esperado.
        
        Args:
            data: Dados unificados
            
        Returns:
            Dados no formato de saída
        """
        # Mapeamento de campos internos para campos de saída
        output = {
            'Company Name (Revised)': data.get('name', ''),
            'Location': data.get('address', ''),
            'CNPJ': data.get('cnpj', ''),
            'Fantasy name': data.get('fantasy_name', ''),
            'Domain': data.get('domain', ''),
            'Size': data.get('size', ''),
            'First name': '',
            'Second Name': '',
            'Office': '',
            'E-mail': data.get('email', ''),
            'Telephone': data.get('phone', ''),
            'Telephone 2': data.get('phone2', ''),
            'City': data.get('city', ''),
            'State': data.get('state', ''),
            'Linkedin': data.get('linkedin', ''),
            'LOTE': 1
        }
        
        # Processar contatos (se disponíveis)
        if 'contacts' in data and data['contacts']:
            contact = data['contacts'][0]  # Usar primeiro contato
            output['First name'] = contact.get('first_name', '')
            output['Second Name'] = contact.get('last_name', '')
            output['Office'] = contact.get('position', '')
        
        return output
