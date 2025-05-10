// SettlementTracker.js

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
  }
};