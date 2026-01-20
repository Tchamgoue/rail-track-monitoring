# -*- coding: utf-8 -*-
"""Génère des images de test avec différents niveaux de criticité"""

import cv2
import numpy as np
import os

def create_low_criticality_image():
    """Image propre avec 1-2 petits défauts"""
    # Fond gris uniforme (comme du béton lisse)
    img = np.ones((800, 1200, 3), dtype=np.uint8) * 180
    
    # Ajouter un peu de texture légère
    noise = np.random.randint(-10, 10, img.shape, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # 1-2 petites fissures
    cv2.line(img, (400, 300), (450, 320), (100, 100, 100), 2)
    cv2.line(img, (700, 500), (730, 510), (90, 90, 90), 1)
    
    return img

def create_medium_criticality_image():
    """Image avec plusieurs défauts moyens"""
    img = np.ones((800, 1200, 3), dtype=np.uint8) * 180
    
    # Plus de texture
    noise = np.random.randint(-20, 20, img.shape, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # 5-8 défauts
    for i in range(6):
        x = np.random.randint(100, 1100)
        y = np.random.randint(100, 700)
        cv2.circle(img, (x, y), np.random.randint(10, 30), (80, 80, 80), -1)
        cv2.line(img, (x-20, y), (x+20, y), (70, 70, 70), 2)
    
    return img

def create_high_criticality_image():
    """Image très dégradée"""
    img = np.ones((800, 1200, 3), dtype=np.uint8) * 180
    
    # Beaucoup de texture
    noise = np.random.randint(-40, 40, img.shape, dtype=np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Nombreux défauts
    for i in range(20):
        x = np.random.randint(50, 1150)
        y = np.random.randint(50, 750)
        size = np.random.randint(20, 60)
        cv2.rectangle(img, (x, y), (x+size, y+size), (60, 60, 60), -1)
        cv2.circle(img, (x, y), np.random.randint(15, 40), (50, 50, 50), 3)
    
    return img

# Génération
os.makedirs("../samples", exist_ok=True)

low = create_low_criticality_image()
cv2.imwrite("../samples/rail_low_criticality.jpg", low)
print("[OK] Created: samples/rail_low_criticality.jpg")

medium = create_medium_criticality_image()
cv2.imwrite("../samples/rail_medium_criticality.jpg", medium)
print("[OK] Created: samples/rail_medium_criticality.jpg")

high = create_high_criticality_image()
cv2.imwrite("../samples/rail_high_criticality.jpg", high)
print("[OK] Created: samples/rail_high_criticality.jpg")

print("\n[DONE] Test images created!")