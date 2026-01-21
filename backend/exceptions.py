# -*- coding: utf-8 -*-
"""
Gestion centralisée des exceptions pour l'API
"""

class APIException(Exception):
    """Exception de base pour l'API"""
    status_code = 500
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
    
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv


class ValidationError(APIException):
    """Erreur de validation des inputs"""
    status_code = 400


class NotFoundError(APIException):
    """Ressource non trouvée"""
    status_code = 404


class ProcessingError(APIException):
    """Erreur lors du traitement d'image"""
    status_code = 500


class DatabaseError(APIException):
    """Erreur base de données"""
    status_code = 500