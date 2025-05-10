// Bastion Tracker Module

// Utility for escaping HTML (use window.modalUtils.escapeHtml if available)
function escapeHtml(unsafe) {
  if (window.modalUtils && window.modalUtils.escapeHtml) return window.modalUtils.escapeHtml(unsafe);
  if (typeof unsafe !== 'string') return '';
  return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

// Logic for Bastion Tracker
// Placeholder for tracker-specific functions

window.bastionTracker = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.bastions) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.bastions = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns);
  },
  renderBastionList: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Bastion Tracker</h2>
      <button class="btn btn-primary" id="add-bastion-btn">Add Bastion</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No bastions yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((bastion, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>${bastion.bastionName || '(No Name)'} </strong> <span class="text-muted small">(${bastion.characterName || ''})</span></div>
            <div>
              <button class="btn btn-sm btn-secondary me-2" data-edit="${idx}">Edit</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">Level: ${bastion.level || ''}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html + `<div id="bastion-form-area"></div>`;
    document.getElementById('add-bastion-btn').onclick = () => this.renderBastionForm(container, campaign);
    container.querySelectorAll('[data-edit]').forEach(btn => {
      btn.onclick = () => this.renderBastionForm(container, campaign, parseInt(btn.getAttribute('data-edit')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this bastion?')) {
          entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveEntries(campaign, entries);
          this.renderBastionList(container, campaign);
        }
      };
    });
  },
  renderBastionForm: function(container, campaign, idx) {
    const entries = this.getEntries(campaign);
    const bastion = idx != null ? {...entries[idx], facilities: [...(entries[idx].facilities||[])]} : {
      bastionName: '', characterName: '', level: '', facilities: [], basicFacilities: '', defenders: ''
    };
    let html = `<form class="card card-body mb-3" id="bastion-form">
      <div class="mb-2">
        <label class="form-label">Bastion's Name</label>
        <input class="form-control" name="bastionName" value="${bastion.bastionName || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Character's Name</label>
        <input class="form-control" name="characterName" value="${bastion.characterName || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Level</label>
        <input class="form-control" name="level" type="number" min="1" value="${bastion.level || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Special Facilities</label>
        <div id="facilities-list"></div>
        <button type="button" class="btn btn-sm btn-outline-primary mt-2" id="add-facility-btn">Add Facility</button>
      </div>
      <div class="mb-2">
        <label class="form-label">Basic Facilities</label>
        <textarea class="form-control" name="basicFacilities">${bastion.basicFacilities || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Bastion Defenders</label>
        <textarea class="form-control" name="defenders">${bastion.defenders || ''}</textarea>
      </div>
      <div class="d-flex gap-2">
        <button type="submit" class="btn btn-success">Save</button>
        <button type="button" class="btn btn-secondary" id="cancel-bastion-btn">Cancel</button>
      </div>
    </form>`;
    document.getElementById('bastion-form-area').innerHTML = html;
    // Render facilities
    function renderFacilities() {
      const list = document.getElementById('facilities-list');
      if (!bastion.facilities) bastion.facilities = [];
      let fHtml = '';
      bastion.facilities.forEach((fac, i) => {
        fHtml += `<div class="card card-body mb-2">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <strong>Facility ${i+1}</strong>
            <button type="button" class="btn btn-outline-danger btn-sm" data-remove-facility="${i}">Remove</button>
          </div>
          <div class="mb-1"><label class="form-label">Facility Name/Type</label><input class="form-control" name="facilityName" value="${fac.facilityName || ''}" /></div>
          <div class="mb-1"><label class="form-label">Space</label><input class="form-control" name="space" value="${fac.space || ''}" /></div>
          <div class="mb-1"><label class="form-label">Order</label><input class="form-control" name="order" value="${fac.order || ''}" /></div>
          <div class="mb-1"><label class="form-label">Hirelings</label><textarea class="form-control" name="hirelings">${fac.hirelings || ''}</textarea></div>
          <div class="mb-1"><label class="form-label">Notes</label><textarea class="form-control" name="notes">${fac.notes || ''}</textarea></div>
        </div>`;
      });
      list.innerHTML = fHtml;
      list.querySelectorAll('[data-remove-facility]').forEach(btn => {
        btn.onclick = () => {
          bastion.facilities.splice(parseInt(btn.getAttribute('data-remove-facility')), 1);
          renderFacilities();
        };
      });
      // Update facility values
      list.querySelectorAll('.card').forEach((card, i) => {
        card.querySelector('input[name="facilityName"]').oninput = e => { bastion.facilities[i].facilityName = e.target.value; };
        card.querySelector('input[name="space"]').oninput = e => { bastion.facilities[i].space = e.target.value; };
        card.querySelector('input[name="order"]').oninput = e => { bastion.facilities[i].order = e.target.value; };
        card.querySelector('textarea[name="hirelings"]').oninput = e => { bastion.facilities[i].hirelings = e.target.value; };
        card.querySelector('textarea[name="notes"]').oninput = e => { bastion.facilities[i].notes = e.target.value; };
      });
    }
    renderFacilities();
    document.getElementById('add-facility-btn').onclick = () => {
      bastion.facilities.push({ facilityName: '', space: '', order: '', hirelings: '', notes: '' });
      renderFacilities();
    };
    document.getElementById('cancel-bastion-btn').onclick = () => {
      this.renderBastionList(container, campaign);
    };
    document.getElementById('bastion-form').onsubmit = (e) => {
      e.preventDefault();
      const form = e.target;
      const newBastion = {
        bastionName: form.bastionName.value,
        characterName: form.characterName.value,
        level: form.level.value,
        facilities: bastion.facilities,
        basicFacilities: form.basicFacilities.value,
        defenders: form.defenders.value
      };
      if (idx != null) {
        entries[idx] = newBastion;
      } else {
        entries.push(newBastion);
      }
      this.saveEntries(campaign, entries);
      this.renderBastionList(container, campaign);
    };
  },
  renderBastionListView: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Bastion Tracker</h2>
      <button class="btn btn-primary" id="add-bastion-btn">Add Bastion</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No bastions yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((bastion, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>${escapeHtml(bastion.bastionName) || '(No Name)'} </strong> <span class="text-muted small">(${escapeHtml(bastion.characterName) || ''})</span></div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">Level: ${escapeHtml(bastion.level) || ''}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html;
    document.getElementById('add-bastion-btn').onclick = () => this.renderBastionFormModal(campaign, null);
    container.querySelectorAll('[data-view]').forEach(btn => {
      btn.onclick = () => this.renderBastionEntryView(entries[parseInt(btn.getAttribute('data-view'))], campaign, parseInt(btn.getAttribute('data-view')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this bastion?')) {
          entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveEntries(campaign, entries);
          this.renderBastionListView(container, campaign);
        }
      };
    });
  },
  renderBastionEntryView: function(bastion, campaign, idx) {
    let html = `<dl class="row">
      <dt class="col-sm-4">Bastion's Name:</dt><dd class="col-sm-8">${escapeHtml(bastion.bastionName) || 'N/A'}</dd>
      <dt class="col-sm-4">Character's Name:</dt><dd class="col-sm-8">${escapeHtml(bastion.characterName) || 'N/A'}</dd>
      <dt class="col-sm-4">Level:</dt><dd class="col-sm-8">${escapeHtml(bastion.level) || 'N/A'}</dd>
      <dt class="col-sm-4">Special Facilities:</dt><dd class="col-sm-8">`;
    if (bastion.facilities && bastion.facilities.length) {
      html += '<ul>' + bastion.facilities.map((fac, i) => `<li><strong>${escapeHtml(fac.facilityName) || 'Facility ' + (i+1)}</strong><br/>Space: ${escapeHtml(fac.space) || 'N/A'}<br/>Order: ${escapeHtml(fac.order) || 'N/A'}<br/>Hirelings: <pre>${escapeHtml(fac.hirelings) || 'N/A'}</pre>Notes: <pre>${escapeHtml(fac.notes) || 'N/A'}</pre></li>`).join('') + '</ul>';
    } else {
      html += 'N/A';
    }
    html += `</dd>
      <dt class="col-sm-4">Basic Facilities:</dt><dd class="col-sm-8"><pre>${escapeHtml(bastion.basicFacilities) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Bastion Defenders:</dt><dd class="col-sm-8"><pre>${escapeHtml(bastion.defenders) || 'N/A'}</pre></dd>
    </dl>`;
    let footer = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editBastionFromViewBtn">Edit</button>`;
    window.modalUtils.showModal(`View Bastion: ${escapeHtml(bastion.bastionName)}`, html, footer);
    document.getElementById('editBastionFromViewBtn').onclick = () => {
      window.bastionTracker.renderBastionFormModal(campaign, idx, true);
    };
  },
  renderBastionFormModal: function(campaign, idx, isEditFromView = false) {
    const entries = this.getEntries(campaign);
    const bastion = idx != null ? {...entries[idx], facilities: [...(entries[idx].facilities||[])]} : {
      bastionName: '', characterName: '', level: '', facilities: [], basicFacilities: '', defenders: ''
    };
    let html = `<form id="bastion-form-modal">
      <div class="mb-2">
        <label class="form-label">Bastion's Name</label>
        <input class="form-control" name="bastionName" value="${escapeHtml(bastion.bastionName) || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Character's Name</label>
        <input class="form-control" name="characterName" value="${escapeHtml(bastion.characterName) || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Level</label>
        <input class="form-control" name="level" type="number" min="1" value="${escapeHtml(bastion.level) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Special Facilities</label>
        <div id="facilities-list-modal"></div>
        <button type="button" class="btn btn-sm btn-outline-primary mt-2" id="add-facility-btn-modal">Add Facility</button>
      </div>
      <div class="mb-2">
        <label class="form-label">Basic Facilities</label>
        <textarea class="form-control" name="basicFacilities">${escapeHtml(bastion.basicFacilities) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Bastion Defenders</label>
        <textarea class="form-control" name="defenders">${escapeHtml(bastion.defenders) || ''}</textarea>
      </div>
    </form>`;
    let footer = `<button type="button" class="btn btn-secondary" id="cancelBastionFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveBastionFormBtn">Save</button>`;
    window.modalUtils.showModal(idx != null ? `Edit Bastion: ${escapeHtml(bastion.bastionName)}` : 'Add Bastion', html, footer);
    // Facilities logic
    function renderFacilities() {
      const list = document.getElementById('facilities-list-modal');
      if (!bastion.facilities) bastion.facilities = [];
      let fHtml = '';
      bastion.facilities.forEach((fac, i) => {
        fHtml += `<div class="card card-body mb-2">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <strong>Facility ${i+1}</strong>
            <button type="button" class="btn btn-outline-danger btn-sm" data-remove-facility="${i}">Remove</button>
          </div>
          <div class="mb-1"><label class="form-label">Facility Name/Type</label><input class="form-control" name="facilityName" value="${escapeHtml(fac.facilityName) || ''}" /></div>
          <div class="mb-1"><label class="form-label">Space</label><input class="form-control" name="space" value="${escapeHtml(fac.space) || ''}" /></div>
          <div class="mb-1"><label class="form-label">Order</label><input class="form-control" name="order" value="${escapeHtml(fac.order) || ''}" /></div>
          <div class="mb-1"><label class="form-label">Hirelings</label><textarea class="form-control" name="hirelings">${escapeHtml(fac.hirelings) || ''}</textarea></div>
          <div class="mb-1"><label class="form-label">Notes</label><textarea class="form-control" name="notes">${escapeHtml(fac.notes) || ''}</textarea></div>
        </div>`;
      });
      list.innerHTML = fHtml;
      list.querySelectorAll('[data-remove-facility]').forEach(btn => {
        btn.onclick = () => {
          bastion.facilities.splice(parseInt(btn.getAttribute('data-remove-facility')), 1);
          renderFacilities();
        };
      });
      // Update facility values
      list.querySelectorAll('.card').forEach((card, i) => {
        card.querySelector('input[name="facilityName"]').oninput = e => { bastion.facilities[i].facilityName = e.target.value; };
        card.querySelector('input[name="space"]').oninput = e => { bastion.facilities[i].space = e.target.value; };
        card.querySelector('input[name="order"]').oninput = e => { bastion.facilities[i].order = e.target.value; };
        card.querySelector('textarea[name="hirelings"]').oninput = e => { bastion.facilities[i].hirelings = e.target.value; };
        card.querySelector('textarea[name="notes"]').oninput = e => { bastion.facilities[i].notes = e.target.value; };
      });
    }
    renderFacilities();
    document.getElementById('add-facility-btn-modal').onclick = () => {
      bastion.facilities.push({ facilityName: '', space: '', order: '', hirelings: '', notes: '' });
      renderFacilities();
    };
    document.getElementById('cancelBastionFormBtn').onclick = () => {
      if (isEditFromView && idx != null) {
        window.bastionTracker.renderBastionEntryView(entries[idx], campaign, idx);
      } else {
        window.modalUtils.hideModal();
      }
    };
    document.getElementById('saveBastionFormBtn').onclick = () => {
      const form = document.getElementById('bastion-form-modal');
      const newBastion = {
        bastionName: form.bastionName.value.trim(),
        characterName: form.characterName.value.trim(),
        level: form.level.value.trim(),
        facilities: bastion.facilities,
        basicFacilities: form.basicFacilities.value.trim(),
        defenders: form.defenders.value.trim()
      };
      if (!newBastion.bastionName) {
        alert('Bastion Name is required.');
        return;
      }
      if (idx != null) {
        entries[idx] = newBastion;
      } else {
        entries.push(newBastion);
      }
      window.bastionTracker.saveEntries(campaign, entries);
      window.modalUtils.hideModal();
      // Refresh list view
      const mainContent = document.getElementById('main-content');
      if (mainContent) {
        window.bastionTracker.renderBastionListView(mainContent, campaign);
      }
    };
  }
};