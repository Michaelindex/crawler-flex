"""
Verificador de qualidade dos dados coletados.
Responsável por avaliar a completude e consistência dos dados.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class QualityChecker:
    """
    Verificador de qualidade dos dados coletados.
    """
    
    def __init__(self):
        """Inicializa o verificador de qualidade."""
        # Pesos para cada campo na avaliação de qualidade
        self.field_weights = {
            'Company Name (Revised)': 10,  # Nome da empresa é essencial
            'Location': 7,                 # Localização é muito importante
            'CNPJ': 8,                     # CNPJ é muito importante
            'Fantasy name': 5,             # Nome fantasia é importante
            'Domain': 7,                   # Domínio é muito importante
            'Size': 6,                     # Tamanho é importante
            'First name': 4,               # Nome do contato é moderadamente importante
            'Second Name': 3,              # Sobrenome do contato é menos importante
            'Office': 4,                   # Cargo é moderadamente importante
            'E-mail': 8,                   # Email é muito importante
            'Telephone': 7,                # Telefone é muito importante
            'Telephone 2': 3,              # Telefone secundário é menos importante
            'City': 6,                     # Cidade é importante
            'State': 6,                    # Estado é importante
            'Linkedin': 5                  # LinkedIn é importante
        }
        
        # Pontuação máxima possível
        self.max_score = sum(self.field_weights.values())
    
    def check_quality(self, data: Dict[str, Any]) -> float:
        """
        Verifica a qualidade dos dados coletados.
        
        Args:
            data: Dados a serem verificados
            
        Returns:
            Pontuação de qualidade (0.0 a 1.0)
        """
        if not data:
            return 0.0
        
        # Verificar campos obrigatórios
        if not data.get('Company Name (Revised)'):
            logger.warning("Dados sem nome da empresa")
            return 0.0
        
        # Calcular pontuação
        score = 0.0
        
        for field, weight in self.field_weights.items():
            if field in data and data[field]:
                score += weight
                
                # Bônus para campos com dados mais completos
                if field == 'CNPJ' and len(str(data[field]).strip()) >= 14:
                    score += 1
                elif field == 'Telephone' and len(str(data[field]).strip()) >= 10:
                    score += 1
                elif field == 'E-mail' and '@' in str(data[field]):
                    score += 1
        
        # Normalizar pontuação (0.0 a 1.0)
        normalized_score = score / self.max_score
        
        logger.info(f"Qualidade dos dados para {data.get('Company Name (Revised)', 'Desconhecido')}: {normalized_score:.2f}")
        
        return normalized_score
    
    def get_missing_fields(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Identifica campos ausentes ou incompletos.
        
        Args:
            data: Dados a serem verificados
            
        Returns:
            Dicionário com campos ausentes e seus pesos
        """
        missing = {}
        
        for field, weight in self.field_weights.items():
            if field not in data or not data[field]:
                missing[field] = weight
        
        return missing
