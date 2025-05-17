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
from ..modules.scrapers import get_scraper, get_all_scrapers
from ..modules.processors.data_processor import DataProcessor
from ..modules.exporters.excel_exporter import ExcelExporter

logger = logging.getLogger(__name__)

class CrawlerController:
    """
    Controlador principal que coordena o fluxo de execução do crawler.
    """
    
    def __init__(self):
        """Inicializa o controlador com componentes necessários."""
        self.criteria_parser = CriteriaParser()
        self.quality_checker = QualityChecker()
        self.data_processor = DataProcessor()
        self.excel_exporter = ExcelExporter()
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
        search_plan = []
        
        # Definir ordem de execução dos scrapers
        scraper_order = ['linkedin', 'cnpj', 'company_site']
        
        # Adicionar etapas de busca para cada scraper
        for scraper_name in scraper_order:
            search_plan.append({
                'type': 'search',
                'scraper': scraper_name,
                'criteria': criteria
            })
        
        return search_plan
    
    def _execute_search(self, search_plan: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Executa o plano de busca.
        
        Args:
            search_plan: Plano de busca a ser executado
            
        Returns:
            Lista de resultados brutos da busca
        """
        all_results = []
        company_data = {}  # Dicionário para armazenar dados por empresa
        
        # Executar cada etapa do plano
        for step in search_plan:
            try:
                logger.info(f"Executando etapa: {step['type']} com {step['scraper']}")
                
                # Obter scraper
                scraper = get_scraper(step['scraper'])
                
                # Executar busca
                if step['type'] == 'search':
                    search_results = scraper.search(step['criteria'])
                    logger.info(f"Busca com {step['scraper']} encontrou {len(search_results)} resultados")
                    
                    # Para cada resultado da busca, coletar dados detalhados
                    for result in search_results:
                        try:
                            # Identificar empresa (por nome ou domínio)
                            company_id = self._get_company_id(result)
                            
                            # Coletar dados detalhados
                            detailed_data = scraper.collect(result, [])
                            
                            # Armazenar dados no dicionário de empresas
                            if company_id not in company_data:
                                company_data[company_id] = []
                            
                            company_data[company_id].append(detailed_data)
                            
                        except Exception as e:
                            logger.error(f"Erro ao coletar dados para {result.get('name', 'desconhecido')}: {e}")
            
            except Exception as e:
                logger.error(f"Erro ao executar etapa {step['type']} com {step['scraper']}: {e}")
        
        # Converter dicionário para lista
        for company_id, data_list in company_data.items():
            all_results.append({
                'company_id': company_id,
                'data_sources': data_list
            })
        
        return all_results
    
    def _get_company_id(self, result: Dict[str, Any]) -> str:
        """
        Obtém um identificador único para a empresa.
        
        Args:
            result: Dados da empresa
            
        Returns:
            Identificador único da empresa
        """
        # Tentar usar CNPJ como identificador
        if 'cnpj' in result and result['cnpj']:
            return f"cnpj:{self._normalize_cnpj(result['cnpj'])}"
        
        # Tentar usar domínio como identificador
        if 'domain' in result and result['domain']:
            return f"domain:{result['domain'].lower()}"
        
        # Usar nome como identificador (menos confiável)
        if 'name' in result and result['name']:
            return f"name:{result['name'].lower()}"
        
        # Fallback para um hash dos dados
        import hashlib
        import json
        data_str = json.dumps(result, sort_keys=True)
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
    
    def _process_results(self, raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processa e valida os resultados brutos.
        
        Args:
            raw_results: Resultados brutos da busca
            
        Returns:
            Lista de resultados processados e validados
        """
        # Usar o processador de dados para unificar informações de múltiplas fontes
        processed_data = self.data_processor.process(raw_results)
        
        # Verificar qualidade dos dados
        validated_results = []
        
        for company_data in processed_data:
            # Verificar qualidade
            quality_score = self.quality_checker.check_quality(company_data)
            
            if quality_score >= settings.MIN_QUALITY_SCORE:
                validated_results.append(company_data)
            else:
                logger.warning(f"Empresa {company_data.get('Company Name (Revised)', 'Desconhecida')} não atingiu score mínimo de qualidade: {quality_score}")
        
        return validated_results
    
    def _export_results(self, results: List[Dict[str, Any]], output_config: Dict[str, Any]) -> str:
        """
        Exporta os resultados para o formato especificado.
        
        Args:
            results: Resultados processados
            output_config: Configurações de saída
            
        Returns:
            Caminho do arquivo de saída
        """
        output_format = output_config.get('format', settings.DEFAULT_OUTPUT_FORMAT)
        
        # Gerar nome de arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'empresas_{timestamp}'
        
        if output_format == 'excel':
            # Usar exportador Excel
            return self.excel_exporter.export_with_formatting(results, f"{filename}.xlsx")
        elif output_format == 'csv':
            # Usar exportador CSV (simplificado)
            import pandas as pd
            output_dir = os.path.join(os.path.dirname(__file__), '..', settings.DEFAULT_OUTPUT_DIR)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{filename}.csv")
            
            df = pd.DataFrame(results)
            df.to_csv(output_path, index=False)
            
            return output_path
        else:
            # Formato JSON
            output_dir = os.path.join(os.path.dirname(__file__), '..', settings.DEFAULT_OUTPUT_DIR)
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{filename}.json")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            return output_path
