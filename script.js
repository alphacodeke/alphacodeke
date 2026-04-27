// script.js — AlphaCode OS main entry point

import { initHeader } from './components/header.js';
import { initDashboard } from './components/dashboard.js';
import { initTerminal } from './components/terminal.js';

// ————————————————————————————————————————————
// BOOT SEQUENCE
// ————————————————————————————————————————————

async function boot() {
  const data = await loadData();
  showBootScreen(data, () => {
    initApp(data);
  });
}

async function loadData() {
  try {
    const res = await fetch('./data/systems.json');
    return await res.json();
  } catch {
    // Fallback inline data if fetch fails (e.g. file:// protocol)
    return window.__ALPHACODE_DATA__ || {};
  }
}

// ————————————————————————————————————————————
// BOOT SCREEN
// ————————————————————————————————————————————

function showBootScreen(data, onComplete) {
  const boot = document.getElementById('boot-screen');
  const bootText = document.getElementById('boot-text');
  const bootBar = document.getElementById('boot-bar-fill');
  const lines = data.terminalBoot || [];
  let i = 0;
  let pct = 0;

  const interval = setInterval(() => {
    if (i < lines.length) {
      const p = document.createElement('p');
      p.className = lines[i].startsWith('[ OK ]') ? 'boot-ok'
        : lines[i].startsWith('——') ? 'boot-sep'
        : lines[i].startsWith('SYSTEM') || lines[i].startsWith('Welcome') ? 'boot-highlight'
        : '';
      p.textContent = lines[i];
      bootText.appendChild(p);
      bootText.scrollTop = bootText.scrollHeight;
      pct = Math.min(100, Math.round(((i + 1) / lines.length) * 100));
      bootBar.style.width = pct + '%';
      i++;
    } else {
      clearInterval(interval);
      setTimeout(() => {
        boot.classList.add('fade-out');
        setTimeout(() => {
          boot.style.display = 'none';
          document.getElementById('main-app').style.display = 'flex';
          onComplete();
        }, 600);
      }, 800);
    }
  }, 110);
}

// ————————————————————————————————————————————
// INIT APP
// ————————————————————————————————————————————

function initApp(data) {
  initHeader(data);
  initDashboard(data);
  initArchitecture(data);
  initSystemsSection(data);
  initTerminal(data);
  initAlphabot(data);
  initParticles();
  startClockTick();

  // Show dashboard by default
  const dashSection = document.getElementById('section-dashboard');
  if (dashSection) {
    dashSection.style.display = 'block';
    setTimeout(() => dashSection.classList.add('active'), 50);
  }
}

// ————————————————————————————————————————————
// ARCHITECTURE SVG ENGINE
// ————————————————————————————————————————————

function initArchitecture(data) {
  const section = document.getElementById('section-architecture');
  if (!section) return;

  section.innerHTML = `
    <div class="arch-container">
      <div class="panel">
        <div class="panel-header">
          <span class="panel-title">◈ LIVE SYSTEM ARCHITECTURE</span>
          <span class="panel-badge online">ANIMATED</span>
        </div>
        <canvas id="arch-canvas" width="900" height="500"></canvas>
      </div>
    </div>
  `;

  const canvas = document.getElementById('arch-canvas');
  const ctx = canvas.getContext('2d');

  // Responsive canvas
  function resizeCanvas() {
    const parent = canvas.parentElement;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = parent.clientWidth * ratio;
    canvas.height = 500 * ratio;
    canvas.style.width = parent.clientWidth + 'px';
    canvas.style.height = '500px';
    ctx.scale(ratio, ratio);
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  const W = () => canvas.style.width ? parseInt(canvas.style.width) : 900;
  const H = 500;

  // Define nodes
  const nodesDef = [
    // CLIENT LAYER y=80
    { id: 'web',     label: 'WEB CLIENT',   sub: 'React + TS',  x: 0.18, y: 80,  layer: 0 },
    { id: 'mobile',  label: 'MOBILE',       sub: 'React Native',x: 0.50, y: 80,  layer: 0 },
    { id: 'cli',     label: 'CLI TOOLS',    sub: 'Node + Go',   x: 0.82, y: 80,  layer: 0 },
    // API LAYER y=200
    { id: 'gateway', label: 'API GATEWAY',  sub: 'Auth · Route',x: 0.50, y: 200, layer: 1, hub: true },
    // CORE LAYER y=320
    { id: 'ai',      label: 'AI ENGINE',    sub: 'AlphaBot',    x: 0.20, y: 320, layer: 2 },
    { id: 'dev',     label: 'DEV SVC',      sub: 'Build·Deploy',x: 0.40, y: 320, layer: 2 },
    { id: 'sec',     label: 'SECURITY',     sub: 'Shield',      x: 0.60, y: 320, layer: 2 },
    { id: 'mon',     label: 'MONITOR',      sub: 'Logs·Metrics',x: 0.80, y: 320, layer: 2 },
    // DATA LAYER y=430
    { id: 'pg',      label: 'MYSQL',   sub: 'Primary',     x: 0.25, y: 430, layer: 3 },
    { id: 'redis',   label: 'REDIS',        sub: 'Cache',       x: 0.45, y: 430, layer: 3 },
    { id: 'vec',     label: 'VECTOR DB',    sub: 'AI Memory',   x: 0.65, y: 430, layer: 3 },
    { id: 'blob',    label: 'BLOB STORE',   sub: 'S3 compat',   x: 0.82, y: 430, layer: 3 },
  ];

  const edges = [
    ['web','gateway'], ['mobile','gateway'], ['cli','gateway'],
    ['gateway','ai'], ['gateway','dev'], ['gateway','sec'], ['gateway','mon'],
    ['ai','pg'], ['ai','vec'], ['dev','redis'], ['sec','pg'], ['mon','blob'],
  ];

  // Particles per edge
  const particles = edges.map(([from, to]) => ({
    from, to,
    t: Math.random(),
    speed: 0.003 + Math.random() * 0.003,
    size: 2 + Math.random() * 2,
  }));

  // Pulse timers per node
  const pulses = nodesDef.map(n => ({ id: n.id, pulse: Math.random() }));

  let animFrame;
  let hoverNode = null;

  function getNodePos(id) {
    const n = nodesDef.find(x => x.id === id);
    return n ? { x: n.x * W(), y: n.y } : null;
  }

  function drawGrid() {
    ctx.clearRect(0, 0, W(), H);
    ctx.strokeStyle = 'rgba(247,194,0,0.04)';
    ctx.lineWidth = 0.5;
    for (let x = 0; x < W(); x += 32) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
    }
    for (let y = 0; y < H; y += 32) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W(), y); ctx.stroke();
    }
  }

  function drawLayerLabels() {
    const labels = ['CLIENT LAYER', 'API LAYER', 'CORE LAYER', 'DATA LAYER'];
    const ys = [58, 178, 298, 408];
    ctx.font = '9px JetBrains Mono, monospace';
    ctx.fillStyle = 'rgba(247,194,0,0.3)';
    labels.forEach((l, i) => {
      ctx.fillText(l, 10, ys[i]);
      ctx.strokeStyle = 'rgba(247,194,0,0.08)';
      ctx.lineWidth = 0.5;
      ctx.setLineDash([6, 12]);
      ctx.beginPath(); ctx.moveTo(90, ys[i] - 4); ctx.lineTo(W() - 10, ys[i] - 4); ctx.stroke();
      ctx.setLineDash([]);
    });
  }

  function drawEdges() {
    edges.forEach(([from, to]) => {
      const a = getNodePos(from);
      const b = getNodePos(to);
      if (!a || !b) return;
      const grad = ctx.createLinearGradient(a.x, a.y, b.x, b.y);
      grad.addColorStop(0, 'rgba(247,194,0,0.08)');
      grad.addColorStop(0.5, 'rgba(247,194,0,0.25)');
      grad.addColorStop(1, 'rgba(247,194,0,0.08)');
      ctx.strokeStyle = grad;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(a.x, a.y + 24);
      // Curved path
      const mx = (a.x + b.x) / 2;
      const my = (a.y + b.y) / 2;
      ctx.quadraticCurveTo(mx, my, b.x, b.y - 24);
      ctx.stroke();
    });
  }

  function drawParticles(time) {
    particles.forEach(p => {
      p.t += p.speed;
      if (p.t > 1) p.t = 0;
      const a = getNodePos(p.from);
      const b = getNodePos(p.to);
      if (!a || !b) return;
      const t = p.t;
      // Quadratic bezier position
      const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      const px = (1 - t) * (1 - t) * a.x + 2 * (1 - t) * t * mx + t * t * b.x;
      const py = (1 - t) * (1 - t) * (a.y + 24) + 2 * (1 - t) * t * my + t * t * (b.y - 24);
      const alpha = Math.sin(t * Math.PI);
      ctx.beginPath();
      ctx.arc(px, py, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(247,194,0,${alpha * 0.9})`;
      ctx.shadowColor = '#F7C200';
      ctx.shadowBlur = 8;
      ctx.fill();
      ctx.shadowBlur = 0;
    });
  }

  function drawNodes(time) {
    nodesDef.forEach((node, i) => {
      const x = node.x * W();
      const y = node.y;
      const isHub = node.hub;
      const isHover = hoverNode === node.id;
      const w = isHub ? 140 : 110;
      const h = isHub ? 52 : 44;
      const pulse = (Math.sin(time * 0.002 + i * 0.7) + 1) / 2;

      // Pulse ring
      const ringR = (isHub ? 80 : 65) + pulse * 15;
      const ringAlpha = (1 - pulse) * (isHub ? 0.2 : 0.12);
      ctx.beginPath();
      ctx.arc(x, y, ringR, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(247,194,0,${ringAlpha})`;
      ctx.lineWidth = 1;
      ctx.stroke();

      // Box shadow glow
      if (isHub || isHover) {
        ctx.shadowColor = '#F7C200';
        ctx.shadowBlur = isHub ? 20 : 10;
      }

      // Box fill
      ctx.fillStyle = isHub ? '#0d0800' : '#0a0a00';
      ctx.strokeStyle = isHub ? `rgba(247,194,0,${0.7 + pulse * 0.3})` : `rgba(247,194,0,${0.4 + pulse * 0.2})`;
      ctx.lineWidth = isHub ? 2 : 1.2;
      roundRect(ctx, x - w / 2, y - h / 2, w, h, 4);
      ctx.fill();
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Label
      ctx.font = `bold ${isHub ? 10 : 9}px JetBrains Mono, monospace`;
      ctx.fillStyle = '#F7C200';
      ctx.textAlign = 'center';
      ctx.fillText(node.label, x, y - 4);

      // Sublabel
      ctx.font = '7px JetBrains Mono, monospace';
      ctx.fillStyle = '#888';
      ctx.fillText(node.sub, x, y + 9);

      // Status dot
      ctx.beginPath();
      ctx.arc(x - w / 2 + 10, y - h / 2 + 10, 3, 0, Math.PI * 2);
      ctx.fillStyle = '#00ff00';
      ctx.shadowColor = '#00ff00';
      ctx.shadowBlur = 6;
      ctx.fill();
      ctx.shadowBlur = 0;
    });
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  function animate(time) {
    drawGrid();
    drawLayerLabels();
    drawEdges();
    drawParticles(time);
    drawNodes(time);
    animFrame = requestAnimationFrame(animate);
  }

  // Mouse hover
  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    hoverNode = null;
    nodesDef.forEach(node => {
      const nx = node.x * W();
      const dist = Math.sqrt((mx - nx) ** 2 + (my - node.y) ** 2);
      if (dist < 55) hoverNode = node.id;
    });
    canvas.style.cursor = hoverNode ? 'pointer' : 'default';
  });

  // Start when section is visible
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) { animFrame = requestAnimationFrame(animate); }
      else { cancelAnimationFrame(animFrame); }
    });
  });
  observer.observe(canvas);
}

// ————————————————————————————————————————————
// SYSTEMS SECTION
// ————————————————————————————————————————————

function initSystemsSection(data) {
  const section = document.getElementById('section-systems');
  if (!section) return;

  section.innerHTML = `
    <div class="systems-section">
      <div class="systems-grid">
        ${data.systems.map(s => renderFullSystemCard(s)).join('')}
      </div>
    </div>
  `;
}

function renderFullSystemCard(sys) {
  const statusColors = { PRODUCTION: '#00ff00', BETA: '#F7C200', RC1: '#88aaff' };
  const color = statusColors[sys.status] || '#888';
  const metricsHTML = Object.entries(sys.metrics)
    .map(([k, v]) => `<div class="sys-metric"><span class="sm-key">${k.toUpperCase()}</span><span class="sm-val">${v}</span></div>`)
    .join('');
  return `
    <div class="sys-full-card">
      <div class="sfc-header">
        <div>
          <div class="sfc-name">${sys.name}</div>
          <div class="sfc-type">${sys.type}</div>
        </div>
        <div class="sfc-status" style="color:${color};border-color:${color}">● ${sys.status}</div>
      </div>
      <div class="sfc-desc">${sys.description}</div>
      <div class="sfc-stack">${sys.stack.map(t => `<span class="tag">${t}</span>`).join('')}</div>
      <div class="sfc-metrics">${metricsHTML}</div>
      <div class="sfc-footer">
        <span class="sfc-stars">★ ${sys.stars.toLocaleString()} stars</span>
        <a href="#" class="sfc-btn" onclick="return false">VIEW SYSTEM →</a>
      </div>
    </div>
  `;
}

// ————————————————————————————————————————————
// ALPHABOT SECTION
// ————————————————————————————————————————————

function initAlphabot(data) {
  const section = document.getElementById('section-alphabot');
  if (!section) return;

  const bot = data.alphabot;
  section.innerHTML = `
    <div class="alphabot-container">
      <div class="panel ab-panel">
        <div class="panel-header">
          <span class="panel-title">◈ ALPHABOT AI LAYER — ${bot.model}</span>
          <span class="panel-badge online">INFERENCE ACTIVE</span>
        </div>
        <div class="ab-grid">
          <div class="ab-info">
            <div class="ab-stat"><span class="ab-key">MODEL</span><span class="ab-val">${bot.model}</span></div>
            <div class="ab-stat"><span class="ab-key">CONTEXT</span><span class="ab-val">${bot.contextWindow} tokens</span></div>
            <div class="ab-stat"><span class="ab-key">MODE</span><span class="ab-val">${bot.mode}</span></div>
            <div class="ab-stat"><span class="ab-key">ACCURACY</span><span class="ab-val ab-green">${bot.accuracy}</span></div>
            <div class="ab-stat"><span class="ab-key">MEMORY</span><span class="ab-val">Persistent Vector</span></div>
          </div>
          <div class="ab-log-panel">
            <div class="ab-log-title">INFERENCE LOG</div>
            <div class="ab-log" id="ab-log"></div>
          </div>
        </div>
        <div class="ab-chat">
          <div class="ab-chat-output" id="ab-chat-output">
            <div class="ab-msg ab-msg-system">AlphaBot online. Ask me anything about the system.</div>
          </div>
          <div class="ab-chat-input-row">
            <span class="ab-prompt">YOU ›</span>
            <input type="text" id="ab-chat-input" class="ab-chat-input" placeholder="Ask AlphaBot..." autocomplete="off"/>
            <button class="ab-send-btn" id="ab-send-btn">SEND</button>
          </div>
        </div>
      </div>
    </div>
  `;

  // Replay logs
  const logEl = document.getElementById('ab-log');
  bot.logs.forEach((entry, i) => {
    setTimeout(() => {
      const line = document.createElement('div');
      line.className = 'ab-log-line';
      line.textContent = `[${String(Math.floor(entry.ts / 1000)).padStart(4, '0')}ms] ${entry.msg}`;
      logEl.appendChild(line);
      logEl.scrollTop = logEl.scrollHeight;
    }, i * 350);
  });

  // Chat
  const chatOut = document.getElementById('ab-chat-output');
  const chatIn = document.getElementById('ab-chat-input');
  const sendBtn = document.getElementById('ab-send-btn');

  const responses = {
    default: [
      'Analyzing query... Code quality index remains at 97.3%.',
      'Running inference... All 143 repositories are healthy.',
      'Processing... No security vulnerabilities detected across your stack.',
      'Understood. I recommend JavaScript strict mode for your next module.',
      'Inference complete. Your deployment pipeline is optimal.',
    ]
  };

  function sendMsg() {
    const val = chatIn.value.trim();
    if (!val) return;
    appendMsg('YOU', val, 'user');
    chatIn.value = '';

    setTimeout(() => {
      const pool = responses.default;
      const reply = pool[Math.floor(Math.random() * pool.length)];
      appendMsg('ALPHABOT', reply, 'bot');
    }, 800 + Math.random() * 600);
  }

  function appendMsg(from, text, type) {
    const div = document.createElement('div');
    div.className = `ab-msg ab-msg-${type}`;
    div.innerHTML = `<span class="ab-msg-from">${from} ›</span> ${text}`;
    chatOut.appendChild(div);
    chatOut.scrollTop = chatOut.scrollHeight;
  }

  sendBtn.addEventListener('click', sendMsg);
  chatIn.addEventListener('keydown', e => { if (e.key === 'Enter') sendMsg(); });
}

// ————————————————————————————————————————————
// BACKGROUND PARTICLES
// ————————————————————————————————————————————

function initParticles() {
  const canvas = document.getElementById('bg-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  const pts = Array.from({ length: 60 }, () => ({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    vx: (Math.random() - 0.5) * 0.3,
    vy: (Math.random() - 0.5) * 0.3,
    size: Math.random() * 1.5 + 0.5,
  }));

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    pts.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(247,194,0,0.15)';
      ctx.fill();
    });
    // Draw connections
    pts.forEach((a, i) => {
      pts.slice(i + 1).forEach(b => {
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        if (d < 120) {
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(247,194,0,${(1 - d / 120) * 0.06})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      });
    });
    requestAnimationFrame(draw);
  }
  draw();
}

// ————————————————————————————————————————————
// CLOCK
// ————————————————————————————————————————————

function startClockTick() {
  const el = document.getElementById('sys-clock');
  if (!el) return;
  function tick() {
    el.textContent = new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC';
  }
  tick();
  setInterval(tick, 1000);
}

// ————————————————————————————————————————————
// START
// ————————————————————————————————————————————

boot();
