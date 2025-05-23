(function() {
// Logic for Campaign Journal tracker

window.campaignJournal = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.campaignJournal) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.campaignJournal = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns); // Assuming 'allCampaigns' is globally available
  },

  renderCampaignJournalListView: function(container, campaign) {
    const entries = this.getEntries(campaign);
    // Sort entries by session number descending, then by date descending if session number is same or missing
    entries.sort((a, b) => {
      const sessionNumA = parseInt(a.sessionNumber, 10);
      const sessionNumB = parseInt(b.sessionNumber, 10);
      if (!isNaN(sessionNumA) && !isNaN(sessionNumB)) {
        if (sessionNumB !== sessionNumA) return sessionNumB - sessionNumA;
      } else if (!isNaN(sessionNumA)) {
        return -1; // A has number, B does not, A comes first (effectively)
      } else if (!isNaN(sessionNumB)) {
        return 1;  // B has number, A does not, B comes first (effectively)
      }
      // If session numbers are the same or both missing, sort by date
      if (b.sessionDate && a.sessionDate) return new Date(b.sessionDate) - new Date(a.sessionDate);
      if (b.sessionDate) return 1; // B has date, A does not
      if (a.sessionDate) return -1; // A has date, B does not
      return 0;
    });


    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Campaign Journal</h2>
      <button class="btn btn-primary" id="add-journal-entry-btn">Add Journal Entry</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No journal entries yet. Add one to get started!</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((entry, originalIndex) => { // Keep originalIndex if needed for direct array modification on delete, though re-fetching is safer
        // Find true index after sort if needed, or rely on re-fetch for delete
        const idx = this.getEntries(campaign).indexOf(entry); // Get current index in potentially sorted array
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong>${window.modalUtils.escapeHtml(entry.sessionTitle) || `Session ${window.modalUtils.escapeHtml(entry.sessionNumber) || (idx + 1)}`}</strong>
              <span class="text-muted small ms-2">(${window.modalUtils.escapeHtml(entry.sessionDate) || 'No Date'})</span>
            </div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view-idx="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete-idx="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted mt-1">Session #: ${window.modalUtils.escapeHtml(entry.sessionNumber) || 'N/A'}</div>
          <div class="small text-muted mt-1">Summary: ${window.modalUtils.escapeHtml(entry.plannedSummary ? entry.plannedSummary.substring(0, 100) + (entry.plannedSummary.length > 100 ? '...' : '') : (entry.notes ? entry.notes.substring(0,100) + (entry.notes.length > 100 ? '...' : '') : 'No summary.'))}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html;

    document.getElementById('add-journal-entry-btn').onclick = () => {
      this.renderJournalEntryFormModal(container, campaign, null, false);
    };

    container.querySelectorAll('[data-view-idx]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-view-idx'));
        this.renderJournalEntryView(container, campaign, idx);
      };
    });

    container.querySelectorAll('[data-delete-idx]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-delete-idx'));
        // Re-fetch entries to ensure `idx` is accurate if list was sorted/modified
        const currentEntries = this.getEntries(campaign);
         // Sort entries by session number descending, then by date descending
        currentEntries.sort((a, b) => {
            const sessionNumA = parseInt(a.sessionNumber, 10);
            const sessionNumB = parseInt(b.sessionNumber, 10);
            if (!isNaN(sessionNumA) && !isNaN(sessionNumB)) {
                if (sessionNumB !== sessionNumA) return sessionNumB - sessionNumA;
            } else if (!isNaN(sessionNumA)) return -1;
              else if (!isNaN(sessionNumB)) return 1;
            if (b.sessionDate && a.sessionDate) return new Date(b.sessionDate) - new Date(a.sessionDate);
            if (b.sessionDate) return 1;
            if (a.sessionDate) return -1;
            return 0;
        });
        const entryToDelete = currentEntries[idx];

        if (confirm(`Are you sure you want to delete the journal entry: "${window.modalUtils.escapeHtml(entryToDelete.sessionTitle) || `Session ${entryToDelete.sessionNumber}`}"?`)) {
          // Find the actual object in the unsorted original array to delete
          const originalEntries = this.getEntries(campaign); // get original unsorted
          const originalIndexToDelete = originalEntries.findIndex(e => e === entryToDelete);

          if (originalIndexToDelete !== -1) {
            originalEntries.splice(originalIndexToDelete, 1);
            this.saveEntries(campaign, originalEntries);
          } else {
            console.error("Could not find entry to delete in original list after sorting.");
            // Fallback: try deleting by the sorted index if the object reference changed, though this is risky
            // this.getEntries(campaign).splice(idx, 1); 
            // this.saveEntries(campaign, this.getEntries(campaign));
          }
          this.renderCampaignJournalListView(container, campaign); 
        }
      };
    });
  },

  renderJournalEntryView: function(listContainer, campaign, idx) {
    // Sort entries by session number descending, then by date descending
    const entries = this.getEntries(campaign).slice().sort((a, b) => { // Use slice() to sort a copy
        const sessionNumA = parseInt(a.sessionNumber, 10);
        const sessionNumB = parseInt(b.sessionNumber, 10);
        if (!isNaN(sessionNumA) && !isNaN(sessionNumB)) {
            if (sessionNumB !== sessionNumA) return sessionNumB - sessionNumA;
        } else if (!isNaN(sessionNumA)) return -1;
          else if (!isNaN(sessionNumB)) return 1;
        if (b.sessionDate && a.sessionDate) return new Date(b.sessionDate) - new Date(a.sessionDate);
        if (b.sessionDate) return 1;
        if (a.sessionDate) return -1;
        return 0;
    });
    const entry = entries[idx];

    if (!entry) {
      console.error("Journal entry not found for view at index:", idx);
      window.modalUtils.hideModal();
      window.modalUtils.showModal("Error", "<p>Could not find the selected journal entry.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
      this.renderCampaignJournalListView(listContainer, campaign);
      return;
    }

    let contentHtml = `<dl class="row">
      <dt class="col-sm-3">Title:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(entry.sessionTitle) || 'N/A'}</dd>
      <dt class="col-sm-3">Session #:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(entry.sessionNumber) || 'N/A'}</dd>
      <dt class="col-sm-3">Date:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(entry.sessionDate) || 'N/A'}</dd>
      <dt class="col-sm-12 mt-2">Earlier Events Summary:</dt><dd class="col-sm-12"><pre>${window.modalUtils.escapeHtml(entry.earlierEvents) || 'N/A'}</pre></dd>
      <dt class="col-sm-12 mt-2">Planned Summary for Session:</dt><dd class="col-sm-12"><pre>${window.modalUtils.escapeHtml(entry.plannedSummary) || 'N/A'}</pre></dd>
      <dt class="col-sm-12 mt-2">Notes & Actual Events:</dt><dd class="col-sm-12"><pre>${window.modalUtils.escapeHtml(entry.notes) || 'N/A'}</pre></dd>
    </dl>`;
    
    let footerHtml = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editJournalEntryFromViewBtn">Edit</button>`;
    
    window.modalUtils.showModal(`Journal: ${window.modalUtils.escapeHtml(entry.sessionTitle) || `Session ${entry.sessionNumber}`}`, contentHtml, footerHtml);
    
    const editButton = document.getElementById('editJournalEntryFromViewBtn');
    if (editButton) {
      editButton.onclick = () => {
        // We need to find the original index of this entry before sorting for editing
        const originalEntries = this.getEntries(campaign);
        const originalIndex = originalEntries.findIndex(e => e === entry);
        if (originalIndex !== -1) {
            this.renderJournalEntryFormModal(listContainer, campaign, originalIndex, true);
        } else {
            console.error("Original entry not found for editing.");
            window.modalUtils.showError("Could not find the entry to edit.");
        }
      };
    }
  },

  renderJournalEntryFormModal: function(listContainer, campaign, idx, isEditFromView = false) {
    const entries = this.getEntries(campaign); // Get original unsorted entries
    const isEditMode = idx !== null && idx !== undefined;
    let entryToEdit;

    if (isEditMode) {
      if (idx < 0 || idx >= entries.length) {
        console.error("Journal entry index out of bounds for edit:", idx);
        window.modalUtils.hideModal();
        window.modalUtils.showModal("Error", "<p>Could not find journal entry to edit.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
        this.renderCampaignJournalListView(listContainer, campaign);
        return;
      }
      entryToEdit = {...entries[idx]}; // Work with a copy
    } else {
      // Default for new entry: find max session number and increment, or default to 1
      const maxSessionNum = entries.reduce((max, e) => Math.max(max, parseInt(e.sessionNumber,10) || 0), 0);
      entryToEdit = { sessionNumber: maxSessionNum + 1, sessionDate: new Date().toISOString().slice(0,10), sessionTitle: '', earlierEvents: '', plannedSummary: '', notes: '' };
    }
    
    const modalTitle = isEditMode ? `Edit Journal: ${window.modalUtils.escapeHtml(entryToEdit.sessionTitle) || `Session ${entryToEdit.sessionNumber}`}` : 'Add New Journal Entry';

    let formHtml = `<form id="journal-entry-form" novalidate>
      <div class="row">
        <div class="col-md-8 mb-3">
          <label for="journal-sessionTitle" class="form-label">Session/Adventure Title</label>
          <input type="text" class="form-control" id="journal-sessionTitle" name="sessionTitle" value="${window.modalUtils.escapeHtml(entryToEdit.sessionTitle)}" required />
          <div class="invalid-feedback">Title is required.</div>
        </div>
        <div class="col-md-4 mb-3">
          <label for="journal-sessionNumber" class="form-label">Session #</label>
          <input type="number" class="form-control" id="journal-sessionNumber" name="sessionNumber" value="${window.modalUtils.escapeHtml(entryToEdit.sessionNumber)}" min="0" />
        </div>
      </div>
      <div class="mb-3">
        <label for="journal-sessionDate" class="form-label">Session Date</label>
        <input type="date" class="form-control" id="journal-sessionDate" name="sessionDate" value="${window.modalUtils.escapeHtml(entryToEdit.sessionDate)}" />
      </div>
      <div class="mb-3">
        <label for="journal-earlierEvents" class="form-label">Important Events from Earlier Sessions (Recap)</label>
        <textarea class="form-control" id="journal-earlierEvents" name="earlierEvents" rows="4">${window.modalUtils.escapeHtml(entryToEdit.earlierEvents)}</textarea>
      </div>
      <div class="mb-3">
        <label for="journal-plannedSummary" class="form-label">Planned Summary for This Session (GM Prep)</label>
        <textarea class="form-control" id="journal-plannedSummary" name="plannedSummary" rows="4">${window.modalUtils.escapeHtml(entryToEdit.plannedSummary)}</textarea>
      </div>
      <div class="mb-3">
        <label for="journal-notes" class="form-label">Notes & Actual Events (Session Log)</label>
        <textarea class="form-control" id="journal-notes" name="notes" rows="6">${window.modalUtils.escapeHtml(entryToEdit.notes)}</textarea>
      </div>
    </form>`;
    
    let footerHtml = `<button type="button" class="btn btn-secondary" id="cancelJournalEntryFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveJournalEntryFormBtn">Save</button>`;
      
    window.modalUtils.showModal(modalTitle, formHtml, footerHtml);

    const form = document.getElementById('journal-entry-form');
    const titleInput = form.querySelector('#journal-sessionTitle');

    document.getElementById('saveJournalEntryFormBtn').onclick = () => {
      const sessionTitle = titleInput.value.trim();
      if (!sessionTitle) {
        titleInput.classList.add('is-invalid');
        form.classList.add('was-validated');
        return;
      }
      titleInput.classList.remove('is-invalid');
      form.classList.remove('was-validated');

      const sessionNumberStr = form.querySelector('#journal-sessionNumber').value.trim();
      const updatedEntryData = {
        sessionTitle: sessionTitle,
        sessionNumber: sessionNumberStr ? parseInt(sessionNumberStr, 10) : null, // Allow null if empty
        sessionDate: form.querySelector('#journal-sessionDate').value,
        earlierEvents: form.querySelector('#journal-earlierEvents').value.trim(),
        plannedSummary: form.querySelector('#journal-plannedSummary').value.trim(),
        notes: form.querySelector('#journal-notes').value.trim()
      };
      
      let currentEntries = this.getEntries(campaign); // Get original unsorted
      if (isEditMode) {
        currentEntries[idx] = updatedEntryData;
      } else {
        currentEntries.push(updatedEntryData);
      }
      this.saveEntries(campaign, currentEntries);
      window.modalUtils.hideModal();
      this.renderCampaignJournalListView(listContainer, campaign); 
    };

    document.getElementById('cancelJournalEntryFormBtn').onclick = () => {
      if (isEditFromView && isEditMode) {
         // idx here is the original index
         this.renderJournalEntryView(listContainer, campaign, idx);
      } else {
        window.modalUtils.hideModal();
      }
    };
  }
};

// Register with main UI rendering system
window.ui = window.ui || {};
window.ui.renderTrackerViews = window.ui.renderTrackerViews || {};
window.ui.renderTrackerViews['Campaign Journal'] = function(container, campaign) {
  window.campaignJournal.renderCampaignJournalListView(container, campaign);
};

})();