// Set PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

document.addEventListener('DOMContentLoaded', function() {
    
    const languageToggle = document.getElementById('languageToggle');
    
    // Set default language (English)
    let currentLanguage = 'english';
    let extractedData ={}; 
    
    // Load saved language preference if available
    const savedLanguage = localStorage.getItem('ocrLanguage');
    if (savedLanguage) {
        currentLanguage = savedLanguage;
        languageToggle.checked = (savedLanguage === 'arabic');
        updateLanguageIndicator();
        updateTextDirection();
    }
    
    // Update language when toggle changes
    languageToggle.addEventListener('change', function() {
        currentLanguage = this.checked ? 'arabic' : 'english';
        localStorage.setItem('ocrLanguage', currentLanguage);
        
        // Update visual indicator
        updateLanguageIndicator();
        
        // Show notification
        showStatus(`Language set to ${currentLanguage.toUpperCase()}`, 'success');
    });
    
    // Update language indicator labels
    function updateLanguageIndicator() {
        const labels = document.querySelectorAll('.language-label');
        if (currentLanguage === 'arabic') {
            labels[0].style.fontWeight = 'normal';
            labels[1].style.fontWeight = 'bold';
            // Update extractedData
            if (!extractedData || Object.keys(extractedData).length === 0) return;
            document.getElementById('firstName').textContent = extractedData.firstname.arabic || "N/A";
            document.getElementById('secondName').textContent = extractedData.parentfullname.arabic || "N/A";
            document.getElementById('fullName').textContent = (extractedData.firstname.arabic + " " + extractedData.parentfullname.arabic) || "N/A";
            document.getElementById('nationalId').textContent = extractedData.NationalID.arabic || "N/A";
            document.getElementById('address').textContent = extractedData.address.arabic || "N/A";
            document.getElementById('birth').textContent = extractedData.birth.arabic || "N/A";
            document.getElementById('gov').textContent = extractedData.gov.arabic || "N/A";
            document.getElementById('gender').textContent = extractedData.gender.arabic || "N/A";
        } else {
            labels[0].style.fontWeight = 'bold';
            labels[1].style.fontWeight = 'normal';
            // Update extractedData
            if (!extractedData || Object.keys(extractedData).length === 0) return;
            document.getElementById('firstName').textContent = extractedData.firstname.english || "N/A";
            document.getElementById('secondName').textContent = extractedData.parentfullname.english || "N/A";
            document.getElementById('fullName').textContent = (extractedData.firstname.english + " " + extractedData.parentfullname.english) || "N/A";
            document.getElementById('nationalId').textContent = extractedData.NationalID.english || "N/A";
            document.getElementById('address').textContent = extractedData.address.english || "N/A";
            document.getElementById('birth').textContent = extractedData.birth.english || "N/A";
            document.getElementById('gov').textContent = extractedData.gov.english || "N/A";
            document.getElementById('gender').textContent = extractedData.gender.english || "N/A";
        }
    }
    
    // Initialize language indicator
    updateLanguageIndicator();
    
    // Function to get current language (for use in your processing logic)
    window.getCurrentLanguage = function() {
        return currentLanguage;
    };
    
    // Optional: Update text direction for Arabic content
    function updateTextDirection() {
        const extractedElements = document.querySelectorAll('#extractedInfo .info-text');
        extractedElements.forEach(el => {
            if (currentLanguage === 'arabic') {
                el.classList.add('arabic-text');
            } else {
                el.classList.remove('arabic-text');
            }
        });
    }
    const API_BASE = 'http://127.0.0.1:5000';
    // DOM Elements
    const loadScannersBtn = document.getElementById('loadScanners');
    const scannerList = document.getElementById('scannerList');
    const scanBtn = document.getElementById('scanBtn');
    const fileInput = document.getElementById('fileInput');
    const dropArea = document.getElementById('dropArea');
    const processBtn = document.getElementById('processBtn');
    const uploadedImage = document.getElementById('uploadedImage');
    const uploadedCanvas = document.getElementById('uploadedCanvas');
    const processedImage = document.getElementById('processedImage');
    const loadingDiv = document.getElementById('loading');
    const statusContainer = document.getElementById('statusContainer');
    const saveAllBtn = document.getElementById('saveAllBtn');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    
    // Track edited fields
    let editedFields = new Set();
    let currentFileBlob = null; // Store the current file for processing
    
    // Enhanced Status Notification System
    function showStatus(message, type, duration = 5000) {
        const icons = {
            success: "check-circle",
            error: "exclamation-circle",
            info: "info-circle",
            warning: "exclamation-triangle"
        };
        // increased duration for error messages
        if (type === "error" && duration === 5000) {
            duration = 8000; // 8 seconds for error messages
        }
        const statusEl = document.createElement('div');
        statusEl.className = `status ${type}`;
        statusEl.innerHTML = `
            <i class="fas fa-${icons[type]} status-icon"></i>
            <div class="status-content">${message}</div>
            <button class="status-close">&times;</button>
        `;
        
        statusContainer.appendChild(statusEl);
        
        // Trigger reflow to enable animation
        void statusEl.offsetWidth;
        statusEl.classList.add('show');
        
        // Close button functionality
        const closeBtn = statusEl.querySelector('.status-close');
        closeBtn.addEventListener('click', () => {
            dismissStatus(statusEl);
        });
        
        // Auto-dismiss after duration
        if (duration > 0) {
            setTimeout(() => {
                dismissStatus(statusEl);
            }, duration);
        }
        
        return statusEl;
    }
    
    function dismissStatus(statusEl) {
        if (!statusEl.classList.contains('hide')) {
            statusEl.classList.add('hide');
            statusEl.addEventListener('animationend', () => {
                statusEl.remove();
            });
        }
    }

    // TIFF Support using Canvas
    function displayTiffImage(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = function(e) {
                // Create an image element to test if browser can handle TIFF
                const testImg = new Image();
                testImg.onload = function() {
                    // Browser can handle TIFF natively
                    showImageInContainer(e.target.result, false);
                    resolve(e.target.result);
                };
                testImg.onerror = function() {
                    // Browser can't handle TIFF, show placeholder
                    showTiffPlaceholder(file.name);
                    // Still resolve with the data URL for backend processing
                    resolve(e.target.result);
                };
                testImg.src = e.target.result;
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }

    function showTiffPlaceholder(filename) {
        uploadedImage.style.display = 'none';
        uploadedCanvas.style.display = 'none';
        uploadPlaceholder.innerHTML = `
            <div style="text-align: center; padding: 20px;">
                <i class="fas fa-file-image" style="font-size: 3rem; color: #4361ee; margin-bottom: 10px;"></i>
                <p style="font-weight: 600; margin-bottom: 5px;">TIFF Image Loaded</p>
                <p style="font-size: 0.9rem; color: #666;">${filename}</p>
                <p style="font-size: 0.8rem; color: #999; margin-top: 10px;">
                    Preview not available in browser<br>
                    File ready for processing
                </p>
            </div>
        `;
        uploadPlaceholder.style.display = 'block';
    }

    // PDF Support using PDF.js
    async function displayPdfAsImage(file) {
        try {
            const arrayBuffer = await file.arrayBuffer();
            const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
            const page = await pdf.getPage(1); // Get first page
            
            const scale = 1.5;
            const viewport = page.getViewport({ scale });
            
            const canvas = uploadedCanvas;
            const context = canvas.getContext('2d');
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            
            await page.render({
                canvasContext: context,
                viewport: viewport
            }).promise;
            
            // Show canvas and hide other elements
            showImageInContainer(null, true);
            
            // Convert canvas to blob for processing
            return new Promise(resolve => {
                canvas.toBlob(resolve, 'image/png');
            });
            
        } catch (error) {
            console.error('PDF processing error:', error);
            throw new Error('Failed to process PDF file');
        }
    }

    function showImageInContainer(src, useCanvas = false) {
        if (useCanvas) {
            uploadedCanvas.style.display = 'block';
            uploadedImage.style.display = 'none';
            uploadPlaceholder.style.display = 'none';
        } else {
            uploadedImage.src = src;
            uploadedImage.style.display = 'block';
            uploadedCanvas.style.display = 'none';
            uploadPlaceholder.style.display = 'none';
        }
    }
    
    // Scanner simulation
    loadScannersBtn.addEventListener('click', function() {
        showStatus("Searching for available scanners...", "info");
        
        setTimeout(function() {
            scannerList.innerHTML = `
                <option value="">Select scanner</option>
                <option value="scanner1">HP ScanJet Pro</option>
                <option value="scanner2">Epson V600</option>
            `;
            scannerList.disabled = false;
            scanBtn.disabled = false;
            showStatus("Scanners loaded successfully", "success");
        }, 1000);
    });
    
    // Scan button handler
    scanBtn.addEventListener('click', function() {
        if (!scannerList.value) {
            showStatus("Please select a scanner first", "error");
            return;
        }
        
        showStatus("Initializing document scan...", "info");
        loadingDiv.style.display = "flex";
        
        setTimeout(function() {
            // Simulate scanned image
            const simulatedImageSrc = "https://via.placeholder.com/600x400/4361ee/ffffff?text=Scanned+ID";
            showImageInContainer(simulatedImageSrc, false);
            loadingDiv.style.display = "none";
            showStatus("Document scanned successfully", "success");
            
            // Create a dummy blob for processing
            fetch(simulatedImageSrc).then(r => r.blob()).then(blob => {
                currentFileBlob = blob;
            });
        }, 2000);
    });
    
    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function(eventName) {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(function(eventName) {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(function(eventName) {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.style.borderColor = "var(--primary-color)";
        dropArea.style.backgroundColor = "rgba(67, 97, 238, 0.05)";
    }
    
    function unhighlight() {
        dropArea.style.borderColor = "#ccc";
        dropArea.style.backgroundColor = "";
    }
    
    dropArea.addEventListener('drop', handleDrop, false);
    dropArea.addEventListener('click', function() {
        fileInput.click();
    });
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }
    
    fileInput.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            handleFiles(this.files);
        }
    });
    
    async function handleFiles(files) {
        if (files.length === 0) return;
        
        const file = files[0];
        const fileType = file.type.toLowerCase();
        const fileName = file.name.toLowerCase();
        
        // Check if file is supported
        const isImage = fileType.match('image.*');
        const isPdf = fileType === 'application/pdf';
        const isTiff = fileType.includes('tiff') || fileName.endsWith('.tiff') || fileName.endsWith('.tif');
        
        if (!isImage && !isPdf && !isTiff) {
            showStatus("Please select an image, TIFF, or PDF file", "error");
            return;
        }
        
        showStatus("Loading document...", "info");
        
        try {
            if (isPdf) {
                // Handle PDF files
                currentFileBlob = await displayPdfAsImage(file);
                showStatus("PDF loaded and converted successfully", "success");
            } else if (isTiff) {
                // Handle TIFF files
                await displayTiffImage(file);
                currentFileBlob = file; // Store original file for backend processing
                showStatus("TIFF image loaded successfully", "success");
            } else {
                // Handle regular images
                const reader = new FileReader();
                reader.onload = function(e) {
                    showImageInContainer(e.target.result, false);
                    showStatus("Image loaded successfully", "success");
                };
                reader.readAsDataURL(file);
                currentFileBlob = file;
            }
        } catch (error) {
            console.error('File processing error:', error);
            showStatus("Error loading file: " + error.message, "error");
        }
    }
    
    // Process button handler
    processBtn.addEventListener('click', async function () {
        if (!currentFileBlob && !uploadedImage.src && uploadedCanvas.style.display !== 'block') {
            showStatus("Please upload or scan a document first", "error");
            return;
        }

        showStatus("Processing document... This may take a moment", "info");
        loadingDiv.style.display = "flex";

        try {
            const formData = new FormData();
            
            if (currentFileBlob) {
                // Use the stored file blob
                formData.append('image', currentFileBlob, 'document');
            } else if (uploadedCanvas.style.display === 'block') {
                // Convert canvas to blob (for PDF)
                const blob = await new Promise(resolve => {
                    uploadedCanvas.toBlob(resolve, 'image/png');
                });
                formData.append('image', blob, 'document.png');
            } else if (uploadedImage.src && uploadedImage.src.startsWith('data:')) {
                // Convert data URL to blob
                const blob = await fetch(uploadedImage.src).then(r => r.blob());
                formData.append('image', blob, 'document.png');
            } else if (uploadedImage.src && !uploadedImage.src.startsWith('data:')) {
                // For simulated scanner images (placeholder), we'll use the URL
                const response = await fetch(uploadedImage.src);
                const blob = await response.blob();
                formData.append('image', blob, 'scanned_document.png');
            }

            // Send to OCR processing API  
            const response = await fetch(`${API_BASE}/process`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`${errorText} -status- ${response.status} ${response.statusText}`);
            }

            const result = await response.json();
            console.log('Processing result:', result);
            // Display the processed image
            if (result.processed_image) {
                processedImage.src = `data:image/png;base64,${result.processed_image}`;
                processedImage.style.display = "block";
            }

            // Update extracted data fields
            console.log('Extracted result data:', result.data);
            if (result.data) {
                console.log('Populating extracted data fields');
                extractedData = result.data; // Store extracted data
                if (currentLanguage === 'arabic') {
                    console.log('Arabic');
                    document.getElementById('firstName').textContent = extractedData.firstname.arabic || "N/A";
                    document.getElementById('secondName').textContent = extractedData.parentfullname.arabic || "N/A";
                    document.getElementById('fullName').textContent = (extractedData.firstname.arabic + " " + extractedData.parentfullname.arabic) || "N/A";
                    document.getElementById('nationalId').textContent = extractedData.NationalID.arabic || "N/A";
                    document.getElementById('address').textContent = extractedData.address.arabic || "N/A";
                    document.getElementById('birth').textContent = extractedData.birth.arabic || "N/A";
                    document.getElementById('gov').textContent = extractedData.gov.arabic || "N/A";
                    document.getElementById('gender').textContent = extractedData.gender.arabic || "N/A";
                } else {
                    console.log('English');
                    console.log(extractedData.firstname);
                    document.getElementById('firstName').textContent = extractedData.firstname.english || "N/A";
                    document.getElementById('secondName').textContent = extractedData.parentfullname.english || "N/A";
                    document.getElementById('fullName').textContent = (extractedData.firstname.english + " " + extractedData.parentfullname.english) || "N/A";
                    document.getElementById('nationalId').textContent = extractedData.NationalID.english || "N/A";
                    document.getElementById('address').textContent = extractedData.address.english || "N/A";
                    document.getElementById('birth').textContent = extractedData.birth.english || "N/A";
                    document.getElementById('gov').textContent = extractedData.gov.english || "N/A";
                    document.getElementById('gender').textContent = extractedData.gender.english || "N/A";
                }
            }
            if( result.warning){
                showStatus("Warning: " + result.warning, "warning");
            }

            showStatus("National ID processed successfully", "success");
        } catch (error) {
            console.error('Processing error:', error);
            showStatus("Failed to process the National ID Card: " + error.message, "error");
        } finally {
            loadingDiv.style.display = "none";
        }
    });
    
    // Edit/Save functionality for extracted data
    document.querySelectorAll('.edit-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            const saveBtn = this.nextElementSibling;
            
            // Enable editing
            targetElement.contentEditable = "true";
            targetElement.classList.add('editable');
            targetElement.focus();
            
            // Toggle button visibility
            this.style.display = 'none';
            saveBtn.style.display = 'inline-flex';
            
            // Track that this field is being edited
            editedFields.add(targetId);
            updateSaveAllButton();
        });
    });
    
    document.querySelectorAll('.save-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            const editBtn = this.previousElementSibling;
            
            // Disable editing
            targetElement.contentEditable = "false";
            targetElement.classList.remove('editable');
            
            // Toggle button visibility
            this.style.display = 'none';
            editBtn.style.display = 'inline-flex';
            
            // Remove from edited fields
            editedFields.delete(targetId);
            updateSaveAllButton();
            
            showStatus("Changes saved", "success", 2000);
            
            // Update full name if first or second name was edited
            if (targetId === 'firstName' || targetId === 'secondName') {
                const firstName = document.getElementById('firstName').textContent;
                const secondName = document.getElementById('secondName').textContent;
                document.getElementById('fullName').textContent = `${firstName} ${secondName}`;
            }
        });
    });
    
    // Copy buttons functionality
    document.querySelectorAll('.copy-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            const textToCopy = targetElement.textContent;
            
            navigator.clipboard.writeText(textToCopy).then(function() {
                const originalText = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-check"></i> Copied';
                btn.style.background = "var(--success-color)";
                btn.style.color = "white";
                btn.style.borderColor = "var(--success-color)";
                
                setTimeout(function() {
                    btn.innerHTML = originalText;
                    btn.style.background = "";
                    btn.style.color = "";
                    btn.style.borderColor = "";
                }, 1500);
                
                showStatus("Copied to clipboard", "success", 2000);
            }).catch(function() {
                showStatus("Failed to copy text", "error", 2000);
            });
        });
    });
    
    // Save All button functionality
    saveAllBtn.addEventListener('click', function() {
        document.querySelectorAll('.save-btn').forEach(btn => {
            if (btn.style.display === 'inline-flex') {
                btn.click();
            }
        });
        
        showStatus("All changes saved", "success");
        saveAllBtn.style.display = 'none';
    });
    
    // Update Save All button visibility
    function updateSaveAllButton() {
        saveAllBtn.style.display = editedFields.size > 0 ? 'block' : 'none';
    }
    
    // Handle Enter key in editable fields
    document.querySelectorAll('.info-text').forEach(field => {
        field.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const saveBtn = this.closest('.info-value').querySelector('.save-btn');
                if (saveBtn) saveBtn.click();
            }
        });
    });
});