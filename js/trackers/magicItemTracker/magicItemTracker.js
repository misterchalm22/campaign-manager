(function() {
// Magic Item Tracker

window.magicItemTracker = {
  getTrackerData: function(campaign) { // Renamed for clarity from generic 'getTracker'
    return (campaign.trackers && campaign.trackers.magicItemTrackerData) || { // Data key changed for clarity
      tiers: [
        { name: 'Levels 1-4', rarities: { Common: [], Uncommon: [], Rare: [], 'Very Rare': [], Legendary: [] } },
        { name: 'Levels 5-10', rarities: { Common: [], Uncommon: [], Rare: [], 'Very Rare': [], Legendary: [] } },
        { name: 'Levels 11-16', rarities: { Common: [], Uncommon: [], Rare: [], 'Very Rare': [], Legendary: [] } },
        { name: 'Levels 17-20', rarities: { Common: [], Uncommon: [], Rare: [], 'Very Rare': [], Legendary: [] } }
      ]
    };
  },
  saveTrackerData: function(campaign, trackerData) { // Renamed for clarity
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.magicItemTrackerData = trackerData; // Data key changed for clarity
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns); // Assuming 'allCampaigns' is globally available
  },

  // Main view function (replaces old renderMagicItemTracker and renderMagicItemTrackerListView)
  renderMagicItemTrackerView: function(container, campaign) {
    const trackerData = this.getTrackerData(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Magic Item Tracker</h2>
      <button class="btn btn-primary" id="edit-magic-item-tracker-btn">Edit Items</button>
    </div>`;

    trackerData.tiers.forEach((tier) => {
      html += `<div class="card mb-3">
        <div class="card-header"><h4>${window.modalUtils.escapeHtml(tier.name)}</h4></div>
        <div class="card-body">`;
      Object.keys(tier.rarities).forEach(rarity => {
        const items = tier.rarities[rarity] || [];
        html += `<div class="mb-3">
          <h5>${window.modalUtils.escapeHtml(rarity)} 
            <span class="badge bg-secondary rounded-pill">${items.length}</span>
          </h5>`;
        if (items.length === 0) {
          html += `<p class="text-muted">No ${window.modalUtils.escapeHtml(rarity.toLowerCase())} items recorded for this tier.</p>`;
        } else {
          html += '<ul class="list-group">';
          items.forEach(item => {
            // For now, items are just strings. If they become objects, this needs to change.
            html += `<li class="list-group-item">${window.modalUtils.escapeHtml(item)}</li>`;
          });
          html += '</ul>';
        }
        html += `</div>`;
      });
      html += `</div></div>`; // Close card-body and card
    });
    
    container.innerHTML = html;

    document.getElementById('edit-magic-item-tracker-btn').onclick = () => {
      this.renderMagicItemFormModal(container, campaign);
    };
  },

  // Form Modal for editing all magic items
  renderMagicItemFormModal: function(viewContainer, campaign) {
    // Deep clone the tracker data to avoid modifying the original object directly during form interaction
    const trackerDataToEdit = JSON.parse(JSON.stringify(this.getTrackerData(campaign))); 

    let formHtml = `<form id="magic-item-tracker-edit-form" class="container-fluid">`;
    trackerDataToEdit.tiers.forEach((tier, tierIndex) => {
      formHtml += `<fieldset class="mb-4 p-3 border rounded">
        <legend class="h5">${window.modalUtils.escapeHtml(tier.name)}</legend>`;
      Object.keys(tier.rarities).forEach(rarity => {
        formHtml += `<div class="mb-3">
          <label class="form-label fw-bold">${window.modalUtils.escapeHtml(rarity)}</label>
          <div id="form-tier${tierIndex}-rarity-${rarity.replace(/\s+/g, '')}-list" class="list-of-items-in-form">`;
        
        (tier.rarities[rarity] || []).forEach((item, itemIndex) => {
          formHtml += `
            <div class="input-group mb-2 item-entry">
              <input type="text" class="form-control item-name-input" value="${window.modalUtils.escapeHtml(item)}" data-tier-index="${tierIndex}" data-rarity="${rarity}" data-item-index="${itemIndex}">
              <button class="btn btn-outline-danger remove-item-btn" type="button">Remove</button>
            </div>`;
        });
        formHtml += `</div>
          <button type="button" class="btn btn-sm btn-outline-primary add-item-btn" data-tier-index="${tierIndex}" data-rarity="${rarity}">+ Add ${window.modalUtils.escapeHtml(rarity)} Item</button>
        </div>`;
      });
      formHtml += `</fieldset>`;
    });
    formHtml += `</form>`;

    const modalTitle = 'Edit Magic Item Distribution';
    const footerHtml = `
      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
      <button type="button" class="btn btn-success" id="save-magic-item-tracker-btn">Save Changes</button>`;

    window.modalUtils.showModal(modalTitle, formHtml, footerHtml, 'modal-xl'); // Use a larger modal

    // Event delegation for dynamically added/removed items
    const formElement = document.getElementById('magic-item-tracker-edit-form');
    formElement.addEventListener('click', function(event) {
      if (event.target.classList.contains('add-item-btn')) {
        const tierIndex = event.target.dataset.tierIndex;
        const rarity = event.target.dataset.rarity;
        const listContainerId = `form-tier${tierIndex}-rarity-${rarity.replace(/\s+/g, '')}-list`;
        const listContainer = document.getElementById(listContainerId);
        const newItemIndex = listContainer.children.length;

        const newItemHtml = `
          <div class="input-group mb-2 item-entry">
            <input type="text" class="form-control item-name-input" value="" data-tier-index="${tierIndex}" data-rarity="${rarity}" data-item-index="${newItemIndex}">
            <button class="btn btn-outline-danger remove-item-btn" type="button">Remove</button>
          </div>`;
        listContainer.insertAdjacentHTML('beforeend', newItemHtml);
      }
      if (event.target.classList.contains('remove-item-btn')) {
        event.target.closest('.item-entry').remove();
        // Note: Re-indexing data-item-index after removal is complex and might not be necessary if data is collected by iterating inputs.
      }
    });
    
    document.getElementById('save-magic-item-tracker-btn').onclick = () => {
      const updatedTrackerData = { tiers: [] };
      trackerDataToEdit.tiers.forEach((originalTier, tierIndex) => {
        const newTier = { name: originalTier.name, rarities: {} };
        Object.keys(originalTier.rarities).forEach(rarity => {
          newTier.rarities[rarity] = [];
          const listContainerId = `form-tier${tierIndex}-rarity-${rarity.replace(/\s+/g, '')}-list`;
          const listContainer = document.getElementById(listContainerId);
          if (listContainer) {
            listContainer.querySelectorAll('.item-name-input').forEach(inputElement => {
              const itemName = inputElement.value.trim();
              if (itemName) { // Only save non-empty item names
                newTier.rarities[rarity].push(itemName);
              }
            });
          }
        });
        updatedTrackerData.tiers.push(newTier);
      });

      this.saveTrackerData(campaign, updatedTrackerData);
      window.modalUtils.hideModal();
      this.renderMagicItemTrackerView(viewContainer, campaign); // Refresh the main view
    };
  }
};

// Register with main UI rendering system
window.ui = window.ui || {};
window.ui.renderTrackerViews = window.ui.renderTrackerViews || {};
window.ui.renderTrackerViews['Magic Item Tracker'] = function(container, campaign) {
  window.magicItemTracker.renderMagicItemTrackerView(container, campaign);
};

})();