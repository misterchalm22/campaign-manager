(function() {
// Campaign Conflicts Tracker

window.campaignConflicts = {
  getConflicts: function(campaign) {
    return (campaign.trackers && campaign.trackers.campaignConflicts) || [];
  },
  saveConflicts: function(campaign, conflicts) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.campaignConflicts = conflicts;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns); // Assuming 'allCampaigns' is globally available
  },

  renderCampaignConflictsListView: function(container, campaign) {
    const conflicts = this.getConflicts(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Campaign Conflicts</h2>
      <button class="btn btn-primary" id="add-conflict-btn">Add Conflict</button>
    </div>`;

    if (conflicts.length === 0) {
      html += '<div class="alert alert-info">No campaign conflicts yet. Add one to get started!</div>';
    } else {
      html += '<div class="list-group mb-3">';
      conflicts.forEach((conflict, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong>${window.modalUtils.escapeHtml(conflict.title) || '(No Title)'}</strong> 
              <span class="text-muted small">vs. ${window.modalUtils.escapeHtml(conflict.antagonist) || 'N/A'}</span>
            </div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted mt-1">${window.modalUtils.escapeHtml(conflict.notes ? conflict.notes.substring(0, 80) + (conflict.notes.length > 80 ? '...' : '') : 'No details.')}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html; // This is the listContainer

    document.getElementById('add-conflict-btn').onclick = () => {
      // Pass the main 'container' so the form modal can refresh the list in it
      this.renderCampaignConflictsFormModal(container, campaign, null, false);
    };

    container.querySelectorAll('[data-view]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-view'));
        // Pass the main 'container' for potential navigation back or refresh
        this.renderCampaignConflictsEntryView(container, campaign, idx);
      };
    });

    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-delete'));
        const conflictToDelete = conflicts[idx]; // Get a reference before potential confirm dialog
        if (confirm(`Are you sure you want to delete the conflict: "${window.modalUtils.escapeHtml(conflictToDelete.title)}"?`)) {
          // Re-fetch conflicts in case of modification elsewhere, though less likely here
          let currentConflicts = this.getConflicts(campaign);
          currentConflicts.splice(idx, 1);
          this.saveConflicts(campaign, currentConflicts);
          this.renderCampaignConflictsListView(container, campaign); // Refresh list in the same container
        }
      };
    });
  },

  renderCampaignConflictsEntryView: function(listContainer, campaign, idx) {
    const conflicts = this.getConflicts(campaign); // Get a fresh copy of conflicts
    const conflict = conflicts[idx];

    if (!conflict) {
      console.error("Conflict not found for view at index:", idx);
      // Potentially hide any existing modal before showing the error.
      window.modalUtils.hideModal(); 
      window.modalUtils.showModal("Error", "<p>Could not find the selected conflict. It might have been deleted.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
      this.renderCampaignConflictsListView(listContainer, campaign); // Refresh list to be safe
      return;
    }

    let contentHtml = `<dl class="row">
      <dt class="col-sm-4">Conflict Title:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(conflict.title) || 'N/A'}</dd>
      <dt class="col-sm-4">Antagonist/Situation:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(conflict.antagonist) || 'N/A'}</dd>
      <dt class="col-sm-4">Notes:</dt><dd class="col-sm-8"><pre style="white-space: pre-wrap; word-wrap: break-word;">${window.modalUtils.escapeHtml(conflict.notes) || 'N/A'}</pre></dd>
    </dl>`;
    
    let footerHtml = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editConflictFromViewBtn">Edit</button>`;
    
    window.modalUtils.showModal(`View Conflict: ${window.modalUtils.escapeHtml(conflict.title)}`, contentHtml, footerHtml);
    
    const editButton = document.getElementById('editConflictFromViewBtn');
    if (editButton) {
      editButton.onclick = () => {
        this.renderCampaignConflictsFormModal(listContainer, campaign, idx, true); // Pass listContainer
      };
    }
  },

  renderCampaignConflictsFormModal: function(listContainer, campaign, idx, isEditFromView = false) {
    let conflicts = this.getConflicts(campaign); // Get a fresh copy
    const isEditMode = idx !== null && idx !== undefined;
    let conflictToEdit = null;

    if (isEditMode) {
        if (idx < 0 || idx >= conflicts.length) {
            console.error("Conflict index out of bounds for edit:", idx);
            window.modalUtils.hideModal();
            window.modalUtils.showModal("Error", "<p>Could not find the selected conflict to edit. Invalid index.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
            this.renderCampaignConflictsListView(listContainer, campaign);
            return;
        }
        conflictToEdit = {...conflicts[idx]}; // Operate on a copy
    } else {
        conflictToEdit = { title: '', antagonist: '', notes: '' }; // New conflict
    }
    
    const modalTitle = isEditMode ? `Edit Conflict: ${window.modalUtils.escapeHtml(conflictToEdit.title)}` : 'Add New Conflict';

    let formHtml = `<form id="conflict-form-modal" novalidate>
      <div class="mb-3">
        <label for="conflict-title" class="form-label">Conflict Title/Identifier</label>
        <input type="text" class="form-control" id="conflict-title" name="title" value="${window.modalUtils.escapeHtml(conflictToEdit.title)}" required />
        <div class="invalid-feedback">Title is required.</div>
      </div>
      <div class="mb-3">
        <label for="conflict-antagonist" class="form-label">Adventurers vs. (Antagonist/Situation)</label>
        <input type="text" class="form-control" id="conflict-antagonist" name="antagonist" value="${window.modalUtils.escapeHtml(conflictToEdit.antagonist)}" />
      </div>
      <div class="mb-3">
        <label for="conflict-notes" class="form-label">Notes</label>
        <textarea class="form-control" id="conflict-notes" name="notes" rows="5">${window.modalUtils.escapeHtml(conflictToEdit.notes)}</textarea>
      </div>
    </form>`;
    
    let footerHtml = `<button type="button" class="btn btn-secondary" id="cancelConflictFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveConflictFormBtn">Save</button>`;
      
    window.modalUtils.showModal(modalTitle, formHtml, footerHtml);

    const form = document.getElementById('conflict-form-modal');
    const titleInput = form.querySelector('#conflict-title'); // More specific selector

    const saveButton = document.getElementById('saveConflictFormBtn');
    if (saveButton) {
      saveButton.onclick = () => {
        const newTitle = titleInput.value.trim();
        if (!newTitle) {
          titleInput.classList.add('is-invalid');
          form.classList.add('was-validated'); 
          // As per requirements, an alert should be shown.
          // However, Bootstrap validation is generally preferred for UX.
          // For strict adherence: alert('Conflict Title is required.');
          return;
        }
        titleInput.classList.remove('is-invalid');
        form.classList.remove('was-validated');

        const updatedConflictData = {
          title: newTitle,
          antagonist: form.querySelector('#conflict-antagonist').value.trim(),
          notes: form.querySelector('#conflict-notes').value.trim()
        };

        let currentConflicts = this.getConflicts(campaign); // Re-fetch for latest state
        if (isEditMode) {
          currentConflicts[idx] = updatedConflictData;
        } else {
          currentConflicts.push(updatedConflictData);
        }
        this.saveConflicts(campaign, currentConflicts);
        window.modalUtils.hideModal();
        this.renderCampaignConflictsListView(listContainer, campaign); 
      };
    }

    const cancelButton = document.getElementById('cancelConflictFormBtn');
    if (cancelButton) {
      cancelButton.onclick = () => {
        if (isEditFromView && isEditMode) {
          // Ensure the conflict for view still exists
          const latestConflicts = this.getConflicts(campaign);
          if (idx < latestConflicts.length) {
            this.renderCampaignConflictsEntryView(listContainer, campaign, idx);
          } else {
            // Conflict might have been deleted in a rare race condition, go to list
            window.modalUtils.hideModal();
            this.renderCampaignConflictsListView(listContainer, campaign);
          }
        } else {
          window.modalUtils.hideModal();
        }
      };
    }
  }
};

// Ensure the main UI rendering function for this tracker is correctly assigned
// This function is called by main.js when the 'Campaign Conflicts' nav is selected
window.ui = window.ui || {};
window.ui.renderTrackerViews = window.ui.renderTrackerViews || {};
window.ui.renderTrackerViews['Campaign Conflicts'] = function(container, campaign) {
  window.campaignConflicts.renderCampaignConflictsListView(container, campaign);
};

})();