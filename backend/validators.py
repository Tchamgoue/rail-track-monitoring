# -*- coding: utf-8 -*-
"""
Validateurs pour les inputs de l'API
"""

from exceptions import ValidationError

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_image_file(file):
    """
    Valide un fichier image uploadé
    
    Args:
        file: Fichier Flask request.files
        
    Raises:
        ValidationError: Si le fichier est invalide
    """
    if not file:
        raise ValidationError('No image file provided')
    
    if file.filename == '':
        raise ValidationError('No file selected')
    
    if not allowed_file(file.filename):
        raise ValidationError(
            f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
        )
    
    # Vérification taille (si possible)
    file.seek(0, 2)  # Aller à la fin
    size = file.tell()
    file.seek(0)  # Revenir au début
    
    if size > MAX_FILE_SIZE:
        raise ValidationError(
            f'File too large. Max size: {MAX_FILE_SIZE / (1024*1024)}MB'
        )
    
    return True


def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_pagination_params(limit, default=100, max_limit=500):
    """
    Valide les paramètres de pagination
    
    Args:
        limit: Limite demandée
        default: Valeur par défaut
        max_limit: Limite maximale autorisée
        
    Returns:
        int: Limite validée
    """
    try:
        limit = int(limit) if limit else default
    except (ValueError, TypeError):
        limit = default
    
    if limit < 1:
        limit = default
    elif limit > max_limit:
        limit = max_limit
    
    return limit