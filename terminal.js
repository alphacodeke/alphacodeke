// terminal.js — Terminal simulation component

export function initTerminal(data) {
  const section = document.getElementById('section-terminal');
  if (!section) return;

  section.innerHTML = `
    <div class="terminal-container">
      <div class="terminal-titlebar">
        <div class="terminal-dots">
          <span class="tdot tdot-red"></span>
          <span class="tdot tdot-yellow"></span>
          <span class="tdot tdot-green"></span>
        </div>
        <span class="terminal-title">ALPHACODE OS — SECURE SHELL v4.2.1</span>
        <span class="terminal-badge">AES-256 ENCRYPTED</span>
      </div>
      <div class="terminal-output" id="terminal-output"></div>
      <div class="terminal-input-row">
        <span class="terminal-prompt">root@alphacode:~$</span>
        <input type="text" class="terminal-input" id="terminal-input" placeholder="Type a command... (try 'help')" autocomplete="off" spellcheck="false"/>
        <span class="cursor-blink">▊</span>
      </div>
    </div>
  `;

  const output = document.getElementById('terminal-output');
  const input = document.getElementById('terminal-input');
  const bootLines = data.terminalBoot;
  const helpLines = data.terminalHelp;
  const { metrics, nodes, systems } = data;

  let bootIndex = 0;

  function printLine(text, cls = '') {
    const line = document.createElement('div');
    line.className = `t-line ${cls}`;
    line.textContent = text;
    output.appendChild(line);
    output.scrollTop = output.scrollHeight;
  }

  function printEmpty() {
    printLine('');
  }

  // Boot sequence
  function runBoot() {
    if (bootIndex < bootLines.length) {
      const delay = bootIndex === 0 ? 0 : (bootLines[bootIndex - 1].startsWith('——') ? 250 : 120);
      setTimeout(() => {
        const cls = bootLines[bootIndex].startsWith('[ OK ]') ? 'ok'
          : bootLines[bootIndex].startsWith('SYSTEM') || bootLines[bootIndex].startsWith('UPTIME') || bootLines[bootIndex].startsWith('OPERATOR') || bootLines[bootIndex].startsWith('Welcome') ? 'highlight'
          : bootLines[bootIndex].startsWith('——') ? 'separator'
          : '';
        printLine(bootLines[bootIndex], cls);
        bootIndex++;
        runBoot();
      }, delay);
    } else {
      printEmpty();
    }
  }

  runBoot();

  // Command handler
  const commands = {
    help: () => helpLines.forEach(l => printLine(l, l.startsWith(' ') ? 'cmd-item' : 'highlight')),
    clear: () => { output.innerHTML = ''; },
    status: () => {
      printLine('SYSTEM STATUS REPORT', 'highlight');
      printLine('————————————————————————————————');
      printLine(`Overall  : ${data.status.overall}`);
      printLine(`AI Layer : ${data.status.aiLayer}`);
      printLine(`Security : ${data.status.security}`);
      printLine(`Network  : ${data.status.network}`);
      printLine(`Uptime   : ${data.meta.uptime}`);
      printLine(`Build    : ${data.meta.build}`);
    },
    nodes: () => {
      printLine('ACTIVE NODES', 'highlight');
      printLine('————————————————————————————————');
      nodes.forEach(n => {
        const bar = '█'.repeat(Math.floor(n.load / 5)) + '░'.repeat(20 - Math.floor(n.load / 5));
        printLine(`[${n.status.toUpperCase().padEnd(7)}] ${n.label.padEnd(16)} ${bar} ${n.load}%`);
      });
    },
    metrics: () => {
      printLine('PERFORMANCE METRICS', 'highlight');
      printLine('————————————————————————————————');
      Object.entries(metrics).forEach(([k, v]) => {
        printLine(`${k.padEnd(20)}: ${v.toLocaleString()}`);
      });
    },
    projects: () => {
      printLine('FEATURED SYSTEMS', 'highlight');
      printLine('————————————————————————————————');
      systems.forEach(s => {
        printLine(`★ ${s.name} [${s.status}]`, 'ok');
        printLine(`  Type : ${s.type}`);
        printLine(`  Stack: ${s.stack.join(', ')}`);
        printLine(`  Stars: ${s.stars}`);
        printEmpty();
      });
    },
    scan: () => {
      printLine('Initiating security scan...', 'highlight');
      const scanSteps = [
        'Scanning dependencies...',
        'Checking CVE database...',
        'Analyzing authentication flows...',
        'Running SAST analysis...',
        'Checking secrets exposure...',
        '————————————————————————————————',
        `SCAN COMPLETE: 0 vulnerabilities found. ${data.metrics.threatsBlocked} threats blocked this week.`
      ];
      scanSteps.forEach((step, i) => {
        setTimeout(() => printLine(step, step.startsWith('SCAN') ? 'ok' : ''), i * 400);
      });
    },
    deploy: () => {
      printLine('Starting deployment pipeline...', 'highlight');
      const steps = [
        '[ BUILD  ] Compiling TypeScript... done (4.2s)',
        '[ TEST   ] Running 847 unit tests... passed',
        '[ LINT   ] Static analysis... clean',
        '[ SCAN   ] Security check... 0 issues',
        '[ PUSH   ] Pushing to registry... sha256:a3f8...',
        '[ DEPLOY ] Rolling update to k8s cluster...',
        '[ HEALTH ] Waiting for health checks...',
        '[ OK     ] Deployment successful! v4.2.1 is live.',
      ];
      steps.forEach((step, i) => {
        setTimeout(() => printLine(step, step.startsWith('[ OK') ? 'ok' : ''), i * 500);
      });
    },
    alphabot: () => {
      printLine('Connecting to AlphaBot v3.1-turbo...', 'highlight');
      setTimeout(() => {
        printLine('AlphaBot: Hello. I am AlphaBot v3.1, your AI code architect.');
        setTimeout(() => printLine('AlphaBot: I have analyzed 2,847 commits and 143 repositories.'), 800);
        setTimeout(() => printLine('AlphaBot: Current code quality index: 97.3% ↑'), 1600);
        setTimeout(() => printLine('AlphaBot: I recommend optimizing 3 modules for latency reduction.'), 2400);
        setTimeout(() => printLine('AlphaBot: Awaiting your next instruction.', 'ok'), 3200);
      }, 600);
    }
  };

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const cmd = input.value.trim().toLowerCase();
      if (!cmd) return;
      printLine(`root@alphacode:~$ ${cmd}`, 'cmd-entered');
      printEmpty();
      if (commands[cmd]) {
        commands[cmd]();
      } else {
        printLine(`bash: ${cmd}: command not found. Type 'help' for commands.`, 'error');
      }
      printEmpty();
      input.value = '';
    }
  });
}
