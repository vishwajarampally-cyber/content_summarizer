// Global state
let currentTab = 'text';
let selectedFile = null;
let historyRecords = [];

// DOM elements
const textareaInput = document.getElementById('input-textarea');
const urlInput = document.getElementById('input-url');
const fileInput = document.getElementById('input-file');
const dropzone = document.getElementById('dropzone');
const fileInfoBadge = document.getElementById('file-info');
const fileNameDisplay = document.getElementById('file-name-display');

const selectContentType = document.getElementById('select-content-type');
const selectStyle = document.getElementById('select-style');
const btnSubmit = document.getElementById('btn-submit');

const outputEmpty = document.getElementById('output-empty');
const outputLoading = document.getElementById('output-loading');
const outputResult = document.getElementById('output-result');
const outputActions = document.getElementById('output-actions');
const statsPanel = document.getElementById('stats-panel');

const statWords = document.getElementById('stat-words');
const statChars = document.getElementById('stat-chars');
const statTime = document.getElementById('stat-time');

const historyGrid = document.getElementById('history-grid');
const historySearch = document.getElementById('history-search');

const historyModal = document.getElementById('history-modal');

// Initial setup
document.addEventListener('DOMContentLoaded', () => {
    // Load history on startup
    loadHistory();
    
    // File drag and drop listeners
    if (dropzone) {
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                dropzone.classList.remove('dragover');
            }, false);
        });

        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });
    }
});

// Tab switching
function switchTab(tabId) {
    currentTab = tabId;
    
    // Update button states
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`tab-${tabId}`).classList.add('active');
    
    // Update pane states
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    document.getElementById(`pane-${tabId}`).classList.add('active');
}

// File handling
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
        alert('Invalid file format. Only PDF files are allowed.');
        return;
    }
    
    // Max 10MB
    if (file.size > 10 * 1024 * 1024) {
        alert('File size exceeds the 10MB limit.');
        return;
    }
    
    selectedFile = file;
    fileNameDisplay.textContent = `${file.name} (${formatBytes(file.size)})`;
    dropzone.style.display = 'none';
    fileInfoBadge.style.display = 'flex';
}

function clearFile(e) {
    if (e) e.stopPropagation();
    selectedFile = null;
    fileInput.value = '';
    fileInfoBadge.style.display = 'none';
    dropzone.style.display = 'block';
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// Simple Markdown parser
function renderMarkdown(text) {
    if (!text) return "";
    
    // Escape HTML to prevent XSS
    let html = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    
    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Headings
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Bullet points conversion
    const lines = html.split('\n');
    let inList = false;
    const outputLines = [];
    
    for (let line of lines) {
        const trimmed = line.trim();
        // Match "- " or "* "
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
            if (!inList) {
                outputLines.push('<ul>');
                inList = true;
            }
            outputLines.push(`<li>${trimmed.substring(2)}</li>`);
        } else {
            if (inList) {
                outputLines.push('</ul>');
                inList = false;
            }
            outputLines.push(line);
        }
    }
    
    if (inList) {
        outputLines.push('</ul>');
    }
    
    return outputLines.join('\n').replace(/\n/g, '<br>');
}

// Main logic: Summarize
async function generateSummary() {
    // 1. Validate based on tab
    let url = '';
    let body = null;
    let headers = {};
    
    const summaryStyle = selectStyle.value;
    const documentStyle = selectContentType.value;
    
    if (currentTab === 'text') {
        const textVal = textareaInput.value.trim();
        if (textVal.split(/\s+/).filter(Boolean).length < 10) {
            alert('Please enter at least 10 words to summarize.');
            return;
        }
        url = '/api/summarize/text';
        body = JSON.stringify({
            text: textVal,
            summary_style: summaryStyle,
            document_style: documentStyle
        });
        headers = { 'Content-Type': 'application/json' };
        
    } else if (currentTab === 'url') {
        const urlVal = urlInput.value.trim();
        if (!urlVal || !urlVal.startsWith('http')) {
            alert('Please enter a valid URL (starting with http:// or https://).');
            return;
        }
        url = '/api/summarize/url';
        body = JSON.stringify({
            url: urlVal,
            summary_style: summaryStyle,
            document_style: documentStyle
        });
        headers = { 'Content-Type': 'application/json' };
        
    } else if (currentTab === 'pdf') {
        if (!selectedFile) {
            alert('Please select or drop a PDF file first.');
            return;
        }
        url = '/api/summarize/pdf';
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('summary_style', summaryStyle);
        formData.append('document_style', documentStyle);
        body = formData;
        // Don't set Content-Type header; fetch will set boundary automatically for FormData
    }
    
    // Set UI states to Loading
    outputEmpty.style.display = 'none';
    outputResult.style.display = 'none';
    outputActions.style.display = 'none';
    statsPanel.style.display = 'none';
    outputLoading.style.display = 'flex';
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: body
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to generate summary.');
        }
        
        // Render Output
        outputResult.innerHTML = renderMarkdown(data.summary);
        
        // Show Output Actions and Stats
        outputLoading.style.display = 'none';
        outputResult.style.display = 'block';
        outputActions.style.display = 'flex';
        
        // Update Stats
        const stats = data.statistics || {};
        statWords.textContent = stats.word_count || 0;
        statChars.textContent = stats.character_count || 0;
        statTime.textContent = (stats.reading_time_minutes || 0).toFixed(1) + 'm';
        statsPanel.style.display = 'grid';
        
        // Reload History
        loadHistory();
        
    } catch (error) {
        outputLoading.style.display = 'none';
        outputEmpty.style.display = 'flex';
        alert(`Error: ${error.message}`);
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = '<i class="fa-solid fa-sparkles"></i> Summarize Content';
    }
}

// Clipboard copying
function copyToClipboard() {
    const textToCopy = outputResult.innerText;
    navigator.clipboard.writeText(textToCopy).then(() => {
        const copyBtn = document.querySelector('.output-actions .action-btn');
        const originalHtml = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fa-solid fa-check" style="color: var(--success)"></i> Copied!';
        setTimeout(() => {
            copyBtn.innerHTML = originalHtml;
        }, 2000);
    }).catch(err => {
        alert('Failed to copy text: ' + err);
    });
}

// Fetch History from DB
async function loadHistory() {
    try {
        const response = await fetch('/api/history?limit=12');
        if (response.ok) {
            historyRecords = await response.json();
            renderHistory();
        }
    } catch (e) {
        console.error('Failed to load history:', e);
    }
}

// Render History Hub Cards
function renderHistory() {
    if (!historyGrid) return;
    
    const query = historySearch.value.toLowerCase().trim();
    historyGrid.innerHTML = '';
    
    const filtered = historyRecords.filter(item => {
        const title = (item.title || '').toLowerCase();
        const summary = (item.summary || '').toLowerCase();
        const src = (item.source_type || '').toLowerCase();
        const type = (item.summary_type || '').toLowerCase();
        return title.includes(query) || summary.includes(query) || src.includes(query) || type.includes(query);
    });
    
    if (filtered.length === 0) {
        historyGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; color: var(--text-muted); padding: 40px;">
                <i class="fa-solid fa-circle-info" style="font-size: 2rem; margin-bottom: 12px;"></i>
                <p>No history items matches your search.</p>
            </div>
        `;
        return;
    }
    
    filtered.forEach(item => {
        const card = document.createElement('div');
        card.className = 'history-card glass-card';
        card.onclick = () => openHistoryModal(item);
        
        const dateStr = item.created_at ? new Date(item.created_at).toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        }) : 'N/A';
        
        const sourceLabel = item.source_type === 'url' ? 'URL' : item.source_type === 'pdf' ? 'PDF' : 'Text';
        const displayTitle = item.title || (item.source_type === 'text' ? 'Pasted Text Summary' : 'Untitled');
        
        card.innerHTML = `
            <div class="card-meta">
                <span class="badge badge-accent">${sourceLabel}</span>
                <span class="card-date">${dateStr}</span>
            </div>
            <h3>${escapeHtml(displayTitle)}</h3>
            <p class="card-snippet">${escapeHtml(item.summary)}</p>
        `;
        historyGrid.appendChild(card);
    });
}

// Detailed History Modal
function openHistoryModal(item) {
    document.getElementById('modal-badge-source').textContent = (item.source_type || 'Text').toUpperCase();
    document.getElementById('modal-badge-style').textContent = item.summary_type || 'Summary';
    document.getElementById('modal-title').textContent = item.title || (item.source_type === 'text' ? 'Pasted Text Summary' : 'Untitled');
    
    const date = item.created_at ? new Date(item.created_at).toLocaleString() : 'N/A';
    document.getElementById('modal-date').textContent = `Created: ${date}`;
    
    const modalContent = document.getElementById('modal-content');
    modalContent.innerHTML = renderMarkdown(item.summary);
    
    const stats = item.statistics || {};
    document.getElementById('modal-stat-words').textContent = stats.word_count || 0;
    document.getElementById('modal-stat-time').textContent = (stats.reading_time_minutes || 0).toFixed(1);
    
    historyModal.classList.add('active');
}

function closeHistoryModal() {
    historyModal.classList.remove('active');
}

function copyModalToClipboard() {
    const content = document.getElementById('modal-content').innerText;
    navigator.clipboard.writeText(content).then(() => {
        const copyBtn = document.querySelector('.modal-footer .btn-secondary');
        const originalHtml = copyBtn.innerHTML;
        copyBtn.innerHTML = '<i class="fa-solid fa-check" style="color: var(--success)"></i> Copied!';
        setTimeout(() => {
            copyBtn.innerHTML = originalHtml;
        }, 2000);
    });
}

function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
