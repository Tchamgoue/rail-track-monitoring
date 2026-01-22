# -*- coding: utf-8 -*-
"""Tests unitaires pour models.py"""

import pytest
from models import Database, Inspection


class TestDatabase:
    """Tests pour la classe Database"""
    
    def test_database_creation(self, temp_db):
        """Test : La base de données est créée correctement"""
        import os
        assert os.path.exists(temp_db.db_path)
    
    def test_table_creation(self, temp_db):
        """Test : La table inspections existe"""
        conn = temp_db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='inspections'"
        )
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result['name'] == 'inspections'


class TestInspection:
    """Tests pour la classe Inspection"""
    
    def test_create_inspection(self, temp_db):
        """Test : Créer une inspection"""
        inspection = Inspection(
            filename="test.jpg",
            original_filename="original.jpg",
            status="completed",
            anomalies_count=5,
            criticality_score=0.45
        )
        
        inspection_id = inspection.save(temp_db)
        
        assert inspection_id is not None
        assert inspection_id > 0
        assert inspection.id == inspection_id
    
    def test_get_inspection_by_id(self, temp_db):
        """Test : Récupérer une inspection par ID"""
        inspection = Inspection(
            filename="test.jpg",
            original_filename="original.jpg",
            anomalies_count=3,
            criticality_score=0.28
        )
        inspection_id = inspection.save(temp_db)
        
        retrieved = Inspection.get_by_id(temp_db, inspection_id)
        
        assert retrieved is not None
        assert retrieved.id == inspection_id
        assert retrieved.filename == "test.jpg"
        assert retrieved.anomalies_count == 3
    
    def test_get_nonexistent_inspection(self, temp_db):
        """Test : Récupérer une inspection inexistante"""
        result = Inspection.get_by_id(temp_db, 9999)
        assert result is None
    
    def test_get_all_inspections(self, temp_db):
        """Test : Récupérer toutes les inspections"""
        for i in range(3):
            inspection = Inspection(
                filename=f"test_{i}.jpg",
                original_filename=f"original_{i}.jpg"
            )
            inspection.save(temp_db)
        
        inspections = Inspection.get_all(temp_db)
        assert len(inspections) == 3
    
    def test_criticality_level_low(self):
        """Test : Niveau de criticité LOW"""
        inspection = Inspection(
            filename="test.jpg",
            original_filename="test.jpg",
            criticality_score=0.3
        )
        assert inspection.get_criticality_level() == "low"
    
    def test_criticality_level_medium(self):
        """Test : Niveau de criticité MEDIUM"""
        inspection = Inspection(
            filename="test.jpg",
            original_filename="test.jpg",
            criticality_score=0.5
        )
        assert inspection.get_criticality_level() == "medium"
    
    def test_criticality_level_high(self):
        """Test : Niveau de criticité HIGH"""
        inspection = Inspection(
            filename="test.jpg",
            original_filename="test.jpg",
            criticality_score=0.8
        )
        assert inspection.get_criticality_level() == "high"
    
    def test_to_dict(self):
        """Test : Conversion en dictionnaire"""
        inspection = Inspection(
            id=1,
            filename="test.jpg",
            original_filename="original.jpg",
            anomalies_count=10,
            criticality_score=0.55
        )
        
        data = inspection.to_dict()
        
        assert isinstance(data, dict)
        assert data['id'] == 1
        assert data['criticality_level'] == "medium"
    
    def test_get_stats_empty(self, temp_db):
        """Test : Statistiques sur base vide"""
        stats = Inspection.get_stats(temp_db)
        
        assert stats['total_inspections'] == 0
        assert stats['criticality_distribution']['high'] == 0
    
    def test_get_stats_with_data(self, temp_db):
        """Test : Statistiques avec données"""
        # Low
        Inspection(
            filename="test1.jpg", original_filename="test1.jpg",
            criticality_score=0.2, anomalies_count=5
        ).save(temp_db)
        
        # Medium
        Inspection(
            filename="test2.jpg", original_filename="test2.jpg",
            criticality_score=0.5, anomalies_count=15
        ).save(temp_db)
        
        # High
        Inspection(
            filename="test3.jpg", original_filename="test3.jpg",
            criticality_score=0.8, anomalies_count=35
        ).save(temp_db)
        
        stats = Inspection.get_stats(temp_db)
        
        assert stats['total_inspections'] == 3
        assert stats['criticality_distribution']['low'] == 1
        assert stats['criticality_distribution']['medium'] == 1
        assert stats['criticality_distribution']['high'] == 1