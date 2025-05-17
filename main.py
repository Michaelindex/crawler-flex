"""
Script principal para execução do crawler flexível.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flexible_crawler.core.controller import CrawlerController
from flexible_crawler.config import settings

def setup_logging():
    """Configura o sistema de logging."""
    log_level = getattr(logging, settings.LOG_LEVEL)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f"crawler_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        ]
    )

def parse_arguments():
    """Processa argumentos da linha de comando."""
    parser = argparse.ArgumentParser(description='Crawler Flexível para Coleta de Dados Empresariais')
    
    # Argumentos para arquivo de critérios ou critérios diretos
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--criteria', type=str, help='Caminho para arquivo JSON com critérios de busca')
    group.add_argument('--sector', type=str, help='Setor principal da empresa')
    
    # Argumentos opcionais
    parser.add_argument('--location', type=str, help='Localização (país, estado ou cidade)')
    parser.add_argument('--min-employees', type=int, help='Número mínimo de funcionários')
    parser.add_argument('--max-employees', type=int, help='Número máximo de funcionários')
    parser.add_argument('--min-revenue', type=int, help='Faturamento mínimo')
    parser.add_argument('--output', type=str, help='Caminho para arquivo de saída')
    parser.add_argument('--format', type=str, choices=['excel', 'csv'], default='excel', help='Formato de saída')
    parser.add_argument('--max-results', type=int, default=50, help='Número máximo de resultados')
    
    return parser.parse_args()

def build_criteria_from_args(args):
    """Constrói critérios a partir dos argumentos da linha de comando."""
    criteria = {}
    
    # Critérios de setor
    if args.sector:
        criteria['sector'] = {
            'main': args.sector
        }
    
    # Critérios de localização
    if args.location:
        criteria['location'] = {
            'country': 'Brasil'  # Default para Brasil
        }
        
        # Tentar identificar se é estado ou cidade
        if len(args.location) == 2 and args.location.isupper():
            criteria['location']['states'] = [args.location]
        else:
            criteria['location']['cities'] = [args.location]
    
    # Critérios de tamanho
    if args.min_employees or args.max_employees:
        criteria['size'] = {
            'employees': {}
        }
        
        if args.min_employees:
            criteria['size']['employees']['min'] = args.min_employees
        
        if args.max_employees:
            criteria['size']['employees']['max'] = args.max_employees
    
    # Critérios de faturamento
    if args.min_revenue:
        if 'size' not in criteria:
            criteria['size'] = {}
        
        criteria['size']['revenue'] = {
            'min': args.min_revenue,
            'currency': 'BRL'
        }
    
    # Configurações de saída
    criteria['output'] = {
        'format': args.format,
        'max_results': args.max_results
    }
    
    return criteria

def main():
    """Função principal."""
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Processar argumentos
    args = parse_arguments()
    
    # Obter critérios
    if args.criteria:
        # Carregar de arquivo
        try:
            with open(args.criteria, 'r', encoding='utf-8') as f:
                criteria = json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar arquivo de critérios: {e}")
            sys.exit(1)
    else:
        # Construir a partir dos argumentos
        criteria = build_criteria_from_args(args)
    
    logger.info(f"Critérios de busca: {criteria}")
    
    # Iniciar controlador
    controller = CrawlerController()
    
    # Executar crawler
    try:
        result = controller.execute(criteria)
        
        # Exibir resultados
        logger.info(f"Busca concluída. {result['total_valid']} empresas encontradas.")
        logger.info(f"Arquivo gerado: {result['output_file']}")
        
        # Se output foi especificado, copiar para o caminho desejado
        if args.output and result['output_file']:
            import shutil
            try:
                shutil.copy(result['output_file'], args.output)
                logger.info(f"Arquivo copiado para: {args.output}")
            except Exception as e:
                logger.error(f"Erro ao copiar arquivo: {e}")
        
    except Exception as e:
        logger.error(f"Erro durante a execução: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
