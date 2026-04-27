// dashboard.js — Dashboard panel component

export function initDashboard(data) {
  const section = document.getElementById('section-dashboard');
  if (!section) return;

  const { metrics, nodes, systems, status } = data;

  section.innerHTML = `
    <div class="dashboard-grid">

      <!-- Metric Cards Row -->
      <div class="metrics-row">
        ${renderMetricCard('COMMITS', metrics.commits.toLocaleString(), '↑ 2.3%', 'yellow')}
        ${renderMetricCard('REPOSITORIES', metrics.repositories, 'Active', 'green')}
        ${renderMetricCard('STARS EARNED', metrics.stars.toLocaleString(), '↑ 8.1%', 'yellow')}
        ${renderMetricCard('AI INFERENCES', metrics.aiInferences.toLocaleString(), 'Today', 'green')}
        ${renderMetricCard('THREATS BLOCKED', metrics.threatsBlocked, 'This week', 'yellow')}
        ${renderMetricCard('DEPLOYMENTS', metrics.deployments, 'Total', 'green')}
      </div>

      <!-- Node Status + Featured System -->
      <div class="dashboard-main">

        <!-- Node Status Panel -->
        <div class="panel node-panel">
          <div class="panel-header">
            <span class="panel-title">◈ ACTIVE NODES</span>
            <span class="panel-badge online">ALL NOMINAL</span>
          </div>
          <div class="node-list">
            ${nodes.map(n => renderNodeRow(n)).join('')}
          </div>
        </div>

        <!-- System Overview Panel -->
        <div class="panel systems-panel">
          <div class="panel-header">
            <span class="panel-title">◈ FEATURED SYSTEMS</span>
            <span class="panel-badge">4 ACTIVE</span>
          </div>
          <div class="systems-list">
            ${systems.map(s => renderSystemCard(s)).join('')}
          </div>
        </div>

      </div>

    </div>
  `;

  // Animate load bars
  setTimeout(() => {
    section.querySelectorAll('.load-bar-fill').forEach(bar => {
      bar.style.width = bar.dataset.load + '%';
    });
  }, 100);
}

function renderMetricCard(label, value, sub, color) {
  return `
    <div class="metric-card glow-${color}">
      <div class="metric-label">${label}</div>
      <div class="metric-value">${value}</div>
      <div class="metric-sub">${sub}</div>
    </div>
  `;
}

function renderNodeRow(node) {
  const colors = { online: '#00ff00', warning: '#F7C200', offline: '#ff4444' };
  const color = colors[node.status] || '#888';
  return `
    <div class="node-row">
      <span class="node-dot" style="background:${color};box-shadow:0 0 6px ${color}"></span>
      <span class="node-label">${node.label}</span>
      <span class="node-layer">[${node.layer.toUpperCase()}]</span>
      <div class="load-bar">
        <div class="load-bar-fill" data-load="${node.load}" style="width:0%"></div>
      </div>
      <span class="node-load">${node.load}%</span>
    </div>
  `;
}

function renderSystemCard(sys) {
  const statusColors = { PRODUCTION: '#00ff00', BETA: '#F7C200', RC1: '#88aaff' };
  const color = statusColors[sys.status] || '#888';
  return `
    <div class="sys-card">
      <div class="sys-card-header">
        <span class="sys-name">${sys.name}</span>
        <span class="sys-status" style="color:${color};border-color:${color}">● ${sys.status}</span>
      </div>
      <div class="sys-type">${sys.type}</div>
      <div class="sys-stack">${sys.stack.map(t => `<span class="tag">${t}</span>`).join('')}</div>
      <div class="sys-stars">★ ${sys.stars.toLocaleString()}</div>
    </div>
  `;
}
