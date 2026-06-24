/* ============================================
   PCS-VIEW PROFESSIONAL UI - MAIN APPLICATION
   ============================================ */

// Application State
const AppState = {
    currentTool: 'upload',
    currentProject: null,
    projects: [],
    processing: false,
    viewerLoaded: false
};

// DOM Elements
const elements = {};

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    initializeEventListeners();
    loadProjects();
    updateStats();
});

function initializeElements() {
    // Navigation
    elements.navTabs = document.querySelectorAll('.nav-tab');
    elements.tabContents = document.querySelectorAll('.tab-content');
    
    // Tools
    elements.toolItems = document.querySelectorAll('.tool-item');
    elements.toolPanel = document.getElementById('toolPanel');
    elements.toolTitle = document.getElementById('toolTitle');
    elements.toolDescription = document.getElementById('toolDescription');
    elements.toolForm = document.getElementById('toolForm');
    
    // Modal
    elements.modal = document.getElementById('modal');
    elements.modalTitle = document.getElementById('modalTitle');
    elements.modalBody = document.getElementById('modalBody');
    elements.modalConfirm = document.getElementById('modalConfirm');
    
    // Status
    elements.statusMessage = document.getElementById('statusMessage');
    elements.progressFill = document.getElementById('progressFill');
}

function initializeEventListeners() {
    // Navigation Tabs
    elements.navTabs.forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });
    
    // Tools
    elements.toolItems.forEach(tool => {
        tool.addEventListener('click', () => selectTool(tool.dataset.tool));
    });
    
    // Tool Categories (Accordion)
    document.querySelectorAll('.tools-category-header').forEach(header => {
        header.addEventListener('click', () => {
            const toolsList = header.nextElementSibling;
            toolsList.classList.toggle('open');
        });
    });
    
    // Modal close
    document.querySelector('.modal-close')?.addEventListener('click', closeModal);
    document.getElementById('modalCancel')?.addEventListener('click', closeModal);
}

// ============================================
// TAB MANAGEMENT
// ============================================

function switchTab(tabId) {
    // Update navigation tabs
    elements.navTabs.forEach(tab => {
        if (tab.dataset.tab === tabId) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Update content tabs
    elements.tabContents.forEach(content => {
        if (content.id === `tab-${tabId}`) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
    
    // Special handling for viewer tab
    if (tabId === 'viewer' && !AppState.viewerLoaded) {
        loadViewer();
    }
}

// ============================================
// TOOL MANAGEMENT (Like QGIS Plugin Dialog)
// ============================================

const ToolTemplates = {
    // Upload Tool
    upload: {
        title: '📤 Upload Point Cloud',
        description: 'Upload LAS, LAZ, PLY, E57, or XYZ files for processing',
        form: `
            <div class="form-group">
                <label>Select File</label>
                <div class="upload-area" id="uploadArea">
                    <i class="fas fa-cloud-upload-alt" style="font-size: 48px;"></i>
                    <div>Drag & drop your file here</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">or click to browse</div>
                    <input type="file" id="fileInput" accept=".las,.laz,.ply,.e57,.xyz,.txt,.cx3d" style="display: none;">
                </div>
                <div id="fileInfo" style="margin-top: 12px; font-size: 0.85rem;"></div>
            </div>
            <div class="form-group">
                <label>Project Name (Optional)</label>
                <input type="text" class="form-control" id="projectName" placeholder="Enter project name...">
            </div>
            <div class="btn-group">
                <button class="btn btn-primary" id="uploadBtn" disabled>
                    <i class="fas fa-exchange-alt"></i> Convert & View
                </button>
                <button class="btn btn-secondary" id="clearUploadBtn">
                    <i class="fas fa-trash-alt"></i> Clear
                </button>
            </div>
        `,
        init: () => {
            initUploadTool();
        }
    },
    
    // Volume Calculation Tool
    volume: {
        title: '📐 Volume Calculation',
        description: 'Calculate volume of stockpiles, excavations, or earthwork',
        form: `
            <div class="form-group">
                <label>Select Project</label>
                <select class="form-control" id="volumeProjectSelect">
                    <option value="">-- Select a project --</option>
                </select>
            </div>
            <div class="form-group">
                <label>Base Elevation (m)</label>
                <input type="number" class="form-control" id="baseElevation" placeholder="Auto from min height" step="0.1">
            </div>
            <div class="form-group">
                <label>Calculation Method</label>
                <div class="radio-group">
                    <label class="radio-item">
                        <input type="radio" name="volumeMethod" value="voxel" checked> Voxel-based
                    </label>
                    <label class="radio-item">
                        <input type="radio" name="volumeMethod" value="advanced"> Advanced (Delaunay)
                    </label>
                </div>
            </div>
            <div class="btn-group">
                <button class="btn btn-primary" id="calculateVolumeBtn">
                    <i class="fas fa-calculator"></i> Calculate Volume
                </button>
            </div>
            <div id="volumeResult" class="status-message"></div>
        `,
        init: () => {
            initVolumeTool();
        }
    },
    
    // Classification Tool
    classification: {
        title: '🏔️ Point Cloud Classification',
        description: 'Classify points by height, ground detection, or intensity',
        form: `
            <div class="form-group">
                <label>Select Project</label>
                <select class="form-control" id="classifyProjectSelect">
                    <option value="">-- Select a project --</option>
                </select>
            </div>
            <div class="form-group">
                <label>Classification Type</label>
                <div class="radio-group">
                    <label class="radio-item">
                        <input type="radio" name="classifyType" value="height" checked> By Height
                    </label>
                    <label class="radio-item">
                        <input type="radio" name="classifyType" value="ground"> Ground Detection
                    </label>
                </div>
            </div>
            <div class="form-group" id="heightThresholdsGroup">
                <label>Height Thresholds (m)</label>
                <div class="range-slider">
                    <input type="range" class="form-control" id="heightLow" min="0" max="20" value="2" step="0.5">
                    <span>Low: <span id="lowVal">2</span>m</span>
                </div>
                <div class="range-slider">
                    <input type="range" class="form-control" id="heightMed" min="0" max="30" value="5" step="0.5">
                    <span>Medium: <span id="medVal">5</span>m</span>
                </div>
                <div class="range-slider">
                    <input type="range" class="form-control" id="heightHigh" min="0" max="50" value="10" step="0.5">
                    <span>High: <span id="highVal">10</span>m</span>
                </div>
            </div>
            <div class="btn-group">
                <button class="btn btn-primary" id="classifyBtn">
                    <i class="fas fa-chart-simple"></i> Run Classification
                </button>
            </div>
            <div id="classificationResult" class="status-message"></div>
        `,
        init: () => {
            initClassificationTool();
        }
    },
    
    // Orthophoto Tool
    orthophoto: {
        title: '🖼️ Orthophoto Generation',
        description: 'Generate orthophotos and contour lines from point clouds',
        form: `
            <div class="form-group">
                <label>Select Project</label>
                <select class="form-control" id="orthoProjectSelect">
                    <option value="">-- Select a project --</option>
                </select>
            </div>
            <div class="form-group">
                <label>Resolution (m/pixel)</label>
                <input type="number" class="form-control" id="orthoResolution" value="0.1" step="0.05" min="0.05" max="1.0">
            </div>
            <div class="form-group">
                <label>Contour Interval (m)</label>
                <input type="number" class="form-control" id="contourInterval" value="1.0" step="0.5" min="0.5" max="10.0">
            </div>
            <div class="btn-group">
                <button class="btn btn-primary" id="generateOrthoBtn">
                    <i class="fas fa-image"></i> Generate Orthophoto
                </button>
                <button class="btn btn-secondary" id="generateContoursBtn">
                    <i class="fas fa-chart-line"></i> Generate Contours
                </button>
            </div>
            <div id="orthoResult" class="status-message"></div>
        `,
        init: () => {
            initOrthophotoTool();
        }
    },
    
    // Cut & Fill Tool
    cutfill: {
        title: '✂️ Cut & Fill Analysis',
        description: 'Calculate cut and fill volumes between two surfaces',
        form: `
            <div class="form-group">
                <label>Reference Surface (Current)</label>
                <select class="form-control" id="cutfillCurrentSelect">
                    <option value="">-- Select a project --</option>
                </select>
            </div>
            <div class="form-group">
                <label>Design Surface (Target)</label>
                <select class="form-control" id="cutfillDesignSelect">
                    <option value="">-- Select or flat plane --</option>
                </select>
            </div>
            <div class="form-group">
                <label>Or use flat elevation (m)</label>
                <input type="number" class="form-control" id="flatElevation" placeholder="Leave empty for auto">
            </div>
            <div class="btn-group">
                <button class="btn btn-primary" id="calculateCutFillBtn">
                    <i class="fas fa-chart-line"></i> Calculate Cut & Fill
                </button>
            </div>
            <div id="cutfillResult" class="status-message"></div>
        `,
        init: () => {
            initCutFillTool();
        }
    },
    
    // Export Tool
    export: {
        title: '📥 Export Point Cloud',
        description: 'Export point cloud to CSV or TXT format',
        form: `
            <div class="form-group">
                <label>Select Project</label>
                <select class="form-control" id="exportProjectSelect">
                    <option value="">-- Select a project --</option>
                </select>
            </div>
            <div class="form-group">
                <label>Export Format</label>
                <div class="radio-group">
                    <label class="radio-item">
                        <input type="radio" name="exportFormat" value="csv" checked> CSV (Excel/GIS)
                    </label>
                    <label class="radio-item">
                        <input type="radio" name="exportFormat" value="txt"> TXT (ASCII)
                    </label>
                </div>
            </div>
            <div class="form-group">
                <label>Maximum Points</label>
                <input type="number" class="form-control" id="maxPoints" value="3000" min="100" max="50000" step="100">
                <small style="color: var(--text-secondary);">Limit points for performance</small>
            </div>
            <div class="btn-group">
                <button class="btn btn-primary" id="exportBtn">
                    <i class="fas fa-download"></i> Export Data
                </button>
            </div>
            <div id="exportResult" class="status-message"></div>
        `,
        init: () => {
            initExportTool();
        }
    }
};

function selectTool(toolId) {
    AppState.currentTool = toolId;
    
    // Update active state in sidebar
    elements.toolItems.forEach(tool => {
        if (tool.dataset.tool === toolId) {
            tool.classList.add('active');
        } else {
            tool.classList.remove('active');
        }
    });
    
    // Load tool template
    const tool = ToolTemplates[toolId];
    if (tool) {
        elements.toolTitle.innerHTML = tool.title;
        elements.toolDescription.innerHTML = tool.description;
        elements.toolForm.innerHTML = tool.form;
        
        // Initialize tool-specific functionality
        if (tool.init) {
            setTimeout(tool.init, 100);
        }
    }
}

// ============================================
// TOOL IMPLEMENTATIONS
// ============================================

function initUploadTool() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInfo = document.getElementById('fileInfo');
    const clearBtn = document.getElementById('clearUploadBtn');
    let selectedFile = null;
    
    uploadArea.addEventListener('click', () => fileInput.click());
    
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.background = 'rgba(255,255,255,0.05)';
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.background = '';
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.background = '';
        if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) handleFile(e.target.files[0]);
    });
    
    function handleFile(file) {
        const ext = file.name.split('.').pop().toLowerCase();
        const allowed = ['las', 'laz', 'ply', 'e57', 'xyz', 'txt', 'cx3d'];
        
        if (!allowed.includes(ext)) {
            showStatus('error', 'Unsupported file format');
            return;
        }
        
        selectedFile = file;
        uploadBtn.disabled = false;
        const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
        fileInfo.innerHTML = `<i class="fas fa-check-circle" style="color: var(--accent-green);"></i> ${file.name} (${sizeMB} MB)`;
    }
    
    uploadBtn.addEventListener('click', async () => {
        if (!selectedFile) return;
        
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Converting...';
        
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        try {
            const response = await fetch('/api/upload', { method: 'POST', body: formData });
            const data = await response.json();
            
            if (response.ok && data.success) {
                showStatus('success', 'Conversion complete! Redirecting to viewer...');
                setTimeout(() => {
                    window.location.href = data.viewer_url;
                }, 1500);
            } else {
                throw new Error(data.detail || 'Conversion failed');
            }
        } catch (error) {
            showStatus('error', error.message);
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="fas fa-exchange-alt"></i> Convert & View';
        }
    });
    
    clearBtn.addEventListener('click', () => {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.innerHTML = '';
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fas fa-exchange-alt"></i> Convert & View';
    });
}

async function initVolumeTool() {
    await loadProjectsToSelect('volumeProjectSelect');
    
    document.getElementById('calculateVolumeBtn').addEventListener('click', async () => {
        const select = document.getElementById('volumeProjectSelect');
        const modelName = select.value;
        const baseElevation = document.getElementById('baseElevation').value;
        const method = document.querySelector('input[name="volumeMethod"]:checked').value;
        const resultDiv = document.getElementById('volumeResult');
        
        if (!modelName) {
            showToolStatus('volumeResult', 'error', 'Please select a project');
            return;
        }
        
        showToolStatus('volumeResult', 'info', 'Calculating volume...');
        
        try {
            const url = method === 'advanced' ? `/api/volume/advanced/${modelName}` : `/api/volume/${modelName}`;
            const options = { method: 'POST' };
            
            if (baseElevation) {
                options.body = JSON.stringify({ base_elevation: parseFloat(baseElevation) });
                options.headers = { 'Content-Type': 'application/json' };
            }
            
            const response = await fetch(url, options);
            const data = await response.json();
            
            if (data.success) {
                showToolStatus('volumeResult', 'success', 
                    `📐 Volume: ${data.volume_cubic_meters} m³ | Area: ${data.area_sqm || 'N/A'} m²`
                );
            } else {
                showToolStatus('volumeResult', 'error', data.error || 'Calculation failed');
            }
        } catch (error) {
            showToolStatus('volumeResult', 'error', error.message);
        }
    });
}

async function initClassificationTool() {
    await loadProjectsToSelect('classifyProjectSelect');
    
    // Slider value updates
    const sliders = ['heightLow', 'heightMed', 'heightHigh'];
    sliders.forEach(sliderId => {
        const slider = document.getElementById(sliderId);
        const span = document.getElementById(`${sliderId}Val`);
        slider.addEventListener('input', () => {
            span.textContent = slider.value;
        });
    });
    
    document.getElementById('classifyBtn').addEventListener('click', async () => {
        const select = document.getElementById('classifyProjectSelect');
        const modelName = select.value;
        const classifyType = document.querySelector('input[name="classifyType"]:checked').value;
        const resultDiv = document.getElementById('classificationResult');
        
        if (!modelName) {
            showToolStatus('classificationResult', 'error', 'Please select a project');
            return;
        }
        
        showToolStatus('classificationResult', 'info', 'Running classification...');
        
        try {
            let url, body = {};
            
            if (classifyType === 'height') {
                url = `/api/classify/height/${modelName}`;
                body = {
                    low_threshold: parseFloat(document.getElementById('heightLow').value),
                    medium_threshold: parseFloat(document.getElementById('heightMed').value),
                    high_threshold: parseFloat(document.getElementById('heightHigh').value)
                };
            } else {
                url = `/api/classify/ground/${modelName}`;
            }
            
            const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
            const data = await response.json();
            
            if (data.success) {
                if (classifyType === 'height') {
                    showToolStatus('classificationResult', 'success',
                        `🌿 Low: ${data.classifications.low_vegetation} | 🌳 Med: ${data.classifications.medium_vegetation} | 🏢 High: ${data.classifications.building}`
                    );
                } else {
                    showToolStatus('classificationResult', 'success',
                        `🌍 Ground: ${data.ground_points} points (${data.ground_percentage}%) | 🏔️ Non-ground: ${data.non_ground_points} points`
                    );
                }
            } else {
                showToolStatus('classificationResult', 'error', data.error || 'Classification failed');
            }
        } catch (error) {
            showToolStatus('classificationResult', 'error', error.message);
        }
    });
}

async function initOrthophotoTool() {
    await loadProjectsToSelect('orthoProjectSelect');
    
    document.getElementById('generateOrthoBtn').addEventListener('click', async () => {
        const select = document.getElementById('orthoProjectSelect');
        const modelName = select.value;
        const resolution = document.getElementById('orthoResolution').value;
        const resultDiv = document.getElementById('orthoResult');
        
        if (!modelName) {
            showToolStatus('orthoResult', 'error', 'Please select a project');
            return;
        }
        
        showToolStatus('orthoResult', 'info', 'Generating orthophoto...');
        
        try {
            const response = await fetch(`/api/orthophoto/generate/${modelName}?resolution=${resolution}`, { method: 'POST' });
            const data = await response.json();
            
            if (data.success && data.orthophoto_url) {
                showToolStatus('orthoResult', 'success', 'Orthophoto generated! Opening in new tab...');
                window.open(data.orthophoto_url, '_blank');
            } else {
                showToolStatus('orthoResult', 'error', data.error || 'Generation failed');
            }
        } catch (error) {
            showToolStatus('orthoResult', 'error', error.message);
        }
    });
    
    document.getElementById('generateContoursBtn').addEventListener('click', async () => {
        const select = document.getElementById('orthoProjectSelect');
        const modelName = select.value;
        const interval = document.getElementById('contourInterval').value;
        const resultDiv = document.getElementById('orthoResult');
        
        if (!modelName) {
            showToolStatus('orthoResult', 'error', 'Please select a project');
            return;
        }
        
        showToolStatus('orthoResult', 'info', 'Generating contours...');
        
        try {
            const response = await fetch(`/api/contours/generate/${modelName}?interval=${interval}`, { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                showToolStatus('orthoResult', 'success',
                    `🗺️ Generated ${data.number_of_contours} contours from ${data.min_elevation}m to ${data.max_elevation}m`
                );
            } else {
                showToolStatus('orthoResult', 'error', data.error || 'Generation failed');
            }
        } catch (error) {
            showToolStatus('orthoResult', 'error', error.message);
        }
    });
}

async function initCutFillTool() {
    await loadProjectsToSelect('cutfillCurrentSelect');
    await loadProjectsToSelect('cutfillDesignSelect');
    
    document.getElementById('calculateCutFillBtn').addEventListener('click', async () => {
        const currentSelect = document.getElementById('cutfillCurrentSelect');
        const designSelect = document.getElementById('cutfillDesignSelect');
        const flatElevation = document.getElementById('flatElevation').value;
        const resultDiv = document.getElementById('cutfillResult');
        
        const currentModel = currentSelect.value;
        if (!currentModel) {
            showToolStatus('cutfillResult', 'error', 'Please select a reference surface');
            return;
        }
        
        showToolStatus('cutfillResult', 'info', 'Calculating cut & fill...');
        
        try {
            let url = `/api/cutfill/${currentModel}`;
            if (designSelect.value) {
                url += `?design_model=${designSelect.value}`;
            }
            
            const response = await fetch(url, { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                showToolStatus('cutfillResult', 'success',
                    `✂️ Cut: ${data.cut_volume_cubic_meters} m³ | 🧱 Fill: ${data.fill_volume_cubic_meters} m³ | 📊 Net: ${data.net_volume} m³`
                );
            } else {
                showToolStatus('cutfillResult', 'error', data.error || 'Analysis failed');
            }
        } catch (error) {
            showToolStatus('cutfillResult', 'error', error.message);
        }
    });
}

async function initExportTool() {
    await loadProjectsToSelect('exportProjectSelect');
    
    document.getElementById('exportBtn').addEventListener('click', async () => {
        const select = document.getElementById('exportProjectSelect');
        const modelName = select.value;
        const format = document.querySelector('input[name="exportFormat"]:checked').value;
        const maxPoints = document.getElementById('maxPoints').value;
        const resultDiv = document.getElementById('exportResult');
        
        if (!modelName) {
            showToolStatus('exportResult', 'error', 'Please select a project');
            return;
        }
        
        showToolStatus('exportResult', 'info', `Exporting to ${format.toUpperCase()}...`);
        
        try {
            const response = await fetch(`/api/export/${modelName}/${format}`);
            if (!response.ok) throw new Error('Export failed');
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${modelName.replace('.ply', `.${format}`)}`;
            a.click();
            window.URL.revokeObjectURL(url);
            
            showToolStatus('exportResult', 'success', 'Export complete! Check downloads folder.');
        } catch (error) {
            showToolStatus('exportResult', 'error', error.message);
        }
    });
}

// ============================================
// HELPER FUNCTIONS
// ============================================

async function loadProjects() {
    try {
        const response = await fetch('/api/projects');
        const data = await response.json();
        AppState.projects = data.projects || [];
        
        // Update dashboard
        const projectsList = document.getElementById('projectsList');
        if (projectsList) {
            if (AppState.projects.length === 0) {
                projectsList.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);">No projects yet. Upload your first point cloud!</div>';
            } else {
                projectsList.innerHTML = AppState.projects.map(project => `
                    <div class="project-item">
                        <div class="project-info">
                            <h4><i class="fas fa-cube"></i> ${project.name}</h4>
                            <p><i class="fas fa-calendar"></i> ${new Date(project.created).toLocaleDateString()} | <i class="fas fa-database"></i> ${project.size_mb} MB</p>
                        </div>
                        <div class="project-actions">
                            <button class="btn btn-primary" onclick="viewProject('${project.url}')">
                                <i class="fas fa-eye"></i> View
                            </button>
                            <button class="btn btn-secondary" onclick="copyShareLink('${project.url}')">
                                <i class="fas fa-share-alt"></i> Share
                            </button>
                        </div>
                    </div>
                `).join('');
            }
        }
        
        updateStats();
    } catch (error) {
        console.error('Error loading projects:', error);
    }
}

async function loadProjectsToSelect(selectId) {
    try {
        const response = await fetch('/api/projects');
        const data = await response.json();
        const projects = data.projects || [];
        
        const select = document.getElementById(selectId);
        if (select) {
            select.innerHTML = '<option value="">-- Select a project --</option>' +
                projects.map(p => `<option value="${p.name}">${p.name}</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading projects to select:', error);
    }
}

function updateStats() {
    const totalProjects = AppState.projects.length;
    const totalSize = AppState.projects.reduce((sum, p) => sum + p.size_mb, 0);
    
    const statsElements = {
        totalProjects: document.getElementById('totalProjects'),
        totalSize: document.getElementById('totalSize'),
        storageUsed: document.getElementById('storageUsed')
    };
    
    if (statsElements.totalProjects) statsElements.totalProjects.textContent = totalProjects;
    if (statsElements.totalSize) statsElements.totalSize.textContent = totalSize.toFixed(2);
    if (statsElements.storageUsed) statsElements.storageUsed.textContent = `${((totalSize / 75000) * 100).toFixed(1)}%`;
}

function viewProject(url) {
    window.location.href = url;
}

function copyShareLink(url) {
    const fullUrl = window.location.origin + url;
    navigator.clipboard.writeText(fullUrl);
    showStatus('success', 'Link copied to clipboard!');
}

function showStatus(type, message) {
    const statusDiv = elements.statusMessage;
    if (statusDiv) {
        statusDiv.className = `status-message status-${type}`;
        statusDiv.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i> ${message}`;
        statusDiv.style.display = 'block';
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
}

function showToolStatus(elementId, type, message) {
    const resultDiv = document.getElementById(elementId);
    if (resultDiv) {
        resultDiv.className = `status-message status-${type}`;
        resultDiv.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-spinner fa-spin'}"></i> ${message}`;
        resultDiv.style.display = 'block';
    }
}

function closeModal() {
    elements.modal.classList.remove('active');
}

function openModal(title, content, onConfirm) {
    elements.modalTitle.textContent = title;
    elements.modalBody.innerHTML = content;
    elements.modal.classList.add('active');
    
    if (onConfirm) {
        const oldConfirm = elements.modalConfirm.cloneNode(true);
        elements.modalConfirm.parentNode.replaceChild(oldConfirm, elements.modalConfirm);
        elements.modalConfirm = oldConfirm;
        elements.modalConfirm.addEventListener('click', () => {
            onConfirm();
            closeModal();
        });
    }
}

function loadViewer() {
    // This will be replaced with actual 3D viewer initialization
    AppState.viewerLoaded = true;
}

// Global functions for HTML buttons
window.viewProject = viewProject;
window.copyShareLink = copyShareLink;
