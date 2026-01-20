// Configuration API
const API_URL = 'http://localhost:5000/api';

// État de l'application
let currentFilter = 'all';
let allInspections = [];
let currentPage = 1;
const itemsPerPage = 10;

// Éléments DOM
const uploadZone = document.getElementById('upload-zone');
const fileInput = document.getElementById('file-input');
const progressContainer = document.getElementById('progress-container');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const resultContainer = document.getElementById('result-container');

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    console.log('[INFO] Application initialized');
    setupEventListeners();
    loadStats();
    loadInspections();
});

// Configuration des événements
function setupEventListeners() {
    // Click sur la zone d'upload
    uploadZone.addEventListener('click', () => fileInput.click());
    
    // Sélection de fichier
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag & drop
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleDrop);
    
    // Filtres
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', handleFilterClick);
    });
}

// Gestion drag & drop
function handleDragOver(e) {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// Sélection de fichier
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

// Upload et analyse
async function handleFile(file) {
    // Validation
    if (!file.type.match('image/(jpeg|jpg|png)')) {
        alert('Format non supporté. Utilisez JPG ou PNG.');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        alert('Fichier trop volumineux (max 10MB)');
        return;
    }
    
    // Affichage de la progression
    resultContainer.style.display = 'none';
    progressContainer.style.display = 'block';
    progressFill.style.width = '30%';
    progressText.textContent = 'Upload en cours...';
    
    // Préparation FormData
    const formData = new FormData();
    formData.append('image', file);
    
    try {
        // Upload
        progressFill.style.width = '60%';
        progressText.textContent = 'Analyse en cours...';
        
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Progression complète
        progressFill.style.width = '100%';
        progressText.textContent = 'Analyse terminée !';
        
        // Affichage des résultats
        setTimeout(() => {
            displayResult(data.inspection);
            progressContainer.style.display = 'none';
            progressFill.style.width = '0%';
            
            // Rafraîchir les stats et la liste
            loadStats();
            loadInspections();
        }, 500);
        
    } catch (error) {
        console.error('[ERROR] Upload failed:', error);
        alert('Erreur lors de l\'analyse. Vérifiez que le serveur est démarré.');
        progressContainer.style.display = 'none';
        progressFill.style.width = '0%';
    }
    
    // Reset input
    fileInput.value = '';
}

// Affichage du résultat
function displayResult(inspection) {
    document.getElementById('result-anomalies').textContent = inspection.anomalies_count;
    document.getElementById('result-score').textContent = inspection.criticality_score;
    
    const levelBadge = document.getElementById('result-level');
    levelBadge.textContent = inspection.criticality_level.toUpperCase();
    levelBadge.className = `info-value inspection-badge badge-${inspection.criticality_level}`;
    
    document.getElementById('result-time').textContent = `${inspection.processing_time}s`;
    document.getElementById('result-notes').textContent = inspection.notes;
    
    // Image annotée
    const annotatedFilename = inspection.filename.replace(/\.(\w+)$/, '_annotated.$1');
    document.getElementById('result-image').src = `http://localhost:5000/uploads/${annotatedFilename}`;
    
    resultContainer.style.display = 'block';
    resultContainer.scrollIntoView({ behavior: 'smooth' });
}

// Chargement des statistiques
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const data = await response.json();
        
        const stats = data.statistics;
        document.getElementById('total-inspections').textContent = stats.total_inspections;
        document.getElementById('critical-count').textContent = stats.criticality_distribution.high;
        document.getElementById('warning-count').textContent = stats.criticality_distribution.medium;
        document.getElementById('safe-count').textContent = stats.criticality_distribution.low;
        
    } catch (error) {
        console.error('[ERROR] Failed to load stats:', error);
    }
}

// Chargement des inspections
async function loadInspections() {
    try {
        const response = await fetch(`${API_URL}/inspections?limit=50`);
        const data = await response.json();
        
        allInspections = data.inspections;
        displayInspections();
        
    } catch (error) {
        console.error('[ERROR] Failed to load inspections:', error);
    }
}

// Affichage des inspections avec pagination
function displayInspections() {
    const container = document.getElementById('inspections-list');
    
    // Filtrage
    let filtered = allInspections;
    if (currentFilter !== 'all') {
        filtered = allInspections.filter(insp => insp.criticality_level === currentFilter);
    }
    
    // Pagination
    const totalPages = Math.ceil(filtered.length / itemsPerPage);
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedInspections = filtered.slice(startIndex, endIndex);
    
    // Affichage
    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                <p>Aucune inspection trouvée</p>
            </div>
        `;
        return;
    }
    
    // Cartes d'inspections
    const cardsHTML = paginatedInspections.map(insp => `
        <div class="inspection-card level-${insp.criticality_level}">
            <img src="http://localhost:5000/uploads/${insp.filename.replace(/\.(\w+)$/, '_annotated.$1')}" 
                 alt="Inspection" 
                 class="inspection-thumbnail"
                 onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'%3E%3Crect fill=\'%23ddd\' width=\'100\' height=\'100\'/%3E%3C/svg%3E'">
            
            <div class="inspection-info">
                <h4>${insp.original_filename}</h4>
                <div class="inspection-meta">
                    <span>${new Date(insp.upload_date).toLocaleString('fr-FR')}</span>
                    <span>${insp.anomalies_count} anomalie(s)</span>
                    <span>Score: ${insp.criticality_score}</span>
                </div>
            </div>
            
            <span class="inspection-badge badge-${insp.criticality_level}">
                ${insp.criticality_level.toUpperCase()}
            </span>
        </div>
    `).join('');
    
    // Pagination controls
    const paginationHTML = totalPages > 1 ? `
        <div class="pagination">
            <button class="page-btn" onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>
                ← Précédent
            </button>
            <span class="page-info">Page ${currentPage} sur ${totalPages}</span>
            <button class="page-btn" onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>
                Suivant →
            </button>
        </div>
    ` : '';
    
    container.innerHTML = cardsHTML + paginationHTML;
}

// Changement de page
function changePage(page) {
    currentPage = page;
    displayInspections();
    document.querySelector('.inspections-section').scrollIntoView({ behavior: 'smooth' });
}

// Modification du handleFilterClick pour reset la pagination
function handleFilterClick(e) {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    e.target.classList.add('active');
    currentFilter = e.target.dataset.filter;
    currentPage = 1;  // Reset à la page 1
    displayInspections();
}

// Gestion des filtres
function handleFilterClick(e) {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    e.target.classList.add('active');
    currentFilter = e.target.dataset.filter;
    displayInspections();
}