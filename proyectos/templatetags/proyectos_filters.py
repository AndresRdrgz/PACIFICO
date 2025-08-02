from django import template

register = template.Library()

@register.filter
def is_image_file(filename):
    """Check if the file is an image based on extension"""
    if not filename:
        return False
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    return any(filename.lower().endswith(ext) for ext in image_extensions)

@register.filter
def is_pdf_file(filename):
    """Check if the file is a PDF"""
    if not filename:
        return False
    return filename.lower().endswith('.pdf')

@register.filter
def is_document_file(filename):
    """Check if the file is a document (Word, etc.)"""
    if not filename:
        return False
    doc_extensions = ['.doc', '.docx', '.txt', '.rtf']
    return any(filename.lower().endswith(ext) for ext in doc_extensions)

@register.filter
def get_file_icon(filename):
    """Get the appropriate icon class for a file type"""
    if not filename:
        return 'fas fa-file'
    
    filename_lower = filename.lower()
    
    if any(filename_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
        return 'fas fa-image'
    elif filename_lower.endswith('.pdf'):
        return 'fas fa-file-pdf'
    elif any(filename_lower.endswith(ext) for ext in ['.doc', '.docx']):
        return 'fas fa-file-word'
    elif any(filename_lower.endswith(ext) for ext in ['.xls', '.xlsx']):
        return 'fas fa-file-excel'
    elif any(filename_lower.endswith(ext) for ext in ['.txt', '.log']):
        return 'fas fa-file-alt'
    else:
        return 'fas fa-file'

@register.filter
def build_filter_url(filter_list, param_name):
    """Build URL parameters for multiple filter values"""
    if not filter_list:
        return ""
    
    url_parts = []
    for value in filter_list:
        url_parts.append(f"{param_name}={value}")
    
    return "&".join(url_parts)

@register.simple_tag
def build_pagination_url(page_number, resultado_filter, modulo_filter, prioridad_filter, tester_filter, desarrollador_filter, sort_by, sort_order):
    """Build complete URL for pagination with all filters and sorting"""
    params = []
    
    if page_number != 1:
        params.append(f"page={page_number}")
    
    if resultado_filter:
        for value in resultado_filter:
            params.append(f"resultado={value}")
    
    if modulo_filter:
        for value in modulo_filter:
            params.append(f"modulo={value}")
    
    if prioridad_filter:
        for value in prioridad_filter:
            params.append(f"prioridad={value}")
    
    if tester_filter:
        for value in tester_filter:
            params.append(f"tester={value}")
    
    if desarrollador_filter:
        for value in desarrollador_filter:
            params.append(f"desarrollador={value}")
    
    if sort_by:
        params.append(f"sort={sort_by}")
    
    if sort_order:
        params.append(f"order={sort_order}")
    
    return "?" + "&".join(params) if params else "?"