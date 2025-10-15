// API Base URL
const API_URL = '/api/people';

// DOM Elements
const peopleGrid = document.getElementById('peopleGrid');
const emptyState = document.getElementById('emptyState');
const searchInput = document.getElementById('searchInput');
const addPersonBtn = document.getElementById('addPersonBtn');
const personModal = document.getElementById('personModal');
const personForm = document.getElementById('personForm');
const modalTitle = document.getElementById('modalTitle');
const closeBtn = document.querySelector('.close');
const cancelBtn = document.getElementById('cancelBtn');

// State
let allPeople = [];
let isEditing = false;
let currentEditId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadPeople();
    setupEventListeners();
});

// Setup Event Listeners
function setupEventListeners() {
    addPersonBtn.addEventListener('click', () => openModal());
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    personForm.addEventListener('submit', handleSubmit);
    searchInput.addEventListener('input', handleSearch);
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === personModal) {
            closeModal();
        }
    });
}

// Load all people
async function loadPeople() {
    try {
        const response = await fetch(API_URL);
        allPeople = await response.json();
        renderPeople(allPeople);
    } catch (error) {
        console.error('Error loading people:', error);
        showError('Failed to load people');
    }
}

// Render people cards
function renderPeople(people) {
    if (people.length === 0) {
        peopleGrid.style.display = 'none';
        emptyState.style.display = 'block';
        return;
    }

    peopleGrid.style.display = 'grid';
    emptyState.style.display = 'none';

    peopleGrid.innerHTML = people.map(person => `
        <div class="person-card" data-id="${person.id}">
            <div class="person-header" onclick="toggleDetails('${person.id}')">
                <div class="person-info">
                    <h3 class="person-name">${person.name}</h3>
                    <div class="person-meta">Added ${formatDate(person.createdAt)}</div>
                </div>
                <div class="toggle-icon">▼</div>
            </div>
            
            <div class="person-details-content" id="details-${person.id}" style="display: none;">
                ${person.details ? `
                    <div class="person-details">${person.details}</div>
                ` : '<div class="no-details">No details available</div>'}
            </div>
            
            <div class="person-actions">
                <button class="btn btn-edit" onclick="editPerson('${person.id}')">Edit</button>
                <button class="btn btn-danger" onclick="deletePerson('${person.id}')">Delete</button>
            </div>
        </div>
    `).join('');
}

// Handle search
async function handleSearch(e) {
    const query = e.target.value.trim();
    
    if (query === '') {
        renderPeople(allPeople);
        return;
    }

    try {
        const response = await fetch(`${API_URL}/search/${encodeURIComponent(query)}`);
        const results = await response.json();
        renderPeople(results);
    } catch (error) {
        console.error('Error searching:', error);
    }
}

// Toggle person details
function toggleDetails(id) {
    const detailsDiv = document.getElementById(`details-${id}`);
    const card = document.querySelector(`[data-id="${id}"]`);
    const toggleIcon = card.querySelector('.toggle-icon');
    
    if (detailsDiv.style.display === 'none') {
        detailsDiv.style.display = 'block';
        toggleIcon.textContent = '▲';
    } else {
        detailsDiv.style.display = 'none';
        toggleIcon.textContent = '▼';
    }
}

// Open modal
function openModal(person = null) {
    isEditing = !!person;
    currentEditId = person ? person.id : null;
    
    modalTitle.textContent = isEditing ? 'Edit Person' : 'Add New Person';
    
    if (person) {
        document.getElementById('personId').value = person.id;
        document.getElementById('personName').value = person.name;
        document.getElementById('personDetails').value = person.details || '';
    } else {
        personForm.reset();
    }
    
    personModal.style.display = 'block';
}

// Close modal
function closeModal() {
    personModal.style.display = 'none';
    personForm.reset();
    isEditing = false;
    currentEditId = null;
}

// Handle form submit
async function handleSubmit(e) {
    e.preventDefault();
    
    const personData = {
        name: document.getElementById('personName').value,
        details: document.getElementById('personDetails').value
    };

    try {
        let response;
        if (isEditing) {
            response = await fetch(`${API_URL}/${currentEditId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(personData)
            });
        } else {
            response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(personData)
            });
        }

        if (response.ok) {
            closeModal();
            loadPeople();
            showSuccess(isEditing ? 'Person updated successfully!' : 'Person added successfully!');
        } else {
            const error = await response.json();
            showError(error.error || 'Failed to save person');
        }
    } catch (error) {
        console.error('Error saving person:', error);
        showError('Failed to save person');
    }
}

// Edit person
async function editPerson(id) {
    try {
        const response = await fetch(`${API_URL}/${id}`);
        const person = await response.json();
        openModal(person);
    } catch (error) {
        console.error('Error loading person:', error);
        showError('Failed to load person details');
    }
}

// Delete person
async function deletePerson(id) {
    if (!confirm('Are you sure you want to delete this person?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadPeople();
            showSuccess('Person deleted successfully!');
        } else {
            showError('Failed to delete person');
        }
    } catch (error) {
        console.error('Error deleting person:', error);
        showError('Failed to delete person');
    }
}

// Utility: Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
        return 'today';
    } else if (diffDays === 1) {
        return 'yesterday';
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else {
        return date.toLocaleDateString();
    }
}

// Show success message
function showSuccess(message) {
    // Simple alert for now - can be replaced with a toast notification
    alert(message);
}

// Show error message
function showError(message) {
    alert('Error: ' + message);
}

