// DM's Character Tracker

window.dmCharacterTracker = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.dmCharacters) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.dmCharacters = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns);
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