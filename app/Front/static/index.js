document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const loadScannersBtn = document.getElementById('loadScanners');
    const scannerList = document.getElementById('scannerList');
    const scanBtn = document.getElementById('scanBtn');
    const fileInput = document.getElementById('fileInput');
    const dropArea = document.getElementById('dropArea');
    const processBtn = document.getElementById('processBtn');
    const uploadedImage = document.getElementById('uploadedImage');
    const processedImage = document.getElementById('processedImage');
    const loadingDiv = document.getElementById('loading');
    const statusContainer = document.getElementById('statusContainer');
    const saveAllBtn = document.getElementById('saveAllBtn');
    
    // Track edited fields
    let editedFields = new Set();
    
    // Enhanced Status Notification System
    function showStatus(message, type, duration = 5000) {
        const icons = {
            success: "check-circle",
            error: "exclamation-circle",
            info: "info-circle",
            warning: "exclamation-triangle"
        };
        
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
            uploadedImage.src = "https://via.placeholder.com/600x400/4361ee/ffffff?text=Scanned+ID";
            uploadedImage.style.display = "block";
            loadingDiv.style.display = "none";
            showStatus("Document scanned successfully", "success");
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
    
    function handleFiles(files) {
        if (files.length === 0) return;
        
        const file = files[0];
        if (!file.type.match('image.*') && !file.type.match('application/pdf')) {
            showStatus("Please select an image or PDF file", "error");
            return;
        }
        
        showStatus("Loading document...", "info");
        
        const reader = new FileReader();
        reader.onload = function(e) {
            uploadedImage.src = e.target.result;
            uploadedImage.style.display = "block";
            showStatus("Document loaded successfully", "success");
        };
        reader.readAsDataURL(file);
    }
    
    // Process button handler
    processBtn.addEventListener('click', function() {
        if (!uploadedImage.src || uploadedImage.src === window.location.href) {
            showStatus("Please upload or scan a document first", "error");
            return;
        }
        
        showStatus("Processing document... This may take a moment", "info");
        loadingDiv.style.display = "flex";
        
        setTimeout(function() {
            // For testing: Use the uploaded image in processed section
            processedImage.src = uploadedImage.src;
            processedImage.style.display = "block";
            
            // Simulate extracted data
            document.getElementById('firstName').textContent = "John";
            document.getElementById('secondName').textContent = "Doe";
            document.getElementById('fullName').textContent = "John Doe";
            document.getElementById('nationalId').textContent = "12345678901234";
            document.getElementById('address').textContent = "123 Main St, Cairo";
            document.getElementById('birth').textContent = "15/05/1985";
            document.getElementById('gov').textContent = "Cairo";
            document.getElementById('gender').textContent = "Male";
            
            loadingDiv.style.display = "none";
            showStatus("Document processed successfully", "success");
        }, 1500);
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