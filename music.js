const audio = new Audio('bgm.mp3');

// Set volume to 50%
audio.volume = 0.5;

audio.loop = true;
  
// Try autoplay immediately (may fail silently)
audio.play().catch(() => {
  console.log("Autoplay blocked, waiting for user interaction.");
});

// Play when user clicks anywhere
document.body.addEventListener('click', () => {
  audio.play();
}, { once: true });
