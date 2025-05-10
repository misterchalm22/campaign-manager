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
            <div><strong>${npc.name || '(No Name)'}</strong> <span class="text-muted small">${npc.statBlock || ''}</span></div>
            <div>
              <button class="btn btn-sm btn-secondary me-2" data-edit="${idx}">Edit</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">Alignment: ${npc.alignment || ''}</div>
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
        <input class="form-control" name="name" value="${npc.name || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Stat Block (Source)</label>
        <input class="form-control" name="statBlock" value="${npc.statBlock || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">MM Page</label>
        <input class="form-control" name="mmPage" value="${npc.mmPage || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Stat Block Alterations</label>
        <textarea class="form-control" name="alterations">${npc.alterations || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Alignment</label>
        <input class="form-control" name="alignment" value="${npc.alignment || ''}" placeholder="e.g. LG, NG, N, CE" />
      </div>
      <div class="mb-2">
        <label class="form-label">Personality</label>
        <textarea class="form-control" name="personality">${npc.personality || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Appearance</label>
        <textarea class="form-control" name="appearance">${npc.appearance || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Secret</label>
        <textarea class="form-control" name="secret">${npc.secret || ''}</textarea>
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

// Utility for escaping HTML (use window.modalUtils.escapeHtml if available)
function escapeHtml(unsafe) {
  if (window.modalUtils && window.modalUtils.escapeHtml) return window.modalUtils.escapeHtml(unsafe);
  if (typeof unsafe !== 'string') return '';
  return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

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
          <div><strong>${escapeHtml(npc.name) || '(No Name)'}</strong> <span class="text-muted small">${escapeHtml(npc.statBlock) || ''}</span></div>
          <div>
            <button class="btn btn-sm btn-info me-2" data-view="${idx}">View Details</button>
            <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
          </div>
        </div>
        <div class="small text-muted">Alignment: ${escapeHtml(npc.alignment) || ''}</div>
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
      if (confirm('Delete this NPC?')) {
        entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
        this.saveEntries(campaign, entries);
        this.renderNPCListView(container, campaign);
      }
    };
  });
};

// New: Entry View (read-only, modal)
window.npcTracker.renderNPCEntryView = function(npc, campaign, idx) {
  let html = `<dl class="row">
    <dt class="col-sm-4">NPC Name:</dt><dd class="col-sm-8">${escapeHtml(npc.name) || 'N/A'}</dd>
    <dt class="col-sm-4">Stat Block (Source):</dt><dd class="col-sm-8">${escapeHtml(npc.statBlock) || 'N/A'}</dd>
    <dt class="col-sm-4">MM Page:</dt><dd class="col-sm-8">${escapeHtml(npc.mmPage) || 'N/A'}</dd>
    <dt class="col-sm-4">Stat Block Alterations:</dt><dd class="col-sm-8"><pre>${escapeHtml(npc.alterations) || 'N/A'}</pre></dd>
    <dt class="col-sm-4">Alignment:</dt><dd class="col-sm-8">${escapeHtml(npc.alignment) || 'N/A'}</dd>
    <dt class="col-sm-4">Personality:</dt><dd class="col-sm-8"><pre>${escapeHtml(npc.personality) || 'N/A'}</pre></dd>
    <dt class="col-sm-4">Appearance:</dt><dd class="col-sm-8"><pre>${escapeHtml(npc.appearance) || 'N/A'}</pre></dd>
    <dt class="col-sm-4">Secret:</dt><dd class="col-sm-8"><pre>${escapeHtml(npc.secret) || 'N/A'}</pre></dd>
  </dl>`;
  let footer = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
    <button type="button" class="btn btn-primary" id="editNPCFromViewBtn">Edit</button>`;
  window.modalUtils.showModal(`View NPC: ${escapeHtml(npc.name)}`, html, footer);
  document.getElementById('editNPCFromViewBtn').onclick = () => {
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
    <div class="mb-2">
      <label class="form-label">NPC Name</label>
      <input class="form-control" name="name" value="${escapeHtml(npc.name) || ''}" required />
    </div>
    <div class="mb-2">
      <label class="form-label">Stat Block (Source)</label>
      <input class="form-control" name="statBlock" value="${escapeHtml(npc.statBlock) || ''}" />
    </div>
    <div class="mb-2">
      <label class="form-label">MM Page</label>
      <input class="form-control" name="mmPage" value="${escapeHtml(npc.mmPage) || ''}" />
    </div>
    <div class="mb-2">
      <label class="form-label">Stat Block Alterations</label>
      <textarea class="form-control" name="alterations">${escapeHtml(npc.alterations) || ''}</textarea>
    </div>
    <div class="mb-2">
      <label class="form-label">Alignment</label>
      <input class="form-control" name="alignment" value="${escapeHtml(npc.alignment) || ''}" placeholder="e.g. LG, NG, N, CE" />
    </div>
    <div class="mb-2">
      <label class="form-label">Personality</label>
      <textarea class="form-control" name="personality">${escapeHtml(npc.personality) || ''}</textarea>
    </div>
    <div class="mb-2">
      <label class="form-label">Appearance</label>
      <textarea class="form-control" name="appearance">${escapeHtml(npc.appearance) || ''}</textarea>
    </div>
    <div class="mb-2">
      <label class="form-label">Secret</label>
      <textarea class="form-control" name="secret">${escapeHtml(npc.secret) || ''}</textarea>
    </div>
  </form>`;
  let footer = `<button type="button" class="btn btn-secondary" id="cancelNPCFormBtn">Cancel</button>
    <button type="button" class="btn btn-success" id="saveNPCFormBtn">Save</button>`;
  window.modalUtils.showModal(idx != null ? `Edit NPC: ${escapeHtml(npc.name)}` : 'Add NPC', html, footer);
  document.getElementById('cancelNPCFormBtn').onclick = () => {
    if (isEditFromView && idx != null) {
      window.npcTracker.renderNPCEntryView(entries[idx], campaign, idx);
    } else {
      window.modalUtils.hideModal();
    }
  };
  document.getElementById('saveNPCFormBtn').onclick = () => {
    const form = document.getElementById('npc-form-modal');
    const newNPC = {
      name: form.name.value.trim(),
      statBlock: form.statBlock.value.trim(),
      mmPage: form.mmPage.value.trim(),
      alterations: form.alterations.value.trim(),
      alignment: form.alignment.value.trim(),
      personality: form.personality.value.trim(),
      appearance: form.appearance.value.trim(),
      secret: form.secret.value.trim()
    };
    if (!newNPC.name) {
      alert('NPC Name is required.');
      return;
    }
    if (idx != null) {
      entries[idx] = newNPC;
    } else {
      entries.push(newNPC);
    }
    window.npcTracker.saveEntries(campaign, entries);
    window.modalUtils.hideModal();
    // Refresh list view
    const mainContent = document.getElementById('main-content');
    if (mainContent) {
      window.npcTracker.renderNPCListView(mainContent, campaign);
    }
  };
};