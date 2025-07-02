// DOM Elements
const imageUpload = document.getElementById('imageUpload');
const audioUpload = document.getElementById('audioUpload');
const imageInput = document.getElementById('imageInput');
const audioInput = document.getElementById('audioInput');
const imagePreview = document.getElementById('imagePreview');
const audioInfo = document.getElementById('audioInfo');
const processBtn = document.getElementById('processBtn');
const testBtn = document.getElementById('testBtn');
const progressSection = document.getElementById('progressSection');
const progressFill = document.querySelector('.progress-fill');
const progressText = document.querySelector('.progress-text');
const resultSection = document.getElementById('resultSection');
const resultVideo = document.getElementById('resultVideo');
const downloadBtn = document.getElementById('downloadBtn');
const resetBtn = document.getElementById('resetBtn');
const styleSelect = document.getElementById('styleSelect');
const canadianInfo = document.getElementById('canadianInfo');
const standardInfo = document.getElementById('standardInfo');
const manualMouthPos = document.getElementById('manualMouthPos');
const mouthControls = document.getElementById('mouthControls');
const mouthX = document.getElementById('mouthX');
const mouthY = document.getElementById('mouthY');
const resetMouthPos = document.getElementById('resetMouthPos');
const positionFeedback = document.getElementById('positionFeedback');
const mouthMarker = document.getElementById('mouthMarker');
const imagePreviewContainer = document.querySelector('.image-preview-container');
const openMouthSelector = document.getElementById('openMouthSelector');
const mouthSelectorModal = document.getElementById('mouthSelectorModal');
const closeMouthSelector = document.getElementById('closeMouthSelector');
const mouthSelectorImage = document.getElementById('mouthSelectorImage');
const mouthSelectorMarker = document.getElementById('mouthSelectorMarker');
const currentCoords = document.getElementById('currentCoords');
const confirmMouthSelection = document.getElementById('confirmMouthSelection');
const cancelMouthSelection = document.getElementById('cancelMouthSelection');
const previewMouthSprite = document.getElementById('previewMouthSprite');
const mouthPreviewCanvas = document.getElementById('mouthPreviewCanvas');

// State
let selectedImage = null;
let selectedAudio = null;
let currentVideoUrl = null;

// API URL - pointing to Flask backend on port 5000
const API_URL = 'http://localhost:5000';

// Setup drag and drop
setupDragDrop(imageUpload, handleImageFile);
setupDragDrop(audioUpload, handleAudioFile);

// Setup click to upload
imageUpload.addEventListener('click', () => imageInput.click());
audioUpload.addEventListener('click', () => audioInput.click());

// File input handlers
imageInput.addEventListener('change', (e) => {
    if (e.target.files[0]) {
        handleImageFile(e.target.files[0]);
    }
});

audioInput.addEventListener('change', (e) => {
    if (e.target.files[0]) {
        handleAudioFile(e.target.files[0]);
    }
});

// Process button
processBtn.addEventListener('click', processAnimation);

// Test button
testBtn.addEventListener('click', testUpload);

// Download button
downloadBtn.addEventListener('click', downloadVideo);

// Reset button
resetBtn.addEventListener('click', resetForm);

// Style selector
styleSelect.addEventListener('change', updateStyleInfo);

// Manual mouth positioning
manualMouthPos.addEventListener('change', toggleMouthControls);

// Click on image to set mouth position
imagePreview.addEventListener('click', setMouthPosition);

// Reset mouth position button
resetMouthPos.addEventListener('click', resetMouthPosition);

// Mouth selector modal events
openMouthSelector.addEventListener('click', openMouthSelectorModal);
closeMouthSelector.addEventListener('click', closeMouthSelectorModal);
cancelMouthSelection.addEventListener('click', closeMouthSelectorModal);
confirmMouthSelection.addEventListener('click', confirmMouthPosition);
previewMouthSprite.addEventListener('click', previewMouthSpriteAtPosition);
mouthSelectorImage.addEventListener('click', setMouthPositionInModal);

// Close modal when clicking outside
mouthSelectorModal.addEventListener('click', (e) => {
    if (e.target === mouthSelectorModal) {
        closeMouthSelectorModal();
    }
});

// Update mouth marker when coordinates change
mouthX.addEventListener('input', updateMouthMarkerPosition);
mouthY.addEventListener('input', updateMouthMarkerPosition);

// Image hover effects for mouth positioning
imagePreview.addEventListener('mouseenter', handleImageHover);
imagePreview.addEventListener('mouseleave', handleImageLeave);

// Initialize style info
updateStyleInfo();

// Enable debug mode with keyboard shortcut
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        testBtn.style.display = testBtn.style.display === 'none' ? 'inline-block' : 'none';
        console.log('Debug mode:', testBtn.style.display !== 'none' ? 'ON' : 'OFF');
    }
});

function setupDragDrop(element, handler) {
    element.addEventListener('dragover', (e) => {
        e.preventDefault();
        element.classList.add('dragover');
    });
    
    element.addEventListener('dragleave', () => {
        element.classList.remove('dragover');
    });
    
    element.addEventListener('drop', (e) => {
        e.preventDefault();
        element.classList.remove('dragover');
        
        const file = e.dataTransfer.files[0];
        if (file) {
            handler(file);
        }
    });
}

function handleImageFile(file) {
    if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
    }
    
    selectedImage = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        imagePreview.src = e.target.result;
        imagePreviewContainer.style.display = 'block';
        imageUpload.querySelector('.upload-content').style.display = 'none';
        imageUpload.classList.add('has-file');
        
        // Reset mouth positioning when new image is loaded
        resetMouthPosition();
    };
    reader.readAsDataURL(file);
    
    checkCanProcess();
}

function handleAudioFile(file) {
    // More flexible audio file validation
    const audioExtensions = ['mp3', 'wav', 'mp4', 'ogg', 'm4a', 'aac'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    
    if (!file.type.startsWith('audio/') && !audioExtensions.includes(fileExtension)) {
        alert('Please select an audio file (MP3, WAV, etc.)');
        return;
    }
    
    console.log('Audio file:', file.name, 'Type:', file.type, 'Size:', file.size);
    
    selectedAudio = file;
    
    // Show audio info
    audioInfo.style.display = 'block';
    audioInfo.querySelector('.audio-name').textContent = file.name;
    audioUpload.querySelector('.upload-content').style.display = 'none';
    audioUpload.classList.add('has-file');
    
    checkCanProcess();
}

function updateStyleInfo() {
    const selectedStyle = styleSelect.value;
    
    // Get nutcracker info element
    const nutcrackerInfo = document.getElementById('nutcrackerInfo');
    
    // Hide all style info divs
    canadianInfo.style.display = 'none';
    standardInfo.style.display = 'none';
    nutcrackerInfo.style.display = 'none';
    
    // Show the selected style info
    if (selectedStyle === 'standard') {
        standardInfo.style.display = 'block';
    } else if (selectedStyle === 'nutcracker') {
        nutcrackerInfo.style.display = 'block';
    } else {
        canadianInfo.style.display = 'block';
    }
}

function toggleMouthControls() {
    if (manualMouthPos.checked) {
        mouthControls.style.display = 'flex';
        updateImageInteractivity();
        updateMouthMarkerPosition();
    } else {
        mouthControls.style.display = 'none';
        mouthX.value = '';
        mouthY.value = '';
        mouthMarker.style.display = 'none';
        updateImageInteractivity();
        clearPositionFeedback();
    }
}

function setMouthPosition(event) {
    if (styleSelect.value !== 'standard' || !manualMouthPos.checked) {
        return;
    }
    
    const rect = imagePreview.getBoundingClientRect();
    const x = Math.round((event.clientX - rect.left) * (imagePreview.naturalWidth / rect.width));
    const y = Math.round((event.clientY - rect.top) * (imagePreview.naturalHeight / rect.height));
    
    mouthX.value = x;
    mouthY.value = y;
    
    console.log(`Mouth position set to: (${x}, ${y})`);
    
    // Update visual marker and feedback
    updateMouthMarkerPosition();
    updatePositionFeedback(x, y);
    
    // Brief animation for confirmation
    mouthMarker.classList.add('marker-pulse');
    setTimeout(() => {
        mouthMarker.classList.remove('marker-pulse');
    }, 600);
}

function checkCanProcess() {
    processBtn.disabled = !(selectedImage && selectedAudio);
    testBtn.disabled = !(selectedImage && selectedAudio);
}

async function testUpload() {
    if (!selectedImage || !selectedAudio) {
        alert('Please select both files first');
        return;
    }
    
    console.log('=== TEST UPLOAD ===');
    console.log('Testing upload with:', {
        image: selectedImage.name,
        audio: selectedAudio.name
    });
    
    const formData = new FormData();
    formData.append('image', selectedImage);
    formData.append('audio', selectedAudio);
    formData.append('style', document.getElementById('styleSelect').value);
    
    try {
        const response = await fetch(`${API_URL}/test-upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        console.log('Test upload response:', data);
        alert('Test upload successful! Check console for details.');
    } catch (error) {
        console.error('Test upload failed:', error);
        alert('Test upload failed! Check console for details.');
    }
}

async function processAnimation() {
    console.log('Starting animation process...');
    console.log('Selected image:', selectedImage?.name, selectedImage?.size);
    console.log('Selected audio:', selectedAudio?.name, selectedAudio?.size);
    
    if (!selectedImage || !selectedAudio) {
        alert('Please select both an image and audio file');
        return;
    }
    
    // Show progress
    progressSection.style.display = 'block';
    resultSection.style.display = 'none';
    processBtn.disabled = true;
    
    // Prepare form data
    const formData = new FormData();
    formData.append('image', selectedImage);
    formData.append('audio', selectedAudio);
    formData.append('style', document.getElementById('styleSelect').value);
    
    // Add manual mouth positioning if enabled
    if (styleSelect.value === 'standard' && manualMouthPos.checked && mouthX.value && mouthY.value) {
        formData.append('mouth_x', mouthX.value);
        formData.append('mouth_y', mouthY.value);
        console.log(`Using manual mouth position: (${mouthX.value}, ${mouthY.value})`);
    }
    
    // Log FormData contents
    console.log('FormData contents:');
    for (let [key, value] of formData.entries()) {
        console.log(`  ${key}:`, value instanceof File ? `${value.name} (${value.size} bytes)` : value);
    }
    
    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) progress = 90;
        progressFill.style.width = progress + '%';
        
        if (progress < 30) {
            progressText.textContent = 'Uploading files...';
        } else if (progress < 60) {
            progressText.textContent = 'Processing character...';
        } else {
            progressText.textContent = 'Generating animation...';
        }
    }, 500);
    
    try {
        console.log(`Sending request to: ${API_URL}/upload`);
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        let data;
        try {
            data = await response.json();
            console.log('Response data:', data);
        } catch (e) {
            console.error('Failed to parse JSON response:', e);
            const text = await response.text();
            console.error('Response text:', text);
            throw new Error('Invalid response from server');
        }
        
        if (!response.ok) {
            throw new Error(data.error || `Server error: ${response.status}`);
        }
        
        if (data.success) {
            clearInterval(progressInterval);
            progressFill.style.width = '100%';
            progressText.textContent = 'Complete!';
            
            // Show result
            setTimeout(() => {
                currentVideoUrl = `${API_URL}${data.video_url}`;
                resultVideo.src = currentVideoUrl;
                progressSection.style.display = 'none';
                resultSection.style.display = 'block';
            }, 500);
        } else {
            throw new Error(data.error || 'Processing failed');
        }
    } catch (error) {
        clearInterval(progressInterval);
        console.error('Upload error:', error);
        alert('Error: ' + error.message + '\n\nMake sure:\n1. Backend is running on port 5000\n2. ffmpeg is installed (for MP3 support)\n3. Files are not too large');
        resetForm();
    }
}

function downloadVideo() {
    if (!currentVideoUrl) return;
    
    const a = document.createElement('a');
    a.href = currentVideoUrl;
    a.download = 'talking_head.mp4';
    a.click();
}

function resetForm() {
    selectedImage = null;
    selectedAudio = null;
    currentVideoUrl = null;
    
    imagePreviewContainer.style.display = 'none';
    imageUpload.querySelector('.upload-content').style.display = 'flex';
    imageUpload.classList.remove('has-file');
    
    audioInfo.style.display = 'none';
    audioUpload.querySelector('.upload-content').style.display = 'flex';
    audioUpload.classList.remove('has-file');
    
    progressSection.style.display = 'none';
    resultSection.style.display = 'none';
    progressFill.style.width = '0%';
    
    imageInput.value = '';
    audioInput.value = '';
    
    // Reset mouth positioning
    resetMouthPosition();
    
    checkCanProcess();
}

// Enhanced mouth positioning functions
function resetMouthPosition() {
    mouthX.value = '';
    mouthY.value = '';
    mouthMarker.style.display = 'none';
    clearPositionFeedback();
    console.log('Mouth position reset to auto-detection');
}

function updateMouthMarkerPosition() {
    const x = parseInt(mouthX.value);
    const y = parseInt(mouthY.value);
    
    if (!isNaN(x) && !isNaN(y) && imagePreview.naturalWidth && imagePreview.naturalHeight) {
        const rect = imagePreview.getBoundingClientRect();
        const displayX = (x / imagePreview.naturalWidth) * rect.width;
        const displayY = (y / imagePreview.naturalHeight) * rect.height;
        
        mouthMarker.style.left = displayX + 'px';
        mouthMarker.style.top = displayY + 'px';
        mouthMarker.style.display = 'block';
        
        updatePositionFeedback(x, y);
    } else {
        mouthMarker.style.display = 'none';
        clearPositionFeedback();
    }
}

function updatePositionFeedback(x, y) {
    if (!x || !y) {
        clearPositionFeedback();
        return;
    }
    
    // Simple validation feedback
    const imageWidth = imagePreview.naturalWidth;
    const imageHeight = imagePreview.naturalHeight;
    
    if (x < 0 || x > imageWidth || y < 0 || y > imageHeight) {
        positionFeedback.innerHTML = '⚠️ Position is outside image bounds';
        positionFeedback.className = 'position-feedback warning';
        return;
    }
    
    // Check if position is in likely mouth area (lower 2/3 of image)
    if (y < imageHeight * 0.33) {
        positionFeedback.innerHTML = '💡 Tip: Mouth is usually in the lower part of the face';
        positionFeedback.className = 'position-feedback info';
    } else if (y > imageHeight * 0.85) {
        positionFeedback.innerHTML = '💡 Position looks a bit low for a mouth';
        positionFeedback.className = 'position-feedback info';
    } else {
        positionFeedback.innerHTML = '✅ Position looks good!';
        positionFeedback.className = 'position-feedback success';
    }
}

function clearPositionFeedback() {
    positionFeedback.innerHTML = '';
    positionFeedback.className = 'position-feedback';
}

function updateImageInteractivity() {
    const isInteractive = styleSelect.value === 'standard' && manualMouthPos.checked;
    
    if (isInteractive) {
        imagePreviewContainer.classList.add('interactive');
        imagePreview.style.cursor = 'crosshair';
    } else {
        imagePreviewContainer.classList.remove('interactive');
        imagePreview.style.cursor = 'default';
    }
}

function handleImageHover() {
    if (styleSelect.value === 'standard' && manualMouthPos.checked) {
        imagePreviewContainer.classList.add('hover-active');
    }
}

function handleImageLeave() {
    imagePreviewContainer.classList.remove('hover-active');
}

// Modal mouth selector functionality
let tempMouthCoordinates = null;

function openMouthSelectorModal() {
    if (!selectedImage) {
        alert('Please select an image first');
        return;
    }
    
    // Set the modal image to the selected image
    mouthSelectorImage.src = imagePreview.src;
    
    // Reset modal state
    tempMouthCoordinates = null;
    mouthSelectorMarker.style.display = 'none';
    confirmMouthSelection.disabled = true;
    previewMouthSprite.disabled = true;
    currentCoords.textContent = 'Not set';
    clearCanvas();
    
    // Show modal
    mouthSelectorModal.style.display = 'flex';
    
    console.log('Opened mouth selector modal');
}

function closeMouthSelectorModal() {
    mouthSelectorModal.style.display = 'none';
    tempMouthCoordinates = null;
    clearCanvas();
    console.log('Closed mouth selector modal');
}

function setMouthPositionInModal(event) {
    const rect = mouthSelectorImage.getBoundingClientRect();
    const x = Math.round((event.clientX - rect.left) * (mouthSelectorImage.naturalWidth / rect.width));
    const y = Math.round((event.clientY - rect.top) * (mouthSelectorImage.naturalHeight / rect.height));
    
    tempMouthCoordinates = { x, y };
    
    // Update marker position
    const displayX = (x / mouthSelectorImage.naturalWidth) * rect.width;
    const displayY = (y / mouthSelectorImage.naturalHeight) * rect.height;
    
    mouthSelectorMarker.style.left = displayX + 'px';
    mouthSelectorMarker.style.top = displayY + 'px';
    mouthSelectorMarker.style.display = 'block';
    
    // Update coordinates display
    currentCoords.textContent = `X: ${x}, Y: ${y}`;
    
    // Enable buttons
    confirmMouthSelection.disabled = false;
    previewMouthSprite.disabled = false;
    
    console.log(`Temporary mouth position set to: (${x}, ${y})`);
}

function confirmMouthPosition() {
    if (!tempMouthCoordinates) {
        return;
    }
    
    // Set the coordinates in the main form
    mouthX.value = tempMouthCoordinates.x;
    mouthY.value = tempMouthCoordinates.y;
    
    // Update the main form's visual feedback
    updateMouthMarkerPosition();
    updatePositionFeedback(tempMouthCoordinates.x, tempMouthCoordinates.y);
    
    // Close modal
    closeMouthSelectorModal();
    
    console.log(`Confirmed mouth position: (${tempMouthCoordinates.x}, ${tempMouthCoordinates.y})`);
}

function previewMouthSpriteAtPosition() {
    if (!tempMouthCoordinates) {
        return;
    }
    
    // For now, just draw a simple mouth sprite preview
    // In a full implementation, you'd load actual mouth sprites
    drawMouthPreview(tempMouthCoordinates.x, tempMouthCoordinates.y);
}

function drawMouthPreview(x, y) {
    const canvas = mouthPreviewCanvas;
    const ctx = canvas.getContext('2d');
    const image = mouthSelectorImage;
    
    // Set canvas size to match image display size
    const rect = image.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    canvas.style.width = rect.width + 'px';
    canvas.style.height = rect.height + 'px';
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Calculate display coordinates
    const displayX = (x / image.naturalWidth) * rect.width;
    const displayY = (y / image.naturalHeight) * rect.height;
    
    // Draw a simple mouth sprite preview (oval shape)
    ctx.fillStyle = 'rgba(139, 69, 19, 0.8)'; // Brown color for mouth
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.8)';
    ctx.lineWidth = 2;
    
    // Draw mouth oval
    ctx.beginPath();
    ctx.ellipse(displayX, displayY, 20, 10, 0, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
    
    // Draw teeth line
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(displayX - 15, displayY);
    ctx.lineTo(displayX + 15, displayY);
    ctx.stroke();
    
    console.log('Drew mouth preview at display coordinates:', displayX, displayY);
}

function clearCanvas() {
    const canvas = mouthPreviewCanvas;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}