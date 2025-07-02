document.addEventListener('DOMContentLoaded', function() {
    const testForm = document.getElementById('testForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const responseCard = document.getElementById('responseCard');
    const responseContent = document.getElementById('responseContent');
    const actionSelect = document.getElementById('action');
    const qualityGroup = document.getElementById('qualityGroup');
    const audioOnlyCheckbox = document.getElementById('audioOnly');

    // Handle action change
    actionSelect.addEventListener('change', function() {
        if (this.value === 'info') {
            qualityGroup.style.display = 'none';
            audioOnlyCheckbox.checked = false;
        } else {
            qualityGroup.style.display = 'block';
        }
    });

    // Handle audio-only checkbox
    audioOnlyCheckbox.addEventListener('change', function() {
        const qualitySelect = document.getElementById('quality');
        if (this.checked) {
            qualitySelect.innerHTML = `
                <option value="128kbps">128kbps</option>
                <option value="192kbps">192kbps</option>
                <option value="256kbps">256kbps</option>
                <option value="320kbps">320kbps</option>
            `;
        } else {
            qualitySelect.innerHTML = `
                <option value="720p">720p (HD)</option>
                <option value="1080p">1080p (Full HD)</option>
                <option value="480p">480p</option>
                <option value="360p">360p</option>
                <option value="240p">240p</option>
                <option value="144p">144p</option>
            `;
        }
    });

    // Handle form submission
    testForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const url = document.getElementById('videoUrl').value;
        const action = document.getElementById('action').value;
        const quality = document.getElementById('quality').value;
        const audioOnly = document.getElementById('audioOnly').checked;
        
        if (!url) {
            alert('Please enter a YouTube URL');
            return;
        }

        // Show loading state
        loadingSpinner.classList.remove('d-none');
        responseCard.style.display = 'none';
        testForm.classList.add('loading');

        try {
            let endpoint = '';
            let requestBody = { url: url };

            if (action === 'info') {
                endpoint = '/api/video-info';
            } else if (action === 'download-link') {
                endpoint = '/api/download-link';
                requestBody.quality = quality;
                requestBody.audio_only = audioOnly;
            }

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            const data = await response.json();
            
            // Display response
            responseContent.textContent = JSON.stringify(data, null, 2);
            responseCard.style.display = 'block';
            
            // Scroll to response
            responseCard.scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            console.error('Error:', error);
            responseContent.textContent = JSON.stringify({
                error: 'Failed to make request: ' + error.message,
                success: false
            }, null, 2);
            responseCard.style.display = 'block';
        } finally {
            // Hide loading state
            loadingSpinner.classList.add('d-none');
            testForm.classList.remove('loading');
        }
    });

    // Add copy to clipboard functionality
    responseContent.addEventListener('click', function() {
        navigator.clipboard.writeText(this.textContent).then(function() {
            // Show temporary success message
            const originalText = responseContent.textContent;
            responseContent.textContent = 'Response copied to clipboard!';
            setTimeout(() => {
                responseContent.textContent = originalText;
            }, 2000);
        }).catch(function(err) {
            console.error('Failed to copy: ', err);
        });
    });

    // Add example URL for testing
    const exampleButton = document.createElement('button');
    exampleButton.type = 'button';
    exampleButton.className = 'btn btn-outline-secondary btn-sm mt-2';
    exampleButton.innerHTML = '<i class="fas fa-magic me-1"></i> Use Example URL';
    exampleButton.addEventListener('click', function() {
        document.getElementById('videoUrl').value = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ';
    });
    
    document.getElementById('videoUrl').parentNode.appendChild(exampleButton);
});
