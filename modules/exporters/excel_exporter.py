"""
Exportador de dados para formato Excel.
Responsável por formatar e exportar os dados coletados para Excel.
"""

import logging
import os
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

class ExcelExporter:
    """
    Exportador para formato Excel com formatação avançada.
    """
    
    def __init__(self):
        """Inicializa o exportador Excel."""
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'output')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Exporta dados para Excel.
        
        Args:
            data: Dados a serem exportados
            filename: Nome do arquivo
            
        Returns:
            Caminho do arquivo exportado
        """
        if not data:
            logger.warning("Nenhum dado para exportar")
            return ""
        
        try:
            # Criar DataFrame
            df = pd.DataFrame(data)
            
            # Definir caminho de saída
            output_path = os.path.join(self.output_dir, filename)
            
            # Exportar para Excel
            df.to_excel(output_path, index=False)
            
            logger.info(f"Dados exportados para {output_path}")
            
            return output_path
        
        except Exception as e:
            logger.error(f"Erro ao exportar dados para Excel: {e}")
            return ""
    
    def export_with_formatting(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Exporta dados para Excel com formatação avançada.
        
        Args:
            data: Dados a serem exportados
            filename: Nome do arquivo
            
        Returns:
            Caminho do arquivo exportado
        """
        if not data:
            logger.warning("Nenhum dado para exportar")
            return ""
        
        try:
            # Criar DataFrame
            df = pd.DataFrame(data)
            
            # Definir caminho de saída
            output_path = os.path.join(self.output_dir, filename)
            
            # Criar Excel writer com formatação
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Exportar dados
                df.to_excel(writer, index=False, sheet_name='Empresas')
                
                # Obter planilha
                worksheet = writer.sheets['Empresas']
                
                # Formatar cabeçalho
                for col_num, column_title in enumerate(df.columns, 1):
                    cell = worksheet.cell(row=1, column=col_num)
                    cell.font = writer.book.create_font(bold=True)
                
                # Ajustar largura das colunas
                for col_num, column in enumerate(df.columns, 1):
                    max_length = 0
                    column_name = column
                    
                    # Verificar comprimento do nome da coluna
                    if len(column_name) > max_length:
                        max_length = len(column_name)
                    
                    # Verificar comprimento dos valores na coluna
                    for row_num in range(len(df)):
                        cell_value = str(df.iloc[row_num][column])
                        if len(cell_value) > max_length:
                            max_length = len(cell_value)
                    
                    # Ajustar largura (com margem)
                    adjusted_width = max_length + 2
                    worksheet.column_dimensions[chr(64 + col_num)].width = adjusted_width
            
            logger.info(f"Dados exportados com formatação para {output_path}")
            
            # Também exportar versão CSV para compatibilidade
            csv_path = output_path.replace('.xlsx', '.csv')
            df.to_csv(csv_path, index=False)
            logger.info(f"Versão CSV exportada para {csv_path}")
            
            return output_path
        
        except Exception as e:
            logger.error(f"Erro ao exportar dados para Excel com formatação: {e}")
            
            # Tentar exportar sem formatação como fallback
            try:
                df = pd.DataFrame(data)
                output_path = os.path.join(self.output_dir, filename)
                df.to_excel(output_path, index=False)
                logger.info(f"Dados exportados sem formatação para {output_path}")
                return output_path
            except Exception as e2:
                logger.error(f"Erro ao exportar dados sem formatação: {e2}")
                return ""
