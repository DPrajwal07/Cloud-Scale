
/**
 * CloudScale Public Landing Page - Core JavaScript
 * Handles navigation, mobile menu, scroll reveal animations,
 * and the interactive product preview load simulator.
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initScrollReveal();
  initInteractivePreview();
  initCounterAnimations();
  initSmoothScroll();
  initLiveHeroTelemetry();
});

/* --------------------------------------------------------------------------
   1. Navbar & Mobile Menu Interaction
   -------------------------------------------------------------------------- */
function initNavbar() {
  const header = document.querySelector('.header');
  const navToggle = document.querySelector('.nav-toggle');
  const navMenu = document.querySelector('.nav-menu');
  const navLinks = document.querySelectorAll('.nav-link');

  // Sticky Header styling on scroll
  window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
    highlightActiveNavLink();
  });

  // Mobile menu toggle
  if (navToggle) {
    navToggle.addEventListener('click', () => {
      const isOpen = navMenu.classList.contains('open');
      if (isOpen) {
        closeMobileMenu();
      } else {
        openMobileMenu();
      }
    });
  }

  // Close menu on clicking nav link
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      closeMobileMenu();
    });
  });

  // Close menu on ESC key press
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navMenu.classList.contains('open')) {
      closeMobileMenu();
    }
  });

  function openMobileMenu() {
    navMenu.classList.add('open');
    navToggle.classList.add('open');
    navToggle.setAttribute('aria-expanded', 'true');
  }

  function closeMobileMenu() {
    navMenu.classList.remove('open');
    navToggle.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
  }

  // Active section nav link detection
  function highlightActiveNavLink() {
    const sections = document.querySelectorAll('section[id]');
    const scrollPos = window.scrollY + 120;

    sections.forEach(section => {
      const top = section.offsetTop;
      const height = section.offsetHeight;
      const id = section.getAttribute('id');
      const targetLink = document.querySelector(`.nav-link[href="#${id}"]`);

      if (targetLink) {
        if (scrollPos >= top && scrollPos < top + height) {
          navLinks.forEach(l => l.classList.remove('active'));
          targetLink.classList.add('active');
        }
      }
    });
  }
}

/* --------------------------------------------------------------------------
   2. Smooth Scroll for Anchor Links
   -------------------------------------------------------------------------- */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (href === '#' || href === '') return;

      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        const headerOffset = 80;
        const elementPosition = target.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        });
      }
    });
  });
}

/* --------------------------------------------------------------------------
   3. Scroll Reveal Animations (IntersectionObserver)
   -------------------------------------------------------------------------- */
function initScrollReveal() {
  const revealElements = document.querySelectorAll('.reveal');

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
        }
      });
    }, {
      threshold: 0.12,
      rootMargin: '0px 0px -40px 0px'
    });

    revealElements.forEach(el => observer.observe(el));
  } else {
    // Fallback for older browsers
    revealElements.forEach(el => el.classList.add('active'));
  }
}

/* --------------------------------------------------------------------------
   4. Interactive Dashboard Load Simulator
   -------------------------------------------------------------------------- */
function initInteractivePreview() {
  const slider = document.getElementById('workloadSlider');
  const sliderVal = document.getElementById('workloadValue');
  const cpuVal = document.getElementById('previewCpuVal');
  const cpuTrack = document.getElementById('previewCpuTrack');
  const memVal = document.getElementById('previewMemVal');
  const memTrack = document.getElementById('previewMemTrack');
  const reqVal = document.getElementById('previewReqVal');
  const instanceVal = document.getElementById('previewInstanceVal');
  const healthStatus = document.getElementById('previewHealthStatus');
  const chartPolyline = document.getElementById('previewChartPolyline');

  if (!slider) return;

  // Base chart points generator
  function updateDashboardMetrics(loadPercentage) {
    const load = parseInt(loadPercentage, 10);

    // CPU calculation: Load + slight variance
    const cpu = Math.min(99, Math.max(12, Math.round(load * 0.85 + 8)));

    // Memory calculation: Base memory + load proportion
    const mem = Math.min(95, Math.max(28, Math.round(35 + load * 0.45)));

    // Requests calculation: Requests scaling with load
    const reqs = Math.round(150 + load * 24.5);

    // Auto-scaling instance logic:
    // Under 40% -> 2 Instances
    // 40%-75% -> 4 Instances
    // Over 75% -> 8 Instances
    let instances = 2;
    let healthText = "HEALTHY — 99.9% Uptime";
    let healthClass = "badge-available";

    if (load > 75) {
      instances = 8;
      healthText = "AUTO-SCALED — Capacity Expanded";
      healthClass = "badge-planned";
    } else if (load > 40) {
      instances = 4;
      healthText = "HEALTHY — Auto-scaling Ready";
      healthClass = "badge-available";
    }

    // Update DOM UI elements
    if (sliderVal) sliderVal.textContent = `${load}%`;
    if (cpuVal) cpuVal.textContent = `${cpu}%`;
    if (cpuTrack) cpuTrack.style.width = `${cpu}%`;

    if (memVal) memVal.textContent = `${mem}%`;
    if (memTrack) memTrack.style.width = `${mem}%`;

    if (reqVal) reqVal.textContent = `${reqs.toLocaleString()} req/s`;
    if (instanceVal) instanceVal.textContent = `${instances} Active`;

    if (healthStatus) {
      healthStatus.textContent = healthText;
      healthStatus.className = `badge ${healthClass}`;
    }

    // Dynamic Chart Update
    if (chartPolyline) {
      const height = 120;
      const points = [];
      const steps = 10;
      for (let i = 0; i <= steps; i++) {
        const x = (i / steps) * 600;
        // Generate wave pattern scaled by load
        const noise = Math.sin(i * 1.5) * 15;
        const targetY = height - ((cpu / 100) * (height - 30) + noise);
        points.push(`${x},${Math.max(10, Math.min(height - 5, targetY))}`);
      }
      chartPolyline.setAttribute('points', points.join(' '));
    }
  }

  slider.addEventListener('input', (e) => {
    updateDashboardMetrics(e.target.value);
  });

  // Initialize with default 45% load
  updateDashboardMetrics(45);
}

/* --------------------------------------------------------------------------
   5. Number Counter Animation for Stats
   -------------------------------------------------------------------------- */
function initCounterAnimations() {
  const counters = document.querySelectorAll('.counter-num');

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    counters.forEach(c => observer.observe(c));
  } else {
    counters.forEach(c => animateCounter(c));
  }

  function animateCounter(el) {
    const target = parseInt(el.getAttribute('data-target'), 10) || 0;
    const duration = 1500;
    const stepTime = 20;
    const steps = duration / stepTime;
    const increment = target / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        el.textContent = target.toLocaleString();
        clearInterval(timer);
      } else {
        el.textContent = Math.ceil(current).toLocaleString();
      }
    }, stepTime);
  }
}

/* --------------------------------------------------------------------------
   6. Real-time Hero Telemetry Integration with FastAPI Backend
   -------------------------------------------------------------------------- */
function initLiveHeroTelemetry() {
  const heroCpuVal = document.getElementById('heroCpuVal');
  const heroCpuFill = document.getElementById('heroCpuFill');
  const heroLatencyVal = document.getElementById('heroLatencyVal');
  const heroLatencyFill = document.getElementById('heroLatencyFill');
  const heroNodesVal = document.getElementById('heroNodesVal');
  const heroNodesFill = document.getElementById('heroNodesFill');
  const heroConsole = document.getElementById('heroConsole');

  if (!heroCpuVal || !heroConsole) return;

  const getApiUrl = () => {
    if (window.location.protocol === 'file:') return "http://localhost:8000/api";
    if (window.location.port && window.location.port !== '8000' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')) {
      return "http://localhost:8000/api";
    }
    return "/api";
  };
  let API_URL = getApiUrl();

  async function fetchHeroTelemetry() {
    try {
      let [metricsRes, activityRes] = await Promise.all([
        fetch(`${API_URL}/metrics`).then(r => r.ok ? r.json() : null).catch(() => null),
        fetch(`${API_URL}/activity`).then(r => r.ok ? r.json() : null).catch(() => null)
      ]);

      // If primary /api call was unmapped on Vercel, attempt direct /api/index.py fallback
      if (!metricsRes && API_URL === "/api") {
        const fallbackRes = await fetch(`/api/index.py/metrics`).then(r => r.ok ? r.json() : null).catch(() => null);
        if (fallbackRes) {
          API_URL = "/api/index.py";
          metricsRes = fallbackRes;
          activityRes = await fetch(`/api/index.py/activity`).then(r => r.ok ? r.json() : null).catch(() => null);
        }
      }

      if (metricsRes) {
        const cpu = metricsRes.cpu;
        const latency = metricsRes.latency;
        const instances = metricsRes.instances;

        if (heroCpuVal) heroCpuVal.textContent = `${cpu.toFixed(1)}%`;
        if (heroCpuFill) heroCpuFill.style.width = `${Math.min(100, cpu)}%`;

        if (heroLatencyVal) heroLatencyVal.textContent = `${latency}ms`;
        if (heroLatencyFill) heroLatencyFill.style.width = `${Math.min(100, (latency / 200) * 100)}%`;

        if (heroNodesVal) heroNodesVal.textContent = `${instances} Node${instances > 1 ? 's' : ''}`;
        if (heroNodesFill) heroNodesFill.style.width = `${Math.min(100, (instances / 8) * 100)}%`;
      }

      if (activityRes && Array.isArray(activityRes) && activityRes.length > 0) {
        const topEvents = activityRes.slice(0, 3);
        heroConsole.innerHTML = topEvents.map(e => {
          let tagClass = 'tag-info';
          let tagText = e.kind.toUpperCase();
          if (e.kind === 'scale') { tagClass = 'tag-scale'; tagText = 'SCALE'; }
          else if (e.kind === 'load') { tagClass = 'tag-load'; tagText = 'LOAD'; }
          else if (e.kind === 'config') { tagClass = 'tag-config'; tagText = 'POLICY'; }
          else if (e.kind === 'system') { tagClass = 'tag-health'; tagText = 'SYSTEM'; }

          return `<div class="console-line"><span class="c-time">${e.time}</span> <span class="c-tag ${tagClass}">${tagText}</span> ${e.message}</div>`;
        }).join('');
      }
    } catch (err) {
      console.warn("Backend API not reachable for hero telemetry:", err);
    }
  }

  fetchHeroTelemetry();
  setInterval(fetchHeroTelemetry, 3000);
}

