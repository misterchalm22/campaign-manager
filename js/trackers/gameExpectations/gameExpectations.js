(function() {
// Logic for Game Expectations tracker

window.gameExpectations = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.gameExpectations) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.gameExpectations = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns);
  },
  renderGameExpectationsView: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Game Expectations</h2>
      <button class="btn btn-primary" id="add-ge-btn">Add Entry</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No entries yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((entry, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>${entry.playerName || '(No Player Name)'}</strong></div>
            <div>
              <button class="btn btn-sm btn-secondary me-2" data-edit="${idx}">Edit</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">Theme: ${entry.gameTheme || ''}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html + `<div id="ge-form-area"></div>`;
    document.getElementById('add-ge-btn').onclick = () => this.renderGameExpectationsForm(container, campaign);
    container.querySelectorAll('[data-edit]').forEach(btn => {
      btn.onclick = () => this.renderGameExpectationsForm(container, campaign, parseInt(btn.getAttribute('data-edit')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this entry?')) {
          entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveEntries(campaign, entries);
          this.renderGameExpectationsView(container, campaign);
        }
      };
    });
  },
  renderGameExpectationsForm: function(container, campaign, idx) {
    const entries = this.getEntries(campaign);
    const entry = idx != null ? {...entries[idx]} : {
      dmName: '', playerName: '', gameTheme: '', sensitive: [], hopes: '', concerns: ''
    };
    let html = `<form class="card card-body mb-3" id="ge-form">
      <div class="mb-2">
        <label class="form-label">DM Name</label>
        <input class="form-control" name="dmName" value="${entry.dmName || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Player Name</label>
        <input class="form-control" name="playerName" value="${entry.playerName || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Game Theme and Flavor</label>
        <textarea class="form-control" name="gameTheme">${entry.gameTheme || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Potentially Sensitive Elements</label>
        <div id="sensitive-list"></div>
        <button type="button" class="btn btn-sm btn-outline-primary mt-2" id="add-sensitive-btn">Add Sensitive Element</button>
      </div>
      <div class="mb-2">
        <label class="form-label">Player's Hopes and Expectations</label>
        <textarea class="form-control" name="hopes">${entry.hopes || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">At-the-Table Concerns</label>
        <textarea class="form-control" name="concerns">${entry.concerns || ''}</textarea>
      </div>
      <div class="d-flex gap-2">
        <button type="submit" class="btn btn-success">Save</button>
        <button type="button" class="btn btn-secondary" id="cancel-ge-btn">Cancel</button>
      </div>
    </form>`;
    document.getElementById('ge-form-area').innerHTML = html;
    // Render sensitive elements
    function renderSensitiveList() {
      const list = document.getElementById('sensitive-list');
      if (!entry.sensitive) entry.sensitive = [];
      let sHtml = '';
      entry.sensitive.forEach((el, i) => {
        sHtml += `<div class="input-group mb-1">
          <input class="form-control" name="sensitive-desc" value="${el.desc || ''}" placeholder="Element description" />
          <div class="input-group-text">
            <input type="checkbox" name="hardLimit" ${el.hardLimit ? 'checked' : ''} /> Hard
          </div>
          <div class="input-group-text">
            <input type="checkbox" name="softLimit" ${el.softLimit ? 'checked' : ''} /> Soft
          </div>
          <button type="button" class="btn btn-outline-danger btn-sm" data-remove="${i}">Remove</button>
        </div>`;
      });
      list.innerHTML = sHtml;
      list.querySelectorAll('[data-remove]').forEach(btn => {
        btn.onclick = () => {
          entry.sensitive.splice(parseInt(btn.getAttribute('data-remove')), 1);
          renderSensitiveList();
        };
      });
      // Update element values
      list.querySelectorAll('.input-group').forEach((row, i) => {
        row.querySelector('input[name="sensitive-desc"]').oninput = e => { entry.sensitive[i].desc = e.target.value; };
        row.querySelector('input[name="hardLimit"]').onchange = e => { entry.sensitive[i].hardLimit = e.target.checked; };
        row.querySelector('input[name="softLimit"]').onchange = e => { entry.sensitive[i].softLimit = e.target.checked; };
      });
    }
    renderSensitiveList();
    document.getElementById('add-sensitive-btn').onclick = () => {
      entry.sensitive.push({ desc: '', hardLimit: false, softLimit: false });
      renderSensitiveList();
    };
    document.getElementById('cancel-ge-btn').onclick = () => {
      this.renderGameExpectationsView(container, campaign);
    };
    document.getElementById('ge-form').onsubmit = (e) => {
      e.preventDefault();
      const form = e.target;
      const newEntry = {
        dmName: form.dmName.value,
        playerName: form.playerName.value,
        gameTheme: form.gameTheme.value,
        sensitive: entry.sensitive,
        hopes: form.hopes.value,
        concerns: form.concerns.value
      };
      if (idx != null) {
        entries[idx] = newEntry;
      } else {
        entries.push(newEntry);
      }
      this.saveEntries(campaign, entries);
      this.renderGameExpectationsView(container, campaign);
    };
  },
  renderGameExpectationsListView: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Game Expectations</h2>
      <button class="btn btn-primary" id="add-ge-btn">Add Entry</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No entries yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((entry, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>${window.modalUtils.escapeHtml(entry.playerName) || '(No Player Name)'}</strong></div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">Theme: ${window.modalUtils.escapeHtml(entry.gameTheme) || ''}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html;
    document.getElementById('add-ge-btn').onclick = () => this.renderGameExpectationsFormModal(campaign, null);
    container.querySelectorAll('[data-view]').forEach(btn => {
      btn.onclick = () => this.renderGameExpectationsEntryView(entries[parseInt(btn.getAttribute('data-view'))], campaign, parseInt(btn.getAttribute('data-view')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this entry?')) {
          entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveEntries(campaign, entries);
          this.renderGameExpectationsListView(container, campaign);
        }
      };
    });
  },
  renderGameExpectationsEntryView: function(entry, campaign, idx) {
    let html = `<dl class="row">
      <dt class="col-sm-4">DM Name:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(entry.dmName) || 'N/A'}</dd>
      <dt class="col-sm-4">Player Name:</dt><dd class="col-sm-8">${window.modalUtils.escapeHtml(entry.playerName) || 'N/A'}</dd>
      <dt class="col-sm-4">Game Theme and Flavor:</dt><dd class="col-sm-8"><pre>${window.modalUtils.escapeHtml(entry.gameTheme) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Potentially Sensitive Elements:</dt><dd class="col-sm-8">`;
    if (entry.sensitive && entry.sensitive.length) {
      html += '<ul>' + entry.sensitive.map(el => `<li>${window.modalUtils.escapeHtml(el.desc)} [${el.hardLimit ? 'Hard' : ''}${el.hardLimit && el.softLimit ? ', ' : ''}${el.softLimit ? 'Soft' : ''}]</li>`).join('') + '</ul>';
    } else {
      html += 'N/A';
    }
    html += `</dd>
      <dt class="col-sm-4">Player's Hopes and Expectations:</dt><dd class="col-sm-8"><pre>${window.modalUtils.escapeHtml(entry.hopes) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">At-the-Table Concerns:</dt><dd class="col-sm-8"><pre>${window.modalUtils.escapeHtml(entry.concerns) || 'N/A'}</pre></dd>
    </dl>`;
    let footer = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editGEFromViewBtn">Edit</button>`;
    window.modalUtils.showModal(`View Game Expectation: ${window.modalUtils.escapeHtml(entry.playerName)}`, html, footer);
    document.getElementById('editGEFromViewBtn').onclick = () => {
      window.gameExpectations.renderGameExpectationsFormModal(campaign, idx, true);
    };
  },
  renderGameExpectationsFormModal: function(campaign, idx, isEditFromView = false) {
    const entries = this.getEntries(campaign);
    const entry = idx != null ? {...entries[idx]} : {
      dmName: '', playerName: '', gameTheme: '', sensitive: [], hopes: '', concerns: ''
    };
    let html = `<form id="ge-form-modal">
      <div class="mb-2">
        <label class="form-label">DM Name</label>
        <input class="form-control" name="dmName" value="${window.modalUtils.escapeHtml(entry.dmName) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Player Name</label>
        <input class="form-control" name="playerName" value="${window.modalUtils.escapeHtml(entry.playerName) || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Game Theme and Flavor</label>
        <textarea class="form-control" name="gameTheme">${window.modalUtils.escapeHtml(entry.gameTheme) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Potentially Sensitive Elements</label>
        <div id="sensitive-list-modal"></div>
        <button type="button" class="btn btn-sm btn-outline-primary mt-2" id="add-sensitive-btn-modal">Add Sensitive Element</button>
      </div>
      <div class="mb-2">
        <label class="form-label">Player's Hopes and Expectations</label>
        <textarea class="form-control" name="hopes">${window.modalUtils.escapeHtml(entry.hopes) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">At-the-Table Concerns</label>
        <textarea class="form-control" name="concerns">${window.modalUtils.escapeHtml(entry.concerns) || ''}</textarea>
      </div>
    </form>`;
    let footer = `<button type="button" class="btn btn-secondary" id="cancelGEFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveGEFormBtn">Save</button>`;
    window.modalUtils.showModal(idx != null ? `Edit Game Expectation: ${window.modalUtils.escapeHtml(entry.playerName)}` : 'Add Game Expectation', html, footer);
    // Sensitive elements logic
    function renderSensitiveList() {
      const list = document.getElementById('sensitive-list-modal');
      if (!entry.sensitive) entry.sensitive = [];
      let sHtml = '';
      entry.sensitive.forEach((el, i) => {
        sHtml += `<div class="input-group mb-1">
          <input class="form-control" name="sensitive-desc" value="${window.modalUtils.escapeHtml(el.desc) || ''}" placeholder="Element description" />
          <div class="input-group-text">
            <input type="checkbox" name="hardLimit" ${el.hardLimit ? 'checked' : ''} /> Hard
          </div>
          <div class="input-group-text">
            <input type="checkbox" name="softLimit" ${el.softLimit ? 'checked' : ''} /> Soft
          </div>
          <button type="button" class="btn btn-outline-danger btn-sm" data-remove="${i}">Remove</button>
        </div>`;
      });
      list.innerHTML = sHtml;
      list.querySelectorAll('[data-remove]').forEach(btn => {
        btn.onclick = () => {
          entry.sensitive.splice(parseInt(btn.getAttribute('data-remove')), 1);
          renderSensitiveList();
        };
      });
      // Update element values
      list.querySelectorAll('.input-group').forEach((row, i) => {
        row.querySelector('input[name="sensitive-desc"]').oninput = e => { entry.sensitive[i].desc = e.target.value; };
        row.querySelector('input[name="hardLimit"]').onchange = e => { entry.sensitive[i].hardLimit = e.target.checked; };
        row.querySelector('input[name="softLimit"]').onchange = e => { entry.sensitive[i].softLimit = e.target.checked; };
      });
    }
    renderSensitiveList();
    document.getElementById('add-sensitive-btn-modal').onclick = () => {
      entry.sensitive.push({ desc: '', hardLimit: false, softLimit: false });
      renderSensitiveList();
    };
    document.getElementById('cancelGEFormBtn').onclick = () => {
      if (isEditFromView && idx != null) {
        window.gameExpectations.renderGameExpectationsEntryView(entries[idx], campaign, idx);
      } else {
        window.modalUtils.hideModal();
      }
    };
    document.getElementById('saveGEFormBtn').onclick = () => {
      const form = document.getElementById('ge-form-modal');
      const newEntry = {
        dmName: form.dmName.value.trim(),
        playerName: form.playerName.value.trim(),
        gameTheme: form.gameTheme.value.trim(),
        sensitive: entry.sensitive,
        hopes: form.hopes.value.trim(),
        concerns: form.concerns.value.trim()
      };
      if (!newEntry.playerName) {
        alert('Player Name is required.');
        return;
      }
      if (idx != null) {
        entries[idx] = newEntry;
      } else {
        entries.push(newEntry);
      }
      window.gameExpectations.saveEntries(campaign, entries);
      window.modalUtils.hideModal();
      // Refresh list view
      const mainContent = document.getElementById('main-content');
      if (mainContent) {
        window.gameExpectations.renderGameExpectationsListView(mainContent, campaign);
      }
    };
  }
};
})();