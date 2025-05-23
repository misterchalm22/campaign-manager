(function() {
// Logic for NPC Tracker
window.npcTracker = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.npcs) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.npcs = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns); // Assuming 'allCampaigns' is globally available
  },

  renderNpcTrackerListView: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>NPC Tracker</h2>
      <button class="btn btn-primary" id="add-npc-btn">Add NPC</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No NPCs yet. Add one to get started!</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((npc, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong>${window.modalUtils.escapeHtml(npc.name) || '(No Name)'}</strong> 
              <span class="text-muted small ms-2">${window.modalUtils.escapeHtml(npc.statBlock) || 'No stat block'}</span>
            </div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted mt-1">Alignment: ${window.modalUtils.escapeHtml(npc.alignment) || 'N/A'}</div>
          <div class="small text-muted mt-1">Appearance (snippet): ${window.modalUtils.escapeHtml(npc.appearance ? npc.appearance.substring(0, 80) + (npc.appearance.length > 80 ? '...' : '') : 'N/A')}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html; // This is the listContainer

    document.getElementById('add-npc-btn').onclick = () => {
      this.renderNpcFormModal(container, campaign, null, false);
    };

    container.querySelectorAll('[data-view]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-view'));
        this.renderNpcEntryView(container, campaign, idx);
      };
    });

    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-delete'));
        const npcToDelete = entries[idx];
        if (confirm(`Are you sure you want to delete the NPC: "${window.modalUtils.escapeHtml(npcToDelete.name)}"?`)) {
          let currentEntries = this.getEntries(campaign);
          currentEntries.splice(idx, 1);
          this.saveEntries(campaign, currentEntries);
          this.renderNpcTrackerListView(container, campaign); 
        }
      };
    });
  },

  renderNpcEntryView: function(listContainer, campaign, idx) {
    const entries = this.getEntries(campaign);
    const npc = entries[idx];

    if (!npc) {
      console.error("NPC not found for view at index:", idx);
      window.modalUtils.hideModal();
      window.modalUtils.showModal("Error", "<p>Could not find the selected NPC. It might have been deleted.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
      this.renderNpcTrackerListView(listContainer, campaign);
      return;
    }

    let contentHtml = `<dl class="row">
      <dt class="col-sm-3">Name:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(npc.name) || 'N/A'}</dd>
      <dt class="col-sm-3">Stat Block:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(npc.statBlock) || 'N/A'}</dd>
      <dt class="col-sm-3">MM Page:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(npc.mmPage) || 'N/A'}</dd>
      <dt class="col-sm-3">Alignment:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(npc.alignment) || 'N/A'}</dd>
      <dt class="col-sm-3">Alterations:</dt><dd class="col-sm-9"><pre>${window.modalUtils.escapeHtml(npc.alterations) || 'N/A'}</pre></dd>
      <dt class="col-sm-3">Personality:</dt><dd class="col-sm-9"><pre>${window.modalUtils.escapeHtml(npc.personality) || 'N/A'}</pre></dd>
      <dt class="col-sm-3">Appearance:</dt><dd class="col-sm-9"><pre>${window.modalUtils.escapeHtml(npc.appearance) || 'N/A'}</pre></dd>
      <dt class="col-sm-3">Secret:</dt><dd class="col-sm-9"><pre>${window.modalUtils.escapeHtml(npc.secret) || 'N/A'}</pre></dd>
    </dl>`;
    
    let footerHtml = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editNPCFromViewBtn">Edit</button>`;
    
    window.modalUtils.showModal(`View NPC: ${window.modalUtils.escapeHtml(npc.name)}`, contentHtml, footerHtml);
    
    const editButton = document.getElementById('editNPCFromViewBtn');
    if (editButton) {
      editButton.onclick = () => {
        this.renderNpcFormModal(listContainer, campaign, idx, true);
      };
    }
  },

  renderNpcFormModal: function(listContainer, campaign, idx, isEditFromView = false) {
    let entries = this.getEntries(campaign);
    const isEditMode = idx !== null && idx !== undefined;
    let npcToEdit;

    if (isEditMode) {
      if (idx < 0 || idx >= entries.length) {
        console.error("NPC index out of bounds for edit:", idx);
        window.modalUtils.hideModal();
        window.modalUtils.showModal("Error", "<p>Could not find NPC to edit. Invalid index.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
        this.renderNpcTrackerListView(listContainer, campaign);
        return;
      }
      npcToEdit = {...entries[idx]};
    } else {
      npcToEdit = { name: '', statBlock: '', mmPage: '', alterations: '', alignment: '', personality: '', appearance: '', secret: '' };
    }
    
    const modalTitle = isEditMode ? `Edit NPC: ${window.modalUtils.escapeHtml(npcToEdit.name)}` : 'Add New NPC';

    let formHtml = `<form id="npc-form-modal" novalidate>
      <div class="row">
        <div class="col-md-6 mb-3">
          <label for="npc-name" class="form-label">Name</label>
          <input type="text" class="form-control" id="npc-name" name="name" value="${window.modalUtils.escapeHtml(npcToEdit.name)}" required />
          <div class="invalid-feedback">Name is required.</div>
        </div>
        <div class="col-md-6 mb-3">
          <label for="npc-alignment" class="form-label">Alignment</label>
          <input type="text" class="form-control" id="npc-alignment" name="alignment" value="${window.modalUtils.escapeHtml(npcToEdit.alignment)}" placeholder="e.g. LG, N, CE" />
        </div>
      </div>
      <div class="row">
        <div class="col-md-6 mb-3">
          <label for="npc-statBlock" class="form-label">Stat Block (Source)</label>
          <input type="text" class="form-control" id="npc-statBlock" name="statBlock" value="${window.modalUtils.escapeHtml(npcToEdit.statBlock)}" />
        </div>
        <div class="col-md-6 mb-3">
          <label for="npc-mmPage" class="form-label">MM Page</label>
          <input type="text" class="form-control" id="npc-mmPage" name="mmPage" value="${window.modalUtils.escapeHtml(npcToEdit.mmPage)}" />
        </div>
      </div>
      <div class="mb-3">
        <label for="npc-appearance" class="form-label">Appearance</label>
        <textarea class="form-control" id="npc-appearance" name="appearance" rows="3">${window.modalUtils.escapeHtml(npcToEdit.appearance)}</textarea>
      </div>
      <div class="mb-3">
        <label for="npc-personality" class="form-label">Personality / Roleplaying Notes</label>
        <textarea class="form-control" id="npc-personality" name="personality" rows="3">${window.modalUtils.escapeHtml(npcToEdit.personality)}</textarea>
      </div>
      <div class="mb-3">
        <label for="npc-alterations" class="form-label">Stat Block Alterations / Abilities</label>
        <textarea class="form-control" id="npc-alterations" name="alterations" rows="3">${window.modalUtils.escapeHtml(npcToEdit.alterations)}</textarea>
      </div>
      <div class="mb-3">
        <label for="npc-secret" class="form-label">Secret / GM Notes</label>
        <textarea class="form-control" id="npc-secret" name="secret" rows="3">${window.modalUtils.escapeHtml(npcToEdit.secret)}</textarea>
      </div>
    </form>`;
    
    let footerHtml = `<button type="button" class="btn btn-secondary" id="cancelNPCFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveNPCFormBtn">Save</button>`;
      
    window.modalUtils.showModal(modalTitle, formHtml, footerHtml);

    const form = document.getElementById('npc-form-modal');
    const nameInput = form.querySelector('#npc-name');

    const saveButton = document.getElementById('saveNPCFormBtn');
    if (saveButton) {
      saveButton.onclick = () => {
        const newName = nameInput.value.trim();
        if (!newName) {
          nameInput.classList.add('is-invalid');
          form.classList.add('was-validated');
          // alert('NPC Name is required.'); // Per spec, but Bootstrap validation is cleaner
          return;
        }
        nameInput.classList.remove('is-invalid');
        form.classList.remove('was-validated');

        const updatedNpcData = {
          name: newName,
          statBlock: form.querySelector('#npc-statBlock').value.trim(),
          mmPage: form.querySelector('#npc-mmPage').value.trim(),
          alterations: form.querySelector('#npc-alterations').value.trim(),
          alignment: form.querySelector('#npc-alignment').value.trim(),
          personality: form.querySelector('#npc-personality').value.trim(),
          appearance: form.querySelector('#npc-appearance').value.trim(),
          secret: form.querySelector('#npc-secret').value.trim()
        };

        let currentEntries = this.getEntries(campaign);
        if (isEditMode) {
          currentEntries[idx] = updatedNpcData;
        } else {
          currentEntries.push(updatedNpcData);
        }
        this.saveEntries(campaign, currentEntries);
        window.modalUtils.hideModal();
        this.renderNpcTrackerListView(listContainer, campaign); 
      };
    }

    const cancelButton = document.getElementById('cancelNPCFormBtn');
    if (cancelButton) {
      cancelButton.onclick = () => {
        if (isEditFromView && isEditMode) {
          const latestEntries = this.getEntries(campaign);
          if (idx < latestEntries.length) {
            this.renderNpcEntryView(listContainer, campaign, idx);
          } else {
            window.modalUtils.hideModal();
            this.renderNpcTrackerListView(listContainer, campaign);
          }
        } else {
          window.modalUtils.hideModal();
        }
      };
    }
  }
};

// Register with main UI rendering system
window.ui = window.ui || {};
window.ui.renderTrackerViews = window.ui.renderTrackerViews || {};
window.ui.renderTrackerViews['NPC Tracker'] = function(container, campaign) {
  window.npcTracker.renderNpcTrackerListView(container, campaign);
};

})();