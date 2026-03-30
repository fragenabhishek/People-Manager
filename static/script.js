// ============================================================
// People Manager - Frontend Application
// ============================================================

const API = '/api/people';
const NOTES_API = '/api/notes';
const ASK_API = '/api/ask';

let allPeople = [];
let currentPersonId = null;
let currentTagFilter = null;
let confirmResolve = null;

// ---- Init ----
document.addEventListener('DOMContentLoaded', () => {
    loadPeople();
    loadTags();
    document.getElementById('searchInput').addEventListener('input', handleSearch);
    initDarkMode();
    initKeyboardShortcuts();
});

// ---- Dark Mode ----
function initDarkMode() {
    const saved = localStorage.getItem('darkMode');
    if (saved === 'true') document.body.classList.add('dark');
    document.getElementById('darkModeToggle').addEventListener('click', () => {
        document.body.classList.toggle('dark');
        localStorage.setItem('darkMode', document.body.classList.contains('dark'));
    });
}

// ---- Keyboard Shortcuts ----
function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
        if (e.key === 'n' || e.key === 'N') { e.preventDefault(); openPersonModal(); }
        if (e.key === '/') { e.preventDefault(); document.getElementById('searchInput').focus(); }
        if (e.key === 'Escape') { closeDrawer(); closePersonModal(); closeNoteModal(); closeImportModal(); closeConfirm(); }
    });
}

// ---- View Switching ----
function switchView(name) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active-view'));
    document.querySelectorAll('.sidebar-link, .mobile-nav-btn[data-view]').forEach(l => l.classList.remove('active'));
    document.getElementById('view-' + name).classList.add('active-view');
    document.querySelectorAll(`[data-view="${name}"]`).forEach(el => el.classList.add('active'));
    if (name === 'dashboard') loadDashboard();
    if (name === 'activity') loadActivity();
}

// ---- Load People ----
async function loadPeople() {
    try {
        let url = API;
        if (currentTagFilter) url += '?tag=' + encodeURIComponent(currentTagFilter);
        const resp = await fetch(url);
        allPeople = await resp.json();
        renderPeople(allPeople);
    } catch (e) { console.error(e); showToast('Failed to load contacts', 'error'); }
}

// ---- Render People Grid ----
function renderPeople(people) {
    const grid = document.getElementById('peopleGrid');
    const empty = document.getElementById('emptyState');
    if (!people.length) { grid.style.display = 'none'; empty.style.display = 'block'; return; }
    grid.style.display = 'grid'; empty.style.display = 'none';
    grid.innerHTML = people.map(p => {
        const statusClass = 'status-' + (p.relationship_status || 'new');
        const initials = p.name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
        const subtitle = [p.job_title, p.company].filter(Boolean).join(' at ');
        const tagHtml = (p.tags || []).map(t => `<span class="tag-chip" onclick="event.stopPropagation();filterByTag('${escapeAttr(t)}')">${escapeHtml(t)}</span>`).join('');
        const followUpHtml = p.next_follow_up ? `<span class="follow-badge ${isOverdue(p.next_follow_up) ? 'overdue' : ''}">${p.next_follow_up}</span>` : '';
        return `<div class="person-card ${statusClass}" onclick="openDrawer('${p.id}')">
            <div class="card-top">
                <div class="avatar">${p.profile_image_url ? `<img src="${escapeAttr(p.profile_image_url)}" alt="" />` : initials}</div>
                <div class="card-info">
                    <div class="card-name">${escapeHtml(p.name)}</div>
                    ${subtitle ? `<div class="card-subtitle">${escapeHtml(subtitle)}</div>` : ''}
                    ${p.location ? `<div class="card-meta">${escapeHtml(p.location)}</div>` : ''}
                </div>
                <div class="card-score"><span class="score-dot ${statusClass}" title="${p.relationship_status}"></span></div>
            </div>
            ${tagHtml ? `<div class="card-tags">${tagHtml}</div>` : ''}
            ${followUpHtml ? `<div class="card-followup">Follow-up: ${followUpHtml}</div>` : ''}
        </div>`;
    }).join('');
}

// ---- Search ----
async function handleSearch(e) {
    const q = e.target.value.trim();
    if (!q) { renderPeople(allPeople); return; }
    try {
        const resp = await fetch(`${API}/search/${encodeURIComponent(q)}`);
        renderPeople(await resp.json());
    } catch (e) { console.error(e); }
}

// ---- Tags ----
async function loadTags() {
    try {
        const resp = await fetch(API + '/tags');
        const tags = await resp.json();
        const el = document.getElementById('tagList');
        el.innerHTML = tags.map(t => `<button class="tag-btn ${currentTagFilter === t ? 'active' : ''}" onclick="filterByTag('${escapeAttr(t)}')">${escapeHtml(t)}</button>`).join('');
    } catch (e) { console.error(e); }
}

function filterByTag(tag) {
    if (currentTagFilter === tag) { clearTagFilter(); return; }
    currentTagFilter = tag;
    document.getElementById('activeFilter').style.display = 'flex';
    document.getElementById('activeFilterTag').textContent = tag;
    loadPeople();
    loadTags();
}

function clearTagFilter() {
    currentTagFilter = null;
    document.getElementById('activeFilter').style.display = 'none';
    loadPeople();
    loadTags();
}

// ---- Person Modal ----
function openPersonModal(person = null) {
    const form = document.getElementById('personForm');
    form.reset();
    document.getElementById('personId').value = '';
    document.getElementById('modalTitle').textContent = person ? 'Edit Contact' : 'Add New Contact';
    if (person) {
        document.getElementById('personId').value = person.id;
        document.getElementById('personName').value = person.name || '';
        document.getElementById('personEmail').value = person.email || '';
        document.getElementById('personPhone').value = person.phone || '';
        document.getElementById('personCompany').value = person.company || '';
        document.getElementById('personJobTitle').value = person.job_title || '';
        document.getElementById('personLocation').value = person.location || '';
        document.getElementById('personLinkedin').value = person.linkedin_url || '';
        document.getElementById('personTwitter').value = person.twitter_handle || '';
        document.getElementById('personWebsite').value = person.website || '';
        document.getElementById('personHowMet').value = person.how_we_met || '';
        document.getElementById('personMetAt').value = person.met_at || '';
        document.getElementById('personBirthday').value = person.birthday || '';
        document.getElementById('personTags').value = (person.tags || []).join(', ');
        document.getElementById('personDetails').value = person.details || '';
        document.getElementById('personFollowUp').value = person.next_follow_up || '';
        document.getElementById('personFollowFreq').value = person.follow_up_frequency_days || 0;
    }
    document.getElementById('personModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closePersonModal() {
    document.getElementById('personModal').style.display = 'none';
    document.body.style.overflow = '';
}

async function handlePersonSubmit(e) {
    e.preventDefault();
    const id = document.getElementById('personId').value;
    const data = {
        name: document.getElementById('personName').value,
        email: document.getElementById('personEmail').value,
        phone: document.getElementById('personPhone').value,
        company: document.getElementById('personCompany').value,
        job_title: document.getElementById('personJobTitle').value,
        location: document.getElementById('personLocation').value,
        linkedin_url: document.getElementById('personLinkedin').value,
        twitter_handle: document.getElementById('personTwitter').value,
        website: document.getElementById('personWebsite').value,
        how_we_met: document.getElementById('personHowMet').value,
        met_at: document.getElementById('personMetAt').value,
        birthday: document.getElementById('personBirthday').value,
        tags: document.getElementById('personTags').value,
        details: document.getElementById('personDetails').value,
        next_follow_up: document.getElementById('personFollowUp').value,
        follow_up_frequency_days: parseInt(document.getElementById('personFollowFreq').value) || 0,
    };
    try {
        const resp = await fetch(id ? `${API}/${id}` : API, {
            method: id ? 'PUT' : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (resp.ok) {
            closePersonModal();
            showToast(id ? 'Contact updated!' : 'Contact added!', 'success');
            loadPeople(); loadTags();
            if (currentPersonId === id) openDrawer(id);
        } else {
            const err = await resp.json();
            showToast(err.error || 'Failed to save', 'error');
        }
    } catch (e) { showToast('Failed to save contact', 'error'); }
}

// ---- Person Detail Drawer ----
async function openDrawer(id) {
    currentPersonId = id;
    const drawer = document.getElementById('personDrawer');
    drawer.classList.add('open');
    document.body.style.overflow = 'hidden';
    try {
        const [personResp, notesResp] = await Promise.all([
            fetch(`${API}/${id}`),
            fetch(`${NOTES_API}/person/${id}`)
        ]);
        const person = await personResp.json();
        const notes = await notesResp.json();
        document.getElementById('drawerName').textContent = person.name;
        document.getElementById('drawerBody').innerHTML = renderDrawerContent(person, notes);
    } catch (e) {
        document.getElementById('drawerBody').innerHTML = '<p>Failed to load details.</p>';
    }
}

function closeDrawer() {
    document.getElementById('personDrawer').classList.remove('open');
    document.body.style.overflow = '';
    currentPersonId = null;
}

function renderDrawerContent(p, notes) {
    const fields = [
        { icon: '&#9993;', label: 'Email', value: p.email, link: p.email ? `mailto:${p.email}` : null },
        { icon: '&#128222;', label: 'Phone', value: p.phone, link: p.phone ? `tel:${p.phone}` : null },
        { icon: '&#127970;', label: 'Company', value: [p.job_title, p.company].filter(Boolean).join(' at ') },
        { icon: '&#128205;', label: 'Location', value: p.location },
        { icon: '&#128279;', label: 'LinkedIn', value: p.linkedin_url ? 'Profile' : '', link: p.linkedin_url },
        { icon: '&#128038;', label: 'Twitter', value: p.twitter_handle },
        { icon: '&#127760;', label: 'Website', value: p.website ? 'Visit' : '', link: p.website },
        { icon: '&#129309;', label: 'How We Met', value: p.how_we_met },
        { icon: '&#128197;', label: 'Met On', value: p.met_at },
        { icon: '&#127874;', label: 'Birthday', value: p.birthday },
    ];
    const infoHtml = fields.filter(f => f.value).map(f =>
        `<div class="detail-row"><span class="detail-icon">${f.icon}</span><span class="detail-label">${f.label}:</span>${f.link ? `<a href="${escapeAttr(f.link)}" target="_blank" rel="noopener">${escapeHtml(f.value)}</a>` : `<span>${escapeHtml(f.value)}</span>`}</div>`
    ).join('');

    const tagsHtml = (p.tags || []).map(t => `<span class="tag-chip">${escapeHtml(t)}</span>`).join('');
    const statusLabel = { warm: 'Warm', lukewarm: 'Lukewarm', cold: 'Cold', new: 'New' }[p.relationship_status] || 'New';
    const scoreHtml = `<div class="detail-row"><span class="detail-icon">&#10084;</span><span class="detail-label">Relationship:</span><span class="score-badge status-${p.relationship_status}">${statusLabel}</span> <small>(score: ${p.relationship_score})</small></div>`;

    const followHtml = p.next_follow_up ? `<div class="detail-row"><span class="detail-icon">&#128276;</span><span class="detail-label">Follow-up:</span><span class="follow-badge ${isOverdue(p.next_follow_up) ? 'overdue' : ''}">${p.next_follow_up}</span> <button class="btn btn-xs btn-outline" onclick="completeFollowUp('${p.id}')">Done</button></div>` : '';

    const detailsHtml = p.details ? `<div class="drawer-section"><h4>Notes / Details</h4><div class="details-text">${escapeHtml(p.details)}</div></div>` : '';

    const notesHtml = notes.length ? notes.map(n => {
        const typeIcon = { meeting: '&#128197;', call: '&#128222;', email: '&#9993;', event: '&#127881;', follow_up: '&#128276;' }[n.note_type] || '&#128221;';
        return `<div class="note-item"><div class="note-header"><span class="note-type">${typeIcon} ${n.note_type}</span><span class="note-date">${formatDate(n.created_at)}</span><button class="btn btn-xs btn-link" onclick="deleteNote('${n.id}')">&#10005;</button></div><div class="note-body">${escapeHtml(n.content)}</div></div>`;
    }).join('') : '<p class="text-muted">No interaction notes yet.</p>';

    const blueprintSection = `<div class="drawer-section"><h4>AI Blueprint</h4><button class="btn btn-sm btn-outline" id="blueprintBtn" onclick="generateBlueprint('${p.id}')">Generate Blueprint</button><div id="blueprintContent"></div></div>`;

    return `
        <div class="drawer-section">${scoreHtml}${followHtml}${infoHtml}</div>
        ${tagsHtml ? `<div class="drawer-section"><h4>Tags</h4><div class="tag-row">${tagsHtml}</div></div>` : ''}
        ${detailsHtml}
        <div class="drawer-section">
            <div class="section-header-row"><h4>Interaction Timeline (${notes.length})</h4><button class="btn btn-sm btn-primary" onclick="openNoteModal('${p.id}')">+ Add Note</button></div>
            <div class="notes-timeline">${notesHtml}</div>
        </div>
        ${blueprintSection}
    `;
}

function editCurrentPerson() {
    const person = allPeople.find(p => p.id === currentPersonId);
    if (person) { closeDrawer(); openPersonModal(person); }
}

async function deleteCurrentPerson() {
    const person = allPeople.find(p => p.id === currentPersonId);
    if (!person) return;
    const ok = await showConfirm(`Delete ${person.name}?`, 'Delete Contact');
    if (!ok) return;
    try {
        const resp = await fetch(`${API}/${currentPersonId}`, { method: 'DELETE' });
        if (resp.ok) { closeDrawer(); showToast('Contact deleted', 'success'); loadPeople(); loadTags(); }
    } catch (e) { showToast('Failed to delete', 'error'); }
}

// ---- Notes ----
function openNoteModal(personId) {
    document.getElementById('notePersonId').value = personId;
    document.getElementById('noteForm').reset();
    document.getElementById('noteModal').style.display = 'block';
}

function closeNoteModal() { document.getElementById('noteModal').style.display = 'none'; }

async function handleNoteSubmit(e) {
    e.preventDefault();
    const personId = document.getElementById('notePersonId').value;
    const data = { content: document.getElementById('noteContent').value, note_type: document.getElementById('noteType').value };
    try {
        const resp = await fetch(`${NOTES_API}/person/${personId}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
        if (resp.ok) { closeNoteModal(); showToast('Note added!', 'success'); openDrawer(personId); loadPeople(); }
        else { const err = await resp.json(); showToast(err.error || 'Failed', 'error'); }
    } catch (e) { showToast('Failed to add note', 'error'); }
}

async function deleteNote(noteId) {
    try {
        const resp = await fetch(`${NOTES_API}/${noteId}`, { method: 'DELETE' });
        if (resp.ok) { showToast('Note deleted', 'success'); if (currentPersonId) openDrawer(currentPersonId); }
    } catch (e) { showToast('Failed', 'error'); }
}

// ---- Follow-ups ----
async function completeFollowUp(personId) {
    try {
        const resp = await fetch(`${API}/${personId}/followup/complete`, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
        if (resp.ok) { showToast('Follow-up completed!', 'success'); loadPeople(); if (currentPersonId === personId) openDrawer(personId); }
    } catch (e) { showToast('Failed', 'error'); }
}

// ---- AI ----
async function generateBlueprint(personId) {
    const btn = document.getElementById('blueprintBtn');
    const content = document.getElementById('blueprintContent');
    btn.disabled = true; btn.textContent = 'Generating...';
    content.innerHTML = '<div class="ai-loading">Analyzing contact data...</div>';
    try {
        const resp = await fetch(`${API}/${personId}/summary`, { method: 'POST', headers: { 'Content-Type': 'application/json' } });
        if (resp.ok) {
            const data = await resp.json();
            content.innerHTML = `<div class="ai-result">${data.summary}</div>`;
            showToast('Blueprint generated!', 'success');
        } else {
            const err = await resp.json();
            content.innerHTML = `<div class="ai-error">${escapeHtml(err.error || 'Failed')}</div>`;
        }
    } catch (e) { content.innerHTML = '<div class="ai-error">Failed to generate. Try again.</div>'; }
    btn.disabled = false; btn.textContent = 'Regenerate Blueprint';
}

function toggleQA() {
    const body = document.getElementById('qaBody');
    const chev = document.getElementById('qaChevron');
    const show = body.style.display === 'none';
    body.style.display = show ? 'block' : 'none';
    chev.innerHTML = show ? '&#9650;' : '&#9660;';
}

async function askAI() {
    const input = document.getElementById('qaInput');
    const q = input.value.trim();
    if (!q) return;
    const history = document.getElementById('qaHistory');
    history.style.display = 'block';
    const item = document.createElement('div');
    item.className = 'qa-item';
    item.innerHTML = `<div class="qa-q"><strong>Q:</strong> ${escapeHtml(q)}</div><div class="qa-a"><strong>A:</strong> <span class="ai-loading">Thinking...</span></div>`;
    history.prepend(item);
    input.value = '';
    const btn = document.getElementById('qaAskBtn');
    btn.disabled = true;
    try {
        const resp = await fetch(ASK_API, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: q }) });
        if (resp.ok) {
            const data = await resp.json();
            item.querySelector('.qa-a').innerHTML = `<strong>A:</strong> ${data.answer}`;
        } else {
            const err = await resp.json();
            item.querySelector('.qa-a').innerHTML = `<strong>A:</strong> <span class="ai-error">${escapeHtml(err.error || 'Failed')}</span>`;
        }
    } catch (e) { item.querySelector('.qa-a').innerHTML = '<strong>A:</strong> <span class="ai-error">Failed.</span>'; }
    btn.disabled = false;
}

// ---- Dashboard ----
async function loadDashboard() {
    try {
        const resp = await fetch(API + '/dashboard/stats');
        const s = await resp.json();
        document.getElementById('statTotal').textContent = s.total_contacts;
        document.getElementById('statWeek').textContent = s.added_this_week;
        document.getElementById('statFollowups').textContent = s.due_followups;
        document.getElementById('statCold').textContent = s.cold_contacts;

        const health = document.getElementById('healthChart');
        const total = Math.max(s.total_contacts, 1);
        health.innerHTML = ['warm', 'lukewarm', 'cold', 'new'].map(k => {
            const count = s.status_counts[k] || 0;
            const pct = Math.round(count / total * 100);
            return `<div class="health-row"><span class="health-label">${k}</span><div class="health-track"><div class="health-fill status-${k}" style="width:${pct}%"></div></div><span class="health-val">${count}</span></div>`;
        }).join('');

        document.getElementById('followupList').innerHTML = (s.due_followup_list || []).map(p =>
            `<div class="mini-item" onclick="openDrawer('${p.id}')"><strong>${escapeHtml(p.name)}</strong><span class="follow-badge overdue">${p.next_follow_up}</span></div>`
        ).join('') || '<p class="text-muted">No follow-ups due</p>';

        document.getElementById('recentList').innerHTML = (s.recently_added || []).map(p =>
            `<div class="mini-item" onclick="openDrawer('${p.id}')"><strong>${escapeHtml(p.name)}</strong><span class="text-muted">${formatDate(p.createdAt)}</span></div>`
        ).join('') || '<p class="text-muted">No contacts yet</p>';

        const tagBreak = document.getElementById('tagBreakdown');
        const tags = Object.entries(s.tag_counts || {}).sort((a, b) => b[1] - a[1]);
        tagBreak.innerHTML = tags.map(([tag, count]) =>
            `<div class="tag-break-item" onclick="filterByTag('${escapeAttr(tag)}');switchView('contacts');"><span class="tag-chip">${escapeHtml(tag)}</span><span>${count}</span></div>`
        ).join('') || '<p class="text-muted">No tags yet</p>';
    } catch (e) { console.error(e); }
}

// ---- Activity Feed ----
async function loadActivity() {
    try {
        const resp = await fetch(NOTES_API + '/activity?limit=30');
        const items = await resp.json();
        document.getElementById('activityFeed').innerHTML = items.map(a => {
            const typeIcon = { meeting: '&#128197;', call: '&#128222;', email: '&#9993;', event: '&#127881;', follow_up: '&#128276;' }[a.note.note_type] || '&#128221;';
            return `<div class="activity-item" onclick="openDrawer('${a.person_id}')"><div class="activity-icon">${typeIcon}</div><div class="activity-body"><strong>${escapeHtml(a.person_name)}</strong> &mdash; ${escapeHtml(a.note.content.substring(0, 120))}${a.note.content.length > 120 ? '...' : ''}<div class="activity-date">${formatDate(a.note.created_at)}</div></div></div>`;
        }).join('') || '<p class="text-muted" style="padding:2rem;">No activity yet. Add notes to your contacts to see them here.</p>';
    } catch (e) { console.error(e); }
}

// ---- Import ----
function showImportModal() { document.getElementById('importModal').style.display = 'block'; }
function closeImportModal() { document.getElementById('importModal').style.display = 'none'; document.getElementById('importResult').style.display = 'none'; }

async function handleImport(e) {
    e.preventDefault();
    const file = document.getElementById('importFile').files[0];
    if (!file) return;
    const fd = new FormData();
    fd.append('file', file);
    try {
        const resp = await fetch(API + '/import/csv', { method: 'POST', body: fd });
        const result = await resp.json();
        const el = document.getElementById('importResult');
        el.style.display = 'block';
        el.innerHTML = `<p><strong>${result.imported}</strong> imported, <strong>${result.skipped}</strong> skipped.</p>${result.errors.length ? '<p class="text-muted">' + result.errors.join('<br>') + '</p>' : ''}`;
        loadPeople(); loadTags();
        showToast(`Imported ${result.imported} contacts`, 'success');
    } catch (e) { showToast('Import failed', 'error'); }
}

// ---- Confirm Dialog ----
function showConfirm(message, title) {
    return new Promise(resolve => {
        document.getElementById('confirmTitle').textContent = title || 'Confirm';
        document.getElementById('confirmMessage').textContent = message;
        document.getElementById('confirmModal').style.display = 'block';
        confirmResolve = resolve;
        document.getElementById('confirmOkBtn').onclick = () => { closeConfirm(); resolve(true); };
    });
}
function closeConfirm() { document.getElementById('confirmModal').style.display = 'none'; if (confirmResolve) { confirmResolve(false); confirmResolve = null; } }

// ---- Toast ----
function showToast(message, type) {
    const container = document.getElementById('toastContainer');
    if (!container) { alert(message); return; }
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span class="toast-msg">${escapeHtml(message)}</span><button class="toast-close" onclick="this.parentElement.remove()">&times;</button>`;
    container.appendChild(toast);
    setTimeout(() => { toast.classList.add('hiding'); setTimeout(() => toast.remove(), 300); }, 3000);
}

// ---- Utils ----
function escapeHtml(t) { if (!t) return ''; const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }
function escapeAttr(t) { return t ? t.replace(/'/g, "\\'").replace(/"/g, '&quot;') : ''; }
function isOverdue(dateStr) { if (!dateStr) return false; return dateStr <= new Date().toISOString().substring(0, 10); }
function formatDate(ds) {
    if (!ds) return '';
    const d = new Date(ds); const now = new Date();
    const diff = Math.floor((now - d) / 86400000);
    if (diff === 0) return 'Today';
    if (diff === 1) return 'Yesterday';
    if (diff < 7) return diff + 'd ago';
    return d.toLocaleDateString();
}
