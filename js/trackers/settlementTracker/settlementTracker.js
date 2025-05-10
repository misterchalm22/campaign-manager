// SettlementTracker.js

// Utility for escaping HTML (use window.modalUtils.escapeHtml if available)
function escapeHtml(unsafe) {
  if (window.modalUtils && window.modalUtils.escapeHtml) return window.modalUtils.escapeHtml(unsafe);
  if (typeof unsafe !== 'string') return '';
  return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

// Logic for Settlement Tracker
window.settlementTracker = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.settlements) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.settlements = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns);
  },
  renderSettlementList: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Settlement Tracker</h2>
      <button class="btn btn-primary" id="add-settlement-btn">Add Settlement</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No settlements yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((settlement, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>${settlement.name || '(No Name)'}</strong> <span class="text-muted small">${settlement.size || ''}</span></div>
            <div>
              <button class="btn btn-sm btn-secondary me-2" data-edit="${idx}">Edit</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">Leader: ${settlement.localLeader || ''}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html + `<div id="settlement-form-area"></div>`;
    document.getElementById('add-settlement-btn').onclick = () => this.renderSettlementForm(container, campaign);
    container.querySelectorAll('[data-edit]').forEach(btn => {
      btn.onclick = () => this.renderSettlementForm(container, campaign, parseInt(btn.getAttribute('data-edit')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this settlement?')) {
          entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveEntries(campaign, entries);
          this.renderSettlementList(container, campaign);
        }
      };
    });
  },
  renderSettlementForm: function(container, campaign, idx) {
    const entries = this.getEntries(campaign);
    const settlement = idx != null ? {...entries[idx]} : {
      name: '', size: '', trait: '', fame: '', calamity: '', localLeader: '', people: '', places: '', gpValue: ''
    };
    let html = `<form class="card card-body mb-3" id="settlement-form">
      <div class="mb-2">
        <label class="form-label">Settlement Name</label>
        <input class="form-control" name="name" value="${settlement.name || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Size</label>
        <select class="form-select" name="size" required>
          <option value="">Select size</option>
          <option value="Village (Pop up to 500)"${settlement.size==="Village (Pop up to 500)"?" selected":""}>Village (Pop up to 500)</option>
          <option value="Town (Pop. 501-5,000)"${settlement.size==="Town (Pop. 501-5,000)"?" selected":""}>Town (Pop. 501-5,000)</option>
          <option value="City (Pop. 5,001+)"${settlement.size==="City (Pop. 5,001+)"?" selected":""}>City (Pop. 5,001+)</option>
        </select>
      </div>
      <div class="mb-2">
        <label class="form-label">Defining Trait</label>
        <textarea class="form-control" name="trait">${settlement.trait || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Claim to Fame</label>
        <textarea class="form-control" name="fame">${settlement.fame || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Current Calamity</label>
        <textarea class="form-control" name="calamity">${settlement.calamity || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Local Leader</label>
        <input class="form-control" name="localLeader" value="${settlement.localLeader || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Noteworthy People</label>
        <textarea class="form-control" name="people">${settlement.people || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Noteworthy Places</label>
        <textarea class="form-control" name="places">${settlement.places || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">GP Value of Most Expensive Item for Sale</label>
        <input class="form-control" name="gpValue" value="${settlement.gpValue || ''}" type="number" min="0" />
      </div>
      <div class="d-flex gap-2">
        <button type="submit" class="btn btn-success">Save</button>
        <button type="button" class="btn btn-secondary" id="cancel-settlement-btn">Cancel</button>
      </div>
    </form>`;
    document.getElementById('settlement-form-area').innerHTML = html;
    document.getElementById('cancel-settlement-btn').onclick = () => {
      this.renderSettlementList(container, campaign);
    };
    document.getElementById('settlement-form').onsubmit = (e) => {
      e.preventDefault();
      const form = e.target;
      const newSettlement = {
        name: form.name.value,
        size: form.size.value,
        trait: form.trait.value,
        fame: form.fame.value,
        calamity: form.calamity.value,
        localLeader: form.localLeader.value,
        people: form.people.value,
        places: form.places.value,
        gpValue: form.gpValue.value
      };
      if (idx != null) {
        entries[idx] = newSettlement;
      } else {
        entries.push(newSettlement);
      }
      this.saveEntries(campaign, entries);
      this.renderSettlementList(container, campaign);
    };
  },
  renderSettlementListView: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Settlement Tracker</h2>
      <button class="btn btn-primary" id="add-settlement-btn">Add Settlement</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No settlements yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((settlement, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>${escapeHtml(settlement.name) || '(No Name)'}</strong> <span class="text-muted small">${escapeHtml(settlement.size) || ''}</span></div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">Leader: ${escapeHtml(settlement.localLeader) || ''}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html;
    document.getElementById('add-settlement-btn').onclick = () => this.renderSettlementFormModal(campaign, null);
    container.querySelectorAll('[data-view]').forEach(btn => {
      btn.onclick = () => this.renderSettlementEntryView(entries[parseInt(btn.getAttribute('data-view'))], campaign, parseInt(btn.getAttribute('data-view')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this settlement?')) {
          entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveEntries(campaign, entries);
          this.renderSettlementListView(container, campaign);
        }
      };
    });
  },
  renderSettlementEntryView: function(settlement, campaign, idx) {
    let html = `<dl class="row">
      <dt class="col-sm-4">Settlement Name:</dt><dd class="col-sm-8">${escapeHtml(settlement.name) || 'N/A'}</dd>
      <dt class="col-sm-4">Size:</dt><dd class="col-sm-8">${escapeHtml(settlement.size) || 'N/A'}</dd>
      <dt class="col-sm-4">Defining Trait:</dt><dd class="col-sm-8"><pre>${escapeHtml(settlement.trait) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Claim to Fame:</dt><dd class="col-sm-8"><pre>${escapeHtml(settlement.fame) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Current Calamity:</dt><dd class="col-sm-8"><pre>${escapeHtml(settlement.calamity) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Local Leader:</dt><dd class="col-sm-8">${escapeHtml(settlement.localLeader) || 'N/A'}</dd>
      <dt class="col-sm-4">Noteworthy People:</dt><dd class="col-sm-8"><pre>${escapeHtml(settlement.people) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Noteworthy Places:</dt><dd class="col-sm-8"><pre>${escapeHtml(settlement.places) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">GP Value of Most Expensive Item:</dt><dd class="col-sm-8">${escapeHtml(settlement.gpValue) || 'N/A'}</dd>
    </dl>`;
    let footer = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editSettlementFromViewBtn">Edit</button>`;
    window.modalUtils.showModal(`View Settlement: ${escapeHtml(settlement.name)}`, html, footer);
    document.getElementById('editSettlementFromViewBtn').onclick = () => {
      window.settlementTracker.renderSettlementFormModal(campaign, idx, true);
    };
  },
  renderSettlementFormModal: function(campaign, idx, isEditFromView = false) {
    const entries = this.getEntries(campaign);
    const settlement = idx != null ? {...entries[idx]} : {
      name: '', size: '', trait: '', fame: '', calamity: '', localLeader: '', people: '', places: '', gpValue: ''
    };
    let html = `<form id="settlement-form-modal">
      <div class="mb-2">
        <label class="form-label">Settlement Name</label>
        <input class="form-control" name="name" value="${escapeHtml(settlement.name) || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Size</label>
        <select class="form-select" name="size" required>
          <option value="">Select size</option>
          <option value="Village (Pop up to 500)"${settlement.size==="Village (Pop up to 500)"?" selected":""}>Village (Pop up to 500)</option>
          <option value="Town (Pop. 501-5,000)"${settlement.size==="Town (Pop. 501-5,000)"?" selected":""}>Town (Pop. 501-5,000)</option>
          <option value="City (Pop. 5,001+)"${settlement.size==="City (Pop. 5,001+)"?" selected":""}>City (Pop. 5,001+)</option>
        </select>
      </div>
      <div class="mb-2">
        <label class="form-label">Defining Trait</label>
        <textarea class="form-control" name="trait">${escapeHtml(settlement.trait) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Claim to Fame</label>
        <textarea class="form-control" name="fame">${escapeHtml(settlement.fame) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Current Calamity</label>
        <textarea class="form-control" name="calamity">${escapeHtml(settlement.calamity) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Local Leader</label>
        <input class="form-control" name="localLeader" value="${escapeHtml(settlement.localLeader) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Noteworthy People</label>
        <textarea class="form-control" name="people">${escapeHtml(settlement.people) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Noteworthy Places</label>
        <textarea class="form-control" name="places">${escapeHtml(settlement.places) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">GP Value of Most Expensive Item for Sale</label>
        <input class="form-control" name="gpValue" value="${escapeHtml(settlement.gpValue) || ''}" type="number" min="0" />
      </div>
    </form>`;
    let footer = `<button type="button" class="btn btn-secondary" id="cancelSettlementFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveSettlementFormBtn">Save</button>`;
    window.modalUtils.showModal(idx != null ? `Edit Settlement: ${escapeHtml(settlement.name)}` : 'Add Settlement', html, footer);
    document.getElementById('cancelSettlementFormBtn').onclick = () => {
      if (isEditFromView && idx != null) {
        window.settlementTracker.renderSettlementEntryView(entries[idx], campaign, idx);
      } else {
        window.modalUtils.hideModal();
      }
    };
    document.getElementById('saveSettlementFormBtn').onclick = () => {
      const form = document.getElementById('settlement-form-modal');
      const newSettlement = {
        name: form.name.value.trim(),
        size: form.size.value.trim(),
        trait: form.trait.value.trim(),
        fame: form.fame.value.trim(),
        calamity: form.calamity.value.trim(),
        localLeader: form.localLeader.value.trim(),
        people: form.people.value.trim(),
        places: form.places.value.trim(),
        gpValue: form.gpValue.value.trim()
      };
      if (!newSettlement.name) {
        alert('Settlement Name is required.');
        return;
      }
      if (idx != null) {
        entries[idx] = newSettlement;
      } else {
        entries.push(newSettlement);
      }
      window.settlementTracker.saveEntries(campaign, entries);
      window.modalUtils.hideModal();
      // Refresh list view
      const mainContent = document.getElementById('main-content');
      if (mainContent) {
        window.settlementTracker.renderSettlementListView(mainContent, campaign);
      }
    };
  }
};