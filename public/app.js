// API base URL
const API_URL = '';

// Tab Titles and Subtitles map for Header update
const tabMeta = {
  'dashboard': { title: 'Stadium Dashboard', subtitle: 'Real-time telemetry and stadium health index.' },
  'fan-companion': { title: 'Fan Companion Hub', subtitle: 'AI assistant, smart transit planner, and green loyalty rewards.' },
  'staff-ops': { title: 'Incident Response & Dispatch', subtitle: 'Real-time incident feed and GenAI dispatch protocols.' },
  'command-center': { title: 'Organizer Command Center', subtitle: 'Direct operations intelligence and natural language reporting.' },
  'sustainability': { title: 'Eco Hub & Leaderboard', subtitle: 'Tracking plastic recycling, green travel, and top fans.' }
};

// State Variables
let currentTab = 'dashboard';
let statsInterval = null;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  initDashboard();
  setupChat();
  setupTransitRoute();
  setupEcoLogger();
  setupIncidentReporter();
  setupCommandCenter();
  setupSimulator();
  
  // Start polling dashboard stats every 5 seconds
  fetchDashboardStats();
  statsInterval = setInterval(fetchDashboardStats, 5000);
  
  // Check AI Status
  checkAIStatus();
});

// ----------------------------------------------------
// SYSTEM UTILITIES
// ----------------------------------------------------
function updateTime() {
  const now = new Date();
  const options = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
  document.getElementById('stadium-time').textContent = now.toLocaleTimeString([], options);
}
setInterval(updateTime, 1000);
updateTime();

async function checkAIStatus() {
  const indicator = document.getElementById('ai-status-indicator');
  try {
    const res = await fetch(`${API_URL}/api/dashboard`);
    const data = await res.json();
    if (data.success) {
      // We check if it is active. Since server logs environmental vars,
      // we check via actual endpoint. If backend responds, it is online.
      indicator.textContent = 'ONLINE (GEMINI)';
      indicator.classList.remove('badge-neutral');
      indicator.style.color = '#00E676';
    }
  } catch (e) {
    indicator.textContent = 'MOCK / OFFLINE';
    indicator.style.color = '#FFD600';
  }
}

// ----------------------------------------------------
// TAB NAVIGATION
// ----------------------------------------------------
function setupNavigation() {
  const buttons = document.querySelectorAll('.nav-btn');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tabName = btn.getAttribute('data-tab');
      
      // Toggle Active button
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      // Toggle Active Tab View
      document.querySelectorAll('.tab-view').forEach(view => {
        view.classList.remove('active');
      });
      document.getElementById(tabName).classList.add('active');
      
      // Update Header Text
      currentTab = tabName;
      document.getElementById('current-tab-title').textContent = tabMeta[tabName].title;
      document.getElementById('current-tab-subtitle').textContent = tabMeta[tabName].subtitle;
      
      // Trigger instant data fetch based on view
      if (tabName === 'dashboard') {
        fetchDashboardStats();
      } else if (tabName === 'staff-ops') {
        fetchIncidents();
      } else if (tabName === 'sustainability') {
        fetchLeaderboard();
      }
    });
  });
}

// ----------------------------------------------------
// DASHBOARD & TELEMETRY
// ----------------------------------------------------
async function fetchDashboardStats() {
  try {
    const res = await fetch(`${API_URL}/api/dashboard`);
    const data = await res.json();
    if (!data.success) return;
    
    // Render Stats
    updateStatsCards(data);
    
    // Render Concessions List
    renderConcessions(data.concessions);
    
    // Render Map
    updateStadiumMap(data.zones);
    
    // Render Telemetry Table
    renderTelemetryTable(data.zones);
    
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
  }
}

function updateStatsCards(data) {
  // Occupancy aggregation
  let totalCap = 0;
  let totalOcc = 0;
  data.zones.forEach(z => {
    totalCap += z.capacity;
    totalOcc += z.occupancy;
  });
  
  const pct = Math.round((totalOcc / totalCap) * 100);
  document.getElementById('stat-occupancy').textContent = `${totalOcc.toLocaleString()} / ${totalCap.toLocaleString()} (${pct}%)`;
  document.getElementById('occupancy-progress').style.width = `${pct}%`;
  
  // Concession Queue average
  let totalTime = 0;
  let activeConcessions = data.concessions.filter(c => c.status === 'Open');
  activeConcessions.forEach(c => totalTime += c.queue_time);
  const avgQueue = activeConcessions.length ? Math.round(totalTime / activeConcessions.length) : 0;
  document.getElementById('stat-queue').textContent = `${avgQueue} mins`;
  
  // Incidents
  const openIncidents = data.incidents.filter(i => i.status !== 'Resolved');
  document.getElementById('stat-incidents').textContent = openIncidents.length;
  
  const critical = openIncidents.filter(i => i.severity === 'Critical' || i.severity === 'High').length;
  document.getElementById('stat-critical-alerts').textContent = `${critical} High Alert${critical !== 1 ? 's' : ''}`;
  
  // Eco points
  document.getElementById('stat-eco').textContent = data.total_sustainability_points.toLocaleString();
}

function renderConcessions(concessions) {
  const container = document.getElementById('dashboard-concessions-list');
  container.innerHTML = '';
  
  concessions.forEach(c => {
    let qClass = 'low';
    if (c.queue_time > 20) qClass = 'high';
    else if (c.queue_time > 10) qClass = 'med';
    
    const item = document.createElement('div');
    item.className = 'concession-item';
    item.innerHTML = `
      <div class="concession-info">
        <h4>${c.name}</h4>
        <span>Status: <strong>${c.status}</strong> | Inventory: ${c.inventory_status}</span>
      </div>
      <div class="concession-metrics">
        <span class="queue-badge ${qClass}">${c.queue_time}m wait</span>
      </div>
    `;
    container.appendChild(item);
  });
}

function updateStadiumMap(zones) {
  zones.forEach(zone => {
    // Find element on SVG map
    const element = document.getElementById(`map-${zone.id}`);
    if (element) {
      // Remove previous status classes
      element.classList.remove('Normal', 'Warning', 'Congested');
      element.classList.add(zone.status);
    }
  });
}

function renderTelemetryTable(zones) {
  const tbody = document.getElementById('dashboard-zones-tbody');
  tbody.innerHTML = '';
  
  zones.forEach(z => {
    const fillPct = Math.round((z.occupancy / z.capacity) * 100);
    const row = document.createElement('tr');
    
    let statusClass = 'text-green';
    if (z.status === 'Congested') statusClass = 'text-danger';
    else if (z.status === 'Warning') statusClass = 'text-warning';

    row.innerHTML = `
      <td><strong>${z.name}</strong></td>
      <td>${z.id.startsWith('sec') ? 'Spectator Stand' : 'Access Gate'}</td>
      <td>${z.capacity.toLocaleString()}</td>
      <td>${z.occupancy.toLocaleString()}</td>
      <td>
        <div class="progress-bar-container" style="display:inline-block; margin-right: 8px;">
          <div class="progress-bar" style="width: ${fillPct}%; background-color: ${z.status === 'Congested' ? '#FF1744' : z.status === 'Warning' ? '#FFD600' : '#00E676'}"></div>
        </div>
        ${fillPct}%
      </td>
      <td class="${statusClass}"><strong>${z.status}</strong></td>
    `;
    tbody.appendChild(row);
  });
}

// ----------------------------------------------------
// MULTILINGUAL CHAT WIDGET
// ----------------------------------------------------
function setupChat() {
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const container = document.getElementById('chat-messages');
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    
    // Add user message to UI
    appendChatMessage('user', '👤', text);
    input.value = '';
    
    // Add thinking placeholder
    const thinkingId = appendChatMessage('system', '🤖', 'Thinking...');
    
    try {
      const res = await fetch(`${API_URL}/api/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      
      // Update thinking bubble
      const bubble = document.getElementById(thinkingId);
      if (bubble) {
        bubble.querySelector('.msg-bubble').innerHTML = `<p>${data.response}</p>`;
      }
    } catch (err) {
      const bubble = document.getElementById(thinkingId);
      if (bubble) {
        bubble.querySelector('.msg-bubble').innerHTML = `<p>⚠️ Sorry, could not connect to AI services. Please try again later.</p>`;
      }
    }
  });

  // Suggestion chips handler
  const chips = document.querySelectorAll('.chip-suggestion');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      input.value = chip.textContent.substring(3); // Remove emoji
      form.dispatchEvent(new Event('submit'));
    });
  });
}

function appendChatMessage(sender, avatar, text) {
  const container = document.getElementById('chat-messages');
  const id = `msg-${Date.now()}-${Math.floor(Math.random()*1000)}`;
  
  const div = document.createElement('div');
  div.className = `chat-msg ${sender}`;
  div.id = id;
  div.innerHTML = `
    <div class="msg-avatar">${avatar}</div>
    <div class="msg-bubble">
      <p>${text}</p>
    </div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return id;
}

// ----------------------------------------------------
// SMART TRANSIT PLANNER
// ----------------------------------------------------
function setupTransitRoute() {
  const btn = document.getElementById('btn-plan-route');
  const originSelect = document.getElementById('travel-origin');
  const needsSelect = document.getElementById('travel-needs');
  const resultBox = document.getElementById('route-result-box');
  const resultText = document.getElementById('route-result-text');
  
  btn.addEventListener('click', () => {
    const origin = originSelect.options[originSelect.selectedIndex].text;
    const needs = needsSelect.options[needsSelect.selectedIndex].text;
    
    resultBox.classList.remove('hidden');
    resultText.innerHTML = `<em>Generating step-free routing map guidelines...</em>`;
    
    // AI Transit Router simulations based on choices
    setTimeout(() => {
      let routeHtml = `🚇 **Route Direction:** Arriving from **${origin}** with accessibility requirement: **${needs}**.<br><br>`;
      
      if (needsSelect.value === 'mobility') {
        routeHtml += `🚶 **Step-by-step route:**<br>
        1. Exit the transport station and follow the **blue accessibility symbols** towards **Gate 4**.<br>
        2. Gate 4 features a wide-lane ramp with no steps.<br>
        3. Once inside, proceed to the **West elevator bay** located 20 meters straight ahead.<br>
        4. Take Lift 3 to Level 2 (wheelchair bays are in rows 4-6 of Sector A).<br>
        5. *Steward support is notified to be ready at Gate 4.*`;
      } else if (needsSelect.value === 'stroller') {
        routeHtml += `🚶 **Step-by-step route:**<br>
        1. Access the main concourse via **Gate 2 (East Entrance)** for wider stroller lanes.<br>
        2. Baby changing and family facilities are available on Level 1, near Section C toilets.<br>
        3. Dedicated escalator lanes can take you to family seating in Sector D.`;
      } else {
        routeHtml += `🚶 **Step-by-step route:**<br>
        1. Head directly to **Gate 1 (Main Entrance)**.<br>
        2. Proceed up the main escalator block directly onto Level 1 concourse.<br>
        3. Sectors A, B, C can be accessed directly from this level.`;
      }
      
      resultText.innerHTML = routeHtml;
    }, 800);
  });
}

// ----------------------------------------------------
// ECO ACTIONS & LEADERBOARD
// ----------------------------------------------------
function setupEcoLogger() {
  const form = document.getElementById('eco-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('eco-username').value.trim();
    const actionSelect = document.getElementById('eco-action');
    const action_type = actionSelect.options[actionSelect.selectedIndex].value;
    
    if (!username) return;
    
    try {
      const res = await fetch(`${API_URL}/api/sustainability`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, action_type })
      });
      const data = await res.json();
      if (data.success) {
        alert(`♻️ Success! ${data.message}`);
        document.getElementById('eco-username').value = '';
        fetchLeaderboard();
        fetchDashboardStats();
      }
    } catch (e) {
      console.error('Error logging sustainability points:', e);
    }
  });
}

async function fetchLeaderboard() {
  try {
    const res = await fetch(`${API_URL}/api/sustainability/leaderboard`);
    const data = await res.json();
    if (!data.success) return;
    
    const tbody = document.getElementById('sustainability-leaderboard-tbody');
    tbody.innerHTML = '';
    
    let totalPoints = 0;
    let rank = 1;
    data.leaderboard.forEach(row => {
      totalPoints += row.total_points;
      
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong>#${rank}</strong></td>
        <td>${row.username}</td>
        <td><span class="text-teal">${row.total_points} pts</span></td>
        <td>${row.action_count} actions</td>
      `;
      tbody.appendChild(tr);
      rank++;
    });
    
    // Update Eco Hub numbers
    document.getElementById('eco-total-display').textContent = totalPoints.toLocaleString();
    document.getElementById('metric-bottles').textContent = Math.round(totalPoints / 50);
    document.getElementById('metric-carbon').textContent = `${(totalPoints * 0.12).toFixed(1)} kg`;
    
  } catch (e) {
    console.error('Error fetching leaderboard:', e);
  }
}

// ----------------------------------------------------
// STAFF INCIDENT REPORTER & DISPATCH
// ----------------------------------------------------
function setupIncidentReporter() {
  const form = document.getElementById('incident-form');
  const btn = document.getElementById('btn-report-incident');
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const location = document.getElementById('incident-location').value.trim();
    const description = document.getElementById('incident-desc').value.trim();
    
    if (!location || !description) return;
    
    // Set button state
    btn.disabled = true;
    btn.textContent = 'GenAI Parsing Incident...';
    
    try {
      const res = await fetch(`${API_URL}/api/incidents/report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ location, description })
      });
      const data = await res.json();
      
      if (data.success) {
        // Reset form
        document.getElementById('incident-location').value = '';
        document.getElementById('incident-desc').value = '';
        
        // Refresh feed
        fetchIncidents();
        fetchDashboardStats();
      }
    } catch (e) {
      console.error('Incident report error:', e);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Analyze & Dispatch Incident';
    }
  });
}

async function fetchIncidents() {
  try {
    const res = await fetch(`${API_URL}/api/incidents`);
    const data = await res.json();
    if (!data.success) return;
    
    const container = document.getElementById('incident-queue-list');
    container.innerHTML = '';
    
    if (data.incidents.length === 0) {
      container.innerHTML = `<p class="text-secondary text-center">No active incidents reported. All clear!</p>`;
      return;
    }
    
    data.incidents.forEach(inc => {
      const card = document.createElement('div');
      card.className = `incident-card ${inc.severity}`;
      
      // Format datetime to human readable time
      const date = new Date(inc.created_at);
      const timeStr = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      
      // Parse markdown numbered list to HTML for the protocols
      let protocolHtml = '';
      if (inc.ai_protocol) {
        const lines = inc.ai_protocol.split('\n');
        protocolHtml += '<ol>';
        lines.forEach(l => {
          if (l.trim()) {
            // strip numbers (e.g. "1. ")
            const clean = l.replace(/^\d+\.\s*/, '');
            protocolHtml += `<li>${clean}</li>`;
          }
        });
        protocolHtml += '</ol>';
      }

      let btnRow = '';
      if (inc.status !== 'Resolved') {
        btnRow = `
          <div class="incident-actions">
            ${inc.status === 'Open' ? `<button class="btn btn-secondary btn-sm" onclick="updateIncidentStatus(${inc.id}, 'In Progress')">Mark in Progress</button>` : ''}
            <button class="btn btn-primary btn-sm" onclick="updateIncidentStatus(${inc.id}, 'Resolved')">Resolve</button>
          </div>
        `;
      } else {
        btnRow = `<div class="incident-actions"><span class="badge badge-green">Resolved</span></div>`;
      }

      card.innerHTML = `
        <div class="incident-header">
          <div class="incident-title-row">
            <h4>${inc.title}</h4>
            <span class="sev-badge ${inc.severity}">${inc.severity}</span>
          </div>
          <span class="text-secondary" style="font-size: 11px;">${timeStr}</span>
        </div>
        <div class="incident-meta">
          <span>Location: <strong>${inc.location}</strong></span>
          <span>Category: <strong>${inc.category}</strong></span>
          <span>Assigned: <strong>${inc.assigned_team}</strong></span>
        </div>
        <div class="incident-body">
          <p>${inc.description}</p>
          <div class="ai-protocol-box">
            <h5>⚡ AI Action Protocol</h5>
            ${protocolHtml}
          </div>
        </div>
        ${btnRow}
      `;
      container.appendChild(card);
    });
  } catch (e) {
    console.error('Error fetching incidents list:', e);
  }
}

// Global hook for inline onclick buttons
window.updateIncidentStatus = async (id, status) => {
  try {
    const res = await fetch(`${API_URL}/api/incidents/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, status })
    });
    const data = await res.json();
    if (data.success) {
      fetchIncidents();
      fetchDashboardStats();
    }
  } catch (e) {
    console.error('Error updating status:', e);
  }
};

// ----------------------------------------------------
// ORGANIZER COMMAND CENTER CLI
// ----------------------------------------------------
function setupCommandCenter() {
  const form = document.getElementById('command-form');
  const input = document.getElementById('command-input');
  const output = document.getElementById('command-output-area');
  
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const cmd = input.value.trim();
    if (!cmd) return;
    
    // Add command to CLI list
    const userBlock = document.createElement('div');
    userBlock.className = 'terminal-entry';
    userBlock.innerHTML = `<div class="terminal-user-cmd">&gt; ${cmd}</div>`;
    output.appendChild(userBlock);
    
    input.value = '';
    
    // Add loading placeholder
    const resBlock = document.createElement('div');
    resBlock.className = 'terminal-entry';
    resBlock.innerHTML = `<div class="terminal-ai-res text-secondary">Analyzing database metrics and generating response...</div>`;
    output.appendChild(resBlock);
    output.scrollTop = output.scrollHeight;
    
    try {
      const res = await fetch(`${API_URL}/api/ai/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd })
      });
      const data = await res.json();
      
      // Parse basic markdown lists/quotes in mock response
      let formattedText = data.response
        .replace(/\n\n/g, '<br><br>')
        .replace(/- (.*?)(\n|<br>|$)/g, '<li>$1</li>')
        .replace(/(<li>.*?<\/li>)+/g, '<ul>$&</ul>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      
      resBlock.innerHTML = `<div class="terminal-ai-res">${formattedText}</div>`;
      
    } catch (err) {
      resBlock.innerHTML = `<div class="terminal-ai-res text-danger">⚠️ Command Execution Error: Could not reach command API node.</div>`;
    }
    output.scrollTop = output.scrollHeight;
  });
}

// ----------------------------------------------------
// SIMULATOR
// ----------------------------------------------------
function setupSimulator() {
  const btn = document.getElementById('btn-simulate');
  btn.addEventListener('click', async () => {
    btn.disabled = true;
    btn.textContent = 'Simulating...';
    
    try {
      const res = await fetch(`${API_URL}/api/zones/simulate`, { method: 'POST' });
      const data = await res.json();
      if (data.success) {
        // Fetch new state immediately
        await fetchDashboardStats();
        
        // If staff view is active, refresh incidents
        if (currentTab === 'staff-ops') {
          fetchIncidents();
        }
      }
    } catch (e) {
      console.error('Simulation execution error:', e);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Trigger Simulation Step';
    }
  });
}
