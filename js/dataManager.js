// Data management for TTRPG Campaign Tracker
window.dataManager = {
  loadCampaignsFromLocalStorage: function() {
    try {
      return JSON.parse(localStorage.getItem('ttrpgCampaigns') || '{}');
    } catch {
      return {};
    }
  },
  saveCampaignsToLocalStorage: function(allCampaignData) {
    localStorage.setItem('ttrpgCampaigns', JSON.stringify(allCampaignData));
  },
  exportDataAsJSON: function(allCampaignData) {
    const dataStr = JSON.stringify(allCampaignData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ttrpg_campaigns.json';
    a.click();
    URL.revokeObjectURL(url);
  },
  handleJSONFileImport: function(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      try {
        const data = JSON.parse(e.target.result);
        localStorage.setItem('ttrpgCampaigns', JSON.stringify(data));
        location.reload();
      } catch (err) {
        const msg = document.getElementById('campaign-message');
        if (msg) msg.textContent = 'Invalid JSON file.';
      }
    };
    reader.readAsText(file);
  }
};