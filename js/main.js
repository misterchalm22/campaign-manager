// Main app logic for TTRPG Campaign Tracker
// Handles campaign management and navigation

let currentCampaign = localStorage.getItem('ttrpgCurrentCampaign') || null;
let allCampaigns = {};

function updateCampaignUI() {
  window.ui.renderCampaignSelector(Object.keys(allCampaigns), currentCampaign);
  window.ui.renderTrackerNavigation(handleNavSelect);
  if (currentCampaign && allCampaigns[currentCampaign]) {
    window.ui.displayTrackerView('Game Expectations', allCampaigns[currentCampaign]);
  }
}

function showMessage(msg, isError = false) {
  const el = document.getElementById('campaign-message');
  el.textContent = msg;
  el.style.color = isError ? 'red' : 'green';
  setTimeout(() => { el.textContent = ''; }, 3000);
}

function handleNavSelect(navId) {
  if (!currentCampaign || !allCampaigns[currentCampaign]) return;
  if (navId === 'nav-game-expectations') {
    window.ui.displayTrackerView('Game Expectations', allCampaigns[currentCampaign]);
  } else if (navId === 'nav-npc-tracker') {
    window.ui.displayTrackerView('NPC Tracker', allCampaigns[currentCampaign]);
  } else if (navId === 'nav-travel-planner') {
    window.ui.displayTrackerView('Travel Planner', allCampaigns[currentCampaign]);
  } else if (navId === 'nav-settlement-tracker') {
    window.ui.displayTrackerView('Settlement Tracker', allCampaigns[currentCampaign]);
  }
  // Add more tracker navs as needed
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
    localStorage.removeItem('ttrpgCurrentCampaign');
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
        localStorage.setItem('ttrpgCurrentCampaign', name);
        showMessage(`Selected campaign: ${name}`);
        window.ui.displayTrackerView('Game Expectations', allCampaigns[currentCampaign]);
      }
    }
  };
});