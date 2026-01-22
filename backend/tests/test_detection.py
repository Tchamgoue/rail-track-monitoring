# -*- coding: utf-8 -*-
"""Script de diagnostic pour vérifier la détection"""

import cv2
import numpy as np
from detector import RailwayDetector

print("[DEBUG] Creating test image...")

# Image de test simple
test_image = np.ones((600, 800, 3), dtype=np.uint8) * 200

# Ajouter 3 rectangles noirs (anomalies)
cv2.rectangle(test_image, (100, 100), (150, 200), (0, 0, 0), -1)
cv2.rectangle(test_image, (300, 300), (350, 400), (0, 0, 0), -1)
cv2.rectangle(test_image, (500, 150), (550, 250), (0, 0, 0), -1)

# Sauvegarder image originale
cv2.imwrite("../samples/debug_original.jpg", test_image)
print("[OK] Original image saved: samples/debug_original.jpg")

# Créer détecteur
detector = RailwayDetector()

# Convertir en niveaux de gris
gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
cv2.imwrite("../samples/debug_gray.jpg", gray)
print("[OK] Grayscale saved: samples/debug_gray.jpg")

# Appliquer flou
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
cv2.imwrite("../samples/debug_blurred.jpg", blurred)
print("[OK] Blurred saved: samples/debug_blurred.jpg")

# Détection de contours
edges = cv2.Canny(blurred, 50, 150)
cv2.imwrite("../samples/debug_edges.jpg", edges)
print("[OK] Edges saved: samples/debug_edges.jpg")

# Trouver contours
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"[INFO] Found {len(contours)} contours")

# Filtrer anomalies
anomalies = []
for contour in contours:
    area = cv2.contourArea(contour)
    if area >= 100:
        x, y, w, h = cv2.boundingRect(contour)
        anomalies.append({'bbox': (x, y, w, h), 'area': area})
        print(f"[INFO] Anomaly: area={area:.0f}, bbox=({x},{y},{w},{h})")

print(f"[INFO] Filtered to {len(anomalies)} anomalies")

# Dessiner rectangles rouges
result = test_image.copy()
for idx, anomaly in enumerate(anomalies, 1):
    x, y, w, h = anomaly['bbox']
    cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 3)  # Rouge, épaisseur 3
    cv2.putText(result, f"#{idx}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

# Texte info
cv2.putText(result, f"Anomalies: {len(anomalies)}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

cv2.imwrite("../samples/debug_annotated.jpg", result)
print("[OK] Annotated image saved: samples/debug_annotated.jpg")

print("\n[DONE] Check these files:")
print("  1. samples/debug_original.jpg    (gray + black rectangles)")
print("  2. samples/debug_edges.jpg       (white edges on black)")
print("  3. samples/debug_annotated.jpg   (RED rectangles around black ones)")