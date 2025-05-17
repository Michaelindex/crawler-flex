"""
Controlador principal do sistema de crawler flexível.
Responsável por orquestrar o fluxo de execução com base nos critérios fornecidos.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..config import settings
from .criteria_parser import CriteriaParser
from .quality_checker import QualityChecker

logger = logging.getLogger(__name__)

class CrawlerController:
    """
    Controlador principal que coordena o fluxo de execução do crawler.
    """
    
    def __init__(self):
        """Inicializa o controlador com componentes necessários."""
        self.criteria_parser = CriteriaParser()
        self.quality_checker = QualityChecker()
        self.sources = self._load_sources()
        self._setup_logging()
        
    def _setup_logging(self):
        """Configura o sistema de logging."""
        log_level = getattr(logging, settings.LOG_LEVEL)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _load_sources(self) -> List[Dict[str, Any]]:
        """Carrega a whitelist de fontes do arquivo de configuração."""
        try:
            sources_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'sources.json')
            with open(sources_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('sources', [])
        except Exception as e:
            logger.error(f"Erro ao carregar fontes: {e}")
            return []
    
    def execute(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa o fluxo completo do crawler com base nos critérios fornecidos.
        
        Args:
            criteria: Dicionário com os critérios de busca
            
        Returns:
            Dicionário com os resultados da execução
        """
        start_time = datetime.now()
        logger.info(f"Iniciando execução com critérios: {criteria}")
        
        # Processar critérios
        parsed_criteria = self.criteria_parser.parse(criteria)
        logger.info(f"Critérios processados: {parsed_criteria}")
        
        # Planejar busca
        search_plan = self._plan_search(parsed_criteria)
        logger.info(f"Plano de busca criado com {len(search_plan)} etapas")
        
        # Executar busca
        raw_results = self._execute_search(search_plan)
        logger.info(f"Busca concluída. {len(raw_results)} empresas encontradas")
        
        # Processar e validar resultados
        processed_results = self._process_results(raw_results)
        logger.info(f"Processamento concluído. {len(processed_results)} empresas válidas")
        
        # Exportar resultados
        output_file = self._export_results(processed_results, criteria.get('output', {}))
        logger.info(f"Resultados exportados para {output_file}")
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            'companies': processed_results,
            'output_file': output_file,
            'execution_time': execution_time,
            'total_found': len(raw_results),
            'total_valid': len(processed_results)
        }
    
    def _plan_search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Cria um plano de busca com base nos critérios processados.
        
        Args:
            criteria: Critérios processados
            
        Returns:
            Lista de etapas de busca a serem executadas
        """
        # Implementação simplificada para o protótipo
        search_plan = []
        
        # Adicionar etapa de descoberta inicial
        search_plan.append({
            'type': 'discovery',
            'source': 'searx',
            'criteria': criteria
        })
        
        # Adicionar etapas de coleta para cada fonte relevante
        for source in self.sources:
            # Verificar se a fonte é relevante para os critérios
            if self._is_source_relevant(source, criteria):
                search_plan.append({
                    'type': 'collection',
                    'source': source['name'],
                    'criteria': criteria
                })
        
        return search_plan
    
    def _is_source_relevant(self, source: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """
        Verifica se uma fonte é relevante para os critérios fornecidos.
        
        Args:
            source: Informações da fonte
            criteria: Critérios de busca
            
        Returns:
            True se a fonte for relevante, False caso contrário
        """
        # Implementação simplificada para o protótipo
        # Na versão completa, verificaria quais tipos de dados são necessários
        # com base nos critérios e compararia com os tipos fornecidos pela fonte
        return True
    
    def _execute_search(self, search_plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Executa o plano de busca.
        
        Args:
            search_plan: Plano de busca a ser executado
            
        Returns:
            Lista de resultados brutos da busca
        """
        # Implementação simplificada para o protótipo
        # Na versão completa, instanciaria os scrapers apropriados
        # e executaria cada etapa do plano
        
        # Simulação de resultados para demonstração
        raw_results = [
            {
                'name': 'Empresa Exemplo 1',
                'cnpj': '12.345.678/0001-90',
                'fantasy_name': 'Exemplo Tech',
                'domain': 'exemplotech.com.br',
                'sources': ['LinkedIn', 'Site Corporativo']
            },
            {
                'name': 'Empresa Exemplo 2',
                'cnpj': '98.765.432/0001-10',
                'fantasy_name': 'Tech Solutions',
                'domain': 'techsolutions.com.br',
                'sources': ['LinkedIn', 'CNPJ.biz']
            }
        ]
        
        return raw_results
    
    def _process_results(self, raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa e valida os resultados brutos.
        
        Args:
            raw_results: Resultados brutos da busca
            
        Returns:
            Lista de resultados processados e validados
        """
        # Implementação simplificada para o protótipo
        processed_results = []
        
        for result in raw_results:
            # Simular processamento e validação
            processed = self._transform_to_output_format(result)
            
            # Verificar qualidade
            quality_score = self.quality_checker.check_quality(processed)
            if quality_score >= settings.MIN_QUALITY_SCORE:
                processed_results.append(processed)
        
        return processed_results
    
    def _transform_to_output_format(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforma o resultado para o formato de saída esperado.
        
        Args:
            result: Resultado bruto
            
        Returns:
            Resultado no formato de saída
        """
        # Implementação simplificada para o protótipo
        # Mapear campos do resultado para o formato de saída
        return {
            'Company Name (Revised)': result.get('name', ''),
            'Location': 'Endereço Exemplo, 123',
            'CNPJ': result.get('cnpj', ''),
            'Fantasy name': result.get('fantasy_name', ''),
            'Domain': result.get('domain', ''),
            'Size': 'Médio Porte',
            'First name': 'Nome',
            'Second Name': 'Sobrenome',
            'Office': 'Cargo Exemplo',
            'E-mail': f'contato@{result.get("domain", "exemplo.com")}',
            'Telephone': '(11) 1234-5678',
            'Telephone 2': '(11) 8765-4321',
            'City': 'São Paulo',
            'State': 'SP',
            'Linkedin': f'https://linkedin.com/company/{result.get("fantasy_name", "").lower().replace(" ", "-")}',
            'LOTE': 1
        }
    
    def _export_results(self, results: List[Dict[str, Any]], output_config: Dict[str, Any]) -> str:
        """
        Exporta os resultados para o formato especificado.
        
        Args:
            results: Resultados processados
            output_config: Configurações de saída
            
        Returns:
            Caminho do arquivo de saída
        """
        # Implementação simplificada para o protótipo
        # Na versão completa, usaria os exportadores apropriados
        
        output_format = output_config.get('format', settings.DEFAULT_OUTPUT_FORMAT)
        output_dir = os.path.join(os.path.dirname(__file__), '..', settings.DEFAULT_OUTPUT_DIR)
        
        # Garantir que o diretório existe
        os.makedirs(output_dir, exist_ok=True)
        
        # Gerar nome de arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'empresas_{timestamp}.{output_format}'
        output_path = os.path.join(output_dir, filename)
        
        # Simular exportação
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(results, indent=2, ensure_ascii=False))
        
        return output_path
