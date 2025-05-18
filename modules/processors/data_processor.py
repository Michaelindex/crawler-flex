"""
Processador de dados para unificar informações de múltiplas fontes.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Processador responsável por unificar dados de múltiplas fontes.
    """
    
    def __init__(self):
        """Inicializa o processador de dados."""
        # Mapeamento de campos de diferentes fontes para campos padronizados
        self.field_mapping = {
            'linkedin': {
                'name': 'Company Name (Revised)',
                'location': 'Location',
                'size': 'Size',
                'first_name': 'First name',
                'last_name': 'Second Name',
                'position': 'Office',
                'website': 'Domain',
                'linkedin': 'Linkedin',
                'city': 'City',
                'state': 'State'
            },
            'cnpj': {
                'name': 'Company Name (Revised)',
                'fantasy_name': 'Fantasy name',
                'cnpj': 'CNPJ',
                'cnpj_formatted': 'CNPJ',
                'location': 'Location',
                'address': 'Location',
                'email': 'E-mail',
                'phone': 'Telephone',
                'phone2': 'Telephone 2',
                'city': 'City',
                'state': 'State'
            },
            'company_site': {
                'name': 'Company Name (Revised)',
                'website': 'Domain',
                'domain': 'Domain',
                'email': 'E-mail',
                'phone': 'Telephone',
                'phone2': 'Telephone 2',
                'address': 'Location',
                'size': 'Size'
            }
        }
        
        # Importar configurações
        from config import settings
        self.export_partial = getattr(settings, 'EXPORT_PARTIAL_DATA', False)
    
    def process(self, raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa e unifica dados de múltiplas fontes.
        
        Args:
            raw_results: Resultados brutos da busca
            
        Returns:
            Lista de resultados processados
        """
        processed_results = []
        
        for company_result in raw_results:
            try:
                # Inicializar dados unificados
                unified_data = {
                    'Company Name (Revised)': '',
                    'Location': '',
                    'CNPJ': '',
                    'Fantasy name': '',
                    'Domain': '',
                    'Size': '',
                    'First name': '',
                    'Second Name': '',
                    'Office': '',
                    'E-mail': '',
                    'Telephone': '',
                    'Telephone 2': '',
                    'City': '',
                    'State': '',
                    'Linkedin': '',
                    'LOTE': 1  # Valor padrão para LOTE
                }
                
                # Processar cada fonte de dados
                for source_data in company_result.get('data_sources', []):
                    source_type = source_data.get('source', '')
                    
                    if source_type in self.field_mapping:
                        # Mapear campos da fonte para campos padronizados
                        for source_field, target_field in self.field_mapping[source_type].items():
                            if source_field in source_data and source_data[source_field]:
                                # Só atualizar se o campo estiver vazio ou a fonte atual for mais confiável
                                if not unified_data[target_field] or self._is_better_source(source_type, target_field, unified_data.get(f"_source_{target_field}", "")):
                                    unified_data[target_field] = source_data[source_field]
                                    unified_data[f"_source_{target_field}"] = source_type
                
                # Verificar se tem dados suficientes
                if self._has_minimum_data(unified_data):
                    # Remover campos temporários de controle
                    for field in list(unified_data.keys()):
                        if field.startswith('_source_'):
                            del unified_data[field]
                    
                    processed_results.append(unified_data)
                elif self.export_partial and unified_data['Company Name (Revised)']:
                    # Se configurado para exportar dados parciais e tiver pelo menos o nome
                    logger.warning(f"Exportando dados parciais para {unified_data['Company Name (Revised)']}")
                    
                    # Remover campos temporários de controle
                    for field in list(unified_data.keys()):
                        if field.startswith('_source_'):
                            del unified_data[field]
                    
                    processed_results.append(unified_data)
                else:
                    logger.warning(f"Empresa {unified_data.get('Company Name (Revised)', 'Desconhecida')} não tem dados mínimos necessários")
            
            except Exception as e:
                logger.error(f"Erro ao processar dados da empresa: {e}")
        
        return processed_results
    
    def _is_better_source(self, new_source: str, field: str, current_source: str) -> bool:
        """
        Verifica se a nova fonte é mais confiável que a atual para um campo específico.
        
        Args:
            new_source: Nova fonte de dados
            field: Campo a ser verificado
            current_source: Fonte atual
            
        Returns:
            True se a nova fonte for mais confiável, False caso contrário
        """
        # Prioridade de fontes por campo
        priorities = {
            'Company Name (Revised)': ['cnpj', 'linkedin', 'company_site'],
            'Location': ['cnpj', 'company_site', 'linkedin'],
            'CNPJ': ['cnpj'],
            'Fantasy name': ['cnpj'],
            'Domain': ['company_site', 'linkedin', 'cnpj'],
            'Size': ['linkedin', 'company_site'],
            'First name': ['linkedin'],
            'Second Name': ['linkedin'],
            'Office': ['linkedin'],
            'E-mail': ['company_site', 'cnpj'],
            'Telephone': ['cnpj', 'company_site'],
            'Telephone 2': ['cnpj', 'company_site'],
            'City': ['cnpj', 'linkedin', 'company_site'],
            'State': ['cnpj', 'linkedin', 'company_site'],
            'Linkedin': ['linkedin']
        }
        
        # Se o campo não estiver no dicionário de prioridades, qualquer fonte é válida
        if field not in priorities:
            return True
        
        # Se a fonte atual não estiver definida, a nova fonte é melhor
        if not current_source:
            return True
        
        # Verificar prioridade
        if new_source in priorities[field] and current_source in priorities[field]:
            return priorities[field].index(new_source) < priorities[field].index(current_source)
        
        # Se a nova fonte estiver na lista de prioridades e a atual não, a nova é melhor
        if new_source in priorities[field] and current_source not in priorities[field]:
            return True
        
        # Em outros casos, manter a fonte atual
        return False
    
    def _has_minimum_data(self, data: Dict[str, Any]) -> bool:
        """
        Verifica se os dados têm o mínimo necessário para serem considerados válidos.
        
        Args:
            data: Dados unificados
            
        Returns:
            True se os dados forem válidos, False caso contrário
        """
        # Campos obrigatórios
        required_fields = ['Company Name (Revised)']
        
        # Verificar campos obrigatórios
        for field in required_fields:
            if not data.get(field):
                return False
        
        # Verificar se tem pelo menos 30% dos campos preenchidos
        total_fields = len(data)
        filled_fields = sum(1 for value in data.values() if value)
        
        return filled_fields / total_fields >= 0.3
