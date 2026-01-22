# -*- coding: utf-8 -*-
"""
Configuration pytest et fixtures partagées
"""

import pytest
import os
import sys
import tempfile

# Ajouter le dossier parent au PYTHONPATH pour importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Database, Inspection
from detector import RailwayDetector
import numpy as np
import cv2


@pytest.fixture
def temp_db():
    """
    Fixture : Base de données temporaire
    Utilisable par tous les tests
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_path = temp_file.name
    temp_file.close()
    
    db = Database(db_path=temp_path)
    
    yield db
    
    # Nettoyage
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def detector():
    """Fixture : Détecteur OpenCV"""
    return RailwayDetector()


@pytest.fixture
def sample_image():
    """
    Fixture : Image de test synthétique
    Image 600x800 grise avec 3 rectangles noirs
    """
    image = np.ones((600, 800, 3), dtype=np.uint8) * 200
    cv2.rectangle(image, (100, 100), (150, 200), (0, 0, 0), -1)
    cv2.rectangle(image, (300, 300), (350, 400), (0, 0, 0), -1)
    cv2.rectangle(image, (500, 150), (550, 250), (0, 0, 0), -1)
    return image


@pytest.fixture
def temp_image_file(sample_image):
    """
    Fixture : Fichier image temporaire sur disque
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    temp_path = temp_file.name
    temp_file.close()
    
    cv2.imwrite(temp_path, sample_image)
    
    yield temp_path
    
    # Nettoyage
    if os.path.exists(temp_path):
        os.remove(temp_path)
    annotated = temp_path.replace('.jpg', '_annotated.jpg')
    if os.path.exists(annotated):
        os.remove(annotated)