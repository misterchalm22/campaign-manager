// DM's Character Tracker

// Utility for escaping HTML (use window.modalUtils.escapeHtml if available)
function escapeHtml(unsafe) {
  if (window.modalUtils && window.modalUtils.escapeHtml) return window.modalUtils.escapeHtml(unsafe);
  if (typeof unsafe !== 'string') return '';
  return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

window.dmCharacterTracker = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.dmCharacters) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.dmCharacters = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns);
  },
  renderDMCharacterListView: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>DM's Character Tracker</h2>
      <button class="btn btn-primary" id="add-dmchar-btn">Add Character</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No DM characters yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((char, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>${escapeHtml(char.characterName) || '(No Name)'}</strong> <span class="text-muted small">${escapeHtml(char.playerName) || ''}</span></div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">Class: ${escapeHtml(char.className) || ''} Level: ${escapeHtml(char.level) || ''}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html;
    document.getElementById('add-dmchar-btn').onclick = () => this.renderDMCharacterFormModal(campaign, null);
    container.querySelectorAll('[data-view]').forEach(btn => {
      btn.onclick = () => this.renderDMCharacterEntryView(entries[parseInt(btn.getAttribute('data-view'))], campaign, parseInt(btn.getAttribute('data-view')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this character?')) {
          entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveEntries(campaign, entries);
          this.renderDMCharacterListView(container, campaign);
        }
      };
    });
  },
  renderDMCharacterEntryView: function(char, campaign, idx) {
    let html = `<dl class="row">
      <dt class="col-sm-4">Character's Name:</dt><dd class="col-sm-8">${escapeHtml(char.characterName) || 'N/A'}</dd>
      <dt class="col-sm-4">Player's Name:</dt><dd class="col-sm-8">${escapeHtml(char.playerName) || 'N/A'}</dd>
      <dt class="col-sm-4">Player Motivation:</dt><dd class="col-sm-8">${(char.motivations && char.motivations.length) ? char.motivations.map(escapeHtml).join(', ') : 'N/A'}</dd>
      <dt class="col-sm-4">Notes on Player Expectations:</dt><dd class="col-sm-8"><pre>${escapeHtml(char.playerExpectations) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Class:</dt><dd class="col-sm-8">${escapeHtml(char.className) || 'N/A'}</dd>
      <dt class="col-sm-4">Subclass:</dt><dd class="col-sm-8">${escapeHtml(char.subclass) || 'N/A'}</dd>
      <dt class="col-sm-4">Level:</dt><dd class="col-sm-8">${escapeHtml(char.level) || 'N/A'}</dd>
      <dt class="col-sm-4">Background:</dt><dd class="col-sm-8">${escapeHtml(char.background) || 'N/A'}</dd>
      <dt class="col-sm-4">Species (Race):</dt><dd class="col-sm-8">${escapeHtml(char.species) || 'N/A'}</dd>
      <dt class="col-sm-4">Alignment:</dt><dd class="col-sm-8">${escapeHtml(char.alignment) || 'N/A'}</dd>
      <dt class="col-sm-4">Goals and Ambitions:</dt><dd class="col-sm-8"><pre>${escapeHtml(char.goals) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Quirks and Whims:</dt><dd class="col-sm-8"><pre>${escapeHtml(char.quirks) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Magic Items:</dt><dd class="col-sm-8"><pre>${escapeHtml(char.magicItems) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Character Details:</dt><dd class="col-sm-8"><pre>${escapeHtml(char.details) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Family, Friends, and Foes:</dt><dd class="col-sm-8"><pre>${escapeHtml(char.family) || 'N/A'}</pre></dd>
      <dt class="col-sm-4">Adventure Ideas:</dt><dd class="col-sm-8"><pre>${escapeHtml(char.adventureIdeas) || 'N/A'}</pre></dd>
    </dl>`;
    let footer = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editDMCharFromViewBtn">Edit</button>`;
    window.modalUtils.showModal(`View Character: ${escapeHtml(char.characterName)}`, html, footer);
    document.getElementById('editDMCharFromViewBtn').onclick = () => {
      window.dmCharacterTracker.renderDMCharacterFormModal(campaign, idx, true);
    };
  },
  renderDMCharacterFormModal: function(campaign, idx, isEditFromView = false) {
    const entries = this.getEntries(campaign);
    const motivations = [
      'Acting', 'Exploring', 'Fighting', 'Instigating', 'Optimizing', 'Problem-Solving', 'Socializing', 'Storytelling'
    ];
    const char = idx != null ? {...entries[idx]} : {
      characterName: '',
      playerName: '',
      motivations: [],
      playerExpectations: '',
      className: '',
      subclass: '',
      level: '',
      background: '',
      species: '',
      alignment: '',
      goals: '',
      quirks: '',
      magicItems: '',
      details: '',
      family: '',
      adventureIdeas: ''
    };
    let html = `<form id="dmchar-form-modal">
      <div class="mb-2">
        <label class="form-label">Character's Name</label>
        <input class="form-control" name="characterName" value="${escapeHtml(char.characterName) || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Player's Name</label>
        <input class="form-control" name="playerName" value="${escapeHtml(char.playerName) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Player Motivation</label><br />
        ${motivations.map(m => `<label class="form-check form-check-inline"><input class="form-check-input" type="checkbox" name="motivations" value="${m}"${char.motivations && char.motivations.includes(m) ? ' checked' : ''}> ${m}</label>`).join(' ')}
      </div>
      <div class="mb-2">
        <label class="form-label">Notes on Player Expectations</label>
        <textarea class="form-control" name="playerExpectations">${escapeHtml(char.playerExpectations) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Class</label>
        <input class="form-control" name="className" value="${escapeHtml(char.className) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Subclass</label>
        <input class="form-control" name="subclass" value="${escapeHtml(char.subclass) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Level</label>
        <input class="form-control" name="level" type="number" min="1" value="${escapeHtml(char.level) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Background</label>
        <input class="form-control" name="background" value="${escapeHtml(char.background) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Species (Race)</label>
        <input class="form-control" name="species" value="${escapeHtml(char.species) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Alignment</label>
        <input class="form-control" name="alignment" value="${escapeHtml(char.alignment) || ''}" placeholder="e.g. LG, NG, N, CE" />
      </div>
      <div class="mb-2">
        <label class="form-label">Goals and Ambitions</label>
        <textarea class="form-control" name="goals">${escapeHtml(char.goals) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Quirks and Whims</label>
        <textarea class="form-control" name="quirks">${escapeHtml(char.quirks) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Magic Items</label>
        <textarea class="form-control" name="magicItems">${escapeHtml(char.magicItems) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Character Details</label>
        <textarea class="form-control" name="details">${escapeHtml(char.details) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Family, Friends, and Foes</label>
        <textarea class="form-control" name="family">${escapeHtml(char.family) || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Adventure Ideas</label>
        <textarea class="form-control" name="adventureIdeas">${escapeHtml(char.adventureIdeas) || ''}</textarea>
      </div>
    </form>`;
    let footer = `<button type="button" class="btn btn-secondary" id="cancelDMCharFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveDMCharFormBtn">Save</button>`;
    window.modalUtils.showModal(idx != null ? `Edit Character: ${escapeHtml(char.characterName)}` : 'Add Character', html, footer);
    document.getElementById('cancelDMCharFormBtn').onclick = () => {
      if (isEditFromView && idx != null) {
        window.dmCharacterTracker.renderDMCharacterEntryView(entries[idx], campaign, idx);
      } else {
        window.modalUtils.hideModal();
      }
    };
    document.getElementById('saveDMCharFormBtn').onclick = () => {
      const form = document.getElementById('dmchar-form-modal');
      const newChar = {
        characterName: form.characterName.value.trim(),
        playerName: form.playerName.value.trim(),
        motivations: Array.from(form.querySelectorAll('input[name="motivations"]:checked')).map(cb => cb.value),
        playerExpectations: form.playerExpectations.value.trim(),
        className: form.className.value.trim(),
        subclass: form.subclass.value.trim(),
        level: form.level.value.trim(),
        background: form.background.value.trim(),
        species: form.species.value.trim(),
        alignment: form.alignment.value.trim(),
        goals: form.goals.value.trim(),
        quirks: form.quirks.value.trim(),
        magicItems: form.magicItems.value.trim(),
        details: form.details.value.trim(),
        family: form.family.value.trim(),
        adventureIdeas: form.adventureIdeas.value.trim()
      };
      if (!newChar.characterName) {
        alert('Character Name is required.');
        return;
      }
      if (idx != null) {
        entries[idx] = newChar;
      } else {
        entries.push(newChar);
      }
      window.dmCharacterTracker.saveEntries(campaign, entries);
      window.modalUtils.hideModal();
      // Refresh list view
      const mainContent = document.getElementById('main-content');
      if (mainContent) {
        window.dmCharacterTracker.renderDMCharacterListView(mainContent, campaign);
      }
    };
  },
  renderDMCharacterList: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>DM's Character Tracker</h2>
      <button class="btn btn-primary" id="add-dmchar-btn">Add Character</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No DM characters yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((char, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>${char.characterName || '(No Name)'}</strong> <span class="text-muted small">${char.playerName || ''}</span></div>
            <div>
              <button class="btn btn-sm btn-secondary me-2" data-edit="${idx}">Edit</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">Class: ${char.className || ''} Level: ${char.level || ''}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html + `<div id="dmchar-form-area"></div>`;
    document.getElementById('add-dmchar-btn').onclick = () => this.renderDMCharacterForm(container, campaign);
    container.querySelectorAll('[data-edit]').forEach(btn => {
      btn.onclick = () => this.renderDMCharacterForm(container, campaign, parseInt(btn.getAttribute('data-edit')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this character?')) {
          entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveEntries(campaign, entries);
          this.renderDMCharacterList(container, campaign);
        }
      };
    });
  },
  renderDMCharacterForm: function(container, campaign, idx) {
    const entries = this.getEntries(campaign);
    const motivations = [
      'Acting', 'Exploring', 'Fighting', 'Instigating', 'Optimizing', 'Problem-Solving', 'Socializing', 'Storytelling'
    ];
    const char = idx != null ? {...entries[idx]} : {
      characterName: '',
      playerName: '',
      motivations: [],
      playerExpectations: '',
      className: '',
      subclass: '',
      level: '',
      background: '',
      species: '',
      alignment: '',
      goals: '',
      quirks: '',
      magicItems: '',
      details: '',
      family: '',
      adventureIdeas: ''
    };
    let html = `<form class="card card-body mb-3" id="dmchar-form">
      <div class="mb-2">
        <label class="form-label">Character's Name</label>
        <input class="form-control" name="characterName" value="${char.characterName || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Player's Name</label>
        <input class="form-control" name="playerName" value="${char.playerName || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Player Motivation</label><br />
        ${motivations.map(m => `<label class="form-check form-check-inline"><input class="form-check-input" type="checkbox" name="motivations" value="${m}"${char.motivations && char.motivations.includes(m) ? ' checked' : ''}> ${m}</label>`).join(' ')}
      </div>
      <div class="mb-2">
        <label class="form-label">Notes on Player Expectations</label>
        <textarea class="form-control" name="playerExpectations">${char.playerExpectations || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Class</label>
        <input class="form-control" name="className" value="${char.className || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Subclass</label>
        <input class="form-control" name="subclass" value="${char.subclass || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Level</label>
        <input class="form-control" name="level" type="number" min="1" value="${char.level || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Background</label>
        <input class="form-control" name="background" value="${char.background || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Species (Race)</label>
        <input class="form-control" name="species" value="${char.species || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Alignment</label>
        <input class="form-control" name="alignment" value="${char.alignment || ''}" placeholder="e.g. LG, NG, N, CE" />
      </div>
      <div class="mb-2">
        <label class="form-label">Goals and Ambitions</label>
        <textarea class="form-control" name="goals">${char.goals || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Quirks and Whims</label>
        <textarea class="form-control" name="quirks">${char.quirks || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Magic Items</label>
        <textarea class="form-control" name="magicItems">${char.magicItems || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Character Details</label>
        <textarea class="form-control" name="details">${char.details || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Family, Friends, and Foes</label>
        <textarea class="form-control" name="family">${char.family || ''}</textarea>
      </div>
      <div class="mb-2">
        <label class="form-label">Adventure Ideas</label>
        <textarea class="form-control" name="adventureIdeas">${char.adventureIdeas || ''}</textarea>
      </div>
      <div class="d-flex gap-2">
        <button type="submit" class="btn btn-success">Save</button>
        <button type="button" class="btn btn-secondary" id="cancel-dmchar-btn">Cancel</button>
      </div>
    </form>`;
    document.getElementById('dmchar-form-area').innerHTML = html;
    document.getElementById('cancel-dmchar-btn').onclick = () => {
      this.renderDMCharacterList(container, campaign);
    };
    document.getElementById('dmchar-form').onsubmit = (e) => {
      e.preventDefault();
      const form = e.target;
      const newChar = {
        characterName: form.characterName.value,
        playerName: form.playerName.value,
        motivations: Array.from(form.querySelectorAll('input[name="motivations"]:checked')).map(cb => cb.value),
        playerExpectations: form.playerExpectations.value,
        className: form.className.value,
        subclass: form.subclass.value,
        level: form.level.value,
        background: form.background.value,
        species: form.species.value,
        alignment: form.alignment.value,
        goals: form.goals.value,
        quirks: form.quirks.value,
        magicItems: form.magicItems.value,
        details: form.details.value,
        family: form.family.value,
        adventureIdeas: form.adventureIdeas.value
      };
      if (idx != null) {
        entries[idx] = newChar;
      } else {
        entries.push(newChar);
      }
      this.saveEntries(campaign, entries);
      this.renderDMCharacterList(container, campaign);
    };
  }
};