(function() {
// Logic for Travel Planner tracker

window.travelPlanner = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.travelPlans) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.travelPlans = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns); // Assuming 'allCampaigns' is globally available
  },

  // Main list view for travel plans
  renderTravelPlannerListView: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Travel Planner</h2>
      <button class="btn btn-primary" id="add-travel-plan-btn">Add Travel Plan</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No travel plans yet. Add one to get started!</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((plan, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong>${window.modalUtils.escapeHtml(plan.name) || '(Unnamed Plan)'}</strong>
              <span class="text-muted small ms-2">(${window.modalUtils.escapeHtml(plan.origin) || 'N/A'} → ${window.modalUtils.escapeHtml(plan.destination) || 'N/A'})</span>
            </div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted mt-1">Stages: ${plan.stages ? plan.stages.length : 0}</div>
          <div class="small text-muted mt-1">Notes: ${window.modalUtils.escapeHtml(plan.notes ? plan.notes.substring(0,100) + (plan.notes.length > 100 ? '...' : '') : 'N/A')}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html;

    document.getElementById('add-travel-plan-btn').onclick = () => {
      this.renderTravelPlanFormModal(container, campaign, null, false);
    };

    container.querySelectorAll('[data-view]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-view'));
        this.renderTravelPlanEntryView(container, campaign, idx);
      };
    });

    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-delete'));
        const planToDelete = entries[idx];
        if (confirm(`Are you sure you want to delete the travel plan: "${window.modalUtils.escapeHtml(planToDelete.name)}"?`)) {
          let currentEntries = this.getEntries(campaign);
          currentEntries.splice(idx, 1);
          this.saveEntries(campaign, currentEntries);
          this.renderTravelPlannerListView(container, campaign);
        }
      };
    });
  },

  // Read-only view for a single travel plan (modal)
  renderTravelPlanEntryView: function(listContainer, campaign, idx) {
    const entries = this.getEntries(campaign);
    const plan = entries[idx];

    if (!plan) {
      console.error("Travel plan not found for view at index:", idx);
      window.modalUtils.hideModal(); // Hide any previous modal
      window.modalUtils.showModal("Error", "<p>Could not find the selected travel plan.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
      this.renderTravelPlannerListView(listContainer, campaign); // Refresh list
      return;
    }

    let stagesHtml = '<p>No stages defined.</p>';
    if (plan.stages && plan.stages.length > 0) {
      stagesHtml = '<ol class="list-group list-group-numbered">';
      plan.stages.forEach((stage, stageIdx) => {
        stagesHtml += `
          <li class="list-group-item">
            <div class="fw-bold">${window.modalUtils.escapeHtml(stage.description) || `Stage ${stageIdx + 1}`}</div>
            <small>
              Distance: ${window.modalUtils.escapeHtml(stage.distance) || 'N/A'} | 
              Pace: ${window.modalUtils.escapeHtml(stage.pace) || 'N/A'} | 
              Encounters: ${window.modalUtils.escapeHtml(stage.encounters) || 'N/A'}
            </small>
          </li>`;
      });
      stagesHtml += '</ol>';
    }

    let contentHtml = `
      <dl class="row">
        <dt class="col-sm-3">Route Name:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(plan.name) || 'N/A'}</dd>
        <dt class="col-sm-3">Start Location:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(plan.origin) || 'N/A'}</dd>
        <dt class="col-sm-3">End Location:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(plan.destination) || 'N/A'}</dd>
        <dt class="col-sm-3">Notes:</dt><dd class="col-sm-9"><pre>${window.modalUtils.escapeHtml(plan.notes) || 'N/A'}</pre></dd>
      </dl>
      <h5>Stages:</h5>
      ${stagesHtml}`;
    
    let footerHtml = `
      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editTravelPlanFromViewBtn">Edit</button>`;
    
    window.modalUtils.showModal(`View Travel Plan: ${window.modalUtils.escapeHtml(plan.name)}`, contentHtml, footerHtml);
    
    const editButton = document.getElementById('editTravelPlanFromViewBtn');
    if (editButton) {
      editButton.onclick = () => {
        this.renderTravelPlanFormModal(listContainer, campaign, idx, true);
      };
    }
  },

  // Form modal for adding/editing a travel plan
  renderTravelPlanFormModal: function(listContainer, campaign, idx, isEditFromView = false) {
    const entries = this.getEntries(campaign);
    const isEditMode = idx !== null && idx !== undefined;
    let planToEdit;

    if (isEditMode) {
      if (idx < 0 || idx >= entries.length) {
        console.error("Travel plan index out of bounds for edit:", idx);
        window.modalUtils.hideModal();
        window.modalUtils.showModal("Error", "<p>Could not find travel plan to edit.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
        this.renderTravelPlannerListView(listContainer, campaign);
        return;
      }
      // Deep copy stages for editing to avoid modifying original data until save
      planToEdit = JSON.parse(JSON.stringify(entries[idx])); 
    } else {
      planToEdit = { name: '', origin: '', destination: '', notes: '', stages: [] };
    }
    if (!planToEdit.stages) planToEdit.stages = []; // Ensure stages array exists

    // Function to render individual stage form fields
    const renderStageFormFields = (stage, stageIndex) => {
      return `
        <div class="card mb-2 stage-entry" data-stage-index="${stageIndex}">
          <div class="card-body">
            <h6 class="card-title">Stage ${stageIndex + 1}</h6>
            <div class="mb-2">
              <label class="form-label">Description</label>
              <input type="text" class="form-control stage-description" value="${window.modalUtils.escapeHtml(stage.description || '')}" placeholder="e.g., Forest path, Mountain pass">
            </div>
            <div class="row">
              <div class="col-md-6 mb-2">
                <label class="form-label">Distance</label>
                <input type="text" class="form-control stage-distance" value="${window.modalUtils.escapeHtml(stage.distance || '')}" placeholder="e.g., 10 miles, 3 days">
              </div>
              <div class="col-md-6 mb-2">
                <label class="form-label">Pace</label>
                <select class="form-select stage-pace">
                  <option value="Slow" ${stage.pace === 'Slow' ? 'selected' : ''}>Slow</option>
                  <option value="Normal" ${stage.pace === 'Normal' || !stage.pace ? 'selected' : ''}>Normal</option>
                  <option value="Fast" ${stage.pace === 'Fast' ? 'selected' : ''}>Fast</option>
                </select>
              </div>
            </div>
            <div class="mb-2">
              <label class="form-label">Potential Encounters/Challenges</label>
              <textarea class="form-control stage-encounters" rows="2">${window.modalUtils.escapeHtml(stage.encounters || '')}</textarea>
            </div>
            <button type="button" class="btn btn-sm btn-outline-danger remove-stage-btn mt-1">Remove Stage</button>
          </div>
        </div>`;
    };
    
    let stagesFormHtml = '<div id="stages-form-area">';
    planToEdit.stages.forEach((stage, stageIndex) => {
      stagesFormHtml += renderStageFormFields(stage, stageIndex);
    });
    stagesFormHtml += '</div>';

    const formHtml = `
      <form id="travel-plan-form" novalidate>
        <div class="mb-3">
          <label for="tp-name" class="form-label">Route Name</label>
          <input type="text" class="form-control" id="tp-name" name="name" value="${window.modalUtils.escapeHtml(planToEdit.name)}" required>
          <div class="invalid-feedback">Route Name is required.</div>
        </div>
        <div class="row">
          <div class="col-md-6 mb-3">
            <label for="tp-origin" class="form-label">Start Location</label>
            <input type="text" class="form-control" id="tp-origin" name="origin" value="${window.modalUtils.escapeHtml(planToEdit.origin)}">
          </div>
          <div class="col-md-6 mb-3">
            <label for="tp-destination" class="form-label">End Location</label>
            <input type="text" class="form-control" id="tp-destination" name="destination" value="${window.modalUtils.escapeHtml(planToEdit.destination)}">
          </div>
        </div>
        <div class="mb-3">
          <label for="tp-notes" class="form-label">Notes</label>
          <textarea class="form-control" id="tp-notes" name="notes" rows="3">${window.modalUtils.escapeHtml(planToEdit.notes)}</textarea>
        </div>
        <hr>
        <h5>Stages</h5>
        ${stagesFormHtml}
        <button type="button" class="btn btn-sm btn-outline-primary mt-2" id="add-stage-to-form-btn">Add Stage</button>
      </form>`;
    
    const modalTitle = isEditMode ? `Edit Travel Plan: ${window.modalUtils.escapeHtml(planToEdit.name)}` : 'Add New Travel Plan';
    const footerHtml = `
      <button type="button" class="btn btn-secondary" id="cancelTravelPlanFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveTravelPlanFormBtn">Save</button>`;
      
    window.modalUtils.showModal(modalTitle, formHtml, footerHtml);

    const form = document.getElementById('travel-plan-form');
    const nameInput = form.querySelector('#tp-name');
    const stagesArea = document.getElementById('stages-form-area');

    const updateStageEventListeners = () => {
      stagesArea.querySelectorAll('.remove-stage-btn').forEach(btn => {
        // Remove existing listener before adding new one to prevent duplicates
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
        newBtn.onclick = (e) => {
          e.target.closest('.stage-entry').remove();
          // Re-index stages after removal if necessary for data collection, though direct collection by class might be okay
        };
      });
    };
    
    document.getElementById('add-stage-to-form-btn').onclick = () => {
      const newStageIndex = stagesArea.children.length;
      const newStageHtml = renderStageFormFields({ description: '', distance: '', pace: 'Normal', encounters: '' }, newStageIndex);
      stagesArea.insertAdjacentHTML('beforeend', newStageHtml);
      updateStageEventListeners();
    };
    
    updateStageEventListeners(); // Initial setup

    document.getElementById('saveTravelPlanFormBtn').onclick = () => {
      const routeName = nameInput.value.trim();
      if (!routeName) {
        nameInput.classList.add('is-invalid');
        form.classList.add('was-validated');
        return;
      }
      nameInput.classList.remove('is-invalid');
      form.classList.remove('was-validated');

      const collectedStages = [];
      stagesArea.querySelectorAll('.stage-entry').forEach(stageElement => {
        collectedStages.push({
          description: stageElement.querySelector('.stage-description').value.trim(),
          distance: stageElement.querySelector('.stage-distance').value.trim(),
          pace: stageElement.querySelector('.stage-pace').value,
          encounters: stageElement.querySelector('.stage-encounters').value.trim()
        });
      });

      const updatedPlanData = {
        name: routeName,
        origin: form.querySelector('#tp-origin').value.trim(),
        destination: form.querySelector('#tp-destination').value.trim(),
        notes: form.querySelector('#tp-notes').value.trim(),
        stages: collectedStages
      };

      let currentEntries = this.getEntries(campaign);
      if (isEditMode) {
        currentEntries[idx] = updatedPlanData;
      } else {
        currentEntries.push(updatedPlanData);
      }
      this.saveEntries(campaign, currentEntries);
      window.modalUtils.hideModal();
      this.renderTravelPlannerListView(listContainer, campaign);
    };

    document.getElementById('cancelTravelPlanFormBtn').onclick = () => {
      if (isEditFromView && isEditMode) {
        const latestEntries = this.getEntries(campaign);
        if (idx < latestEntries.length) {
          this.renderTravelPlanEntryView(listContainer, campaign, idx);
        } else {
          window.modalUtils.hideModal(); // Fallback if entry was somehow deleted
          this.renderTravelPlannerListView(listContainer, campaign);
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
window.ui.renderTrackerViews['Travel Planner'] = function(container, campaign) {
  window.travelPlanner.renderTravelPlannerListView(container, campaign);
};

})();