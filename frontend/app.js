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
        imagePreview.style.display = 'block';
        imageUpload.querySelector('.upload-content').style.display = 'none';
        imageUpload.classList.add('has-file');
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
    
    if (selectedStyle === 'standard') {
        canadianInfo.style.display = 'none';
        standardInfo.style.display = 'block';
    } else {
        canadianInfo.style.display = 'block';
        standardInfo.style.display = 'none';
    }
}

function toggleMouthControls() {
    if (manualMouthPos.checked) {
        mouthControls.style.display = 'flex';
    } else {
        mouthControls.style.display = 'none';
        mouthX.value = '';
        mouthY.value = '';
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
    
    // Visual feedback
    imagePreview.style.cursor = 'crosshair';
    setTimeout(() => {
        imagePreview.style.cursor = 'default';
    }, 1000);
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
    formData.append('style', 'canadian');
    
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
    
    imagePreview.style.display = 'none';
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
    
    checkCanProcess();
}