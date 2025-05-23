(function() {
// Bastion Tracker Module

window.bastionTracker = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.bastions) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.bastions = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns); // Assuming 'allCampaigns' is globally available
  },

  renderBastionTrackerListView: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Bastion Tracker</h2>
      <button class="btn btn-primary" id="add-bastion-entry-btn">Add Bastion</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No bastions recorded yet. Add one to get started!</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((bastion, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong>${window.modalUtils.escapeHtml(bastion.bastionName) || '(Unnamed Bastion)'}</strong>
              <span class="text-muted small ms-2">(${window.modalUtils.escapeHtml(bastion.characterName) || 'N/A'})</span>
            </div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view-idx="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete-idx="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted mt-1">Level: ${window.modalUtils.escapeHtml(bastion.level) || 'N/A'} | Facilities: ${bastion.facilities ? bastion.facilities.length : 0} special</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html;

    document.getElementById('add-bastion-entry-btn').onclick = () => {
      this.renderBastionFormModal(container, campaign, null, false);
    };

    container.querySelectorAll('[data-view-idx]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-view-idx'));
        this.renderBastionEntryView(container, campaign, idx);
      };
    });

    container.querySelectorAll('[data-delete-idx]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-delete-idx'));
        const bastionToDelete = entries[idx];
        if (confirm(`Are you sure you want to delete the bastion: "${window.modalUtils.escapeHtml(bastionToDelete.bastionName)}"?`)) {
          let currentEntries = this.getEntries(campaign);
          currentEntries.splice(idx, 1);
          this.saveEntries(campaign, currentEntries);
          this.renderBastionTrackerListView(container, campaign); 
        }
      };
    });
  },

  renderBastionEntryView: function(listContainer, campaign, idx) {
    const entries = this.getEntries(campaign);
    const bastion = entries[idx];

    if (!bastion) {
      console.error("Bastion not found for view at index:", idx);
      window.modalUtils.hideModal();
      window.modalUtils.showModal("Error", "<p>Could not find the selected bastion.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
      this.renderBastionTrackerListView(listContainer, campaign);
      return;
    }

    let facilitiesHtml = '<p>No special facilities defined.</p>';
    if (bastion.facilities && bastion.facilities.length > 0) {
      facilitiesHtml = '<ul class="list-group mt-2">';
      bastion.facilities.forEach(fac => {
        facilitiesHtml += `
          <li class="list-group-item">
            <h6 class="mb-1">${window.modalUtils.escapeHtml(fac.facilityName) || 'Unnamed Facility'}</h6>
            <small>Space: ${window.modalUtils.escapeHtml(fac.space) || 'N/A'} | Order: ${window.modalUtils.escapeHtml(fac.order) || 'N/A'}</small>
            <p class="mb-1 mt-1"><strong>Hirelings:</strong> <pre class="mb-0 small">${window.modalUtils.escapeHtml(fac.hirelings) || 'N/A'}</pre></p>
            <p class="mb-0"><strong>Notes:</strong> <pre class="mb-0 small">${window.modalUtils.escapeHtml(fac.notes) || 'N/A'}</pre></p>
          </li>`;
      });
      facilitiesHtml += '</ul>';
    }

    let contentHtml = `<dl class="row">
      <dt class="col-sm-3">Bastion Name:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(bastion.bastionName) || 'N/A'}</dd>
      <dt class="col-sm-3">Character:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(bastion.characterName) || 'N/A'}</dd>
      <dt class="col-sm-3">Level:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(bastion.level) || 'N/A'}</dd>
      <dt class="col-sm-12 mt-2">Basic Facilities:</dt><dd class="col-sm-12"><pre>${window.modalUtils.escapeHtml(bastion.basicFacilities) || 'N/A'}</pre></dd>
      <dt class="col-sm-12 mt-2">Defenders:</dt><dd class="col-sm-12"><pre>${window.modalUtils.escapeHtml(bastion.defenders) || 'N/A'}</pre></dd>
      <dt class="col-sm-12 mt-2">Special Facilities:</dt><dd class="col-sm-12">${facilitiesHtml}</dd>
    </dl>`;
    
    let footerHtml = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editBastionFromViewBtn">Edit</button>`;
    
    window.modalUtils.showModal(`View Bastion: ${window.modalUtils.escapeHtml(bastion.bastionName)}`, contentHtml, footerHtml, 'modal-lg');
    
    const editButton = document.getElementById('editBastionFromViewBtn');
    if (editButton) {
      editButton.onclick = () => {
        this.renderBastionFormModal(listContainer, campaign, idx, true);
      };
    }
  },

  renderBastionFormModal: function(listContainer, campaign, idx, isEditFromView = false) {
    const entries = this.getEntries(campaign);
    const isEditMode = idx !== null && idx !== undefined;
    let bastionToEdit;

    if (isEditMode) {
      if (idx < 0 || idx >= entries.length) {
        console.error("Bastion index out of bounds for edit:", idx);
        window.modalUtils.hideModal();
        window.modalUtils.showModal("Error", "<p>Could not find bastion to edit.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
        this.renderBastionTrackerListView(listContainer, campaign);
        return;
      }
      bastionToEdit = JSON.parse(JSON.stringify(entries[idx])); // Deep copy for editing
      if (!bastionToEdit.facilities) bastionToEdit.facilities = [];
    } else {
      bastionToEdit = { bastionName: '', characterName: '', level: '1', facilities: [], basicFacilities: '', defenders: '' };
    }
    
    const modalTitle = isEditMode ? `Edit Bastion: ${window.modalUtils.escapeHtml(bastionToEdit.bastionName)}` : 'Add New Bastion';

    const renderFacilitySubForm = (facility, facilityIndex) => `
      <div class="card mb-2 facility-entry" data-facility-index="${facilityIndex}">
        <div class="card-body">
          <h6 class="card-title">Special Facility ${facilityIndex + 1}</h6>
          <div class="row">
            <div class="col-md-6 mb-2">
              <label class="form-label">Name/Type</label>
              <input type="text" class="form-control facility-name" value="${window.modalUtils.escapeHtml(facility.facilityName || '')}">
            </div>
            <div class="col-md-3 mb-2">
              <label class="form-label">Space</label>
              <input type="text" class="form-control facility-space" value="${window.modalUtils.escapeHtml(facility.space || '')}" placeholder="e.g., 1">
            </div>
            <div class="col-md-3 mb-2">
              <label class="form-label">Order Built</label>
              <input type="number" class="form-control facility-order" value="${window.modalUtils.escapeHtml(facility.order || '')}" min="0">
            </div>
          </div>
          <div class="mb-2">
            <label class="form-label">Hirelings</label>
            <textarea class="form-control facility-hirelings" rows="2">${window.modalUtils.escapeHtml(facility.hirelings || '')}</textarea>
          </div>
          <div class="mb-2">
            <label class="form-label">Notes</label>
            <textarea class="form-control facility-notes" rows="2">${window.modalUtils.escapeHtml(facility.notes || '')}</textarea>
          </div>
          <button type="button" class="btn btn-sm btn-outline-danger remove-facility-btn mt-1">Remove Facility</button>
        </div>
      </div>`;

    let facilitiesFormHtml = '<div id="facilities-form-area">';
    bastionToEdit.facilities.forEach((facility, facilityIndex) => {
      facilitiesFormHtml += renderFacilitySubForm(facility, facilityIndex);
    });
    facilitiesFormHtml += '</div>';

    let formHtml = `<form id="bastion-entry-form" novalidate>
      <div class="row">
        <div class="col-md-8 mb-3">
          <label for="bastion-name" class="form-label">Bastion's Name</label>
          <input type="text" class="form-control" id="bastion-name" name="bastionName" value="${window.modalUtils.escapeHtml(bastionToEdit.bastionName)}" required />
          <div class="invalid-feedback">Bastion Name is required.</div>
        </div>
        <div class="col-md-4 mb-3">
          <label for="bastion-level" class="form-label">Level</label>
          <input type="number" class="form-control" id="bastion-level" name="level" value="${window.modalUtils.escapeHtml(bastionToEdit.level)}" min="1" />
        </div>
      </div>
      <div class="mb-3">
        <label for="bastion-characterName" class="form-label">Character's Name (Owner)</label>
        <input type="text" class="form-control" id="bastion-characterName" name="characterName" value="${window.modalUtils.escapeHtml(bastionToEdit.characterName)}" />
      </div>
      <div class="mb-3">
        <label for="bastion-basicFacilities" class="form-label">Basic Facilities (e.g., Walls, Gate)</label>
        <textarea class="form-control" id="bastion-basicFacilities" name="basicFacilities" rows="3">${window.modalUtils.escapeHtml(bastionToEdit.basicFacilities)}</textarea>
      </div>
      <div class="mb-3">
        <label for="bastion-defenders" class="form-label">Bastion Defenders (e.g., Guards, Traps)</label>
        <textarea class="form-control" id="bastion-defenders" name="defenders" rows="3">${window.modalUtils.escapeHtml(bastionToEdit.defenders)}</textarea>
      </div>
      <hr>
      <h5>Special Facilities</h5>
      ${facilitiesFormHtml}
      <button type="button" class="btn btn-sm btn-outline-primary mt-2" id="add-facility-to-form-btn">Add Special Facility</button>
    </form>`;
    
    let footerHtml = `<button type="button" class="btn btn-secondary" id="cancelBastionFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveBastionFormBtn">Save</button>`;
      
    window.modalUtils.showModal(modalTitle, formHtml, footerHtml, 'modal-lg');

    const form = document.getElementById('bastion-entry-form');
    const nameInput = form.querySelector('#bastion-name');
    const facilitiesArea = document.getElementById('facilities-form-area');

    const updateFacilityEventListeners = () => {
      facilitiesArea.querySelectorAll('.remove-facility-btn').forEach(btn => {
        const newBtn = btn.cloneNode(true); // Avoid duplicate listeners
        btn.parentNode.replaceChild(newBtn, btn);
        newBtn.onclick = (e) => e.target.closest('.facility-entry').remove();
      });
    };
    
    document.getElementById('add-facility-to-form-btn').onclick = () => {
      const newFacilityIndex = facilitiesArea.children.length;
      const newFacilityHtml = renderFacilitySubForm({ facilityName: '', space: '', order: '', hirelings: '', notes: '' }, newFacilityIndex);
      facilitiesArea.insertAdjacentHTML('beforeend', newFacilityHtml);
      updateFacilityEventListeners();
    };
    
    updateFacilityEventListeners(); // Initial setup

    document.getElementById('saveBastionFormBtn').onclick = () => {
      const bastionName = nameInput.value.trim();
      if (!bastionName) {
        nameInput.classList.add('is-invalid');
        form.classList.add('was-validated');
        return;
      }
      nameInput.classList.remove('is-invalid');
      form.classList.remove('was-validated');

      const collectedFacilities = [];
      facilitiesArea.querySelectorAll('.facility-entry').forEach(el => {
        collectedFacilities.push({
          facilityName: el.querySelector('.facility-name').value.trim(),
          space: el.querySelector('.facility-space').value.trim(),
          order: el.querySelector('.facility-order').value.trim(),
          hirelings: el.querySelector('.facility-hirelings').value.trim(),
          notes: el.querySelector('.facility-notes').value.trim()
        });
      });

      const updatedBastionData = {
        bastionName: bastionName,
        characterName: form.querySelector('#bastion-characterName').value.trim(),
        level: form.querySelector('#bastion-level').value.trim(),
        basicFacilities: form.querySelector('#bastion-basicFacilities').value.trim(),
        defenders: form.querySelector('#bastion-defenders').value.trim(),
        facilities: collectedFacilities
      };

      let currentEntries = this.getEntries(campaign);
      if (isEditMode) {
        currentEntries[idx] = updatedBastionData;
      } else {
        currentEntries.push(updatedBastionData);
      }
      this.saveEntries(campaign, currentEntries);
      window.modalUtils.hideModal();
      this.renderBastionTrackerListView(listContainer, campaign); 
    };

    document.getElementById('cancelBastionFormBtn').onclick = () => {
      if (isEditFromView && isEditMode) {
         const latestEntries = this.getEntries(campaign);
         if (idx < latestEntries.length) {
            this.renderBastionEntryView(listContainer, campaign, idx);
         } else {
            window.modalUtils.hideModal();
            this.renderBastionTrackerListView(listContainer, campaign);
         }
      } else {
        window.modalUtils.hideModal();
      }
    };
  }
}; // Fixed: Added closing brace for window.bastionTracker object

// Register with main UI rendering system
window.ui = window.ui || {};
window.ui.renderTrackerViews = window.ui.renderTrackerViews || {};
window.ui.renderTrackerViews['Bastion Tracker'] = function(container, campaign) {
  window.bastionTracker.renderBastionTrackerListView(container, campaign);
};

})();