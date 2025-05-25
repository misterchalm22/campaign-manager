(function() {
// Logic for NPC Tracker
window.npcTracker = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.npcs) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.npcs = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns);
  },
  renderNPCList: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>NPC Tracker</h2>
      <button class="btn btn-primary" id="add-npc-btn">Add NPC</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No NPCs yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((npc, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>${window.modalUtils.escapeHtml(npc.name) || '(No Name)'}</strong> <span class="text-muted small">${window.modalUtils.escapeHtml(npc.statBlock) || ''}</span></div>
            <div>
              <button class="btn btn-sm btn-secondary me-2" data-edit="${idx}">Edit</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">Alignment: ${window.modalUtils.escapeHtml(npc.alignment) || ''}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html + `<div id="npc-form-area"></div>`;
    document.getElementById('add-npc-btn').onclick = () => this.renderNPCForm(container, campaign);
    container.querySelectorAll('[data-edit]').forEach(btn => {
      btn.onclick = () => this.renderNPCForm(container, campaign, parseInt(btn.getAttribute('data-edit')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this NPC?')) {
          entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveEntries(campaign, entries);
          this.renderNPCList(container, campaign);
        }
      };
    });
  },
  renderNPCForm: function(container, campaign, idx) {
    const entries = this.getEntries(campaign);
    const npc = idx != null ? {...entries[idx]} : {
      name: '', statBlock: '', mmPage: '', alterations: '', alignment: '', personality: '', appearance: '', secret: ''
    };
    let html = `<form class="card card-body mb-3" id="npc-form">
      <div class="mb-2">
        <label class="form-label">NPC Name</label>
        <input class="form-control" name="name" value="${window.modalUtils.escapeHtml(npc.name) || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Stat Block (Source)</label>
        <input class="form-control" name="statBlock" value="${window.modalUtils.escapeHtml(npc.statBlock) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">MM Page</label>
        <input class="form-control" name="mmPage" value="${window.modalUtils.escapeHtml(npc.mmPage) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Stat Block Alterations</label>
        <textarea class="form-control" name="alterations">${window.modalUtils.escapeHtml(npc.alterations) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Alignment</label>
        <input class="form-control" name="alignment" value="${window.modalUtils.escapeHtml(npc.alignment) || ''}" placeholder="e.g. LG, NG, N, CE" />
      </div>
      <div class="mb-2">
        <label class="form-label">Personality</label>
        <textarea class="form-control" name="personality">${window.modalUtils.escapeHtml(npc.personality) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Appearance</label>
        <textarea class="form-control" name="appearance">${window.modalUtils.escapeHtml(npc.appearance) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Secret</label>
        <textarea class="form-control" name="secret">${window.modalUtils.escapeHtml(npc.secret) || ''}</textarea>
      </div>
      <div class="d-flex gap-2">
        <button type="submit" class="btn btn-success">Save</button>
        <button type="button" class="btn btn-secondary" id="cancel-npc-btn">Cancel</button>
      </div>
    </form>`;
    document.getElementById('npc-form-area').innerHTML = html;
    document.getElementById('cancel-npc-btn').onclick = () => {
      this.renderNPCList(container, campaign);
    };
    document.getElementById('npc-form').onsubmit = (e) => {
      e.preventDefault();
      const form = e.target;
      const newNPC = {
        name: form.name.value,
        statBlock: form.statBlock.value,
        mmPage: form.mmPage.value,
        alterations: form.alterations.value,
        alignment: form.alignment.value,
        personality: form.personality.value,
        appearance: form.appearance.value,
        secret: form.secret.value
      };
      if (idx != null) {
        entries[idx] = newNPC;
      } else {
        entries.push(newNPC);
      }
      this.saveEntries(campaign, entries);
      this.renderNPCList(container, campaign);
    };
  }
};

// Refactored: List View (calls EntryView in modal)
window.npcTracker.renderNPCListView = function(container, campaign) {
  const entries = this.getEntries(campaign);
  let html = `<div class="d-flex justify-content-between align-items-center mb-3">
    <h2>NPC Tracker</h2>
    <button class="btn btn-primary" id="add-npc-btn">Add NPC</button>
  </div>`;
  if (entries.length === 0) {
    html += '<div class="alert alert-info">No NPCs yet.</div>';
  } else {
    html += '<div class="list-group mb-3">';
    entries.forEach((npc, idx) => {
      html += `<div class="list-group-item">
        <div class="d-flex justify-content-between align-items-center">
          <div><strong>${window.modalUtils.escapeHtml(npc.name) || '(No Name)'}</strong> <span class="text-muted small">${window.modalUtils.escapeHtml(npc.statBlock) || ''}</span></div>
          <div>
            <button class="btn btn-sm btn-info me-2" data-view="${idx}">View Details</button>
            <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
          </div>
        </div>
        <div class="small text-muted">Alignment: ${window.modalUtils.escapeHtml(npc.alignment) || ''}</div>
      </div>`;
    });
    html += '</div>';
  }
  container.innerHTML = html;
  document.getElementById('add-npc-btn').onclick = () => this.renderNPCFormModal(campaign, null);
  container.querySelectorAll('[data-view]').forEach(btn => {
    btn.onclick = () => this.renderNPCEntryView(entries[parseInt(btn.getAttribute('data-view'))], campaign, parseInt(btn.getAttribute('data-view')));
  });
  container.querySelectorAll('[data-delete]').forEach(btn => {
    btn.onclick = () => {
      const idxToDelete = parseInt(btn.getAttribute('data-delete'));
      const npcToDelete = entries[idxToDelete];
      window.modalUtils.showConfirmModal(
        'Delete NPC',
        `Are you sure you want to delete NPC: "${window.modalUtils.escapeHtml(npcToDelete.name || 'Unnamed')}"? This action cannot be undone.`,
        () => { // onConfirm
          entries.splice(idxToDelete, 1);
          this.saveEntries(campaign, entries);
          this.renderNPCListView(container, campaign); // Refresh the list
        },
        null // onCancel - do nothing
      );
    };
  });
};

// New: Entry View (read-only, modal)
window.npcTracker.renderNPCEntryView = function(npc, campaign, idx) {
  let html = `<dl class="row">
    <dt class="col-sm-4">NPC Name:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(npc.name) || 'N/A'}</dd>
    <dt class="col-sm-4">Stat Block (Source):</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(npc.statBlock) || 'N/A'}</dd>
    <dt class="col-sm-4">MM Page:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(npc.mmPage) || 'N/A'}</dd>
    <dt class="col-sm-4">Stat Block Alterations:</dt><dd class="col-sm-8">${(npc.alterations && npc.alterations.trim() !== '') ? window.modalUtils.renderMarkdown(npc.alterations) : '<div class="markdown-content">N/A</div>'}</dd>
    <dt class="col-sm-4">Alignment:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(npc.alignment) || 'N/A'}</dd>
    <dt class="col-sm-4">Personality:</dt><dd class="col-sm-8">${(npc.personality && npc.personality.trim() !== '') ? window.modalUtils.renderMarkdown(npc.personality) : '<div class="markdown-content">N/A</div>'}</dd>
    <dt class="col-sm-4">Appearance:</dt><dd class="col-sm-8">${(npc.appearance && npc.appearance.trim() !== '') ? window.modalUtils.renderMarkdown(npc.appearance) : '<div class="markdown-content">N/A</div>'}</dd>
    <dt class="col-sm-4">Secret:</dt><dd class="col-sm-8">${(npc.secret && npc.secret.trim() !== '') ? window.modalUtils.renderMarkdown(npc.secret) : '<div class="markdown-content">N/A</div>'}</dd>
  </dl>`;
  let footer = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
    <button type="button" class="btn btn-primary" id="editNPCFromViewBtn">Edit</button>`;
  window.modalUtils.showModal(`View NPC: ${window.modalUtils.escapeHtml(npc.name)}`, html, footer);
  
  const editButton = document.getElementById('editNPCFromViewBtn');
  const newEditButton = editButton.cloneNode(true); // Clone to remove old listeners
  editButton.parentNode.replaceChild(newEditButton, editButton);
  newEditButton.onclick = () => {
    window.npcTracker.renderNPCFormModal(campaign, idx, true);
  };
};

// Refactored: Form (modal)
window.npcTracker.renderNPCFormModal = function(campaign, idx, isEditFromView = false) {
  const entries = this.getEntries(campaign);
  const npc = idx != null ? {...entries[idx]} : {
    name: '', statBlock: '', mmPage: '', alterations: '', alignment: '', personality: '', appearance: '', secret: ''
  };
  let html = `<form id="npc-form-modal">
    <div class="mb-3">
      <label class="form-label">NPC Name</label>
      <input class="form-control" name="name" value="${window.modalUtils.escapeHtml(npc.name) || ''}" required />
    </div>
    <div class="mb-3">
      <label class="form-label">Stat Block (Source)</label>
      <input class="form-control" name="statBlock" value="${window.modalUtils.escapeHtml(npc.statBlock) || ''}" />
    </div>
    <div class="mb-3">
      <label class="form-label">MM Page</label>
      <input class="form-control" name="mmPage" value="${window.modalUtils.escapeHtml(npc.mmPage) || ''}" />
    </div>
    <div class="mb-3">
      <label class="form-label">Stat Block Alterations</label>
      <textarea class="form-control" name="alterations">${window.modalUtils.escapeHtml(npc.alterations) || ''}</textarea>
    </div>
    <div class="mb-3">
      <label class="form-label">Alignment</label>
      <input class="form-control" name="alignment" value="${window.modalUtils.escapeHtml(npc.alignment) || ''}" placeholder="e.g. LG, NG, N, CE" />
    </div>
    <div class="mb-3">
      <label class="form-label">Personality</label>
      <textarea class="form-control" name="personality">${window.modalUtils.escapeHtml(npc.personality) || ''}</textarea>
    </div>
    <div class="mb-3">
      <label class="form-label">Appearance</label>
      <textarea class="form-control" name="appearance">${window.modalUtils.escapeHtml(npc.appearance) || ''}</textarea>
    </div>
    <div class="mb-3">
      <label class="form-label">Secret</label>
      <textarea class="form-control" name="secret">${window.modalUtils.escapeHtml(npc.secret) || ''}</textarea>
    </div>
  </form>`;
  let footer = `<button type="button" class="btn btn-secondary" id="cancelNPCFormBtn">Cancel</button>
    <button type="button" class="btn btn-success" id="saveNPCFormBtn">Save</button>`;
  window.modalUtils.showModal(idx != null ? `Edit NPC: ${window.modalUtils.escapeHtml(npc.name)}` : 'Add NPC', html, footer);

  const form = document.getElementById('npc-form-modal');
  const simpleMDEInstances = {
    alterations: new SimpleMDE({element: form.alterations, spellChecker: false, status: false, toolbarTips: false}),
    personality: new SimpleMDE({element: form.personality, spellChecker: false, status: false, toolbarTips: false}),
    appearance: new SimpleMDE({element: form.appearance, spellChecker: false, status: false, toolbarTips: false}),
    secret: new SimpleMDE({element: form.secret, spellChecker: false, status: false, toolbarTips: false})
  };

  document.getElementById('cancelNPCFormBtn').onclick = () => {
    // Clean up SimpleMDE instances
    Object.values(simpleMDEInstances).forEach(sde => {
      if (sde && sde.toTextArea) {
        sde.toTextArea();
      }
    });
    if (isEditFromView && idx != null) {
      window.npcTracker.renderNPCEntryView(entries[idx], campaign, idx);
    } else {
      window.modalUtils.hideModal();
    }
  };
  document.getElementById('saveNPCFormBtn').onclick = () => {
    // const form = document.getElementById('npc-form-modal'); // Already declared above
    const newNPC = {
      name: form.name.value.trim(),
      statBlock: form.statBlock.value.trim(),
      mmPage: form.mmPage.value.trim(),
      alterations: simpleMDEInstances.alterations.value().trim(),
      alignment: form.alignment.value.trim(),
      personality: simpleMDEInstances.personality.value().trim(),
      appearance: simpleMDEInstances.appearance.value().trim(),
      secret: simpleMDEInstances.secret.value().trim()
    };

    if (!newNPC.name) {
    window.modalUtils.showAlertModal('Validation Error', 'NPC Name is required. Please enter a name for the NPC.', () => {
      // This callback ensures that if showAlertModal itself is a modal,
      // focus or other states are correctly handled when it's dismissed.
      // No SimpleMDE cleanup here, as the form modal should remain open and active.
      });
      return;
    }

  // If validation passes, then proceed to save.
  // Clean up SimpleMDE instances now that we are sure we are closing the form modal.
  Object.values(simpleMDEInstances).forEach(sde => {
    if (sde && sde.toTextArea) {
      sde.toTextArea();
    }
  });

    if (idx != null) {
      entries[idx] = newNPC;
    } else {
      entries.push(newNPC);
    }
    window.npcTracker.saveEntries(campaign, entries);
  // window.modalUtils.hideModal(); // This will be called after successful save or explicit cancel.
    // Refresh list view
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
      window.npcTracker.renderNPCListView(mainContent, campaign);
    }
  window.modalUtils.hideModal(); // Hide modal after successful save and list refresh
  };
};
})();