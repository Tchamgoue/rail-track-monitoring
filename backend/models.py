"""
Modèles de données pour le système de monitoring ferroviaire
Utilise SQLite pour la simplicité (production: PostgreSQL)
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict
import json


class Database:
    """Gestionnaire de base de données SQLite"""
    
    def __init__(self, db_path: str = "database/inspections.db"):
        """
        Initialise la connexion à la base de données
        
        Args:
            db_path: Chemin vers le fichier SQLite
        """
        self.db_path = db_path
        # Crée le dossier si nécessaire
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Crée une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        # Retourne les résultats comme des dictionnaires au lieu de tuples
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Crée les tables si elles n'existent pas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table des inspections
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inspections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                upload_date TEXT NOT NULL,
                status TEXT NOT NULL,
                anomalies_count INTEGER DEFAULT 0,
                criticality_score REAL DEFAULT 0.0,
                processing_time REAL DEFAULT 0.0,
                notes TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        print("Database initialized successfully")


class Inspection:
    """Modèle représentant une inspection de voie ferrée"""
    
    def __init__(
        self,
        filename: str,
        original_filename: str,
        status: str = "pending",
        anomalies_count: int = 0,
        criticality_score: float = 0.0,
        processing_time: float = 0.0,
        notes: str = None,
        id: int = None,
        upload_date: str = None
    ):
        self.id = id
        self.filename = filename
        self.original_filename = original_filename
        self.upload_date = upload_date or datetime.now().isoformat()
        self.status = status
        self.anomalies_count = anomalies_count
        self.criticality_score = criticality_score
        self.processing_time = processing_time
        self.notes = notes
    
    def to_dict(self) -> Dict:
        """Convertit l'inspection en dictionnaire (pour JSON)"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'upload_date': self.upload_date,
            'status': self.status,
            'anomalies_count': self.anomalies_count,
            'criticality_score': round(self.criticality_score, 2),
            'criticality_level': self.get_criticality_level(),
            'processing_time': round(self.processing_time, 3),
            'notes': self.notes
        }
    
    def get_criticality_level(self) -> str:
        """Détermine le niveau de criticité basé sur le score"""
        if self.criticality_score >= 0.7:
            return "high"
        elif self.criticality_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def save(self, db: Database) -> int:
        """
        Sauvegarde l'inspection dans la base de données
        
        Args:
            db: Instance de Database
            
        Returns:
            ID de l'inspection créée
        """
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO inspections (
                filename, original_filename, upload_date, status,
                anomalies_count, criticality_score, processing_time, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.filename,
            self.original_filename,
            self.upload_date,
            self.status,
            self.anomalies_count,
            self.criticality_score,
            self.processing_time,
            self.notes
        ))
        
        conn.commit()
        inspection_id = cursor.lastrowid
        conn.close()
        
        self.id = inspection_id
        return inspection_id
    
    @staticmethod
    def get_all(db: Database, limit: int = 100) -> List['Inspection']:
        """
        Récupère toutes les inspections
        
        Args:
            db: Instance de Database
            limit: Nombre maximum d'inspections à retourner
            
        Returns:
            Liste d'objets Inspection
        """
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM inspections 
            ORDER BY upload_date DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        inspections = []
        for row in rows:
            inspection = Inspection(
                id=row['id'],
                filename=row['filename'],
                original_filename=row['original_filename'],
                upload_date=row['upload_date'],
                status=row['status'],
                anomalies_count=row['anomalies_count'],
                criticality_score=row['criticality_score'],
                processing_time=row['processing_time'],
                notes=row['notes']
            )
            inspections.append(inspection)
        
        return inspections
    
    @staticmethod
    def get_by_id(db: Database, inspection_id: int) -> Optional['Inspection']:
        """
        Récupère une inspection par son ID
        
        Args:
            db: Instance de Database
            inspection_id: ID de l'inspection
            
        Returns:
            Objet Inspection ou None si non trouvé
        """
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM inspections WHERE id = ?", (inspection_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return Inspection(
            id=row['id'],
            filename=row['filename'],
            original_filename=row['original_filename'],
            upload_date=row['upload_date'],
            status=row['status'],
            anomalies_count=row['anomalies_count'],
            criticality_score=row['criticality_score'],
            processing_time=row['processing_time'],
            notes=row['notes']
        )
    
    @staticmethod
    def get_stats(db: Database) -> Dict:
        """
        Calcule les statistiques globales
        
        Args:
            db: Instance de Database
            
        Returns:
            Dictionnaire avec les statistiques
        """
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Total inspections
        cursor.execute("SELECT COUNT(*) as total FROM inspections")
        total = cursor.fetchone()['total']
        
        # Inspections par criticité
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN criticality_score >= 0.7 THEN 1 ELSE 0 END) as high,
                SUM(CASE WHEN criticality_score >= 0.4 AND criticality_score < 0.7 THEN 1 ELSE 0 END) as medium,
                SUM(CASE WHEN criticality_score < 0.4 THEN 1 ELSE 0 END) as low
            FROM inspections
        """)
        criticality = cursor.fetchone()
        
        # Moyenne des anomalies
        cursor.execute("SELECT AVG(anomalies_count) as avg FROM inspections")
        avg_anomalies = cursor.fetchone()['avg'] or 0
        
        conn.close()
        
        return {
            'total_inspections': total,
            'criticality_distribution': {
                'high': criticality['high'] or 0,
                'medium': criticality['medium'] or 0,
                'low': criticality['low'] or 0
            },
            'average_anomalies': round(avg_anomalies, 2)
        }


# Test du module si exécuté directement
if __name__ == "__main__":
    print("Testing database models...")
    
    # Initialisation
    db = Database()
    
    # Création d'une inspection de test
    test_inspection = Inspection(
        filename="test_rail_001.jpg",
        original_filename="rail_track.jpg",
        status="completed",
        anomalies_count=3,
        criticality_score=0.65,
        processing_time=1.23,
        notes="Test inspection"
    )
    
    # Sauvegarde
    inspection_id = test_inspection.save(db)
    print(f"Created inspection with ID: {inspection_id}")
    
    # Récupération
    retrieved = Inspection.get_by_id(db, inspection_id)
    print(f"Retrieved: {retrieved.to_dict()}")
    
    # Stats
    stats = Inspection.get_stats(db)
    print(f"Stats: {stats}")
    
    print("\nAll tests passed!")