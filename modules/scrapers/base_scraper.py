"""
Classe base para todos os scrapers do sistema.
Fornece funcionalidades comuns a todos os scrapers.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from ...config import settings

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Classe base para todos os scrapers do sistema.
    """
    
    def __init__(self, name: str, requires_selenium: bool = False):
        """
        Inicializa o scraper base.
        
        Args:
            name: Nome do scraper
            requires_selenium: Se o scraper requer Selenium
        """
        self.name = name
        self.requires_selenium = requires_selenium
        self.max_retries = settings.MAX_RETRIES
        self.retry_delay = settings.RETRY_DELAY
        self.user_agent = settings.USER_AGENT
    
    @abstractmethod
    def search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Realiza uma busca com base nos critérios fornecidos.
        
        Args:
            criteria: Critérios de busca
            
        Returns:
            Lista de resultados encontrados
        """
        pass
    
    @abstractmethod
    def collect(self, target: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
        """
        Coleta dados específicos de um alvo.
        
        Args:
            target: Alvo da coleta (ex: empresa)
            fields: Campos a serem coletados
            
        Returns:
            Dados coletados
        """
        pass
    
    def _retry_operation(self, operation, *args, **kwargs):
        """
        Tenta executar uma operação com retentativas em caso de falha.
        
        Args:
            operation: Função a ser executada
            *args: Argumentos para a função
            **kwargs: Argumentos nomeados para a função
            
        Returns:
            Resultado da operação
            
        Raises:
            Exception: Se todas as tentativas falharem
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Tentativa {attempt + 1}/{self.max_retries} falhou: {e}")
                
                if attempt < self.max_retries - 1:
                    # Esperar antes da próxima tentativa (com backoff exponencial)
                    delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"Aguardando {delay}s antes da próxima tentativa")
                    time.sleep(delay)
        
        # Se chegou aqui, todas as tentativas falharam
        logger.error(f"Todas as {self.max_retries} tentativas falharam")
        raise last_exception
    
    def _extract_field(self, data: Dict[str, Any], field_path: str, default: Any = None) -> Any:
        """
        Extrai um campo de um dicionário aninhado usando um caminho de acesso.
        
        Args:
            data: Dicionário de dados
            field_path: Caminho do campo (ex: "company.info.name")
            default: Valor padrão se o campo não existir
            
        Returns:
            Valor do campo ou valor padrão
        """
        parts = field_path.split('.')
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        
        return current
    
    def _normalize_text(self, text: Optional[str]) -> str:
        """
        Normaliza um texto removendo espaços extras e quebras de linha.
        
        Args:
            text: Texto a ser normalizado
            
        Returns:
            Texto normalizado
        """
        if not text:
            return ""
        
        # Remover espaços extras e quebras de linha
        normalized = ' '.join(text.split())
        return normalized.strip()
    
    def _is_valid_data(self, data: Dict[str, Any]) -> bool:
        """
        Verifica se os dados coletados são válidos.
        
        Args:
            data: Dados a serem verificados
            
        Returns:
            True se os dados forem válidos, False caso contrário
        """
        # Verificar se há pelo menos um campo não vazio
        return any(value for value in data.values() if value)
