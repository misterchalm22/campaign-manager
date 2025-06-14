(function() {
// Campaign Conflicts Tracker

window.campaignConflicts = {
  getConflicts: function(campaign) {
    return (campaign.trackers && campaign.trackers.campaignConflicts) || [];
  },
  saveConflicts: function(campaign, conflicts) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.campaignConflicts = conflicts;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns);
  },
  renderCampaignConflictsList: function(container, campaign) {
    const conflicts = this.getConflicts(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Campaign Conflicts</h2>
      <button class="btn btn-primary" id="add-conflict-btn">Add Conflict</button>
    </div>`;
    if (conflicts.length === 0) {
      html += '<div class="alert alert-info">No campaign conflicts yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      conflicts.forEach((conflict, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>${conflict.title || '(No Title)'}</strong> <span class="text-muted small">vs. ${conflict.antagonist || ''}</span></div>
            <div>
              <button class="btn btn-sm btn-secondary me-2" data-edit="${idx}">Edit</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">${conflict.notes ? conflict.notes.substring(0, 80) : ''}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html + `<div id="conflict-form-area"></div>`;
    document.getElementById('add-conflict-btn').onclick = () => this.renderCampaignConflictsForm(container, campaign);
    container.querySelectorAll('[data-edit]').forEach(btn => {
      btn.onclick = () => this.renderCampaignConflictsForm(container, campaign, parseInt(btn.getAttribute('data-edit')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this conflict?')) {
          conflicts.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveConflicts(campaign, conflicts);
          this.renderCampaignConflictsList(container, campaign);
        }
      };
    });
  },
  renderCampaignConflictsForm: function(container, campaign, idx) {
    const conflicts = this.getConflicts(campaign);
    const conflict = idx != null ? {...conflicts[idx]} : {
      title: '',
      antagonist: '',
      notes: ''
    };
    let html = `<form class="card card-body mb-3" id="conflict-form">
      <div class="mb-2">
        <label class="form-label">Conflict Title/Identifier</label>
        <input class="form-control" name="title" value="${conflict.title || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Adventurers vs. (Antagonist/Situation)</label>
        <input class="form-control" name="antagonist" value="${conflict.antagonist || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Notes</label>
        <textarea class="form-control" name="notes">${conflict.notes || ''}</textarea>
      </div>
      <div class="d-flex gap-2">
        <button type="submit" class="btn btn-success">Save</button>
        <button type="button" class="btn btn-secondary" id="cancel-conflict-btn">Cancel</button>
      </div>
    </form>`;
    document.getElementById('conflict-form-area').innerHTML = html;
    document.getElementById('cancel-conflict-btn').onclick = () => {
      this.renderCampaignConflictsList(container, campaign);
    };
    document.getElementById('conflict-form').onsubmit = (e) => {
      e.preventDefault();
      const form = e.target;
      const newConflict = {
        title: form.title.value,
        antagonist: form.antagonist.value,
        notes: form.notes.value
      };
      if (idx != null) {
        conflicts[idx] = newConflict;
      } else {
        conflicts.push(newConflict);
      }
      this.saveConflicts(campaign, conflicts);
      this.renderCampaignConflictsList(container, campaign);
    };
  },
  renderCampaignConflictsListView: function(container, campaign) {
    const conflicts = this.getConflicts(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Campaign Conflicts</h2>
      <button class="btn btn-primary" id="add-conflict-btn">Add Conflict</button>
    </div>`;
    if (conflicts.length === 0) {
      html += '<div class="alert alert-info">No campaign conflicts yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      conflicts.forEach((conflict, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>${window.modalUtils.escapeHtml(conflict.title) || '(No Title)'}</strong> <span class="text-muted small">vs. ${window.modalUtils.escapeHtml(conflict.antagonist) || ''}</span></div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">${window.modalUtils.escapeHtml(conflict.notes ? conflict.notes.substring(0, 80) : '')}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html;
    document.getElementById('add-conflict-btn').onclick = () => this.renderCampaignConflictsFormModal(campaign, null);
    container.querySelectorAll('[data-view]').forEach(btn => {
      btn.onclick = () => this.renderCampaignConflictsEntryView(conflicts[parseInt(btn.getAttribute('data-view'))], campaign, parseInt(btn.getAttribute('data-view')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        const indexToDelete = parseInt(btn.getAttribute('data-delete'));
        const conflictName = entries[indexToDelete] && entries[indexToDelete].name ? entries[indexToDelete].name : 'this conflict';
        const conflictNameEscaped = window.modalUtils.escapeHtml(conflictName);
        window.modalUtils.showConfirmModal(
          'Delete Conflict',
          `Are you sure you want to delete the conflict "${conflictNameEscaped}"? This action cannot be undone.`,
          () => { // onConfirm
            entries.splice(indexToDelete, 1);
            this.saveEntries(campaign, entries);
            this.renderConflictList(container, campaign);
          },
          null // onCancel
        );
      };
    });
  },
  renderCampaignConflictsEntryView: function(conflict, campaign, idx) {
    let html = `<dl class="row">
      <dt class="col-sm-4">Conflict Title:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(conflict.title) || 'N/A'}</dd>
      <dt class="col-sm-4">Antagonist/Situation:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(conflict.antagonist) || 'N/A'}</dd>
      <dt class="col-sm-4">Notes:</dt><dd class="col-sm-8"><pre>${window.modalUtils.escapeHtml(conflict.notes) || 'N/A'}</pre></dd>
    </dl>`;
    let footer = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editConflictFromViewBtn">Edit</button>`;
    window.modalUtils.showModal(`View Conflict: ${window.modalUtils.escapeHtml(conflict.title)}`, html, footer);
    document.getElementById('editConflictFromViewBtn').onclick = () => {
      window.campaignConflicts.renderCampaignConflictsFormModal(campaign, idx, true);
    };
  },
  renderCampaignConflictsFormModal: function(campaign, idx, isEditFromView = false) {
    const conflicts = this.getConflicts(campaign);
    const conflict = idx != null ? {...conflicts[idx]} : { title: '', antagonist: '', notes: '' };
    let html = `<form id="conflict-form-modal">
      <div class="mb-2">
        <label class="form-label">Conflict Title/Identifier</label>
        <input class="form-control" name="title" value="${window.modalUtils.escapeHtml(conflict.title) || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Adventurers vs. (Antagonist/Situation)</label>
        <input class="form-control" name="antagonist" value="${window.modalUtils.escapeHtml(conflict.antagonist) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Notes</label>
        <textarea class="form-control" name="notes">${window.modalUtils.escapeHtml(conflict.notes) || ''}</textarea>
      </div>
    </form>`;
    let footer = `<button type="button" class="btn btn-secondary" id="cancelConflictFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveConflictFormBtn">Save</button>`;
    window.modalUtils.showModal(idx != null ? `Edit Conflict: ${window.modalUtils.escapeHtml(conflict.title)}` : 'Add Conflict', html, footer);
    document.getElementById('cancelConflictFormBtn').onclick = () => {
      if (isEditFromView && idx != null) {
        window.campaignConflicts.renderCampaignConflictsEntryView(conflicts[idx], campaign, idx);
      } else {
        window.modalUtils.hideModal();
      }
    };
    document.getElementById('saveConflictFormBtn').onclick = () => {
      const form = document.getElementById('conflict-form-modal');
      const newConflict = {
        title: form.title.value.trim(),
        antagonist: form.antagonist.value.trim(),
        notes: form.notes.value.trim()
      };
      if (!newConflict.title) {
        window.modalUtils.showAlertModal('Validation Error', 'Conflict Title is required.', null);
        return;
      }
      if (idx != null) {
        conflicts[idx] = newConflict;
      } else {
        conflicts.push(newConflict);
      }
      window.campaignConflicts.saveConflicts(campaign, conflicts);
      window.modalUtils.hideModal();
      // Refresh list view
      const mainContent = document.getElementById('main-content');
      if (mainContent) {
        window.campaignConflicts.renderCampaignConflictsListView(mainContent, campaign);
      }
    };
  }
};
})();