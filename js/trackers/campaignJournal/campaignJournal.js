(function() {
// Logic for Campaign Journal tracker

window.campaignJournal = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.campaignJournal) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.campaignJournal = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns);
  },
  renderJournalList: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Campaign Journal</h2>
      <button class="btn btn-primary" id="add-journal-btn">Add Session Log</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No journal entries yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((entry, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>Session ${entry.sessionNumber || idx+1}</strong> <span class="text-muted small">${entry.sessionDate || ''}</span></div>
            <div>
              <button class="btn btn-sm btn-secondary me-2" data-edit="${idx}">Edit</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">${entry.sessionTitle || ''}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html + `<div id="journal-form-area"></div>`;
    document.getElementById('add-journal-btn').onclick = () => this.renderJournalForm(container, campaign);
    container.querySelectorAll('[data-edit]').forEach(btn => {
      btn.onclick = () => this.renderJournalForm(container, campaign, parseInt(btn.getAttribute('data-edit')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this journal entry?')) {
          entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveEntries(campaign, entries);
          this.renderJournalList(container, campaign);
        }
      };
    });
  },
  renderJournalForm: function(container, campaign, idx) {
    const entries = this.getEntries(campaign);
    const entry = idx != null ? {...entries[idx]} : {
      sessionNumber: entries.length + 1,
      sessionDate: '',
      sessionTitle: '',
      earlierEvents: '',
      plannedSummary: '',
      notes: ''
    };
    let html = `<form class="card card-body mb-3" id="journal-form">
      <div class="mb-2">
        <label class="form-label">Session Number</label>
        <input class="form-control" name="sessionNumber" type="number" min="1" value="${entry.sessionNumber || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Session Date</label>
        <input class="form-control" name="sessionDate" type="date" value="${entry.sessionDate || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Session/Adventure Title</label>
        <input class="form-control" name="sessionTitle" value="${entry.sessionTitle || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Important Events from Earlier Sessions</label>
        <textarea class="form-control" name="earlierEvents">${entry.earlierEvents || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Planned Summary for This Session</label>
        <textarea class="form-control" name="plannedSummary">${entry.plannedSummary || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Additional Notes</label>
        <textarea class="form-control" name="notes">${entry.notes || ''}</textarea>
      </div>
      <div class="d-flex gap-2">
        <button type="submit" class="btn btn-success">Save</button>
        <button type="button" class="btn btn-secondary" id="cancel-journal-btn">Cancel</button>
      </div>
    </form>`;
    document.getElementById('journal-form-area').innerHTML = html;
    document.getElementById('cancel-journal-btn').onclick = () => {
      this.renderJournalList(container, campaign);
    };
    document.getElementById('journal-form').onsubmit = (e) => {
      e.preventDefault();
      const form = e.target;
      const newEntry = {
        sessionNumber: parseInt(form.sessionNumber.value, 10),
        sessionDate: form.sessionDate.value,
        sessionTitle: form.sessionTitle.value,
        earlierEvents: form.earlierEvents.value,
        plannedSummary: form.plannedSummary.value,
        notes: form.notes.value
      };
      if (idx != null) {
        entries[idx] = newEntry;
      } else {
        entries.push(newEntry);
      }
      this.saveEntries(campaign, entries);
      this.renderJournalList(container, campaign);
    };
  },
  renderCampaignJournalListView: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Campaign Journal</h2>
      <button class="btn btn-primary" id="add-journal-btn">Add Session Log</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No journal entries yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((entry, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>Session ${window.modalUtils.escapeHtml(entry.sessionNumber) || idx+1}</strong> <span class="text-muted small">${window.modalUtils.escapeHtml(entry.sessionDate) || ''}</span></div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">${window.modalUtils.escapeHtml(entry.sessionTitle) || ''}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html;
    document.getElementById('add-journal-btn').onclick = () => this.renderCampaignJournalFormModal(campaign, null);
    container.querySelectorAll('[data-view]').forEach(btn => {
      btn.onclick = () => this.renderCampaignJournalEntryView(entries[parseInt(btn.getAttribute('data-view'))], campaign, parseInt(btn.getAttribute('data-view')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this journal entry?')) {
          entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveEntries(campaign, entries);
          this.renderCampaignJournalListView(container, campaign);
        }
      };
    });
  },
  renderCampaignJournalEntryView: function(entry, campaign, idx) {
    let html = `<dl class="row">
      <dt class="col-sm-4">Session Number:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(entry.sessionNumber) || 'N/A'}</dd>
      <dt class="col-sm-4">Session Date:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(entry.sessionDate) || 'N/A'}</dd>
      <dt class="col-sm-4">Session/Adventure Title:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(entry.sessionTitle) || 'N/A'}</dd>
      <dt class="col-sm-4">Important Events from Earlier Sessions:</dt><dd class="col-sm-8"><pre>${window.modalUtils.escapeHtml(entry.earlierEvents) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Planned Summary for This Session:</dt><dd class="col-sm-8"><pre>${window.modalUtils.escapeHtml(entry.plannedSummary) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Additional Notes:</dt><dd class="col-sm-8"><pre>${window.modalUtils.escapeHtml(entry.notes) || 'N/A'}</pre></dd>
    </dl>`;
    let footer = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editJournalFromViewBtn">Edit</button>`;
    window.modalUtils.showModal(`View Session Log: Session ${window.modalUtils.escapeHtml(entry.sessionNumber)}`, html, footer);
    document.getElementById('editJournalFromViewBtn').onclick = () => {
      window.campaignJournal.renderCampaignJournalFormModal(campaign, idx, true);
    };
  },
  renderCampaignJournalFormModal: function(campaign, idx, isEditFromView = false) {
    const entries = this.getEntries(campaign);
    const entry = idx != null ? {...entries[idx]} : {
      sessionNumber: entries.length + 1,
      sessionDate: '',
      sessionTitle: '',
      earlierEvents: '',
      plannedSummary: '',
      notes: ''
    };
    let html = `<form id="journal-form-modal">
      <div class="mb-2">
        <label class="form-label">Session Number</label>
        <input class="form-control" name="sessionNumber" type="number" min="1" value="${window.modalUtils.escapeHtml(entry.sessionNumber) || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Session Date</label>
        <input class="form-control" name="sessionDate" type="date" value="${window.modalUtils.escapeHtml(entry.sessionDate) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Session/Adventure Title</label>
        <input class="form-control" name="sessionTitle" value="${window.modalUtils.escapeHtml(entry.sessionTitle) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Important Events from Earlier Sessions</label>
        <textarea class="form-control" name="earlierEvents">${window.modalUtils.escapeHtml(entry.earlierEvents) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Planned Summary for This Session</label>
        <textarea class="form-control" name="plannedSummary">${window.modalUtils.escapeHtml(entry.plannedSummary) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Additional Notes</label>
        <textarea class="form-control" name="notes">${window.modalUtils.escapeHtml(entry.notes) || ''}</textarea>
      </div>
    </form>`;
    let footer = `<button type="button" class="btn btn-secondary" id="cancelJournalFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveJournalFormBtn">Save</button>`;
    window.modalUtils.showModal(idx != null ? `Edit Session Log: Session ${window.modalUtils.escapeHtml(entry.sessionNumber)}` : 'Add Session Log', html, footer);
    document.getElementById('cancelJournalFormBtn').onclick = () => {
      if (isEditFromView && idx != null) {
        window.campaignJournal.renderCampaignJournalEntryView(entries[idx], campaign, idx);
      } else {
        window.modalUtils.hideModal();
      }
    };
    document.getElementById('saveJournalFormBtn').onclick = () => {
      const form = document.getElementById('journal-form-modal');
      const newEntry = {
        sessionNumber: form.sessionNumber.value.trim(),
        sessionDate: form.sessionDate.value.trim(),
        sessionTitle: form.sessionTitle.value.trim(),
        earlierEvents: form.earlierEvents.value.trim(),
        plannedSummary: form.plannedSummary.value.trim(),
        notes: form.notes.value.trim()
      };
      if (!newEntry.sessionNumber) {
        alert('Session Number is required.');
        return;
      }
      if (idx != null) {
        entries[idx] = newEntry;
      } else {
        entries.push(newEntry);
      }
      window.campaignJournal.saveEntries(campaign, entries);
      window.modalUtils.hideModal();
      // Refresh list view
      const mainContent = document.getElementById('main-content');
      if (mainContent) {
        window.campaignJournal.renderCampaignJournalListView(mainContent, campaign);
      }
    };
  }
};
})();