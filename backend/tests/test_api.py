# -*- coding: utf-8 -*-
"""Tests d'intégration pour l'API Flask"""

import pytest
import sys
import os

# Importer l'app Flask
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app


@pytest.fixture
def client():
    """Fixture : Client de test Flask"""
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests pour /api/health"""
    
    def test_health_check(self, client):
        """Test : GET /api/health retourne 200"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'timestamp' in data


class TestInspectionsEndpoints:
    """Tests pour les endpoints inspections"""
    
    def test_get_inspections(self, client):
        """Test : GET /api/inspections"""
        response = client.get('/api/inspections')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'inspections' in data
        assert isinstance(data['inspections'], list)
    
    def test_get_nonexistent_inspection(self, client):
        """Test : GET /api/inspections/9999"""
        response = client.get('/api/inspections/9999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


class TestStatsEndpoint:
    """Tests pour /api/stats"""
    
    def test_get_stats(self, client):
        """Test : GET /api/stats"""
        response = client.get('/api/stats')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'statistics' in data
        assert 'total_inspections' in data['statistics']


class TestUploadEndpoint:
    """Tests pour /api/upload"""
    
    def test_upload_without_file(self, client):
        """Test : POST /api/upload sans fichier"""
        response = client.post('/api/upload')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data