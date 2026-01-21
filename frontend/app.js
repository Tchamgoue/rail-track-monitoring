// Configuration API
const API_URL = 'http://localhost:5000/api';

// État de l'application
let currentFilter = 'all';
let allInspections = [];
let currentPage = 1;
const itemsPerPage = 10;
let selectedInspectionId = null;

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

    // Suppression d'une inspection
    document.getElementById('delete-btn').addEventListener('click', handleDeleteClick);
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
    // Stockage de l'ID de l'inspection affichée
    selectedInspectionId = inspection.id;
    
    // Mise à jour du titre
    document.getElementById('result-title').textContent = 
        inspection.id ? `Inspection #${inspection.id}` : 'Résultats de l\'analyse';
    
    // Affichage du bouton suppression si c'est une inspection existante
    const deleteBtn = document.getElementById('delete-btn');
    deleteBtn.style.display = inspection.id ? 'block' : 'none';
    
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
        <div class="inspection-card level-${insp.criticality_level} ${selectedInspectionId === insp.id ? 'selected' : ''}" 
            onclick="showInspectionDetail(${insp.id})">
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

// Afficher le détail d'une inspection
async function showInspectionDetail(inspectionId) {
    try {
        const response = await fetch(`${API_URL}/inspections/${inspectionId}`);
        
        if (!response.ok) {
            throw new Error('Inspection non trouvée');
        }
        
        const data = await response.json();
        displayResult(data.inspection);
        
        // Mettre à jour la sélection visuelle dans le DOM
        document.querySelectorAll('.inspection-card').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Trouver la carte cliquée par son data-id
        const clickedCard = document.querySelector(`.inspection-card[data-id="${inspectionId}"]`);
        if (clickedCard) {
            clickedCard.classList.add('selected');
        }
        
    } catch (error) {
        console.error('[ERROR] Failed to load inspection:', error);
        alert('Erreur lors du chargement de l\'inspection');
    }
}

// Gestion du clic sur suppression
function handleDeleteClick() {
    if (!selectedInspectionId) {
        alert('Aucune inspection sélectionnée');
        return;
    }
    
    showDeleteConfirmation(selectedInspectionId);
}

// Modal de confirmation de suppression
function showDeleteConfirmation(inspectionId) {
    // Créer la modal
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>⚠️ Confirmer la suppression</h3>
            <p>Êtes-vous sûr de vouloir supprimer cette inspection ? Cette action est irréversible.</p>
            <div class="modal-actions">
                <button class="modal-btn cancel" onclick="closeDeleteModal()">Annuler</button>
                <button class="modal-btn confirm" onclick="confirmDelete(${inspectionId})">Supprimer</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Fermer avec clic sur overlay
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeDeleteModal();
        }
    });
}

// Fermer la modal
function closeDeleteModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.remove();
    }
}

// Confirmer et exécuter la suppression
async function confirmDelete(inspectionId) {
    try {
        const response = await fetch(`${API_URL}/inspections/${inspectionId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Erreur lors de la suppression');
        }
        
        const data = await response.json();
        console.log('[INFO] Inspection deleted:', data);
        
        // Fermer la modal
        closeDeleteModal();
        
        // Masquer la zone de résultat
        resultContainer.style.display = 'none';
        selectedInspectionId = null;
        
        // Recharger les données
        await loadStats();
        await loadInspections();
        
        // Message de succès
        showSuccessMessage('Inspection supprimée avec succès');
        
    } catch (error) {
        console.error('[ERROR] Failed to delete inspection:', error);
        alert('Erreur lors de la suppression de l\'inspection');
        closeDeleteModal();
    }
}

// Message de succès temporaire
function showSuccessMessage(message) {
    const successDiv = document.createElement('div');
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: var(--success);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 2000;
        font-weight: 500;
        animation: slideIn 0.3s ease-out;
    `;
    successDiv.textContent = `✓ ${message}`;
    
    document.body.appendChild(successDiv);
    
    setTimeout(() => {
        successDiv.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => successDiv.remove(), 300);
    }, 3000);
}

function exportToCSV() {
    window.open(`${API_URL}/export/csv`, '_blank');
    showSuccessMessage('Export CSV en cours...');
}

// Ajouter les animations CSS (si pas déjà dans le CSS)
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);