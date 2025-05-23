(function() {
// SettlementTracker.js

// Logic for Settlement Tracker
window.settlementTracker = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.settlements) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.settlements = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns); // Assuming 'allCampaigns' is globally available
  },

  renderSettlementTrackerListView: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Settlement Tracker</h2>
      <button class="btn btn-primary" id="add-settlement-btn">Add Settlement</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No settlements yet. Add one to get started!</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((settlement, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong>${window.modalUtils.escapeHtml(settlement.name) || '(Unnamed Settlement)'}</strong>
              <span class="text-muted small ms-2">(${window.modalUtils.escapeHtml(settlement.size) || 'N/A'})</span>
            </div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted mt-1">Leader: ${window.modalUtils.escapeHtml(settlement.localLeader) || 'N/A'}</div>
          <div class="small text-muted mt-1">Trait: ${window.modalUtils.escapeHtml(settlement.trait ? settlement.trait.substring(0,100) + (settlement.trait.length > 100 ? '...' : '') : 'N/A')}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html; // This is the listContainer

    document.getElementById('add-settlement-btn').onclick = () => {
      this.renderSettlementFormModal(container, campaign, null, false);
    };

    container.querySelectorAll('[data-view]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-view'));
        this.renderSettlementEntryView(container, campaign, idx);
      };
    });

    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-delete'));
        const settlementToDelete = entries[idx];
        if (confirm(`Are you sure you want to delete the settlement: "${window.modalUtils.escapeHtml(settlementToDelete.name)}"?`)) {
          let currentEntries = this.getEntries(campaign);
          currentEntries.splice(idx, 1);
          this.saveEntries(campaign, currentEntries);
          this.renderSettlementTrackerListView(container, campaign); 
        }
      };
    });
  },

  renderSettlementEntryView: function(listContainer, campaign, idx) {
    const entries = this.getEntries(campaign);
    const settlement = entries[idx];

    if (!settlement) {
      console.error("Settlement not found for view at index:", idx);
      window.modalUtils.hideModal();
      window.modalUtils.showModal("Error", "<p>Could not find the selected settlement.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
      this.renderSettlementTrackerListView(listContainer, campaign);
      return;
    }

    let contentHtml = `<dl class="row">
      <dt class="col-sm-4">Name:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(settlement.name) || 'N/A'}</dd>
      <dt class="col-sm-4">Size:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(settlement.size) || 'N/A'}</dd>
      <dt class="col-sm-4">Local Leader:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(settlement.localLeader) || 'N/A'}</dd>
      <dt class="col-sm-4">GP Value of Item for Sale:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(settlement.gpValue) || 'N/A'}</dd>
      <dt class="col-sm-4">Defining Trait:</dt><dd class="col-sm-8"><pre>${window.modalUtils.escapeHtml(settlement.trait) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Claim to Fame:</dt><dd class="col-sm-8"><pre>${window.modalUtils.escapeHtml(settlement.fame) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Current Calamity:</dt><dd class="col-sm-8"><pre>${window.modalUtils.escapeHtml(settlement.calamity) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Noteworthy People:</dt><dd class="col-sm-8"><pre>${window.modalUtils.escapeHtml(settlement.people) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Noteworthy Places:</dt><dd class="col-sm-8"><pre>${window.modalUtils.escapeHtml(settlement.places) || 'N/A'}</pre></dd>
    </dl>`;
    
    let footerHtml = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editSettlementFromViewBtn">Edit</button>`;
    
    window.modalUtils.showModal(`View Settlement: ${window.modalUtils.escapeHtml(settlement.name)}`, contentHtml, footerHtml);
    
    const editButton = document.getElementById('editSettlementFromViewBtn');
    if (editButton) {
      editButton.onclick = () => {
        this.renderSettlementFormModal(listContainer, campaign, idx, true);
      };
    }
  },

  renderSettlementFormModal: function(listContainer, campaign, idx, isEditFromView = false) {
    const entries = this.getEntries(campaign);
    const isEditMode = idx !== null && idx !== undefined;
    let settlementToEdit;

    if (isEditMode) {
      if (idx < 0 || idx >= entries.length) {
        console.error("Settlement index out of bounds for edit:", idx);
        window.modalUtils.hideModal();
        window.modalUtils.showModal("Error", "<p>Could not find settlement to edit.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
        this.renderSettlementTrackerListView(listContainer, campaign);
        return;
      }
      settlementToEdit = {...entries[idx]};
    } else {
      settlementToEdit = { name: '', size: '', trait: '', fame: '', calamity: '', localLeader: '', people: '', places: '', gpValue: '' };
    }
    
    const modalTitle = isEditMode ? `Edit Settlement: ${window.modalUtils.escapeHtml(settlementToEdit.name)}` : 'Add New Settlement';

    let formHtml = `<form id="settlement-form-modal" novalidate>
      <div class="mb-3">
        <label for="settlement-name" class="form-label">Name</label>
        <input type="text" class="form-control" id="settlement-name" name="name" value="${window.modalUtils.escapeHtml(settlementToEdit.name)}" required />
        <div class="invalid-feedback">Name is required.</div>
      </div>
      <div class="row">
        <div class="col-md-6 mb-3">
          <label for="settlement-size" class="form-label">Size</label>
          <select class="form-select" id="settlement-size" name="size">
            <option value="">Select size...</option>
            <option value="Hamlet (Pop. <100)" ${settlementToEdit.size === "Hamlet (Pop. <100)" ? "selected" : ""}>Hamlet (Pop. &lt;100)</option>
            <option value="Village (Pop. 100-1k)" ${settlementToEdit.size === "Village (Pop. 100-1k)" ? "selected" : ""}>Village (Pop. 100-1k)</option>
            <option value="Town (Pop. 1k-6k)" ${settlementToEdit.size === "Town (Pop. 1k-6k)" ? "selected" : ""}>Town (Pop. 1k-6k)</option>
            <option value="City (Pop. 6k-25k)" ${settlementToEdit.size === "City (Pop. 6k-25k)" ? "selected" : ""}>City (Pop. 6k-25k)</option>
            <option value="Metropolis (Pop. >25k)" ${settlementToEdit.size === "Metropolis (Pop. >25k)" ? "selected" : ""}>Metropolis (Pop. &gt;25k)</option>
          </select>
        </div>
        <div class="col-md-6 mb-3">
          <label for="settlement-localLeader" class="form-label">Local Leader</label>
          <input type="text" class="form-control" id="settlement-localLeader" name="localLeader" value="${window.modalUtils.escapeHtml(settlementToEdit.localLeader)}" />
        </div>
      </div>
      <div class="mb-3">
        <label for="settlement-trait" class="form-label">Defining Trait</label>
        <textarea class="form-control" id="settlement-trait" name="trait" rows="2">${window.modalUtils.escapeHtml(settlementToEdit.trait)}</textarea>
      </div>
      <div class="mb-3">
        <label for="settlement-fame" class="form-label">Claim to Fame</label>
        <textarea class="form-control" id="settlement-fame" name="fame" rows="2">${window.modalUtils.escapeHtml(settlementToEdit.fame)}</textarea>
      </div>
      <div class="mb-3">
        <label for="settlement-calamity" class="form-label">Current Calamity</label>
        <textarea class="form-control" id="settlement-calamity" name="calamity" rows="2">${window.modalUtils.escapeHtml(settlementToEdit.calamity)}</textarea>
      </div>
      <div class="mb-3">
        <label for="settlement-people" class="form-label">Noteworthy People (use newlines for list)</label>
        <textarea class="form-control" id="settlement-people" name="people" rows="3">${window.modalUtils.escapeHtml(settlementToEdit.people)}</textarea>
      </div>
      <div class="mb-3">
        <label for="settlement-places" class="form-label">Noteworthy Places (use newlines for list)</label>
        <textarea class="form-control" id="settlement-places" name="places" rows="3">${window.modalUtils.escapeHtml(settlementToEdit.places)}</textarea>
      </div>
      <div class="mb-3">
        <label for="settlement-gpValue" class="form-label">GP Value of Most Expensive Item for Sale</label>
        <input type="number" class="form-control" id="settlement-gpValue" name="gpValue" value="${window.modalUtils.escapeHtml(settlementToEdit.gpValue)}" min="0" />
      </div>
    </form>`;
    
    let footerHtml = `<button type="button" class="btn btn-secondary" id="cancelSettlementFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveSettlementFormBtn">Save</button>`;
      
    window.modalUtils.showModal(modalTitle, formHtml, footerHtml);

    const form = document.getElementById('settlement-form-modal');
    const nameInput = form.querySelector('#settlement-name');

    document.getElementById('saveSettlementFormBtn').onclick = () => {
      const newName = nameInput.value.trim();
      if (!newName) {
        nameInput.classList.add('is-invalid');
        form.classList.add('was-validated');
        // alert('Settlement Name is required.'); // Requirement, but Bootstrap validation is cleaner
        return;
      }
      nameInput.classList.remove('is-invalid');
      form.classList.remove('was-validated');

      const updatedSettlementData = {
        name: newName,
        size: form.querySelector('#settlement-size').value,
        trait: form.querySelector('#settlement-trait').value.trim(),
        fame: form.querySelector('#settlement-fame').value.trim(),
        calamity: form.querySelector('#settlement-calamity').value.trim(),
        localLeader: form.querySelector('#settlement-localLeader').value.trim(),
        people: form.querySelector('#settlement-people').value.trim(), // Stays as text block
        places: form.querySelector('#settlement-places').value.trim(), // Stays as text block
        gpValue: form.querySelector('#settlement-gpValue').value.trim()
      };

      let currentEntries = this.getEntries(campaign);
      if (isEditMode) {
        currentEntries[idx] = updatedSettlementData;
      } else {
        currentEntries.push(updatedSettlementData);
      }
      this.saveEntries(campaign, currentEntries);
      window.modalUtils.hideModal();
      this.renderSettlementTrackerListView(listContainer, campaign); 
    };

    document.getElementById('cancelSettlementFormBtn').onclick = () => {
      if (isEditFromView && isEditMode) {
        const latestEntries = this.getEntries(campaign); // Re-fetch in case of race conditions
        if (idx < latestEntries.length) {
           this.renderSettlementEntryView(listContainer, campaign, idx);
        } else { // Should not happen if idx was valid
           window.modalUtils.hideModal();
           this.renderSettlementTrackerListView(listContainer, campaign);
        }
      } else {
        window.modalUtils.hideModal();
      }
    };
  }
};

// Register with main UI rendering system
window.ui = window.ui || {};
window.ui.renderTrackerViews = window.ui.renderTrackerViews || {};
window.ui.renderTrackerViews['Settlement Tracker'] = function(container, campaign) {
  window.settlementTracker.renderSettlementTrackerListView(container, campaign);
};

})();