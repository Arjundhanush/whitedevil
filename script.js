
// Access webcam and display the video feed
navigator.mediaDevices.getUserMedia({ video: true })
  .then(function (stream) {
    const video = document.getElementById('video');
    video.srcObject = stream;
  })
  .catch(function (err) {
    console.log("Camera access error: ", err);
  });

// Capture photo on button click
document.getElementById('capture').addEventListener('click', function () {
  const video = document.getElementById('video');
  const canvas = document.getElementById('canvas');
  const context = canvas.getContext('2d');

  // Set canvas size to video size
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  // Draw the video frame onto the canvas
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Convert the canvas to base64 image
  const dataURL = canvas.toDataURL('image/png');
  
  // Display captured image on the page
  const capturedImg = document.getElementById('captured-img');
  capturedImg.src = dataURL;

  // Send the captured image to the server for recognition
  fetch('http://localhost:5000/recognize', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ image: dataURL }) // Send base64 encoded image
  })
  .then(res => res.json())
  .then(data => {
    // Handle the server response
    alert('Recognition result: ' + data.name); // Display recognized name or "Unknown"
  })
  .catch(err => {
    console.error("Error with the recognition request:", err);
  });
});
