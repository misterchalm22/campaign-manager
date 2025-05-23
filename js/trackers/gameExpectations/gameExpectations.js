(function() {
// Logic for Game Expectations tracker (Single Document per Campaign)

window.gameExpectations = {
  // Fetches the single game expectations object for the campaign
  getGameExpectations: function(campaign) {
    return (campaign.trackers && campaign.trackers.gameExpectationsData) || {
      campaignTone: '',
      themes: '',
      playerBuyIn: '',
      forbiddenTopics: '',
      sensitiveElements: [] // Array of strings
    };
  },

  // Saves the single game expectations object for the campaign
  saveGameExpectations: function(campaign, expectationsData) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.gameExpectationsData = expectationsData;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns); // Assuming 'allCampaigns' is globally available
  },

  // Renders the read-only view of game expectations
  renderGameExpectationsView: function(container, campaign) {
    const expectations = this.getGameExpectations(campaign);
    
    let sensitiveHtml = 'N/A';
    if (expectations.sensitiveElements && expectations.sensitiveElements.length > 0) {
      sensitiveHtml = '<ul class="list-unstyled mb-0">';
      expectations.sensitiveElements.forEach(element => {
        sensitiveHtml += `<li>${window.modalUtils.escapeHtml(element)}</li>`;
      });
      sensitiveHtml += '</ul>';
    }

    let html = `
      <div class="card">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h2>Game Expectations</h2>
          <button class="btn btn-primary" id="edit-expectations-btn">Edit Expectations</button>
        </div>
        <div class="card-body">
          <dl class="row">
            <dt class="col-sm-3">Campaign Tone:</dt>
            <dd class="col-sm-9"><pre>${window.modalUtils.escapeHtml(expectations.campaignTone) || 'N/A'}</pre></dd>

            <dt class="col-sm-3">Themes:</dt>
            <dd class="col-sm-9"><pre>${window.modalUtils.escapeHtml(expectations.themes) || 'N/A'}</pre></dd>

            <dt class="col-sm-3">Player Buy-in/Consent:</dt>
            <dd class="col-sm-9"><pre>${window.modalUtils.escapeHtml(expectations.playerBuyIn) || 'N/A'}</pre></dd>

            <dt class="col-sm-3">Forbidden Topics/Hard Limits:</dt>
            <dd class="col-sm-9"><pre>${window.modalUtils.escapeHtml(expectations.forbiddenTopics) || 'N/A'}</pre></dd>

            <dt class="col-sm-3">Potentially Sensitive Elements (Soft Limits/Veil):</dt>
            <dd class="col-sm-9">${sensitiveHtml}</dd>
          </dl>
        </div>
      </div>`;
      
    container.innerHTML = html;

    document.getElementById('edit-expectations-btn').onclick = () => {
      this.renderGameExpectationsFormModal(container, campaign);
    };
  },

  // Renders the form modal for editing game expectations
  renderGameExpectationsFormModal: function(viewContainer, campaign) {
    const currentExpectations = this.getGameExpectations(campaign);

    // Build sensitive elements form area
    let sensitiveElementsFormHtml = '<div id="sensitive-elements-form-area">';
    currentExpectations.sensitiveElements.forEach((element, index) => {
      sensitiveElementsFormHtml += `
        <div class="input-group mb-2 sensitive-element-entry">
          <input type="text" class="form-control sensitive-element-input" value="${window.modalUtils.escapeHtml(element)}" placeholder="Sensitive element description">
          <button class="btn btn-outline-danger remove-sensitive-element-btn" type="button" data-index="${index}">Remove</button>
        </div>`;
    });
    sensitiveElementsFormHtml += '</div>';
    sensitiveElementsFormHtml += `<button type="button" class="btn btn-sm btn-outline-primary mt-1" id="add-sensitive-element-btn">Add Sensitive Element</button>`;

    const formHtml = `
      <form id="game-expectations-form" novalidate>
        <div class="mb-3">
          <label for="ge-campaignTone" class="form-label">Campaign Tone:</label>
          <textarea class="form-control" id="ge-campaignTone" name="campaignTone" rows="3">${window.modalUtils.escapeHtml(currentExpectations.campaignTone)}</textarea>
        </div>
        <div class="mb-3">
          <label for="ge-themes" class="form-label">Themes:</label>
          <textarea class="form-control" id="ge-themes" name="themes" rows="3">${window.modalUtils.escapeHtml(currentExpectations.themes)}</textarea>
        </div>
        <div class="mb-3">
          <label for="ge-playerBuyIn" class="form-label">Player Buy-in/Consent:</label>
          <textarea class="form-control" id="ge-playerBuyIn" name="playerBuyIn" rows="3">${window.modalUtils.escapeHtml(currentExpectations.playerBuyIn)}</textarea>
        </div>
        <div class="mb-3">
          <label for="ge-forbiddenTopics" class="form-label">Forbidden Topics/Hard Limits:</label>
          <textarea class="form-control" id="ge-forbiddenTopics" name="forbiddenTopics" rows="3">${window.modalUtils.escapeHtml(currentExpectations.forbiddenTopics)}</textarea>
        </div>
        <div class="mb-3">
          <label class="form-label">Potentially Sensitive Elements (Soft Limits/Veil):</label>
          ${sensitiveElementsFormHtml}
        </div>
      </form>`;

    const modalTitle = 'Edit Game Expectations';
    const footerHtml = `
      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
      <button type="button" class="btn btn-success" id="save-expectations-btn">Save Changes</button>`;

    window.modalUtils.showModal(modalTitle, formHtml, footerHtml);

    const form = document.getElementById('game-expectations-form');
    const sensitiveElementsArea = document.getElementById('sensitive-elements-form-area');

    const updateSensitiveElementListeners = () => {
      sensitiveElementsArea.querySelectorAll('.remove-sensitive-element-btn').forEach(btn => {
        btn.onclick = (e) => {
          e.target.closest('.sensitive-element-entry').remove();
        };
      });
    };
    
    document.getElementById('add-sensitive-element-btn').onclick = () => {
      const newElementEntry = document.createElement('div');
      newElementEntry.className = 'input-group mb-2 sensitive-element-entry';
      newElementEntry.innerHTML = `
        <input type="text" class="form-control sensitive-element-input" placeholder="Sensitive element description">
        <button class="btn btn-outline-danger remove-sensitive-element-btn" type="button">Remove</button>`;
      sensitiveElementsArea.appendChild(newElementEntry);
      updateSensitiveElementListeners();
    };
    
    updateSensitiveElementListeners(); // Initial setup for existing elements

    document.getElementById('save-expectations-btn').onclick = () => {
      const sensitiveElements = [];
      sensitiveElementsArea.querySelectorAll('.sensitive-element-input').forEach(input => {
        const value = input.value.trim();
        if (value) {
          sensitiveElements.push(value);
        }
      });

      const newExpectations = {
        campaignTone: form.campaignTone.value.trim(),
        themes: form.themes.value.trim(),
        playerBuyIn: form.playerBuyIn.value.trim(),
        forbiddenTopics: form.forbiddenTopics.value.trim(),
        sensitiveElements: sensitiveElements
      };

      this.saveGameExpectations(campaign, newExpectations);
      window.modalUtils.hideModal();
      this.renderGameExpectationsView(viewContainer, campaign); // Refresh the view
    };
  }
};

// Register with main UI rendering system
window.ui = window.ui || {};
window.ui.renderTrackerViews = window.ui.renderTrackerViews || {};
window.ui.renderTrackerViews['Game Expectations'] = function(container, campaign) {
  window.gameExpectations.renderGameExpectationsView(container, campaign);
};

})();