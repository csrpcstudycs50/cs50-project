const imagePicker = document.getElementById('imagePicker');
const canvas = document.getElementById('measurementCanvas');
const ctx = canvas.getContext('2d');


imagePicker.addEventListener('change', function(e) {
    const file = e.target.files[0];
    const img = new Image();
    img.src = URL.createObjectURL(file);
    img.onload = function() {
        canvas.width = img.naturalWidth;
        canvas.height = img.naturalHeight;
        ctx.drawImage(img, 0, 0);
    }

});


const calibrationButton = document.getElementById('calibrationButton');

calibrationButton.addEventListener('click', function() {
  // Check current state
  const isChecked = this.getAttribute('aria-pressed') === 'true';

  // Toggle state
  this.setAttribute('aria-pressed', !isChecked);
  this.classList.toggle('active', !isChecked);

  // Example action based on state
  if (!isChecked) {
    console.log('Button is NOW CHECKED (Active)');
  } else {
    console.log('Button is NOW UNCHECKED (Inactive)');
  }
});
