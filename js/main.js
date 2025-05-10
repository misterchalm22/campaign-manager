// Main app logic for TTRPG Campaign Tracker
// Handles campaign management and navigation

let currentCampaign = null;
let allCampaigns = {};

function updateCampaignUI() {
  window.ui.renderCampaignSelector(Object.keys(allCampaigns));
  window.ui.renderTrackerNavigation();
}

function showMessage(msg, isError = false) {
  const el = document.getElementById('campaign-message');
  el.textContent = msg;
  el.style.color = isError ? 'red' : 'green';
  setTimeout(() => { el.textContent = ''; }, 3000);
}

document.addEventListener('DOMContentLoaded', () => {
  // Initialize app
  window.dataManager = window.dataManager || {};
  window.ui = window.ui || {};
  
  // Load campaigns and render UI
  allCampaigns = window.dataManager.loadCampaignsFromLocalStorage();
  updateCampaignUI();

  document.getElementById('create-campaign-btn').onclick = () => {
    const name = prompt('Enter new campaign name:');
    if (!name) return;
    if (allCampaigns[name]) {
      showMessage('Campaign already exists!', true);
      return;
    }
    allCampaigns[name] = { trackers: {} };
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns);
    updateCampaignUI();
    showMessage('Campaign created!');
  };

  document.getElementById('delete-campaign-btn').onclick = () => {
    const selector = document.getElementById('campaign-selector-dropdown');
    const name = selector && selector.value;
    if (!name || !allCampaigns[name]) return;
    if (!confirm(`Delete campaign '${name}'?`)) return;
    delete allCampaigns[name];
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns);
    currentCampaign = null;
    updateCampaignUI();
    showMessage('Campaign deleted!');
  };

  document.getElementById('export-campaigns-btn').onclick = () => {
    window.dataManager.exportDataAsJSON(allCampaigns);
    showMessage('Exported campaigns!');
  };

  document.getElementById('import-campaigns-btn').onclick = () => {
    document.getElementById('import-campaigns-input').click();
  };

  document.getElementById('import-campaigns-input').onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
      window.dataManager.handleJSONFileImport(file);
      showMessage('Imported campaigns!');
    }
  };

  document.getElementById('campaign-selector').onclick = (e) => {
    if (e.target && e.target.id === 'campaign-selector-dropdown') {
      // handled by change event
    }
  };

  document.getElementById('campaign-selector').onchange = (e) => {
    if (e.target && e.target.id === 'campaign-selector-dropdown') {
      const name = e.target.value;
      if (allCampaigns[name]) {
        currentCampaign = name;
        showMessage(`Selected campaign: ${name}`);
        // Optionally, update tracker view here
      }
    }
  };
});