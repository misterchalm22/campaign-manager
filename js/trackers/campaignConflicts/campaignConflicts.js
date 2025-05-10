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
  }
};