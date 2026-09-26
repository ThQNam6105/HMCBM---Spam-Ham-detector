document.addEventListener('DOMContentLoaded', () => {
    // --- STATE VARIABLES ---
    let selectedFiles = [];
    let currentResults = [];
    let selectedModelKeys = ['naive_bayes', 'knn', 'decision_tree'];

    // --- DOM ELEMENTS ---
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const selectedFilesContainer = document.getElementById('selectedFilesContainer');
    const filesList = document.getElementById('filesList');
    const fileCount = document.getElementById('fileCount');
    const clearFilesBtn = document.getElementById('clearFilesBtn');

    const modelAll = document.getElementById('model-all');
    const modelNb = document.getElementById('model-nb');
    const modelKnn = document.getElementById('model-knn');
    const modelDt = document.getElementById('model-dt');

    const analyzeBtn = document.getElementById('analyzeBtn');
    const analyzeBtnText = document.getElementById('analyzeBtnText');

    const emptyStateCard = document.getElementById('emptyStateCard');
    const resultsSection = document.getElementById('resultsSection');
    const metricTotal = document.getElementById('metricTotal');
    const metricSpam = document.getElementById('metricSpam');
    const metricHam = document.getElementById('metricHam');
    const metricAgreement = document.getElementById('metricAgreement');
    const agreementBox = document.getElementById('agreementBox');
    const modelBreakdownRow = document.getElementById('modelBreakdownRow');

    const tableHeaderRow = document.getElementById('tableHeaderRow');
    const tableBody = document.getElementById('tableBody');
    const singleCardsContainer = document.getElementById('singleCardsContainer');

    const detailCard = document.getElementById('detailCard');
    const closeDetailBtn = document.getElementById('closeDetailBtn');
    const detailFilename = document.getElementById('detailFilename');
    const detailSubject = document.getElementById('detailSubject');
    const detailAgreement = document.getElementById('detailAgreement');
    const detailAgreementWrapper = document.getElementById('detailAgreementWrapper');
    const detailPredictionsGrid = document.getElementById('detailPredictionsGrid');
    const toggleProcessedBtn = document.getElementById('toggleProcessedBtn');
    const processedTextContent = document.getElementById('processedTextContent');
    const preprocessedTextCode = document.getElementById('preprocessedTextCode');
    const toggleIcon = document.getElementById('toggleIcon');

    // --- HELPER FUNCTIONS ---
    function formatBytes(bytes, decimals = 1) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    function updateAnalyzeButtonState() {
        const hasFiles = selectedFiles.length > 0;
        const hasModels = getSelectedModels().length > 0;
        analyzeBtn.disabled = !(hasFiles && hasModels);
    }

    function getSelectedModels() {
        const models = [];
        if (modelNb.checked) models.push('naive_bayes');
        if (modelKnn.checked) models.push('knn');
        if (modelDt.checked) models.push('decision_tree');
        return models;
    }

    function syncModelSelectionUI() {
        const indModels = [modelNb, modelKnn, modelDt];
        const allChecked = indModels.every(m => m.checked);
        modelAll.checked = allChecked;

        document.getElementById('opt-all').classList.toggle('active', allChecked);
        document.getElementById('opt-nb').classList.toggle('active', modelNb.checked);
        document.getElementById('opt-knn').classList.toggle('active', modelKnn.checked);
        document.getElementById('opt-dt').classList.toggle('active', modelDt.checked);

        updateAnalyzeButtonState();
    }

    // --- DRAG & DROP & FILE INPUT LISTENERS ---
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const files = Array.from(e.dataTransfer.files).filter(f => f.name.toLowerCase().endsWith('.eml'));
        if (files.length > 0) {
            addFiles(files);
        } else {
            alert('Vui lòng chọn hoặc kéo thả định dạng file email hợp lệ (.eml).');
        }
    });

    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files).filter(f => f.name.toLowerCase().endsWith('.eml'));
        if (files.length > 0) {
            addFiles(files);
        }
        fileInput.value = '';
    });

    function addFiles(newFiles) {
        newFiles.forEach(file => {
            if (!selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
                selectedFiles.push(file);
            }
        });
        renderFilesList();
        updateAnalyzeButtonState();
    }

    function renderFilesList() {
        if (selectedFiles.length === 0) {
            selectedFilesContainer.style.display = 'none';
            filesList.innerHTML = '';
            fileCount.textContent = '0';
            return;
        }

        selectedFilesContainer.style.display = 'block';
        fileCount.textContent = selectedFiles.length;
        filesList.innerHTML = '';

        selectedFiles.forEach((file, index) => {
            const li = document.createElement('li');
            li.className = 'file-item';
            li.innerHTML = `
                <div class="file-item-info">
                    <i class="fa-solid fa-envelope text-muted"></i>
                    <span class="file-name" title="${file.name}">${file.name}</span>
                    <span class="file-size">(${formatBytes(file.size)})</span>
                </div>
                <button type="button" class="remove-file-btn" data-index="${index}" title="Xóa file">&times;</button>
            `;
            filesList.appendChild(li);
        });

        document.querySelectorAll('.remove-file-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = parseInt(e.currentTarget.getAttribute('data-index'), 10);
                selectedFiles.splice(idx, 1);
                renderFilesList();
                updateAnalyzeButtonState();
            });
        });
    }

    clearFilesBtn.addEventListener('click', () => {
        selectedFiles = [];
        renderFilesList();
        updateAnalyzeButtonState();
    });

    // --- MODEL SELECTION LISTENERS ---
    modelAll.addEventListener('change', () => {
        const isChecked = modelAll.checked;
        modelNb.checked = isChecked;
        modelKnn.checked = isChecked;
        modelDt.checked = isChecked;
        syncModelSelectionUI();
    });

    [modelNb, modelKnn, modelDt].forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            syncModelSelectionUI();
        });
    });

    // --- ANALYZE ACTION ---
    analyzeBtn.addEventListener('click', async () => {
        selectedModelKeys = getSelectedModels();
        if (selectedFiles.length === 0 || selectedModelKeys.length === 0) return;

        // UI Loading state
        analyzeBtn.disabled = true;
        analyzeBtnText.textContent = 'Đang phân tích...';
        analyzeBtn.querySelector('i').className = 'fa-solid fa-spinner fa-spin';

        const formData = new FormData();
        selectedFiles.forEach(file => formData.append('files', file));
        selectedModelKeys.forEach(m => formData.append('models', m));

        try {
            const response = await fetch('/api/classify', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (!data.success) {
                alert('Phân tích thất bại: ' + (data.error || 'Lỗi không xác định từ máy chủ'));
                return;
            }

            currentResults = data.results;
            renderResultsDashboard();

        } catch (err) {
            console.error(err);
            alert('Đã xảy ra lỗi kết nối với máy chủ khi phân tích email.');
        } finally {
            // Restore button state
            analyzeBtn.disabled = false;
            analyzeBtnText.textContent = 'Phân tích Email';
            analyzeBtn.querySelector('i').className = 'fa-solid fa-microchip';
        }
    });

    // --- RENDER RESULTS DASHBOARD ---
    function renderResultsDashboard() {
        emptyStateCard.style.display = 'none';
        resultsSection.style.display = 'block';
        detailCard.style.display = 'none';

        const validResults = currentResults.filter(r => !r.error);
        const totalCount = currentResults.length;

        metricTotal.textContent = totalCount;

        // Populate Table Header
        tableHeaderRow.innerHTML = `
            <th>Tên file</th>
            <th>Tiêu đề</th>
        `;

        const modelDisplayNames = {
            'naive_bayes': 'Naive Bayes',
            'knn': 'KNN',
            'decision_tree': 'Decision Tree'
        };

        selectedModelKeys.forEach(key => {
            const th = document.createElement('th');
            th.textContent = modelDisplayNames[key] || key;
            tableHeaderRow.appendChild(th);
        });

        // Compute batch stats
        let totalSpam = 0;
        let totalHam = 0;
        let agreeCount = 0;

        const modelStats = {};
        selectedModelKeys.forEach(k => modelStats[k] = { spam: 0, ham: 0 });

        validResults.forEach(item => {
            const preds = item.predictions || {};
            const labels = [];

            selectedModelKeys.forEach(k => {
                if (preds[k]) {
                    const lbl = preds[k].label;
                    labels.push(lbl);
                    if (lbl === 'spam') modelStats[k].spam++;
                    else if (lbl === 'ham') modelStats[k].ham++;
                }
            });

            const spamVotes = labels.filter(l => l === 'spam').length;
            const hamVotes = labels.filter(l => l === 'ham').length;

            if (spamVotes >= hamVotes && spamVotes > 0) totalSpam++;
            else totalHam++;

            if (selectedModelKeys.length > 1 && labels.length === selectedModelKeys.length) {
                const allSame = labels.every(l => l === labels[0]);
                if (allSame) agreeCount++;
            }
        });

        metricSpam.textContent = totalSpam;
        metricHam.textContent = totalHam;

        if (selectedModelKeys.length > 1 && validResults.length > 0) {
            agreementBox.style.display = 'flex';
            metricAgreement.textContent = `${agreeCount} / ${validResults.length}`;
        } else {
            agreementBox.style.display = 'none';
        }

        // Render Model Breakdown Row
        modelBreakdownRow.innerHTML = '';
        selectedModelKeys.forEach(k => {
            const pill = document.createElement('div');
            pill.className = 'model-stat-pill';
            pill.innerHTML = `
                <div class="model-stat-title">${modelDisplayNames[k]}</div>
                <div class="model-stat-counts">
                    <span class="text-danger">Spam: ${modelStats[k].spam}</span>
                    <span class="text-success" style="color:#16a34a;">Ham: ${modelStats[k].ham}</span>
                </div>
            `;
            modelBreakdownRow.appendChild(pill);
        });

        // Render Table Rows
        tableBody.innerHTML = '';
        currentResults.forEach((item, index) => {
            const tr = document.createElement('tr');
            tr.setAttribute('data-index', index);

            if (item.error) {
                tr.innerHTML = `
                    <td><strong>${item.filename}</strong></td>
                    <td colspan="${selectedModelKeys.length + 1}" class="text-danger">
                        <i class="fa-solid fa-triangle-exclamation"></i> ${item.error}
                    </td>
                `;
            } else {
                let rowHTML = `
                    <td><strong>${item.filename}</strong></td>
                    <td class="eml-subject-cell">${item.subject}</td>
                `;

                selectedModelKeys.forEach(k => {
                    const p = (item.predictions || {})[k];
                    if (p) {
                        const isSpam = p.label === 'spam';
                        const badgeClass = isSpam ? 'badge-spam' : 'badge-ham';
                        const labelText = isSpam ? 'SPAM' : 'HAM';
                        const probText = p.probability !== null && p.probability !== undefined 
                            ? ` (${(p.probability * 100).toFixed(1)}%)` 
                            : '';
                        rowHTML += `
                            <td>
                                <span class="badge ${badgeClass}">${labelText}${probText}</span>
                            </td>
                        `;
                    } else {
                        rowHTML += `<td><span class="text-muted">N/A</span></td>`;
                    }
                });

                tr.innerHTML = rowHTML;

                tr.addEventListener('click', () => {
                    openDetailView(item);
                });
            }

            tableBody.appendChild(tr);
        });

        // Single Email View Cards (if 1 email)
        if (totalCount === 1 && validResults.length === 1) {
            singleCardsContainer.style.display = 'grid';
            singleCardsContainer.innerHTML = '';
            const singleItem = validResults[0];

            selectedModelKeys.forEach(k => {
                const p = singleItem.predictions[k];
                if (p) {
                    const isSpam = p.label === 'spam';
                    const badgeClass = isSpam ? 'badge-spam' : 'badge-ham';
                    const labelText = isSpam ? 'SPAM' : 'HAM';
                    const confHTML = p.probability !== null && p.probability !== undefined
                        ? `Độ tin cậy: <strong>${(p.probability * 100).toFixed(2)}%</strong>`
                        : `Kết quả dự đoán: <strong>${labelText}</strong>`;

                    const card = document.createElement('div');
                    card.className = 'model-res-card';
                    card.innerHTML = `
                        <h3>${modelDisplayNames[k]}</h3>
                        <div class="prediction-badge-lg badge ${badgeClass}">${labelText}</div>
                        <div class="prediction-confidence">${confHTML}</div>
                    `;
                    singleCardsContainer.appendChild(card);
                }
            });

            openDetailView(singleItem);
        } else {
            singleCardsContainer.style.display = 'none';
        }

        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // --- OPEN DETAIL VIEW PANEL ---
    function openDetailView(item) {
        if (item.error) return;

        detailCard.style.display = 'block';
        detailFilename.textContent = item.filename;
        detailSubject.textContent = item.subject;

        const modelDisplayNames = {
            'naive_bayes': 'Naive Bayes',
            'knn': 'K-Nearest Neighbors (KNN)',
            'decision_tree': 'Decision Tree'
        };

        const preds = item.predictions || {};
        const activeKeys = Object.keys(preds);

        let spamCount = 0;
        let totalModels = activeKeys.length;

        detailPredictionsGrid.innerHTML = '';

        activeKeys.forEach(k => {
            const p = preds[k];
            if (p.label === 'spam') spamCount++;

            const isSpam = p.label === 'spam';
            const badgeClass = isSpam ? 'badge-spam' : 'badge-ham';
            const labelText = isSpam ? 'SPAM' : 'HAM';
            const confHTML = p.probability !== null && p.probability !== undefined
                ? `Độ tin cậy: <strong>${(p.probability * 100).toFixed(2)}%</strong>`
                : `Kết quả dự đoán: <strong>${labelText}</strong>`;

            const card = document.createElement('div');
            card.className = 'model-res-card';
            card.innerHTML = `
                <h3>${modelDisplayNames[k] || k}</h3>
                <div class="prediction-badge-lg badge ${badgeClass}">${labelText}</div>
                <div class="prediction-confidence">${confHTML}</div>
            `;
            detailPredictionsGrid.appendChild(card);
        });

        if (totalModels > 1) {
            detailAgreementWrapper.style.display = 'flex';
            detailAgreement.textContent = `${spamCount} / ${totalModels} mô hình phân loại email này là SPAM`;
        } else {
            detailAgreementWrapper.style.display = 'none';
        }

        // Preprocessed text preview
        preprocessedTextCode.textContent = item.processed_text || '(Không có nội dung sau khi tiền xử lý)';
        processedTextContent.style.display = 'none';
        toggleIcon.className = 'fa-solid fa-chevron-down toggle-icon';

        detailCard.scrollIntoView({ behavior: 'smooth' });
    }

    closeDetailBtn.addEventListener('click', () => {
        detailCard.style.display = 'none';
    });

    toggleProcessedBtn.addEventListener('click', () => {
        const isHidden = processedTextContent.style.display === 'none';
        processedTextContent.style.display = isHidden ? 'block' : 'none';
        toggleIcon.className = isHidden 
            ? 'fa-solid fa-chevron-up toggle-icon' 
            : 'fa-solid fa-chevron-down toggle-icon';
    });
});
