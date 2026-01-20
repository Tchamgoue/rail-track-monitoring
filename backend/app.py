# -*- coding: utf-8 -*-
"""
API Flask pour le système de monitoring ferroviaire
Expose 4 endpoints REST pour gérer les inspections
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import traceback

from models import Database, Inspection
from detector import RailwayDetector

# Configuration de l'application
app = Flask(__name__)
CORS(app)  # Permet les requêtes depuis le frontend

# Configuration des dossiers
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Initialisation base de données et détecteur
db = Database()
detector = RailwayDetector()

# Créer le dossier uploads s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Endpoint de santé pour vérifier que l'API fonctionne
    GET /api/health
    """
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'Railway Track Monitoring API'
    }), 200


@app.route('/api/upload', methods=['POST'])
def upload_inspection():
    """
    Upload et analyse d'une image de voie ferrée
    POST /api/upload
    Body: multipart/form-data avec 'image' file
    
    Returns:
        JSON avec les résultats de l'inspection
    """
    try:
        # Vérification présence du fichier
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        
        # Vérification nom de fichier
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Vérification extension
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Sécurisation du nom de fichier et ajout timestamp
        original_filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{original_filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Sauvegarde du fichier
        file.save(filepath)
        print(f"[INFO] File saved: {filepath}")
        
        # Analyse de l'image avec OpenCV
        print(f"[INFO] Starting analysis...")
        analysis_result = detector.process_image(filepath)
        
        # Création de l'objet Inspection
        inspection = Inspection(
            filename=filename,
            original_filename=original_filename,
            status='completed',
            anomalies_count=analysis_result['anomalies_count'],
            criticality_score=analysis_result['criticality_score'],
            processing_time=analysis_result['processing_time'],
            notes=analysis_result['notes']
        )
        
        # Sauvegarde en base de données
        inspection_id = inspection.save(db)
        print(f"[INFO] Inspection saved with ID: {inspection_id}")
        
        # Retour de la réponse
        return jsonify({
            'success': True,
            'inspection': inspection.to_dict(),
            'message': 'Image analyzed successfully'
        }), 201
    
    except Exception as e:
        print(f"[ERROR] Upload failed: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@app.route('/api/inspections', methods=['GET'])
def get_inspections():
    """
    Récupère la liste de toutes les inspections
    GET /api/inspections?limit=50
    
    Query params:
        limit (optional): Nombre maximum d'inspections à retourner (défaut: 100)
    
    Returns:
        JSON avec la liste des inspections
    """
    try:
        limit = request.args.get('limit', default=100, type=int)
        
        inspections = Inspection.get_all(db, limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(inspections),
            'inspections': [insp.to_dict() for insp in inspections]
        }), 200
    
    except Exception as e:
        print(f"[ERROR] Failed to get inspections: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve inspections',
            'details': str(e)
        }), 500


@app.route('/api/inspections/<int:inspection_id>', methods=['GET'])
def get_inspection(inspection_id):
    """
    Récupère une inspection spécifique par son ID
    GET /api/inspections/123
    
    Returns:
        JSON avec les détails de l'inspection
    """
    try:
        inspection = Inspection.get_by_id(db, inspection_id)
        
        if not inspection:
            return jsonify({
                'error': 'Inspection not found',
                'id': inspection_id
            }), 404
        
        return jsonify({
            'success': True,
            'inspection': inspection.to_dict()
        }), 200
    
    except Exception as e:
        print(f"[ERROR] Failed to get inspection {inspection_id}: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve inspection',
            'details': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """
    Récupère les statistiques globales du système
    GET /api/stats
    
    Returns:
        JSON avec les statistiques (total, criticité, moyenne)
    """
    try:
        stats = Inspection.get_stats(db)
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
    
    except Exception as e:
        print(f"[ERROR] Failed to get statistics: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve statistics',
            'details': str(e)
        }), 500


@app.route('/uploads/<filename>')
def serve_image(filename):
    """
    Sert les images uploadées et annotées
    GET /uploads/image.jpg
    """
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404


@app.errorhandler(413)
def file_too_large(e):
    """Gestion des fichiers trop volumineux"""
    return jsonify({
        'error': 'File too large',
        'max_size': '10MB'
    }), 413


@app.errorhandler(404)
def not_found(e):
    """Gestion des routes inexistantes"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /api/health',
            'POST /api/upload',
            'GET /api/inspections',
            'GET /api/inspections/<id>',
            'GET /api/stats'
        ]
    }), 404


if __name__ == '__main__':
    print("=" * 50)
    print("Railway Track Monitoring API")
    print("=" * 50)
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Database: {db.db_path}")
    print(f"Allowed extensions: {ALLOWED_EXTENSIONS}")
    print(f"Max file size: {MAX_FILE_SIZE / (1024*1024)}MB")
    print("=" * 50)
    print("\nAPI Endpoints:")
    print("  - GET  /api/health")
    print("  - POST /api/upload")
    print("  - GET  /api/inspections")
    print("  - GET  /api/inspections/<id>")
    print("  - GET  /api/stats")
    print("=" * 50)
    print("\nStarting server on http://localhost:5000")
    print("Press CTRL+C to stop\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

"""

##  Explications de l'API

### **5 endpoints REST :**

1. **`GET /api/health`** : Vérification que l'API fonctionne
2. **`POST /api/upload`** : Upload + analyse d'image
3. **`GET /api/inspections`** : Liste toutes les inspections
4. **`GET /api/inspections/<id>`** : Détail d'une inspection
5. **`GET /api/stats`** : Statistiques globales

### **Sécurité implémentée :**

- ✅ Validation des extensions de fichiers
- ✅ Limite de taille (10MB)
- ✅ `secure_filename()` contre injections
- ✅ Gestion d'erreurs complète
- ✅ CORS activé pour le frontend

### **Workflow d'upload :**

1. Réception fichier
2. Validation (extension, taille)
3. Sauvegarde avec timestamp
4. Analyse OpenCV
5. Sauvegarde en DB
6. Retour JSON avec résultats

"""