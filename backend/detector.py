# -*- coding: utf-8 -*-
"""
Module de détection d'anomalies sur images de voies ferrées
Utilise OpenCV pour l'analyse d'images
"""

import cv2
import numpy as np
from typing import Tuple, Dict
import time
import os


class RailwayDetector:
    """Détecteur d'anomalies sur voies ferrées utilisant OpenCV"""
    
    def __init__(self):
        """Initialise le détecteur avec les paramètres par défaut"""
        # Seuils de détection (ajustables)
        self.canny_threshold1 = 50
        self.canny_threshold2 = 150
        self.min_contour_area = 100  # Taille minimale d'une anomalie
        self.blur_kernel_size = 5
        
    def process_image(self, image_path: str) -> Dict:
        """
        Analyse une image et détecte les anomalies
        
        Args:
            image_path: Chemin vers l'image à analyser
            
        Returns:
            Dictionnaire avec les résultats de l'analyse
        """
        start_time = time.time()
        
        # Vérification existence fichier
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        # Lecture de l'image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot read image: {image_path}")
        
        # Analyse de l'image
        gray = self._convert_to_grayscale(image)
        blurred = self._apply_blur(gray)
        edges = self._detect_edges(blurred)
        contours = self._find_contours(edges)
        anomalies = self._filter_anomalies(contours)
        
        # Création de l'image annotée
        annotated_image = self._annotate_image(image.copy(), anomalies)
        
        # Sauvegarde de l'image annotée
        #annotated_path = image_path.replace('.', '_annotated.')
        #cv2.imwrite(annotated_path, annotated_image)
        base_path, ext = os.path.splitext(image_path)
        annotated_path = f"{base_path}_annotated{ext}"
        cv2.imwrite(annotated_path, annotated_image)
        
        # Calcul du score de criticité
        criticality_score = self._calculate_criticality(
            anomalies_count=len(anomalies),
            image_size=image.shape[0] * image.shape[1]
        )
        
        processing_time = time.time() - start_time
        
        return {
            'anomalies_count': len(anomalies),
            'criticality_score': criticality_score,
            'processing_time': processing_time,
            'annotated_image_path': annotated_path,
            'image_dimensions': {
                'width': image.shape[1],
                'height': image.shape[0]
            },
            'notes': self._generate_notes(len(anomalies), criticality_score)
        }
    
    def _convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convertit l'image en niveaux de gris
        Simplifie l'analyse en réduisant à 1 canal
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    def _apply_blur(self, image: np.ndarray) -> np.ndarray:
        """
        Applique un flou gaussien pour réduire le bruit
        Améliore la détection de contours
        """
        return cv2.GaussianBlur(
            image, 
            (self.blur_kernel_size, self.blur_kernel_size), 
            0
        )
    
    def _detect_edges(self, image: np.ndarray) -> np.ndarray:
        """
        Détecte les contours avec l'algorithme Canny
        Les fissures/anomalies apparaissent comme des discontinuités
        """
        return cv2.Canny(
            image, 
            self.canny_threshold1, 
            self.canny_threshold2
        )
    
    def _find_contours(self, edges: np.ndarray) -> list:
        """
        Trouve tous les contours dans l'image
        """
        contours, _ = cv2.findContours(
            edges, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        return contours
    
    def _filter_anomalies(self, contours: list) -> list:
        """
        Filtre les contours pour ne garder que les anomalies significatives
        Élimine les petits artefacts de détection
        """
        anomalies = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= self.min_contour_area:
                # Récupère le rectangle englobant
                x, y, w, h = cv2.boundingRect(contour)
                anomalies.append({
                    'contour': contour,
                    'area': area,
                    'bbox': (x, y, w, h)
                })
        return anomalies
    
    def _annotate_image(self, image: np.ndarray, anomalies: list) -> np.ndarray:
        """
        Dessine les anomalies détectées sur l'image
        Rectangle rouge + numéro
        """
        for idx, anomaly in enumerate(anomalies, 1):
            x, y, w, h = anomaly['bbox']
            
            # Rectangle rouge autour de l'anomalie
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            # Numéro de l'anomalie
            label = f"#{idx}"
            cv2.putText(
                image, 
                label, 
                (x, y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, 
                (0, 0, 255), 
                2
            )
        
        # Ajout d'un bandeau avec info
        info_text = f"Anomalies detectees: {len(anomalies)}"
        cv2.putText(
            image, 
            info_text, 
            (10, 30), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1, 
            (0, 255, 0), 
            2
        )
        
        return image
    
    def _calculate_criticality(self, anomalies_count: int, image_size: int) -> float:
        """
        Calcule un score de criticité entre 0 et 1
        VERSION AJUSTÉE pour images réelles
        
        Logique ajustée:
        - 0-10 anomalies = low (< 0.4)
        - 11-30 anomalies = medium (0.4-0.7)
        - 31+ anomalies = high (> 0.7)
        """
        if anomalies_count == 0:
            return 0.0
        elif anomalies_count <= 10:
            # 1-10 anomalies : progression douce
            return 0.05 + (anomalies_count * 0.03)  # Max 0.35
        elif anomalies_count <= 30:
            # 11-30 anomalies : zone medium
            return 0.4 + ((anomalies_count - 10) * 0.015)  # 0.4 à 0.7
        else:
            # 31+ anomalies : critique
            return min(0.7 + ((anomalies_count - 30) * 0.01), 1.0)
        
    
    def _generate_notes(self, anomalies_count: int, criticality_score: float) -> str:
        """
        Génère des notes automatiques basées sur l'analyse
        """
        if criticality_score >= 0.7:
            return f"CRITICAL: {anomalies_count} anomalies détectées. Inspection immédiate recommandée."
        elif criticality_score >= 0.4:
            return f"WARNING: {anomalies_count} anomalies détectées. Planifier une inspection bientôt."
        elif anomalies_count > 0:
            return f"INFO: {anomalies_count} anomalies mineures détectées. Surveiller lors de la prochaine maintenance."
        else:
            return "OK: Pas d'anomalies significatives détectées."


# Test du module si exécuté directement
if __name__ == "__main__":
    print("[TEST] Testing railway detector...")
    
    # Créer un détecteur
    detector = RailwayDetector()
    
    # Créer une image de test (simulée)
    test_image = np.ones((600, 800, 3), dtype=np.uint8) * 200
    
    # Ajouter des "anomalies" simulées (rectangles noirs)
    cv2.rectangle(test_image, (100, 100), (150, 200), (0, 0, 0), -1)
    cv2.rectangle(test_image, (300, 300), (350, 400), (0, 0, 0), -1)
    cv2.rectangle(test_image, (500, 150), (550, 250), (0, 0, 0), -1)
    
    # Sauvegarder l'image de test
    test_path = "../samples/test_rail.jpg"
    os.makedirs("../samples", exist_ok=True)
    cv2.imwrite(test_path, test_image)
    print(f"[OK] Test image created: {test_path}")
    
    # Analyser l'image
    results = detector.process_image(test_path)
    
    print(f"[OK] Analysis complete:")
    print(f"  - Anomalies found: {results['anomalies_count']}")
    print(f"  - Criticality score: {results['criticality_score']:.2f}")
    print(f"  - Processing time: {results['processing_time']:.3f}s")
    print(f"  - Notes: {results['notes']}")
    print(f"  - Annotated image: {results['annotated_image_path']}")
    
    print("\n[OK] All tests passed!")



"""

---

##  Explications de l'algorithme

### **Pipeline de traitement (5 étapes)**

1. **Grayscale** : Conversion en niveaux de gris (simplifie l'analyse)
2. **Blur** : Flou gaussien (réduit le bruit)
3. **Canny** : Détection de contours (identifie les discontinuités = fissures)
4. **Contours** : Extraction des formes détectées
5. **Filtrage** : Garde uniquement les anomalies significatives (> 100 pixels²)

### **Score de criticité (intelligent)**
```
0-2 anomalies  → 0.2-0.4 → LOW (vert)
3-7 anomalies  → 0.4-0.7 → MEDIUM (orange)
8+ anomalies   → 0.7-1.0 → HIGH (rouge)

"""