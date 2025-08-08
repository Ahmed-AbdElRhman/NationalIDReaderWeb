
document.addEventListener('DOMContentLoaded', function () {

    processBtn.addEventListener('click', async function () {
        if (!uploadedImage.src || uploadedImage.src === window.location.href) {
            showStatus("Please upload or scan a document first", "error");
            return;
        }

        showStatus("Processing document... This may take a moment", "info");
        loadingDiv.style.display = "flex";

        try {
            // Prepare the form data
            const formData = new FormData();

            // Check if the image is from a file upload or scanner simulation
            if (uploadedImage.src.startsWith('data:')) {
                // Convert data URL to blob
                const blob = await fetch(uploadedImage.src).then(r => r.blob());
                formData.append('image', blob, 'document.png');
            } else {
                // For simulated scanner images (placeholder), we'll use the URL
                // Note: In a real app, you'd want to upload the actual scanned image
                const response = await fetch(uploadedImage.src);
                const blob = await response.blob();
                formData.append('image', blob, 'scanned_document.png');
            }

            // Send to OCR processing API
            const response = await fetch('http://127.0.0.1:5000/process', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}`);
            }

            const result = await response.json();

            // Display the processed image
            if (result.processed_image) {
                processedImage.src = `data:image/png;base64,${result.processed_image}`;
                processedImage.style.display = "block";
            }

            // Update extracted data fields
            if (result.data) {
                document.getElementById('firstName').textContent = result.data.first_name || "N/A";
                document.getElementById('secondName').textContent = result.data.second_name || "N/A";
                document.getElementById('fullName').textContent = result.data.full_name || "N/A";
                document.getElementById('nationalId').textContent = result.data.national_id || "N/A";
                document.getElementById('address').textContent = result.data.address || "N/A";
                document.getElementById('birth').textContent = result.data.birth || "N/A";
                document.getElementById('gov').textContent = result.data.gov || "N/A";
                document.getElementById('gender').textContent = result.data.gender || "N/A";
            }

            showStatus("Document processed successfully", "success");
        } catch (error) {
            console.error('Processing error:', error);
            showStatus("Failed to process document: " + error.message, "error");
        } finally {
            loadingDiv.style.display = "none";
        }
    });

    // [Rest of the JavaScript code remains the same]
    // ...
});
