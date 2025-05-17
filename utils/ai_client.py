"""
Cliente para interação com a API de IA local.
"""

import logging
import requests
from typing import Dict, Any, Optional

from ..config import settings

logger = logging.getLogger(__name__)

class AIClient:
    """
    Cliente para realizar consultas à API de IA local.
    """
    
    def __init__(self, api_url: Optional[str] = None, model: Optional[str] = None):
        """
        Inicializa o cliente de IA.
        
        Args:
            api_url: URL da API de IA (opcional)
            model: Modelo de IA a ser utilizado (opcional)
        """
        self.api_url = api_url or settings.AI_API_URL
        self.model = model or settings.AI_MODEL
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def generate(self, prompt: str, stream: bool = False) -> Dict[str, Any]:
        """
        Gera texto com base em um prompt.
        
        Args:
            prompt: Prompt para geração de texto
            stream: Se deve usar streaming de resposta
            
        Returns:
            Resposta da IA
        """
        logger.info(f"Enviando prompt para IA: {prompt[:50]}...")
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream
        }
        
        try:
            response = requests.post(
                self.api_url,
                json=data,
                headers=self.headers,
                timeout=settings.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro na consulta à IA: {e}")
            return {"error": str(e), "response": ""}
    
    def enrich_company_data(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriquece dados de uma empresa usando IA.
        
        Args:
            company_data: Dados da empresa
            
        Returns:
            Dados enriquecidos
        """
        # Construir prompt
        company_name = company_data.get("Company Name (Revised)", "")
        sector = company_data.get("Sector", "")
        
        prompt = f"""
        Com base nas informações a seguir sobre a empresa {company_name}, 
        preencha os dados faltantes ou incompletos:
        
        Dados atuais:
        {company_data}
        
        Por favor, forneça apenas os campos que estão vazios ou incompletos,
        no formato JSON. Não invente informações que não possam ser inferidas
        dos dados existentes.
        """
        
        # Enviar para IA
        result = self.generate(prompt)
        
        # Processar resposta
        if "error" in result:
            logger.error(f"Erro ao enriquecer dados: {result['error']}")
            return company_data
        
        try:
            # Extrair JSON da resposta (implementação simplificada)
            response_text = result.get("response", "")
            
            # Na versão completa, implementaria um parser mais robusto
            # para extrair o JSON da resposta da IA
            
            # Por enquanto, retornar dados originais
            return company_data
            
        except Exception as e:
            logger.error(f"Erro ao processar resposta da IA: {e}")
            return company_data
    
    def classify_company_sector(self, description: str) -> str:
        """
        Classifica o setor de uma empresa com base em sua descrição.
        
        Args:
            description: Descrição da empresa
            
        Returns:
            Setor classificado
        """
        prompt = f"""
        Com base na seguinte descrição de empresa, classifique-a em um dos seguintes setores:
        - Tecnologia
        - Saúde
        - Finanças
        - Varejo
        - Educação
        - Indústria
        - Serviços
        - Outro (especificar)
        
        Descrição: {description}
        
        Responda apenas com o nome do setor.
        """
        
        result = self.generate(prompt)
        
        if "error" in result:
            logger.error(f"Erro ao classificar setor: {result['error']}")
            return "Não classificado"
        
        response = result.get("response", "").strip()
        return response or "Não classificado"
