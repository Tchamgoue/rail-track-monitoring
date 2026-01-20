# 🚂 Railway Track Monitor

Système de détection d'anomalies sur voies ferrées utilisant OpenCV et Flask.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-red)

## 📋 Description

Application FullStack de monitoring ferroviaire permettant de détecter automatiquement des anomalies (fissures, défauts) sur des images de voies ferrées à l'aide de traitement d'image par OpenCV.

### Fonctionnalités principales

- ✅ Upload et analyse d'images de voies ferrées
- ✅ Détection automatique d'anomalies avec OpenCV (algorithme Canny)
- ✅ Scoring de criticité (LOW / MEDIUM / HIGH)
- ✅ Dashboard avec statistiques en temps réel
- ✅ Historique complet des inspections avec filtres
- ✅ API REST documentée
- ✅ Interface moderne avec drag & drop

## 🏗️ Architecture
```
rail-track-monitor/
│
├── backend/                    # API Flask + logique métier
│   ├── app.py                 # API REST (5 endpoints)
│   ├── models.py              # Modèles de données SQLite
│   ├── detector.py            # Algorithme OpenCV
│   ├── uploads/               # Images uploadées
│   └── requirements.txt       # Dépendances Python
│
├── frontend/                   # Interface utilisateur
│   ├── index.html             # Structure HTML
│   ├── style.css              # Styles modernes
│   └── app.js                 # Logique JavaScript
│
├── database/                   # Base de données
│   └── inspections.db         # SQLite
│
├── samples/                    # Images de test
│
└── README.md
```

## 🛠️ Stack Technique

### Backend
- **Python 3.12** - Langage principal
- **Flask 3.0** - Framework web REST
- **OpenCV 4.8** - Traitement d'images
- **SQLite** - Base de données
- **NumPy** - Calculs matriciels

### Frontend
- **HTML5 / CSS3** - Structure et styles
- **JavaScript ES6+** - Logique côté client
- **Fetch API** - Communication avec l'API

### Algorithme de détection
1. **Conversion en niveaux de gris** - Simplifie l'analyse
2. **Flou gaussien** - Réduit le bruit
3. **Détection de contours (Canny)** - Identifie les discontinuités
4. **Filtrage** - Garde uniquement les anomalies significatives (>500px²)
5. **Scoring** - Calcul de criticité 0-1

## 📊 Barème de criticité

| Anomalies détectées | Score | Niveau | Action recommandée |
|---------------------|-------|--------|-------------------|
| 0-10 | 0.05-0.35 | LOW | Surveillance normale |
| 11-30 | 0.40-0.70 | MEDIUM | Inspection programmée |
| 31+ | 0.71-1.00 | HIGH | Intervention urgente |

## 🚀 Installation et lancement

### Prérequis
- Python 3.12+
- Git

### Installation
```bash
# Cloner le repository
git clone https://github.com/YOUR_USERNAME/rail-track-monitoring.git
cd rail-track-monitoring

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows Git Bash)
source venv/Scripts/activate

# Installer les dépendances
pip install -r backend/requirements.txt
```

### Lancement
```bash
# Démarrer le serveur backend
cd backend
python app.py

# Le serveur démarre sur http://localhost:5000
```

Ensuite, ouvrez `frontend/index.html` dans votre navigateur.

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
  "timestamp": "2025-01-20T14:30:00",
  "service": "Railway Track Monitoring API"
}
```

#### 2. Upload et analyse
```http
POST /api/upload
Content-Type: multipart/form-data
```
Upload une image pour analyse.

**Body :** `image` (file)

**Réponse :**
```json
{
  "success": true,
  "inspection": {
    "id": 1,
    "filename": "20250120_143000_rail.jpg",
    "anomalies_count": 15,
    "criticality_score": 0.52,
    "criticality_level": "medium",
    "processing_time": 0.234,
    "notes": "WARNING: 15 anomalies detected. Schedule inspection soon."
  }
}
```

#### 3. Liste des inspections
```http
GET /api/inspections?limit=50
```

#### 4. Détail d'une inspection
```http
GET /api/inspections/{id}
```

#### 5. Statistiques globales
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

## 🧪 Tests

### Générer des images de test
```bash
cd backend
python create_test_images.py
```

Crée 3 images avec différents niveaux de criticité dans `samples/`.

### Tester l'API avec curl
```bash
# Health check
curl http://localhost:5000/api/health

# Upload
curl -X POST -F "image=@samples/rail_low_criticality.jpg" \
  http://localhost:5000/api/upload

# Stats
curl http://localhost:5000/api/stats
```

## 📈 Perspectives d'amélioration

### Court terme
- [ ] Authentification utilisateur (JWT)
- [ ] Export des rapports en PDF
- [ ] Notifications par email pour criticité haute
- [ ] Géolocalisation des inspections sur carte interactive

### Moyen terme
- [ ] Modèle de Machine Learning (CNN) pour détection plus précise
- [ ] API temps réel avec WebSockets
- [ ] Application mobile (React Native)
- [ ] Intégration base de données PostgreSQL

### Long terme
- [ ] Analyse vidéo en temps réel
- [ ] Prédiction de maintenance (ML)
- [ ] Intégration avec systèmes SCADA ferroviaires
- [ ] Déploiement edge computing sur drones d'inspection

## 🎓 Concepts techniques démontrés

### Backend
- Architecture REST propre
- Traitement d'images avec OpenCV
- Gestion de fichiers et uploads sécurisés
- Base de données relationnelle (SQLite/ORM)
- Gestion d'erreurs robuste
- Validation des inputs

### Frontend
- Interface responsive moderne
- Drag & drop natif
- Communication asynchrone (Fetch API)
- Gestion d'état JavaScript
- Pagination côté client
- Mise à jour dynamique du DOM

### Qualité du code
- Type hints Python
- Docstrings détaillées
- Séparation des responsabilités (MVC)
- Gestion d'erreurs exhaustive
- Code commenté et documenté
- Commits Git atomiques

## 👤 Auteur

**[Adrienne Louise TCHAMGOUE KAMENI]**
- GitHub: [@Tchamgoue](https://github.com/Tchamgoue)
- LinkedIn: [Adrienne Louise TCHAMGOUE](https://linkedin.com/in/adrienne-kameni)

## 📄 Licence

Ce projet est un projet de démonstration technique créé dans le cadre d'un entretien.

---

**Développé avec 💙 pour ISKernel**