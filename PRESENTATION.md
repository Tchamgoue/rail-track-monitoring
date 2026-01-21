# Présentation Railway Track Monitor
## Système de surveillance ferroviaire avec OpenCV

---

## Slide 1 : Page de titre

**Railway Track Monitor**
*Système de détection d'anomalies sur voies ferrées*

TCHAMGOUE KAMENI Adrienne
Janvier 2025



---

## SLIDE 2 : Contexte et problématique

### Le défi
- **Sécurité ferroviaire** = priorité absolue pour ISKernel
- **Inspection manuelle** = coûteuse, chronophage, incomplète
- **Détection précoce** = prévention d'incidents graves

### Solution proposée
Système automatisé d'analyse d'images de voies ferrées utilisant le traitement d'image et OpenCV

### Alignement avec ISKernel
✅ Applications critiques (ferroviaire)  
✅ Performance et fiabilité (< 0.5s/analyse)  
✅ Stack technique (OpenCV mentionné dans l'offre)  
✅ Innovation technique (base pour ML)  

---

## SLIDE 3 : Architecture technique
```
Composants:

┌─────────────┐
│  Frontend   │ → HTML/CSS/JS responsive
│  (Interface)│    Drag & drop, dashboard
└──────┬──────┘
       │ HTTP REST
┌──────▼────────────┐
│  API Flask (7 EP) │ → CRUD + Upload + Stats
│  + Swagger        │    + Search + Export
└──────┬────────────┘
       │
   ┌───▼────┬─────────┬──────────┐
   │        │         │          │
┌──▼───┐ ┌─▼────┐ ┌──▼──────┐ ┌─▼─────┐
│SQLite│ │OpenCV│ │Validators│ │Export │
│ ORM  │ │Canny │ │Exceptions│ │  CSV  │
└──────┘ └──────┘ └──────────┘ └───────┘
```

**Stack :**
- Backend : Python 3.12, Flask 3.0, OpenCV 4.8, SQLite
- Frontend : Vanilla JS (ES6+), HTML5, CSS3
- Algorithme : Canny Edge Detection (standard industrie)

---

## Slide 4 : Algorithme de détection

### Pipeline de traitement (5 étapes)

1. **Grayscale** → Conversion niveaux de gris
2. **Blur** → Réduction du bruit (Gaussien)
3. **Canny** → Détection de contours
4. **Contours** → Extraction des formes
5. **Filtrage** → Anomalies significatives (>500px²)

**Temps de traitement moyen :** 0.2-0.5 secondes

**Pourquoi Canny ?**
- Standard industrie depuis 1986
- Excellent rapport précision/performance
- Base idéale pour évolution ML

---

## Slide 5 : Scoring de criticité

### Barème intelligent

| Anomalies | Score | Niveau | Action |
|-----------|-------|--------|--------|
| 0-10 | 0.05-0.35 | 🟢 LOW | Surveillance normale |
| 11-30 | 0.40-0.70 | 🟡 MEDIUM | Inspection programmée |
| 31+ | 0.71-1.00 | 🔴 HIGH | Intervention urgente |

**Calibré pour contexte opérationnel réel**
- Adapté aux textures naturelles (ballast, rails)
- Progression non-linéaire du risque
- Seuils basés sur logique métier ferroviaire

---

## Slide 6 : Fonctionnalités développées

### MVP Fonctionnel (2 jours)

✅ **Upload intelligent**
- Drag & drop
- Validation format/taille
- Analyse automatique

✅ **Dashboard temps réel**
- Statistiques globales
- Distribution criticité
- Métriques clés

✅ **Historique complet**
- Toutes les inspections
- Filtres par criticité
- Pagination (10/page)

✅ **API REST documentée**
- 5 endpoints
- Gestion erreurs robuste
- Validation inputs

---

## Slide 7 : Démo technique

### Captures d'écran annotées

**1. Interface d'upload**
[Screenshot : Zone drag & drop]

**2. Résultats d'analyse**
[Screenshot : Image annotée + métadonnées]

**3. Dashboard statistiques**
[Screenshot : Cards statistiques]

**4. Historique filtrable**
[Screenshot : Liste avec pagination]

---

## Slide 8 : Qualité du code

### Bonnes pratiques implémentées

**Backend**
- Type hints Python
- Docstrings complètes
- Séparation des responsabilités (models/detector/api)
- Gestion d'erreurs exhaustive
- Logs structurés

**Frontend**
- Code ES6+ moderne
- Architecture modulaire
- Gestion d'état claire
- Interface responsive

**DevOps**
- Git avec commits atomiques
- Structure projet claire
- Documentation complète
- Code testé

---

## Slide 9 : Perspectives d'évolution

### Court terme (1-2 semaines)
- Carte interactive avec géolocalisation (Leaflet.js)
- Workflow de résolution d'incidents
- Export PDF des rapports
- Notifications email

### Moyen terme (1-3 mois)
- Modèle ML (CNN) pour détection avancée
- API temps réel (WebSockets)
- Migration PostgreSQL
- Application mobile

### Long terme (6+ mois)
- Analyse vidéo temps réel
- Maintenance prédictive (ML)
- Intégration SCADA
- Déploiement edge (drones)

---

## Slide 10 : Compétences démontrées

### Alignement avec ISKernel

**Technique**
- ✅ Python (Flask, OpenCV, NumPy)
- ✅ JavaScript ES6+ (Vanilla, pas de framework lourd)
- ✅ API REST robuste
- ✅ Traitement d'images
- ✅ Base de données

**Soft Skills**
- ✅ Autonomie (projet complet en 2 jours)
- ✅ Rigueur (code propre, documenté)
- ✅ Vision produit (MVP + roadmap)
- ✅ Apprentissage rapide (OpenCV maîtrisé)

**Valeurs ISKernel**
- Applications critiques (ferroviaire)
- Performance (< 0.5s/analyse)
- Fiabilité (validation, gestion erreurs)

---

## Slide 11 : Difficultés rencontrées et solutions

### Challenge 1 : Calibrage de l'algorithme
**Problème :** Images réelles → trop de contours détectés
**Solution :** Ajustement des seuils + recalibrage du scoring

### Challenge 2 : Gestion des chemins fichiers
**Problème :** `replace('.')` cassait les chemins avec `../`
**Solution :** Utilisation de `os.path.splitext()`

### Challenge 3 : Scores toujours élevés
**Problème :** Ballast = beaucoup de textures
**Solution :** Nouveau barème adapté au contexte opérationnel

**Apprentissage :** Importance de tester avec données réelles !

---

## Slide 12 : Démo live

### Démonstration en direct

1. Upload d'une image de test
2. Analyse en temps réel
3. Affichage des résultats
4. Navigation dans l'historique
5. Utilisation des filtres

**Questions / Discussion technique**

---

## Slide 13 : Conclusion

### Réalisations

✅ Application FullStack complète et fonctionnelle
✅ Algorithme OpenCV opérationnel
✅ Interface moderne et intuitive
✅ Code production-ready
✅ Documentation exhaustive



**Merci pour votre attention !**

Questions ?

---

## Slide 14 : Annexes (Backup slides)

### Code samples
### Architecture détaillée
### Métriques de performance
### Roadmap technique détaillée
