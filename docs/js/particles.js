/**
 * 星尘粒子效果 — 首页 Hero 区域
 * Falling star dust particles with gentle drift
 */
(function () {
  const canvas = document.getElementById('particles-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let particles = [];
  let animationId;
  let width, height;

  const CONFIG = {
    count: 80,
    minSize: 0.5,
    maxSize: 2.5,
    minSpeed: 0.15,
    maxSpeed: 0.6,
    colors: [
      'rgba(200, 168, 110, ',   // gold
      'rgba(224, 201, 138, ',   // light gold
      'rgba(184, 115, 51, ',    // copper
      'rgba(180, 180, 200, ',   // silver-blue
    ],
    drift: 0.3,
    twinkleSpeed: 0.01,
  };

  function resize() {
    const rect = canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    width = rect.width;
    height = rect.height;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function createParticle(startFromTop) {
    const color = CONFIG.colors[Math.floor(Math.random() * CONFIG.colors.length)];
    return {
      x: Math.random() * width,
      y: startFromTop ? -10 : Math.random() * height,
      size: CONFIG.minSize + Math.random() * (CONFIG.maxSize - CONFIG.minSize),
      speed: CONFIG.minSpeed + Math.random() * (CONFIG.maxSpeed - CONFIG.minSpeed),
      drift: (Math.random() - 0.5) * CONFIG.drift,
      color: color,
      opacity: Math.random() * 0.6 + 0.1,
      twinklePhase: Math.random() * Math.PI * 2,
      twinkleSpeed: 0.005 + Math.random() * CONFIG.twinkleSpeed,
    };
  }

  function init() {
    resize();
    particles = [];
    for (let i = 0; i < CONFIG.count; i++) {
      particles.push(createParticle(false));
    }
  }

  function draw() {
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];

      // Twinkle
      p.twinklePhase += p.twinkleSpeed;
      const twinkle = (Math.sin(p.twinklePhase) + 1) / 2;
      const alpha = p.opacity * (0.3 + twinkle * 0.7);

      // Draw
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = p.color + alpha.toFixed(3) + ')';
      ctx.fill();

      // Optional glow for larger particles
      if (p.size > 1.5) {
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * 3, 0, Math.PI * 2);
        ctx.fillStyle = p.color + (alpha * 0.1).toFixed(3) + ')';
        ctx.fill();
      }

      // Move
      p.y += p.speed;
      p.x += p.drift;

      // Reset when out of bounds
      if (p.y > height + 10 || p.x < -10 || p.x > width + 10) {
        particles[i] = createParticle(true);
      }
    }

    animationId = requestAnimationFrame(draw);
  }

  // Lifecycle
  init();
  draw();

  let resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      init();
    }, 200);
  });

  // Pause when not visible
  document.addEventListener('visibilitychange', function () {
    if (document.hidden) {
      cancelAnimationFrame(animationId);
    } else {
      draw();
    }
  });
})();
