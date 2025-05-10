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
  renderTrackerNavigation: function() {
    const nav = document.getElementById('tracker-nav');
    nav.innerHTML = '<ul><li>Game Expectations</li><li>NPC Tracker</li><li>Travel Planner</li></ul>';
  },
  displayTrackerView: function(trackerName, campaignData) {
    const main = document.getElementById('main-content');
    main.innerHTML = `<h2>${trackerName}</h2><div>Tracker UI goes here.</div>`;
  }
};