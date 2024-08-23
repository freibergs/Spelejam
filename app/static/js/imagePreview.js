document.addEventListener('DOMContentLoaded', function() {
    // Handle main image preview
    const mainImageInput = document.getElementById('mainImageInput');
    if (mainImageInput) {
        mainImageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.getElementById('mainImagePreview');
                    if (preview) {
                        preview.innerHTML = `<img src="${e.target.result}" alt="Main Image Preview">`;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Handle additional images preview
    const additionalImagesInput = document.getElementById('additionalImagesInput');
    if (additionalImagesInput) {
        additionalImagesInput.addEventListener('change', function() {
            const previewContainer = document.getElementById('imagePreviewContainer');
            if (previewContainer) {
                previewContainer.innerHTML = ''; // Clear previous previews
                const files = Array.from(this.files).slice(0, 5); // Limit to 5 files
                files.forEach(file => {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const preview = document.createElement('div');
                        preview.className = 'image-preview';
                        preview.innerHTML = `<img src="${e.target.result}" alt="Image Preview">`;
                        previewContainer.appendChild(preview);
                    };
                    reader.readAsDataURL(file);
                });
            }
        });
    }
});
