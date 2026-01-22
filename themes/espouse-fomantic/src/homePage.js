// Lazy load particles.js only when needed (homepage only)
const particleJSConfig = {
    "particles": {
          "number": {
                  "value": 80,
                  "density": {
                            "enable": true,
                            "value_area": 800
                          }
                },
          "color": {
                  "value": "#ffffff"
                },
          "shape": {
                  "type": "circle",
                  "stroke": {
                            "width": 0,
                            "color": "#000000"
                          },
                  "polygon": {
                            "nb_sides": 5
                          },
                },
          "opacity": {
                  "value": 0.5,
                  "random": false,
                  "anim": {
                            "enable": false,
                            "speed": 1,
                            "opacity_min": 0.1,
                            "sync": false
                          }
                },
          "size": {
                  "value": 3,
                  "random": true,
                  "anim": {
                            "enable": false,
                            "speed": 40,
                            "size_min": 0.1,
                            "sync": false
                          }
                },
          "line_linked": {
                  "enable": true,
                  "distance": 150,
                  "color": "#ffffff",
                  "opacity": 0.4,
                  "width": 1
                },
          "move": {
                  "enable": true,
                  "speed": 6,
                  "direction": "none",
                  "random": false,
                  "straight": false,
                  "out_mode": "out",
                  "attract": {
                            "enable": false,
                            "rotateX": 600,
                            "rotateY": 1200
                          }
                }
        },
    "interactivity": {
          "detect_on": "canvas",
          "events": {
                  "onhover": {
                            "enable": true,
                            "mode": "repulse"
                          },
                  "onclick": {
                            "enable": true,
                            "mode": "push"
                          },
                  "resize": true
                },
        },
    "retina_detect": true,
};

// Only load particles.js if the particles-js element exists (homepage)
async function initParticles() {
  const particlesContainer = document.getElementById('particles-js');
  if (!particlesContainer) {
    return; // Not on homepage, skip loading particles.js
  }

  // Dynamically import particles.js only when needed
  const pJS = await import(/* webpackChunkName: "particles" */ "particles.js");

  // Remove any existing canvas elements from preprocessing
  window.addEventListener('load', function() {
    const existCanvas = document.getElementsByTagName('canvas');
    if (existCanvas[0]) {
      existCanvas[0].remove();
      console.log("Deleted canvas");
    }

    if (typeof particlesJS !== 'undefined') {
      particlesJS('particles-js', particleJSConfig);
    }
  });
}

// Initialize particles when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initParticles);
} else {
  initParticles();
}
