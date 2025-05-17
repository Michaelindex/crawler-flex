"""
Verificador de qualidade dos dados coletados.
Responsável por validar a completude e qualidade dos dados.
"""

import logging
from typing import Dict, Any, List

from ..config import settings

logger = logging.getLogger(__name__)

class QualityChecker:
    """
    Verificador de qualidade dos dados coletados.
    """
    
    def __init__(self):
        """Inicializa o verificador de qualidade."""
        self.required_fields = settings.REQUIRED_FIELDS
    
    def check_quality(self, data: Dict[str, Any]) -> float:
        """
        Verifica a qualidade dos dados coletados.
        
        Args:
            data: Dados a serem verificados
            
        Returns:
            Score de qualidade (0.0 a 1.0)
        """
        logger.info(f"Verificando qualidade dos dados: {data.get('Company Name (Revised)', 'Desconhecido')}")
        
        # Verificar campos obrigatórios
        completeness_score = self._check_completeness(data)
        logger.debug(f"Score de completude: {completeness_score}")
        
        # Verificar formato dos dados
        format_score = self._check_format(data)
        logger.debug(f"Score de formato: {format_score}")
        
        # Verificar consistência dos dados
        consistency_score = self._check_consistency(data)
        logger.debug(f"Score de consistência: {consistency_score}")
        
        # Calcular score final (média ponderada)
        final_score = (
            completeness_score * 0.5 +
            format_score * 0.3 +
            consistency_score * 0.2
        )
        
        logger.info(f"Score final de qualidade: {final_score}")
        return final_score
    
    def _check_completeness(self, data: Dict[str, Any]) -> float:
        """
        Verifica a completude dos dados.
        
        Args:
            data: Dados a serem verificados
            
        Returns:
            Score de completude (0.0 a 1.0)
        """
        # Contar campos obrigatórios preenchidos
        filled_required = sum(1 for field in self.required_fields if field in data and data[field])
        total_required = len(self.required_fields)
        
        # Contar campos opcionais preenchidos
        optional_fields = [field for field in data if field not in self.required_fields]
        filled_optional = sum(1 for field in optional_fields if data[field])
        total_optional = len(optional_fields) if optional_fields else 1  # Evitar divisão por zero
        
        # Calcular scores
        required_score = filled_required / total_required
        optional_score = filled_optional / total_optional
        
        # Calcular score final (peso maior para campos obrigatórios)
        return required_score * 0.8 + optional_score * 0.2
    
    def _check_format(self, data: Dict[str, Any]) -> float:
        """
        Verifica o formato dos dados.
        
        Args:
            data: Dados a serem verificados
            
        Returns:
            Score de formato (0.0 a 1.0)
        """
        # Implementação simplificada para o protótipo
        # Na versão completa, verificaria o formato de cada campo
        # (ex: email válido, CNPJ válido, telefone válido, etc.)
        
        format_checks = []
        
        # Verificar formato de email
        if 'E-mail' in data and data['E-mail']:
            format_checks.append('@' in data['E-mail'] and '.' in data['E-mail'])
        
        # Verificar formato de CNPJ
        if 'CNPJ' in data and data['CNPJ']:
            format_checks.append(len(data['CNPJ'].replace('.', '').replace('/', '').replace('-', '')) == 14)
        
        # Verificar formato de telefone
        if 'Telephone' in data and data['Telephone']:
            format_checks.append(len(data['Telephone'].replace('(', '').replace(')', '').replace('-', '').replace(' ', '')) >= 10)
        
        # Verificar formato de domínio
        if 'Domain' in data and data['Domain']:
            format_checks.append('.' in data['Domain'])
        
        # Calcular score
        if not format_checks:
            return 0.5  # Score neutro se não houver verificações
        
        return sum(1 for check in format_checks if check) / len(format_checks)
    
    def _check_consistency(self, data: Dict[str, Any]) -> float:
        """
        Verifica a consistência dos dados.
        
        Args:
            data: Dados a serem verificados
            
        Returns:
            Score de consistência (0.0 a 1.0)
        """
        # Implementação simplificada para o protótipo
        # Na versão completa, verificaria a consistência entre campos relacionados
        # (ex: cidade/estado, domínio/email, etc.)
        
        consistency_checks = []
        
        # Verificar consistência entre domínio e email
        if 'Domain' in data and data['Domain'] and 'E-mail' in data and data['E-mail']:
            domain = data['Domain'].lower()
            email = data['E-mail'].lower()
            consistency_checks.append(domain in email)
        
        # Verificar consistência entre cidade e estado
        if 'City' in data and data['City'] and 'State' in data and data['State']:
            # Simplificado - na versão completa, verificaria com base em dados geográficos
            consistency_checks.append(True)
        
        # Verificar consistência entre nome da empresa e domínio
        if 'Company Name (Revised)' in data and data['Company Name (Revised)'] and 'Domain' in data and data['Domain']:
            # Simplificado - na versão completa, faria uma verificação mais sofisticada
            consistency_checks.append(True)
        
        # Calcular score
        if not consistency_checks:
            return 0.5  # Score neutro se não houver verificações
        
        return sum(1 for check in consistency_checks if check) / len(consistency_checks)
