// UI rendering functions for TTRPG Campaign Tracker
window.ui = {
  renderCampaignSelector: function(campaignNames, selectedCampaign) {
    const selector = document.getElementById('campaign-selector');
    if (!selector) return;
    let html = '<select id="campaign-selector-dropdown"><option value="">Select Campaign</option>';
    for (const name of campaignNames) {
      html += `<option value="${name}"${selectedCampaign === name ? ' selected' : ''}>${name}</option>`;
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
        <li class="nav-item">
          <button class="nav-link" id="nav-settlement-tracker">Settlement Tracker</button>
        </li>
        <li class="nav-item">
          <button class="nav-link" id="nav-campaign-journal">Campaign Journal</button>
        </li>
        <li class="nav-item">
          <button class="nav-link" id="nav-dm-character-tracker">DM's Character Tracker</button>
        </li>
        <li class="nav-item">
          <button class="nav-link" id="nav-campaign-conflicts">Campaign Conflicts</button>
        </li>
        <li class="nav-item">
          <button class="nav-link" id="nav-magic-item-tracker">Magic Item Tracker</button>
        </li>
        <li class="nav-item">
          <button class="nav-link" id="nav-bastion-tracker">Bastion Tracker</button>
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
    } else if (trackerName === 'NPC Tracker') {
      window.npcTracker.renderNPCList(main, campaignData);
    } else if (trackerName === 'Travel Planner') {
      window.travelPlanner.renderTravelList(main, campaignData);
    } else if (trackerName === 'Settlement Tracker') {
      window.settlementTracker.renderSettlementList(main, campaignData);
    } else if (trackerName === 'Campaign Journal') {
      window.campaignJournal.renderJournalList(main, campaignData);
    } else if (trackerName === "DM's Character Tracker") {
      window.dmCharacterTracker.renderDMCharacterList(main, campaignData);
    } else if (trackerName === 'Campaign Conflicts') {
      window.campaignConflicts.renderCampaignConflictsList(main, campaignData);
    } else if (trackerName === 'Magic Item Tracker') {
      window.magicItemTracker.renderMagicItemTracker(main, campaignData);
    } else if (trackerName === 'Bastion Tracker') {
      window.bastionTracker.renderBastionList(main, campaignData);
    } else {
      main.innerHTML = `<h2>${trackerName}</h2><div>Tracker UI goes here.</div>`;
    }
  }
};