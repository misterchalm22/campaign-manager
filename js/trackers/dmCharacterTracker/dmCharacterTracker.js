(function() {
// DM's Character Tracker

window.dmCharacterTracker = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.dmCharacters) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.dmCharacters = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns); // Assuming 'allCampaigns' is globally available
  },

  // Main list view
  renderDMCharacterTrackerListView: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>DM's Character Tracker</h2>
      <button class="btn btn-primary" id="add-dm-character-btn">Add DM Character</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No DM-controlled characters yet. Add one to get started!</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((char, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <strong>${window.modalUtils.escapeHtml(char.characterName) || '(Unnamed Character)'}</strong>
              <span class="text-muted small ms-2">(${window.modalUtils.escapeHtml(char.playerName) || 'DM Controlled'})</span>
            </div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view-idx="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete-idx="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted mt-1">
            Class: ${window.modalUtils.escapeHtml(char.className) || 'N/A'} | 
            Level: ${window.modalUtils.escapeHtml(char.level) || 'N/A'} | 
            Species: ${window.modalUtils.escapeHtml(char.species) || 'N/A'}
          </div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html;

    document.getElementById('add-dm-character-btn').onclick = () => {
      this.renderDMCharacterFormModal(container, campaign, null, false);
    };

    container.querySelectorAll('[data-view-idx]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-view-idx'));
        this.renderDMCharacterEntryView(container, campaign, idx);
      };
    });

    container.querySelectorAll('[data-delete-idx]').forEach(btn => {
      btn.onclick = () => {
        const idx = parseInt(btn.getAttribute('data-delete-idx'));
        const charToDelete = entries[idx]; // Get reference before modifying array
        if (confirm(`Are you sure you want to delete the character: "${window.modalUtils.escapeHtml(charToDelete.characterName)}"?`)) {
          let currentEntries = this.getEntries(campaign); // Re-fetch for safety
          currentEntries.splice(idx, 1);
          this.saveEntries(campaign, currentEntries);
          this.renderDMCharacterTrackerListView(container, campaign); 
        }
      };
    });
  },

  // Read-only view for a single DM character (modal)
  renderDMCharacterEntryView: function(listContainer, campaign, idx) {
    const entries = this.getEntries(campaign);
    const char = entries[idx];

    if (!char) {
      console.error("DM Character not found for view at index:", idx);
      window.modalUtils.hideModal();
      window.modalUtils.showModal("Error", "<p>Could not find the selected DM character.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
      this.renderDMCharacterTrackerListView(listContainer, campaign);
      return;
    }
    
    const motivationsHtml = (char.motivations && char.motivations.length) 
        ? char.motivations.map(m => `<span class="badge bg-secondary me-1">${window.modalUtils.escapeHtml(m)}</span>`).join('') 
        : 'N/A';

    let contentHtml = `<dl class="row">
      <dt class="col-sm-3">Character Name:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(char.characterName) || 'N/A'}</dd>
      <dt class="col-sm-3">Player Name:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(char.playerName) || 'DM Controlled'}</dd>
      <dt class="col-sm-3">Class:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(char.className) || 'N/A'}</dd>
      <dt class="col-sm-3">Subclass:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(char.subclass) || 'N/A'}</dd>
      <dt class="col-sm-3">Level:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(char.level) || 'N/A'}</dd>
      <dt class="col-sm-3">Species (Race):</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(char.species) || 'N/A'}</dd>
      <dt class="col-sm-3">Background:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(char.background) || 'N/A'}</dd>
      <dt class="col-sm-3">Alignment:</dt><dd class="col-sm-9">${window.modalUtils.escapeHtml(char.alignment) || 'N/A'}</dd>
      <dt class="col-sm-3">Motivations:</dt><dd class="col-sm-9">${motivationsHtml}</dd>
      <dt class="col-sm-12 mt-2">Player Expectations:</dt><dd class="col-sm-12"><pre>${window.modalUtils.escapeHtml(char.playerExpectations) || 'N/A'}</pre></dd>
      <dt class="col-sm-12 mt-2">Goals & Ambitions:</dt><dd class="col-sm-12"><pre>${window.modalUtils.escapeHtml(char.goals) || 'N/A'}</pre></dd>
      <dt class="col-sm-12 mt-2">Quirks & Whims:</dt><dd class="col-sm-12"><pre>${window.modalUtils.escapeHtml(char.quirks) || 'N/A'}</pre></dd>
      <dt class="col-sm-12 mt-2">Magic Items:</dt><dd class="col-sm-12"><pre>${window.modalUtils.escapeHtml(char.magicItems) || 'N/A'}</pre></dd>
      <dt class="col-sm-12 mt-2">Character Details:</dt><dd class="col-sm-12"><pre>${window.modalUtils.escapeHtml(char.details) || 'N/A'}</pre></dd>
      <dt class="col-sm-12 mt-2">Family, Friends & Foes:</dt><dd class="col-sm-12"><pre>${window.modalUtils.escapeHtml(char.family) || 'N/A'}</pre></dd>
      <dt class="col-sm-12 mt-2">Adventure Ideas:</dt><dd class="col-sm-12"><pre>${window.modalUtils.escapeHtml(char.adventureIdeas) || 'N/A'}</pre></dd>
    </dl>`;
    
    let footerHtml = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editDMCharacterFromViewBtn">Edit</button>`;
    
    window.modalUtils.showModal(`View DM Character: ${window.modalUtils.escapeHtml(char.characterName)}`, contentHtml, footerHtml);
    
    const editButton = document.getElementById('editDMCharacterFromViewBtn');
    if (editButton) {
      editButton.onclick = () => {
        this.renderDMCharacterFormModal(listContainer, campaign, idx, true);
      };
    }
  },

  // Form modal for adding/editing a DM character
  renderDMCharacterFormModal: function(listContainer, campaign, idx, isEditFromView = false) {
    const entries = this.getEntries(campaign);
    const isEditMode = idx !== null && idx !== undefined;
    let charToEdit;
     const motivationsList = [
      'Acting', 'Exploring', 'Fighting', 'Instigating', 'Optimizing', 'Problem-Solving', 'Socializing', 'Storytelling'
    ];

    if (isEditMode) {
      if (idx < 0 || idx >= entries.length) {
        console.error("DM Character index out of bounds for edit:", idx);
        window.modalUtils.hideModal();
        window.modalUtils.showModal("Error", "<p>Could not find DM character to edit.</p>", `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>`);
        this.renderDMCharacterTrackerListView(listContainer, campaign);
        return;
      }
      charToEdit = {...entries[idx]}; // Create a copy to edit
      if (!charToEdit.motivations) charToEdit.motivations = []; // Ensure motivations is an array
    } else {
      charToEdit = { characterName: '', playerName: '', motivations: [], playerExpectations: '', className: '', subclass: '', level: '1', background: '', species: '', alignment: '', goals: '', quirks: '', magicItems: '', details: '', family: '', adventureIdeas: '' };
    }
    
    const modalTitle = isEditMode ? `Edit DM Character: ${window.modalUtils.escapeHtml(charToEdit.characterName)}` : 'Add New DM Character';

    let motivationsCheckboxesHtml = motivationsList.map(m => `
      <div class="form-check form-check-inline">
        <input class="form-check-input" type="checkbox" name="motivations" value="${m}" id="motivation-${m}" ${charToEdit.motivations.includes(m) ? 'checked' : ''}>
        <label class="form-check-label" for="motivation-${m}">${m}</label>
      </div>`).join('');

    let formHtml = `<form id="dm-character-form" novalidate>
      <div class="row">
        <div class="col-md-6 mb-3">
          <label for="dmc-characterName" class="form-label">Character's Name</label>
          <input type="text" class="form-control" id="dmc-characterName" name="characterName" value="${window.modalUtils.escapeHtml(charToEdit.characterName)}" required />
          <div class="invalid-feedback">Character Name is required.</div>
        </div>
        <div class="col-md-6 mb-3">
          <label for="dmc-playerName" class="form-label">Player's Name (or "DM")</label>
          <input type="text" class="form-control" id="dmc-playerName" name="playerName" value="${window.modalUtils.escapeHtml(charToEdit.playerName)}" />
        </div>
      </div>
      <div class="row">
        <div class="col-md-6 mb-3">
          <label for="dmc-className" class="form-label">Class</label>
          <input type="text" class="form-control" id="dmc-className" name="className" value="${window.modalUtils.escapeHtml(charToEdit.className)}" />
        </div>
        <div class="col-md-3 mb-3">
          <label for="dmc-subclass" class="form-label">Subclass</label>
          <input type="text" class="form-control" id="dmc-subclass" name="subclass" value="${window.modalUtils.escapeHtml(charToEdit.subclass)}" />
        </div>
        <div class="col-md-3 mb-3">
          <label for="dmc-level" class="form-label">Level</label>
          <input type="number" class="form-control" id="dmc-level" name="level" value="${window.modalUtils.escapeHtml(charToEdit.level)}" min="1" />
        </div>
      </div>
      <div class="row">
        <div class="col-md-6 mb-3">
          <label for="dmc-species" class="form-label">Species (Race)</label>
          <input type="text" class="form-control" id="dmc-species" name="species" value="${window.modalUtils.escapeHtml(charToEdit.species)}" />
        </div>
        <div class="col-md-6 mb-3">
          <label for="dmc-background" class="form-label">Background</label>
          <input type="text" class="form-control" id="dmc-background" name="background" value="${window.modalUtils.escapeHtml(charToEdit.background)}" />
        </div>
      </div>
       <div class="mb-3">
          <label for="dmc-alignment" class="form-label">Alignment</label>
          <input type="text" class="form-control" id="dmc-alignment" name="alignment" value="${window.modalUtils.escapeHtml(charToEdit.alignment)}" placeholder="e.g. LG, N, CE" />
        </div>
      <div class="mb-3">
        <label class="form-label">Player Motivation(s)</label>
        <div>${motivationsCheckboxesHtml}</div>
      </div>
      <div class="mb-3">
        <label for="dmc-playerExpectations" class="form-label">Player Expectations Notes</label>
        <textarea class="form-control" id="dmc-playerExpectations" name="playerExpectations" rows="2">${window.modalUtils.escapeHtml(charToEdit.playerExpectations)}</textarea>
      </div>
      <div class="mb-3">
        <label for="dmc-goals" class="form-label">Goals & Ambitions</label>
        <textarea class="form-control" id="dmc-goals" name="goals" rows="3">${window.modalUtils.escapeHtml(charToEdit.goals)}</textarea>
      </div>
      <div class="mb-3">
        <label for="dmc-quirks" class="form-label">Quirks & Whims</label>
        <textarea class="form-control" id="dmc-quirks" name="quirks" rows="2">${window.modalUtils.escapeHtml(charToEdit.quirks)}</textarea>
      </div>
      <div class="mb-3">
        <label for="dmc-magicItems" class="form-label">Magic Items</label>
        <textarea class="form-control" id="dmc-magicItems" name="magicItems" rows="3">${window.modalUtils.escapeHtml(charToEdit.magicItems)}</textarea>
      </div>
      <div class="mb-3">
        <label for="dmc-details" class="form-label">Character Details (Appearance, Backstory Snippets)</label>
        <textarea class="form-control" id="dmc-details" name="details" rows="4">${window.modalUtils.escapeHtml(charToEdit.details)}</textarea>
      </div>
      <div class="mb-3">
        <label for="dmc-family" class="form-label">Family, Friends & Foes</label>
        <textarea class="form-control" id="dmc-family" name="family" rows="3">${window.modalUtils.escapeHtml(charToEdit.family)}</textarea>
      </div>
      <div class="mb-3">
        <label for="dmc-adventureIdeas" class="form-label">Adventure Ideas / Plot Hooks</label>
        <textarea class="form-control" id="dmc-adventureIdeas" name="adventureIdeas" rows="3">${window.modalUtils.escapeHtml(charToEdit.adventureIdeas)}</textarea>
      </div>
    </form>`;
    
    let footerHtml = `<button type="button" class="btn btn-secondary" id="cancelDMCharacterFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveDMCharacterFormBtn">Save</button>`;
      
    window.modalUtils.showModal(modalTitle, formHtml, footerHtml);

    const form = document.getElementById('dm-character-form');
    const nameInput = form.querySelector('#dmc-characterName');

    document.getElementById('saveDMCharacterFormBtn').onclick = () => {
      const charName = nameInput.value.trim();
      if (!charName) {
        nameInput.classList.add('is-invalid');
        form.classList.add('was-validated');
        return;
      }
      nameInput.classList.remove('is-invalid');
      form.classList.remove('was-validated');

      const selectedMotivations = Array.from(form.querySelectorAll('input[name="motivations"]:checked')).map(cb => cb.value);

      const updatedCharData = {
        characterName: charName,
        playerName: form.querySelector('#dmc-playerName').value.trim(),
        className: form.querySelector('#dmc-className').value.trim(),
        subclass: form.querySelector('#dmc-subclass').value.trim(),
        level: form.querySelector('#dmc-level').value.trim(),
        species: form.querySelector('#dmc-species').value.trim(),
        background: form.querySelector('#dmc-background').value.trim(),
        alignment: form.querySelector('#dmc-alignment').value.trim(),
        motivations: selectedMotivations,
        playerExpectations: form.querySelector('#dmc-playerExpectations').value.trim(),
        goals: form.querySelector('#dmc-goals').value.trim(),
        quirks: form.querySelector('#dmc-quirks').value.trim(),
        magicItems: form.querySelector('#dmc-magicItems').value.trim(),
        details: form.querySelector('#dmc-details').value.trim(),
        family: form.querySelector('#dmc-family').value.trim(),
        adventureIdeas: form.querySelector('#dmc-adventureIdeas').value.trim()
      };

      let currentEntries = this.getEntries(campaign);
      if (isEditMode) {
        currentEntries[idx] = updatedCharData;
      } else {
        currentEntries.push(updatedCharData);
      }
      this.saveEntries(campaign, currentEntries);
      window.modalUtils.hideModal();
      this.renderDMCharacterTrackerListView(listContainer, campaign); 
    };

    document.getElementById('cancelDMCharacterFormBtn').onclick = () => {
      if (isEditFromView && isEditMode) {
         const latestEntries = this.getEntries(campaign);
         if (idx < latestEntries.length) { // Check if entry still exists
            this.renderDMCharacterEntryView(listContainer, campaign, idx);
         } else {
            window.modalUtils.hideModal();
            this.renderDMCharacterTrackerListView(listContainer, campaign);
         }
      } else {
        window.modalUtils.hideModal();
      }
    };
  }
};

// Register with main UI rendering system
window.ui = window.ui || {};
window.ui.renderTrackerViews = window.ui.renderTrackerViews || {};
window.ui.renderTrackerViews["DM's Character Tracker"] = function(container, campaign) {
  window.dmCharacterTracker.renderDMCharacterTrackerListView(container, campaign);
};

})();