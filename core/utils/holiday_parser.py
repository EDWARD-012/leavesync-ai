import os
import re
from datetime import datetime
from typing import List, Tuple, Optional
from django.core.files.uploadedfile import UploadedFile

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False


def parse_holiday_file(file: UploadedFile) -> List[Tuple[str, datetime.date]]:
    """
    Parse holiday file (XLSX or PDF) and return list of (name, date) tuples.
    Returns empty list if parsing fails.
    """
    filename = file.name.lower()
    
    if filename.endswith('.xlsx') or filename.endswith('.xls'):
        return _parse_xlsx(file)
    elif filename.endswith('.pdf'):
        return _parse_pdf(file)
    else:
        return []


def _parse_xlsx(file: UploadedFile) -> List[Tuple[str, datetime.date]]:
    """Parse Excel file for holidays."""
    if not OPENPYXL_AVAILABLE:
        return []
    
    holidays = []
    try:
        workbook = openpyxl.load_workbook(file)
        sheet = workbook.active
        
        # Try to find date and name columns (common patterns)
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if not row or not any(row):
                continue
            
            date_val = None
            name_val = None
            
            # Look for date in any column
            for cell in row:
                if cell is None:
                    continue
                
                # Try to parse as date
                if isinstance(cell, datetime):
                    date_val = cell.date()
                elif isinstance(cell, str):
                    # Try parsing date string
                    parsed_date = _parse_date_string(cell)
                    if parsed_date:
                        date_val = parsed_date
                    elif not name_val and len(cell.strip()) > 2:
                        name_val = cell.strip()
            
            # If we found a date, look for name in adjacent cells
            if date_val and not name_val:
                for cell in row:
                    if cell and isinstance(cell, str) and len(cell.strip()) > 2:
                        name_val = cell.strip()
                        break
            
            if date_val and name_val:
                holidays.append((name_val, date_val))
    
    except Exception as e:
        print(f"Error parsing XLSX: {e}")
        return []
    
    return holidays


def _parse_pdf(file: UploadedFile) -> List[Tuple[str, datetime.date]]:
    """Parse PDF file for holidays."""
    if not PDFPLUMBER_AVAILABLE:
        return []
    
    holidays = []
    try:
        # Read PDF content
        file.seek(0)
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        
        # Extract date patterns and holiday names
        # Common patterns: "January 1, 2025", "1/1/2025", "2025-01-01", etc.
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\w+)\s+(\d{1,2}),\s+(\d{4})',  # Month Day, Year
            r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})',  # YYYY-MM-DD
        ]
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            for pattern in date_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    try:
                        date_str = match.group(0)
                        parsed_date = _parse_date_string(date_str)
                        if parsed_date:
                            # Extract holiday name (text before or after date)
                            name = line.replace(date_str, '').strip()
                            # Clean up name
                            name = re.sub(r'[^\w\s-]', '', name).strip()
                            if name and len(name) > 2:
                                holidays.append((name, parsed_date))
                    except:
                        continue
    
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return []
    
    return holidays


def _parse_date_string(date_str: str) -> Optional[datetime.date]:
    """Try to parse various date string formats."""
    if not date_str:
        return None
    
    date_str = date_str.strip()
    
    # Common formats
    formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%B %d, %Y',
        '%b %d, %Y',
        '%d %B %Y',
        '%d %b %Y',
        '%Y/%m/%d',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except:
            continue
    
    return None

