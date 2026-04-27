// header.js — System header component

export function initHeader(data) {
  const header = document.getElementById('sys-header');
  if (!header) return;

  header.innerHTML = `
    <div class="header-inner">
      <div class="header-logo">
        <span class="logo-bracket">[</span>
        <span class="logo-text">ALPHACODE</span>
        <span class="logo-bracket">]</span>
        <span class="logo-sub">OS v${data.meta.version}</span>
      </div>
      <nav class="header-nav">
        <button class="nav-btn active" data-section="dashboard">DASHBOARD</button>
        <button class="nav-btn" data-section="architecture">ARCHITECTURE</button>
        <button class="nav-btn" data-section="systems">SYSTEMS</button>
        <button class="nav-btn" data-section="terminal">TERMINAL</button>
        <button class="nav-btn" data-section="alphabot">ALPHABOT</button>
      </nav>
      <div class="header-status">
        <span class="status-dot online"></span>
        <span class="status-text">SYS: ${data.status.overall}</span>
        <span class="status-uptime">↑ ${data.meta.uptime}</span>
      </div>
    </div>
  `;

  // Nav switching
  const navBtns = header.querySelectorAll('.nav-btn');
  navBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      navBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      document.querySelectorAll('.section-panel').forEach(p => {
        p.classList.remove('active');
        p.style.display = 'none';
      });

      const target = document.getElementById(`section-${btn.dataset.section}`);
      if (target) {
        target.style.display = 'block';
        setTimeout(() => target.classList.add('active'), 10);
      }
    });
  });
}
