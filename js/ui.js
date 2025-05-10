// UI rendering functions for TTRPG Campaign Tracker
window.ui = {
  renderCampaignSelector: function(campaignNames) {
    const selector = document.getElementById('campaign-selector');
    if (!selector) return;
    let html = '<select id="campaign-selector-dropdown"><option value="">Select Campaign</option>';
    for (const name of campaignNames) {
      html += `<option value="${name}">${name}</option>`;
    }
    html += '</select>';
    selector.innerHTML = html;
  },
  renderTrackerNavigation: function(onSelect) {
    const nav = document.getElementById('tracker-nav');
    nav.innerHTML = `
      <ul class="nav flex-column nav-pills">
        <li class="nav-item">
          <button class="nav-link" id="nav-game-expectations">Game Expectations</button>
        </li>
        <li class="nav-item">
          <button class="nav-link" id="nav-npc-tracker">NPC Tracker</button>
        </li>
        <li class="nav-item">
          <button class="nav-link" id="nav-travel-planner">Travel Planner</button>
        </li>
      </ul>
    `;
    if (onSelect) {
      nav.querySelectorAll('.nav-link').forEach(btn => {
        btn.onclick = (e) => onSelect(e.target.id);
      });
    }
  },
  displayTrackerView: function(trackerName, campaignData) {
    const main = document.getElementById('main-content');
    if (trackerName === 'Game Expectations') {
      window.gameExpectations.renderGameExpectationsView(main, campaignData);
    } else {
      main.innerHTML = `<h2>${trackerName}</h2><div>Tracker UI goes here.</div>`;
    }
  }
};