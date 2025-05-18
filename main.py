"""
Script principal para execução do crawler flexível.
Ponto de entrada para o sistema.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime

from core.controller import CrawlerController
from config import settings

def setup_logging():
    """Configura o sistema de logging."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"crawler_{timestamp}.log"
    
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),  # Forçar UTF-8
            logging.StreamHandler(sys.stdout)
        ]
    )

def parse_arguments():
    """Analisa argumentos da linha de comando."""
    parser = argparse.ArgumentParser(description='Crawler Flexível para Coleta de Dados Empresariais')
    
    # Argumentos principais
    parser.add_argument('--criteria', type=str, help='Caminho para arquivo JSON com critérios de busca')
    
    # Argumentos diretos
    parser.add_argument('--sector', type=str, help='Setor principal da empresa')
    parser.add_argument('--location', type=str, help='Localização (país, estado ou cidade)')
    parser.add_argument('--min-employees', type=int, help='Número mínimo de funcionários')
    parser.add_argument('--max-employees', type=int, help='Número máximo de funcionários')
    parser.add_argument('--min-revenue', type=float, help='Faturamento mínimo')
    parser.add_argument('--output', type=str, help='Caminho para arquivo de saída')
    parser.add_argument('--format', type=str, choices=['excel', 'csv', 'json'], default='excel', help='Formato de saída')
    parser.add_argument('--max-results', type=int, default=5, help='Número máximo de resultados')
    
    return parser.parse_args()

def load_criteria_from_file(file_path):
    """Carrega critérios de busca de um arquivo JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Erro ao carregar critérios do arquivo {file_path}: {e}")
        return None

def build_criteria_from_args(args):
    """Constrói critérios de busca a partir dos argumentos da linha de comando."""
    criteria = {}
    
    # Setor
    if args.sector:
        criteria['sector'] = {
            'main': args.sector
        }
    
    # Localização
    if args.location:
        criteria['location'] = {
            'country': 'Brasil'  # Padrão
        }
        
        # Tentar identificar se é estado ou cidade
        if len(args.location) == 2 and args.location.isupper():
            criteria['location']['states'] = [args.location]
        else:
            criteria['location']['cities'] = [args.location]
    
    # Tamanho
    if args.min_employees or args.max_employees:
        criteria['size'] = {
            'employees': {}
        }
        
        if args.min_employees:
            criteria['size']['employees']['min'] = args.min_employees
        
        if args.max_employees:
            criteria['size']['employees']['max'] = args.max_employees
    
    # Faturamento
    if args.min_revenue:
        if 'size' not in criteria:
            criteria['size'] = {}
        
        criteria['size']['revenue'] = {
            'min': args.min_revenue,
            'currency': 'BRL'
        }
    
    # Saída
    criteria['output'] = {
        'format': args.format,
        'max_results': args.max_results
    }
    
    return criteria

def main():
    """Função principal."""
    # Configurar logging
    setup_logging()
    
    # Analisar argumentos
    args = parse_arguments()
    
    # Carregar critérios
    criteria = None
    
    if args.criteria:
        criteria = load_criteria_from_file(args.criteria)
        if not criteria:
            logging.error("Falha ao carregar critérios. Encerrando.")
            return 1
    else:
        criteria = build_criteria_from_args(args)
    
    # Verificar se há critérios
    if not criteria:
        logging.error("Nenhum critério fornecido. Use --criteria ou argumentos diretos.")
        return 1
    
    # Inicializar controlador
    controller = CrawlerController()
    
    # Executar crawler
    try:
        logging.info("Iniciando execução do crawler...")
        results = controller.execute(criteria)
        
        # Exibir resultados
        logging.info(f"Execução concluída em {results['execution_time']:.2f} segundos")
        logging.info(f"Total de empresas encontradas: {results['total_found']}")
        logging.info(f"Total de empresas válidas: {results['total_valid']}")
        logging.info(f"Resultados exportados para: {results['output_file']}")
        
        # Exibir dados no console
        if results['companies']:
            print("\nEmpresas encontradas:")
            for i, company in enumerate(results['companies'], 1):
                print(f"\n{i}. {company.get('Company Name (Revised)', 'Desconhecido')}")
                print(f"   CNPJ: {company.get('CNPJ', 'N/A')}")
                print(f"   Localização: {company.get('Location', 'N/A')}")
                print(f"   Contato: {company.get('E-mail', 'N/A')}")
        else:
            print("\nNenhuma empresa válida encontrada que atenda aos critérios.")
            print("Verifique os logs para mais detalhes sobre os problemas encontrados.")
        
        return 0
    
    except Exception as e:
        logging.error(f"Erro durante execução: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
