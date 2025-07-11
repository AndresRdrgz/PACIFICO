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