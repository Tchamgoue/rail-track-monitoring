# 🚂 Railway Track Monitor

Système de détection automatique d'anomalies sur voies ferrées utilisant OpenCV et Flask.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-red)

## 📋 Description

Application FullStack de monitoring ferroviaire permettant de détecter automatiquement des anomalies (fissures, défauts) sur des images de voies ferrées à l'aide de traitement d'image par OpenCV.

**Développé en 3 jours** dans le cadre d'un entretien technique pour ISKernel.

### ✨ Fonctionnalités principales

- ✅ Upload et analyse d'images de voies ferrées (drag & drop)
- ✅ Détection automatique d'anomalies avec OpenCV (algorithme Canny)
- ✅ Scoring de criticité intelligent (LOW / MEDIUM / HIGH)
- ✅ Dashboard avec statistiques en temps réel
- ✅ Historique complet des inspections avec filtres et pagination
- ✅ Affichage détaillé des inspections avec images annotées
- ✅ Suppression sécurisée d'inspections (avec confirmation)
- ✅ Export des données en CSV
- ✅ Recherche par nom de fichier
- ✅ API REST documentée avec Swagger UI
- ✅ Gestion d'erreurs centralisée et professionnelle

## 🏗️ Architecture
```
rail-track-monitor/
│
├── backend/                   # API Flask + logique métier
│   ├── app.py                 # API REST (7 endpoints)
│   ├── models.py              # Modèles de données SQLite
│   ├── detector.py            # Algorithme OpenCV de détection
│   ├── exceptions.py          # Exceptions personnalisées
│   ├── validators.py          # Validateurs d'inputs
│   ├── exporters.py           # Export CSV
│   ├── tests/                 # Tests unitaires
│   ├── uploads/               # Images uploadées et annotées
│   └── requirements.txt       # Dépendances Python
│
├── frontend/                   # Interface utilisateur
│   ├── index.html             # Structure HTML responsive
│   ├── style.css              # Styles modernes avec gradient
│   └── app.js                 # Logique JavaScript (ES6+)
│
├── database/                   # Base de données
│   └── inspections.db         # SQLite
│
├── samples/                    # Images de test
│
└── README.md                  # Documentation complète

```

## 🛠️ Stack Technique

### Backend
- **Python 3.12** - Langage principal
- **Flask 3.0** - Framework web REST
- **OpenCV 4.8** - Traitement d'images et détection
- **SQLite** - Base de données relationnelle
- **NumPy** - Calculs matriciels
- **Flasgger** - Documentation API Swagger

### Frontend
- **HTML5 / CSS3** - Structure et styles modernes
- **JavaScript ES6+** - Logique côté client (Vanilla JS)
- **Fetch API** - Communication asynchrone avec l'API
- **CSS Grid & Flexbox** - Layout responsive

### Algorithme de détection (OpenCV)

Pipeline en 5 étapes :

1. **Conversion en niveaux de gris** - Simplifie l'analyse en réduisant à 1 canal
2. **Flou gaussien** - Réduit le bruit de l'image
3. **Détection de contours (Canny)** - Identifie les discontinuités (fissures)
4. **Extraction de contours** - Trouve toutes les formes détectées
5. **Filtrage** - Garde uniquement les anomalies significatives (>500px²)

**Performance :** 0.2-0.5 secondes par image en moyenne

## 📊 Barème de criticité

Le score est calculé en fonction du nombre d'anomalies détectées, calibré pour des images réelles :

| Anomalies détectées | Score | Niveau | Couleur | Action recommandée |
|---------------------|-------|--------|---------|-------------------|
| 0-10 | 0.05-0.35 | 🟢 LOW | Vert | Surveillance normale |
| 11-30 | 0.40-0.70 | 🟡 MEDIUM | Orange | Inspection programmée |
| 31+ | 0.71-1.00 | 🔴 HIGH | Rouge | Intervention urgente |

**Calibration :** Adapté aux textures naturelles des voies ferrées (ballast, rails) pour éviter les faux positifs.

## 🚀 Installation et lancement

### Prérequis
- Python 3.12+
- Git
- Navigateur web moderne

### Installation
```bash
# 1. Cloner le repository
git clone https://github.com/YOUR_USERNAME/rail-track-monitoring.git
cd rail-track-monitoring

# 2. Créer l'environnement virtuel
python -m venv venv

# 3. Activer l'environnement
# Windows (Git Bash)
source venv/Scripts/activate

# Linux/Mac
source venv/bin/activate

# 4. Installer les dépendances
pip install -r backend/requirements.txt
```

### Lancement
```bash
# Démarrer le serveur backend
cd backend
python app.py

# Le serveur démarre sur http://localhost:5000
# Message affiché :
# "Starting server on http://localhost:5000"
```

Ensuite, ouvrez `frontend/index.html` dans votre navigateur.

**URLs importantes :**
- Interface principale : `frontend/index.html`
- API Swagger : `http://localhost:5000/api/docs`
- API Health Check : `http://localhost:5000/api/health`

## 🔌 API REST

### Endpoints disponibles

#### 1. Health Check
```http
GET /api/health
```
Vérifie que l'API fonctionne.

**Réponse :**
```json
{
  "status": "ok",
  "timestamp": "2025-01-21T14:30:00",
  "service": "Railway Track Monitoring API"
}
```

---

#### 2. Upload et analyse d'image
```http
POST /api/upload
Content-Type: multipart/form-data
```
Upload une image pour détection automatique d'anomalies.

**Body :** `image` (file, JPG/PNG, max 10MB)

**Réponse (201 Created) :**
```json
{
  "success": true,
  "inspection": {
    "id": 1,
    "filename": "20250121_143000_rail.jpg",
    "original_filename": "rail.jpg",
    "upload_date": "2025-01-21T14:30:00",
    "status": "completed",
    "anomalies_count": 15,
    "criticality_score": 0.52,
    "criticality_level": "medium",
    "processing_time": 0.234,
    "notes": "WARNING: 15 anomalies detected. Schedule inspection soon."
  },
  "message": "Image analyzed successfully"
}
```

---

#### 3. Liste des inspections
```http
GET /api/inspections?limit=50
```

**Paramètres query (optionnels) :**
- `limit` : Nombre maximum d'inspections (défaut: 100, max: 500)

**Réponse :**
```json
{
  "success": true,
  "count": 42,
  "inspections": [...]
}
```

---

#### 4. Détail d'une inspection
```http
GET /api/inspections/{id}
```

**Réponse :**
```json
{
  "success": true,
  "inspection": {
    "id": 1,
    "filename": "20250121_143000_rail.jpg",
    ...
  }
}
```

---

#### 5. Suppression d'une inspection
```http
DELETE /api/inspections/{id}
```

Supprime l'inspection et ses fichiers associés (original + annoté).

**Réponse :**
```json
{
  "success": true,
  "message": "Inspection deleted successfully",
  "id": 1
}
```

---

#### 6. Statistiques globales
```http
GET /api/stats
```

**Réponse :**
```json
{
  "success": true,
  "statistics": {
    "total_inspections": 42,
    "criticality_distribution": {
      "high": 8,
      "medium": 19,
      "low": 15
    },
    "average_anomalies": 18.5
  }
}
```

---

#### 7. Recherche par nom de fichier
```http
GET /api/search?q=rail&limit=50
```

**Paramètres query :**
- `q` : Terme de recherche (requis)
- `limit` : Nombre max de résultats (optionnel)

**Réponse :**
```json
{
  "success": true,
  "query": "rail",
  "count": 12,
  "inspections": [...]
}
```

---

#### 7. Export CSV
```http
GET /api/export/csv
```

Télécharge toutes les inspections au format CSV.

**Headers de réponse :**
```
Content-Type: text/csv
Content-Disposition: attachment; filename=inspections_20250121_143000.csv
```

---

### Documentation interactive Swagger

Accédez à `http://localhost:5000/api/docs` pour :
- Voir tous les endpoints documentés
- Tester les requêtes directement dans le navigateur
- Consulter les schémas de réponse détaillés

## 🧪 Tests et validation

### Générer des images de test
```bash
cd backend
python create_test_images.py
```

Crée 3 images dans `samples/` avec différents niveaux de criticité :
- `rail_low_criticality.jpg` → 1-2 anomalies
- `rail_medium_criticality.jpg` → 5-8 anomalies
- `rail_high_criticality.jpg` → 20+ anomalies

### Tester l'API avec curl
```bash
# Health check
curl http://localhost:5000/api/health

# Upload d'image
curl -X POST -F "image=@samples/rail_low_criticality.jpg" \
  http://localhost:5000/api/upload

# Récupérer les statistiques
curl http://localhost:5000/api/stats

# Export CSV
curl http://localhost:5000/api/export/csv -o inspections.csv
```

### Tester le frontend

1. Ouvrez `frontend/index.html`
2. Glissez-déposez une image dans la zone d'upload
3. Vérifiez que l'analyse se lance automatiquement
4. Testez les filtres (Toutes / Haute / Moyenne / Basse)
5. Cliquez sur une inspection pour voir ses détails
6. Testez la suppression avec confirmation
7. Exportez en CSV

## 🎓 Concepts techniques employés

### Architecture et design patterns
- ✅ Architecture REST propre avec séparation des responsabilités
- ✅ Pattern MVC (Models-Views-Controllers)
- ✅ Gestion d'exceptions centralisée avec classes custom
- ✅ Validation des inputs avec validateurs dédiés
- ✅ Event delegation pour gestion événements frontend

### Backend avancé
- ✅ Traitement d'images avec OpenCV (Canny Edge Detection)
- ✅ Gestion sécurisée des uploads (validation, secure_filename)
- ✅ ORM-like pattern pour SQLite avec méthodes CRUD
- ✅ API REST avec documentation Swagger automatique
- ✅ Gestion d'erreurs robuste (try-except, logging)
- ✅ Export de données (CSV)

### Frontend moderne
- ✅ Interface responsive (mobile-first)
- ✅ Drag & drop natif HTML5
- ✅ Communication asynchrone (Fetch API, async/await)
- ✅ Gestion d'état JavaScript
- ✅ Pagination côté client
- ✅ Mise à jour dynamique du DOM
- ✅ Modal de confirmation
- ✅ Feedback visuel (messages de succès, animations)

### Qualité du code
- ✅ Type hints Python
- ✅ Docstrings détaillées (Google style)
- ✅ Code commenté et auto-documenté
- ✅ Commits Git atomiques et bien nommés
- ✅ README complet avec exemples
- ✅ Gestion des cas d'erreur exhaustive
- ✅ Validation des inputs systématique

## 📈 Perspectives d'amélioration

### Court terme (1-2 semaines)
- [ ] Authentification utilisateur (JWT)
- [ ] Géolocalisation GPS des inspections
- [ ] Carte interactive (Leaflet.js)
- [ ] Notifications email pour criticité haute
- [ ] Workflow de résolution d'incidents (statuts)
- [ ] Export PDF des rapports avec images

### Moyen terme (1-3 mois)
- [ ] Modèle de Machine Learning (CNN) pour détection plus précise
- [ ] Fine-tuning sur dataset labellisé de défauts ferroviaires
- [ ] API temps réel avec WebSockets
- [ ] Migration PostgreSQL pour scalabilité
- [ ] Application mobile (React Native)
- [ ] Containerisation Docker + Kubernetes
- [ ] CI/CD avec GitHub Actions

### Long terme (6+ mois)
- [ ] Analyse vidéo en temps réel (streaming)
- [ ] Maintenance prédictive avec ML
- [ ] Intégration systèmes SCADA ferroviaires
- [ ] Déploiement edge computing sur drones d'inspection
- [ ] Multi-tenancy pour plusieurs opérateurs ferroviaires
- [ ] Tableau de bord analytics avancé

## 🎯 Cas d'usage et applications

Ce système peut être adapté à de nombreux secteurs critiques :

### Infrastructure
- **Ferroviaire** : Voies, caténaires, signalisation
- **Aéroports** : Pistes d'atterrissage, détection FOD
- **Ponts & ouvrages** : Fissures béton, corrosion métal
- **Routes** : Nids-de-poule, dégradations

### Industrie
- **Automobile** : Contrôle qualité peinture/soudure
- **Textile** : Détection défauts tissus
- **Papier** : Détection taches/trous

### Énergie
- **Panneaux solaires** : Cellules cassées, salissures
- **Éoliennes** : Fissures pales, érosion
- **Pipelines** : Corrosion, fuites

### Autres
- **Agriculture** : Maladies cultures (drones)
- **Médical** : Aide au diagnostic (radiographies)
- **Smart City** : Surveillance infrastructures urbaines

## 🔒 Sécurité

### Mesures implémentées
- ✅ Validation stricte des fichiers (extension, taille)
- ✅ `secure_filename()` contre injections de noms
- ✅ Limite de taille (10MB)
- ✅ CORS configuré
- ✅ Gestion d'erreurs sans fuite d'informations sensibles
- ✅ SQLite avec paramètres bindés (protection SQL injection)

### À ajouter en production
- [ ] Authentification JWT
- [ ] Rate limiting (limite requêtes/IP)
- [ ] HTTPS obligatoire
- [ ] Scanning antivirus des uploads
- [ ] Audit logs
- [ ] Secrets management (variables d'environnement)

## 📊 Performance

- **Temps d'analyse moyen :** 0.2-0.5s par image
- **Taille images supportées :** Jusqu'à 10MB
- **Formats supportés :** JPG, PNG
- **Base de données :** SQLite (adapté jusqu'à 100k inspections)
- **API :** Synchrone (adapté pour usage ponctuel)

**Pour scaling :**
- Celery + Redis pour traitement asynchrone
- PostgreSQL avec indexation
- Cache avec Redis
- CDN pour images
- Load balancing

## 👤 Auteur

**TCHAMGOUE Adrienne**
- GitHub: [@Tchamgoue](https://github.com/Tchamgoue)
- LinkedIn: [Adrienne Louise Tchamgoue](https://linkedin.com/in/adrienne-kameni)



**Développé avec 💙 pour ISKernel - Janvier 2025**

*Ce projet démontre ma capacité à créer rapidement des applications critiques fonctionnelles, propres et évolutives.*
```
