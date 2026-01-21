# -*- coding: utf-8 -*-
"""
API Flask pour le système de monitoring ferroviaire
Expose 4 endpoints REST pour gérer les inspections
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flasgger import Swagger, swag_from
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import traceback

from models import Database, Inspection
from detector import RailwayDetector
from exceptions import APIException, ValidationError, NotFoundError, ProcessingError, DatabaseError
from validators import validate_image_file, validate_pagination_params
from flask import make_response
try:
    from exporters import export_inspections_to_csv
except ImportError:
    print("[WARNING] exporters.py not found, CSV export will not be available")
    export_inspections_to_csv = None

# Configuration de l'application
app = Flask(__name__)
CORS(app)  # Permet les requêtes depuis le frontend

# Configuration Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Railway Track Monitoring API",
        "description": "API pour la détection automatique d'anomalies sur voies ferrées",
        "version": "1.0.0",
        "contact": {
            "name": "Adrienne Tchamgoue",
            "email": "adrienne.tchamgoue@gmail.com"
        }
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http"],
    "tags": [
        {
            "name": "Health",
            "description": "Endpoints de santé du service"
        },
        {
            "name": "Inspections",
            "description": "Gestion des inspections de voies ferrées"
        },
        {
            "name": "Statistics",
            "description": "Statistiques et analytics"
        }
    ]
}
swagger = Swagger(app, config=swagger_config, template=swagger_template)


@app.errorhandler(APIException)
def handle_api_exception(error):
    """Handler global pour les exceptions API"""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handler pour les erreurs de validation"""
    return jsonify({'error': error.message}), error.status_code


@app.errorhandler(NotFoundError)
def handle_not_found_error(error):
    """Handler pour les ressources non trouvées"""
    return jsonify({'error': error.message}), error.status_code


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    """Handler pour les erreurs non gérées"""
    print(f"[ERROR] Unexpected error: {str(error)}")
    traceback.print_exc()
    return jsonify({
        'error': 'Internal server error',
        'details': str(error) if app.debug else 'An unexpected error occurred'
    }), 500

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
    ---
    tags:
      - Health
    responses:
      200:
        description: Service opérationnel
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            timestamp:
              type: string
              example: "2025-01-20T14:30:00"
            service:
              type: string
              example: "Railway Track Monitoring API"
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
        # Validation avec le validateur
        file = request.files.get('image')
        validate_image_file(file)
        
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
        try:
            analysis_result = detector.process_image(filepath)
        except Exception as e:
            # Supprimer le fichier si l'analyse échoue
            if os.path.exists(filepath):
                os.remove(filepath)
            raise ProcessingError(f'Image analysis failed: {str(e)}')
        
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
        try:
            inspection_id = inspection.save(db)
            print(f"[INFO] Inspection saved with ID: {inspection_id}")
        except Exception as e:
            raise DatabaseError(f'Failed to save inspection: {str(e)}')
        
        # Retour de la réponse
        return jsonify({
            'success': True,
            'inspection': inspection.to_dict(),
            'message': 'Image analyzed successfully'
        }), 201
    
    except (ValidationError, ProcessingError, DatabaseError) as e:
        # Les exceptions custom sont gérées par les handlers
        raise
    except Exception as e:
        # Erreur inattendue
        print(f"[ERROR] Upload failed: {str(e)}")
        traceback.print_exc()
        raise APIException('Internal server error', 500, {'details': str(e)})
    

@app.route('/api/inspections', methods=['GET'])
def get_inspections():
    """
    Récupère la liste de toutes les inspections
    GET /api/inspections?limit=50
    
    Query params:
        limit (optional): Nombre maximum d'inspections à retourner (défaut: 100)
    
    Returns:
        JSON avec la liste des inspections   
    ---
    tags:
      - Inspections
    parameters:
      - name: limit
        in: query
        type: integer
        default: 100
        description: Nombre maximum d'inspections à retourner
    responses:
      200:
        description: Liste des inspections
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            count:
              type: integer
              example: 42
            inspections:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  filename:
                    type: string
                  anomalies_count:
                    type: integer
                  criticality_score:
                    type: number
                  criticality_level:
                    type: string
    """
    try:
        limit = validate_pagination_params(
            request.args.get('limit'),
            default=100,
            max_limit=500
        )
        
        inspections = Inspection.get_all(db, limit=limit)
        
        return jsonify({
            'success': True,
            'count': len(inspections),
            'inspections': [insp.to_dict() for insp in inspections]
        }), 200
    
    except Exception as e:
        print(f"[ERROR] Failed to get inspections: {str(e)}")
        raise DatabaseError('Failed to retrieve inspections')
        

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
            raise NotFoundError(f'Inspection {inspection_id} not found')
        
        return jsonify({
            'success': True,
            'inspection': inspection.to_dict()
        }), 200
    
    except NotFoundError:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to get inspection {inspection_id}: {str(e)}")
        raise DatabaseError('Failed to retrieve inspection')
        
        
@app.route('/api/inspections/<int:inspection_id>', methods=['DELETE'])
def delete_inspection(inspection_id):
    """
    Supprime une inspection et ses fichiers associés
    DELETE /api/inspections/123
    
    Returns:
        JSON confirmation de suppression
    """
    try:
        # Récupérer l'inspection avant de la supprimer
        inspection = Inspection.get_by_id(db, inspection_id)
        
        if not inspection:
            return jsonify({
                'error': 'Inspection not found',
                'id': inspection_id
            }), 404
        
        # Suppression des fichiers images
        try:
            # Image originale
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], inspection.filename)
            if os.path.exists(original_path):
                os.remove(original_path)
                print(f"[INFO] Deleted file: {original_path}")
            
            # Image annotée
            base_path, ext = os.path.splitext(inspection.filename)
            annotated_filename = f"{base_path}_annotated{ext}"
            annotated_path = os.path.join(app.config['UPLOAD_FOLDER'], annotated_filename)
            if os.path.exists(annotated_path):
                os.remove(annotated_path)
                print(f"[INFO] Deleted file: {annotated_path}")
        
        except Exception as e:
            print(f"[WARNING] Could not delete files: {str(e)}")
            # Continue même si fichiers non supprimés
        
        # Suppression en base de données
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inspections WHERE id = ?", (inspection_id,))
        conn.commit()
        conn.close()
        
        print(f"[INFO] Inspection {inspection_id} deleted successfully")
        
        return jsonify({
            'success': True,
            'message': 'Inspection deleted successfully',
            'id': inspection_id
        }), 200
    
    except Exception as e:
        print(f"[ERROR] Failed to delete inspection {inspection_id}: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to delete inspection',
            'details': str(e)
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """
    Récupère les statistiques globales du système
    GET /api/stats
    
    Returns:
        JSON avec les statistiques (total, criticité, moyenne)
    ---
    tags:
      - Statistics
    responses:
      200:
        description: Statistiques du système
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            statistics:
              type: object
              properties:
                total_inspections:
                  type: integer
                  example: 42
                criticality_distribution:
                  type: object
                  properties:
                    high:
                      type: integer
                    medium:
                      type: integer
                    low:
                      type: integer
                average_anomalies:
                  type: number
                  example: 18.5
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
        
@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """
    Exporte toutes les inspections en CSV
    """
    try:
        # Vérifier que le module est disponible
        if export_inspections_to_csv is None:
            return jsonify({
                'error': 'CSV export not available',
                'details': 'exporters module not found'
            }), 500
        
        # Récupérer toutes les inspections
        inspections = Inspection.get_all(db, limit=10000)
        
        if not inspections:
            return jsonify({
                'error': 'No inspections to export'
            }), 404
        
        # Générer le CSV
        csv_content = export_inspections_to_csv(inspections)
        
        # Créer la réponse
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = \
            f'attachment; filename=inspections_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        print(f"[INFO] Exported {len(inspections)} inspections to CSV")
        return response
    
    except Exception as e:
        print(f"[ERROR] Failed to export CSV: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Failed to export CSV',
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