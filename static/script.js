// API Base URL
const API_URL = '/api/people';
const ASK_API_URL = '/api/ask';

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

// Confirmation Modal Elements
const confirmModal = document.getElementById('confirmModal');
const confirmTitle = document.getElementById('confirmTitle');
const confirmMessage = document.getElementById('confirmMessage');
const confirmClose = document.getElementById('confirmClose');
const confirmCancel = document.getElementById('confirmCancel');
const confirmOk = document.getElementById('confirmOk');

// State
let allPeople = [];
let isEditing = false;
let isUpdating = false;
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
    
    // Confirmation modal listeners
    confirmClose.addEventListener('click', closeConfirmModal);
    confirmCancel.addEventListener('click', closeConfirmModal);
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === personModal) {
            closeModal();
        }
        if (e.target === confirmModal) {
            closeConfirmModal();
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
                
                <!-- AI Blueprint Section -->
                <div class="ai-summary-section" id="summary-section-${person.id}" style="display: none;">
                    <div class="ai-summary-header">
                        <span class="ai-badge">🧠 Person Blueprint</span>
                    </div>
                    <div class="ai-summary-content" id="summary-content-${person.id}"></div>
                </div>
            </div>
            
            <div class="person-actions">
                <button class="btn btn-edit" onclick="editPerson('${person.id}')">Edit</button>
                <button class="btn btn-update" onclick="updatePersonInfo('${person.id}')">Update</button>
                <button class="btn btn-ai btn-blueprint" onclick="generateAISummary('${person.id}')" id="ai-btn-${person.id}">
                    🧠 Blueprint
                </button>
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
        showError('Search failed. Please try again.');
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
function openModal(person = null, updateMode = false) {
    isEditing = !!person && !updateMode;
    isUpdating = updateMode;
    currentEditId = person ? person.id : null;
    
    if (updateMode) {
        modalTitle.textContent = 'Add Update';
    } else {
        modalTitle.textContent = isEditing ? 'Edit Person' : 'Add New Person';
    }
    
    if (person) {
        document.getElementById('personId').value = person.id;
        if (updateMode) {
            // Update mode: show name but clear details field for new info
            document.getElementById('personName').value = person.name;
            document.getElementById('personName').readOnly = true; // Don't allow name change in update mode
            document.getElementById('personDetails').value = '';
            document.getElementById('personDetails').placeholder = 'Add new information...';
        } else {
            // Edit mode: show existing data
            document.getElementById('personName').value = person.name;
            document.getElementById('personName').readOnly = false;
            document.getElementById('personDetails').value = person.details || '';
            document.getElementById('personDetails').placeholder = 'Add notes or details...';
        }
    } else {
        personForm.reset();
        document.getElementById('personName').readOnly = false;
        document.getElementById('personDetails').placeholder = 'Add notes or details...';
    }
    
    personModal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent body scroll
}

// Close modal
function closeModal() {
    personModal.style.display = 'none';
    personForm.reset();
    isEditing = false;
    isUpdating = false;
    currentEditId = null;
    document.getElementById('personName').readOnly = false;
    document.getElementById('personDetails').placeholder = 'Add notes or details...';
    document.body.style.overflow = ''; // Restore body scroll
}

// Custom confirm dialog
function showConfirm(message, title = 'Confirm Action') {
    return new Promise((resolve) => {
        confirmTitle.textContent = title;
        confirmMessage.textContent = message;
        confirmModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // Handle OK button click
        const handleOk = () => {
            cleanup();
            resolve(true);
        };
        
        // Handle cancel
        const handleCancel = () => {
            cleanup();
            resolve(false);
        };
        
        // Cleanup function
        const cleanup = () => {
            confirmOk.removeEventListener('click', handleOk);
            document.body.style.overflow = '';
            closeConfirmModal();
        };
        
        // Add event listener for OK button
        confirmOk.addEventListener('click', handleOk);
    });
}

// Close confirmation modal
function closeConfirmModal() {
    confirmModal.style.display = 'none';
    document.body.style.overflow = '';
}

// Handle form submit
async function handleSubmit(e) {
    e.preventDefault();
    
    const newDetails = document.getElementById('personDetails').value;
    const personData = {
        name: document.getElementById('personName').value,
        details: newDetails
    };

    try {
        let response;
        const timestamp = new Date().toLocaleString('en-US', { 
            month: 'short', 
            day: 'numeric', 
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        if (isUpdating) {
            // Update mode: Append new info to existing details
            const person = allPeople.find(p => p.id === currentEditId);
            
            // Append new info with timestamp
            const updatedDetails = person.details 
                ? `${person.details}\n\n--- Update (${timestamp}) ---\n${newDetails}`
                : `--- Update (${timestamp}) ---\n${newDetails}`;
            
            personData.details = updatedDetails;
            
            response = await fetch(`${API_URL}/${currentEditId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(personData)
            });
        } else if (isEditing) {
            // Edit mode: Keep the content as-is (user manually edits)
            // Just save whatever the user typed
            personData.details = newDetails;
            
            response = await fetch(`${API_URL}/${currentEditId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(personData)
            });
        } else {
            // Add new person with timestamp
            if (newDetails.trim()) {
                personData.details = `--- Added (${timestamp}) ---\n${newDetails}`;
            } else {
                personData.details = '';
            }
            
            response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(personData)
            });
        }

        if (response.ok) {
            closeModal();
            let successMsg;
            if (isUpdating) {
                successMsg = `${personData.name} - new update added!`;
            } else if (isEditing) {
                successMsg = `${personData.name} edited successfully!`;
            } else {
                successMsg = `${personData.name} added successfully!`;
            }
            showSuccess(successMsg);
            loadPeople();
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
        openModal(person, false); // false = edit mode
    } catch (error) {
        console.error('Error loading person:', error);
        showError('Failed to load person details');
    }
}

// Update person (add new info)
async function updatePersonInfo(id) {
    try {
        const response = await fetch(`${API_URL}/${id}`);
        const person = await response.json();
        openModal(person, true); // true = update mode
    } catch (error) {
        console.error('Error loading person:', error);
        showError('Failed to load person details');
    }
}

// Generate AI Summary
async function generateAISummary(id) {
    const summarySection = document.getElementById(`summary-section-${id}`);
    const summaryContent = document.getElementById(`summary-content-${id}`);
    const aiButton = document.getElementById(`ai-btn-${id}`);
    
    // Show loading state
    aiButton.disabled = true;
    aiButton.innerHTML = 'Generating...';
    summaryContent.innerHTML = '<div class="ai-loading">Generating summary...</div>';
    summarySection.style.display = 'block';
    
    try {
        const response = await fetch(`${API_URL}/${id}/summary`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const data = await response.json();
            summaryContent.innerHTML = `<div class="ai-summary-text">${data.summary}</div>`;
            aiButton.innerHTML = 'Refresh';
            showSuccess('Summary generated!');
        } else {
            const error = await response.json();
            summaryContent.innerHTML = `<div class="ai-error">${error.error || 'Failed to generate summary'}</div>`;
            aiButton.innerHTML = 'Summary';
            showError(error.error || 'Failed to generate summary');
        }
    } catch (error) {
        console.error('Error generating summary:', error);
        summaryContent.innerHTML = '<div class="ai-error">Failed to generate summary. Please try again.</div>';
        aiButton.innerHTML = 'Summary';
        showError('Failed to generate summary');
    } finally {
        aiButton.disabled = false;
    }
}

// Delete person
async function deletePerson(id) {
    // Get person name for toast message
    const person = allPeople.find(p => p.id === id);
    const personName = person ? person.name : 'Person';
    
    // Show custom confirmation dialog
    const confirmed = await showConfirm(
        `Are you sure you want to delete ${personName}?`,
        'Delete Person'
    );
    
    if (!confirmed) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadPeople();
            showSuccess(`${personName} deleted successfully!`);
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

// Toast notification system
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    
    // Safety check
    if (!toastContainer) {
        console.error('Toast container not found!');
        alert(message); // Fallback to alert
        return;
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    // Icon based on type
    const icon = type === 'success' ? '✓' : '✕';
    
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
        <button class="toast-close">×</button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Add click event to close button
    const closeButton = toast.querySelector('.toast-close');
    closeButton.addEventListener('click', function() {
        removeToast(toast);
    });
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        removeToast(toast);
    }, 3000);
}

// Remove toast with animation
function removeToast(toast) {
    // Check if toast still exists and isn't already being removed
    if (!toast || toast.classList.contains('hiding')) {
        return;
    }
    
    toast.classList.add('hiding');
    
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 300);
}

// Show success message
function showSuccess(message) {
    showToast(message, 'success');
}

// Show error message
function showError(message) {
    showToast(message, 'error');
}

// Central Q&A - Handle Enter key press
function handleCentralQuestionKeyPress(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        askCentralQuestion();
    }
}

// Central Q&A - Ask a question about any person
async function askCentralQuestion() {
    const questionInput = document.getElementById('centralQuestionInput');
    const question = questionInput.value.trim();
    const askButton = document.getElementById('centralAskBtn');
    const qaHistory = document.getElementById('centralQAHistory');
    
    if (!question) {
        showError('Please enter a question');
        return;
    }
    
    // Show history section if hidden
    qaHistory.style.display = 'block';
    
    // Show loading state
    askButton.disabled = true;
    askButton.innerHTML = '<span class="loading-spinner">⏳</span> Thinking...';
    
    // Add question to history immediately
    const qaItem = document.createElement('div');
    qaItem.className = 'central-qa-item';
    qaItem.innerHTML = `
        <div class="central-qa-question">
            <div class="qa-icon">❓</div>
            <div class="qa-text">${escapeHtml(question)}</div>
        </div>
        <div class="central-qa-answer">
            <div class="qa-icon">🤖</div>
            <div class="qa-text"><span class="ai-loading">Analyzing your contacts...</span></div>
        </div>
    `;
    qaHistory.insertBefore(qaItem, qaHistory.firstChild);
    
    // Clear input
    questionInput.value = '';
    
    try {
        const response = await fetch(ASK_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: question })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Update the answer in the history
            const answerText = qaItem.querySelector('.central-qa-answer .qa-text');
            answerText.innerHTML = escapeHtml(data.answer);
            
            // Scroll to top to see the new answer
            qaItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        } else {
            const error = await response.json();
            const answerText = qaItem.querySelector('.central-qa-answer .qa-text');
            answerText.innerHTML = `<span class="ai-error">${escapeHtml(error.error || 'Failed to get answer. Make sure GEMINI_API_KEY is configured.')}</span>`;
            showError(error.error || 'Failed to get answer');
        }
    } catch (error) {
        console.error('Error asking question:', error);
        const answerText = qaItem.querySelector('.central-qa-answer .qa-text');
        answerText.innerHTML = '<span class="ai-error">Failed to get answer. Please try again.</span>';
        showError('Failed to get answer');
    } finally {
        askButton.disabled = false;
        askButton.innerHTML = 'Ask AI';
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

