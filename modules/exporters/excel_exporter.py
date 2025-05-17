"""
Exportador de dados para formato Excel.
"""

import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

class ExcelExporter:
    """
    Exportador para gerar arquivos Excel a partir dos dados coletados.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Inicializa o exportador Excel.
        
        Args:
            output_dir: Diretório de saída para os arquivos
        """
        self.output_dir = output_dir or os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'output')
        os.makedirs(self.output_dir, exist_ok=True)
    
    def export(self, data: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Exporta dados para um arquivo Excel.
        
        Args:
            data: Lista de dados a serem exportados
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo gerado
        """
        logger.info(f"Exportando {len(data)} registros para Excel")
        
        # Criar DataFrame
        df = pd.DataFrame(data)
        
        # Gerar nome de arquivo se não fornecido
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'empresas_{timestamp}.xlsx'
        
        # Garantir extensão .xlsx
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        # Caminho completo do arquivo
        file_path = os.path.join(self.output_dir, filename)
        
        # Exportar para Excel
        df.to_excel(file_path, index=False)
        logger.info(f"Arquivo Excel gerado: {file_path}")
        
        return file_path
    
    def export_with_formatting(self, data: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
        """
        Exporta dados para um arquivo Excel com formatação avançada.
        
        Args:
            data: Lista de dados a serem exportados
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo gerado
        """
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
        
        logger.info(f"Exportando {len(data)} registros para Excel com formatação")
        
        # Criar DataFrame
        df = pd.DataFrame(data)
        
        # Gerar nome de arquivo se não fornecido
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'empresas_{timestamp}_formatado.xlsx'
        
        # Garantir extensão .xlsx
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        # Caminho completo do arquivo
        file_path = os.path.join(self.output_dir, filename)
        
        # Exportar para Excel (primeiro passo)
        df.to_excel(file_path, index=False)
        
        # Aplicar formatação
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        
        # Estilo para cabeçalho
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        # Estilo para bordas
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        # Aplicar estilo ao cabeçalho
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border
        
        # Ajustar largura das colunas
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            
            adjusted_width = max_length + 2
            ws.column_dimensions[column_letter].width = min(adjusted_width, 50)
        
        # Aplicar bordas e alinhamento a todas as células
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(vertical="center")
        
        # Salvar arquivo formatado
        wb.save(file_path)
        logger.info(f"Arquivo Excel formatado gerado: {file_path}")
        
        return file_path
