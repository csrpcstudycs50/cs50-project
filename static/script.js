// ==========================================
// 1. DOM Elements
// ==========================================
const imagePicker = document.getElementById('imagePicker');
const canvas = document.getElementById('measurementCanvas');
const ctx = canvas.getContext('2d');

const calBtn = document.getElementById('calibrationButton');
const measBtn = document.getElementById('measurementButton');
const calInput = document.getElementById('calibrationValue');
const calUnit = document.getElementById('calibrationUnit');
const measValueSpan = document.getElementById('measurementValue');
const hiddenMeasInput = document.getElementById('hiddenMeasurementValue');
const resetBtn = document.querySelector('button[type="reset"]');

// ==========================================
// 2. Application State
// ==========================================
let loadedImage = null;
let currentMode = null;               // 'calibrate' or 'measure'
let calibrationPoints = [];           // Stores [{x, y}, {x, y}]
let currentCalibrationPixels = null;  // Pixel length of calibration line
let scaleRatio = null;                // Real-world units per pixel
let measurementPoints = [];           // Stores current measurement clicks [{x, y}, {x, y}]

// ==========================================
// 3. Step 1: Image Loading
// ==========================================
imagePicker.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const img = new Image();
    const objectUrl = URL.createObjectURL(file);

    img.onload = function() {
        loadedImage = img;
        
        // Set canvas internal resolution to image native resolution
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;

        // Render original image
        ctx.drawImage(img, 0, 0);

        // Ensure canvas element is visible
        canvas.classList.remove('d-none');

        // Free browser memory
        URL.revokeObjectURL(objectUrl);
    };

    img.src = objectUrl;
});

// ==========================================
// 4. Mode Selection Handlers
// ==========================================
calBtn.addEventListener('click', function() {
    currentMode = 'calibrate';
    calBtn.setAttribute('aria-pressed', 'true');
    measBtn.setAttribute('aria-pressed', 'false');

    // Reset calibration state
    calibrationPoints = [];
    currentCalibrationPixels = null;
    
    // Redraw clean image if re-calibrating
    if (loadedImage) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(loadedImage, 0, 0);
    }
});

measBtn.addEventListener('click', function() {
    if (!scaleRatio) {
        alert("Please draw a calibration line and enter its length first!");
        return;
    }
    currentMode = 'measure';
    measBtn.setAttribute('aria-pressed', 'true');
    calBtn.setAttribute('aria-pressed', 'false');
    measurementPoints = [];
});

// ==========================================
// 5. Input & Scale Ratio Calculation
// ==========================================
function updateScaleRatio() {
    const knownLength = parseFloat(calInput.value);

    if (currentCalibrationPixels && knownLength > 0) {
        scaleRatio = knownLength / currentCalibrationPixels;
        console.log(`Scale calculated: 1 pixel = ${scaleRatio} ${calUnit.value}`);
    }
}

calInput.addEventListener('input', updateScaleRatio);
calUnit.addEventListener('change', updateScaleRatio);

// ==========================================
// 6. Canvas Pointer Click Handler
// ==========================================
canvas.addEventListener('pointerdown', function(e) {
    if (!currentMode) return;

    // Map screen clicks to canvas high-res coordinate system
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const clickX = (e.clientX - rect.left) * scaleX;
    const clickY = (e.clientY - rect.top) * scaleY;

    if (currentMode === 'calibrate') {
        handleCalibrationClick(clickX, clickY);
    } else if (currentMode === 'measure') {
        handleMeasurementClick(clickX, clickY);
    }
});

// ==========================================
// 7. Workflow Handlers (Calibrate & Measure)
// ==========================================
function handleCalibrationClick(x, y) {
    if (calibrationPoints.length < 2) {
        calibrationPoints.push({ x: x, y: y });
        drawDot(x, y, 'red');
    }

    if (calibrationPoints.length === 2) {
        const p1 = calibrationPoints[0];
        const p2 = calibrationPoints[1];

        // Draw connecting calibration line
        drawLine(p1, p2, 'red');

        // Calculate and save pixel distance
        currentCalibrationPixels = Math.hypot(p2.x - p1.x, p2.y - p1.y);

        // Update ratio if length was entered prior to drawing
        updateScaleRatio();

        // Focus user cursor on input box for immediate typing
        calInput.focus();
    }
}

function handleMeasurementClick(x, y) {
    if (measurementPoints.length === 2) {
        // Reset points when starting a new measurement line
        measurementPoints = [];
    }

    measurementPoints.push({ x: x, y: y });
    drawDot(x, y, 'blue');

    if (measurementPoints.length === 2) {
        const p1 = measurementPoints[0];
        const p2 = measurementPoints[1];

        drawLine(p1, p2, 'blue');

        // Measure pixel distance
        const pixelDistance = Math.hypot(p2.x - p1.x, p2.y - p1.y);

        // Convert to real-world units
        const realDistance = pixelDistance * scaleRatio;
        const formattedResult = realDistance.toFixed(2);

        // Display in UI text span
        measValueSpan.textContent = formattedResult;

        // Populate hidden form field for Flask POST submission
        if (hiddenMeasInput) {
            hiddenMeasInput.value = formattedResult;
        }
    }
}

// ==========================================
// 8. Reset Listener
// ==========================================
if (resetBtn) {
    resetBtn.addEventListener('click', function(e) {
        e.preventDefault();

        // Clear stored values and points
        calibrationPoints = [];
        currentCalibrationPixels = null;
        scaleRatio = null;
        measurementPoints = [];

        // Clear form values and text displays
        calInput.value = '';
        measValueSpan.textContent = '0.00';
        if (hiddenMeasInput) {
            hiddenMeasInput.value = '';
        }

        // Reset toggle button states
        calBtn.setAttribute('aria-pressed', 'false');
        measBtn.setAttribute('aria-pressed', 'false');
        currentMode = null;

        // Redraw clean original image on canvas without page reload
        if (loadedImage) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(loadedImage, 0, 0);
        }
    });
}

// ==========================================
// 9. Drawing Helpers
// ==========================================
function drawDot(x, y, color = 'red') {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(x, y, 8, 0, 2 * Math.PI);
    ctx.fill();
}

function drawLine(p1, p2, color = 'red') {
    ctx.strokeStyle = color;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.stroke();
}