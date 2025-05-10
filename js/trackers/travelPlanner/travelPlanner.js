// Logic for Travel Planner tracker

// Utility for escaping HTML (use window.modalUtils.escapeHtml if available)
function escapeHtml(unsafe) {
  if (window.modalUtils && window.modalUtils.escapeHtml) return window.modalUtils.escapeHtml(unsafe);
  if (typeof unsafe !== 'string') return '';
  return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

window.travelPlanner = {
  getEntries: function(campaign) {
    return (campaign.trackers && campaign.trackers.travelPlans) || [];
  },
  saveEntries: function(campaign, entries) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.travelPlans = entries;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns);
  },
  renderTravelList: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Travel Planner</h2>
      <button class="btn btn-primary" id="add-travel-btn">Add Journey</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No journeys yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((journey, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>${journey.name || '(No Name)'}</strong> <span class="text-muted small">${journey.origin || ''} → ${journey.destination || ''}</span></div>
            <div>
              <button class="btn btn-sm btn-secondary me-2" data-edit="${idx}">Edit</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">Stages: ${journey.stages ? journey.stages.length : 0}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html + `<div id="travel-form-area"></div>`;
    document.getElementById('add-travel-btn').onclick = () => this.renderTravelForm(container, campaign);
    container.querySelectorAll('[data-edit]').forEach(btn => {
      btn.onclick = () => this.renderTravelForm(container, campaign, parseInt(btn.getAttribute('data-edit')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this journey?')) {
          entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveEntries(campaign, entries);
          this.renderTravelList(container, campaign);
        }
      };
    });
  },
  renderTravelForm: function(container, campaign, idx) {
    const entries = this.getEntries(campaign);
    const journey = idx != null ? {...entries[idx], stages: [...(entries[idx].stages||[])]} : {
      name: '', origin: '', destination: '', stages: []
    };
    let html = `<form class="card card-body mb-3" id="travel-form">
      <div class="mb-2">
        <label class="form-label">Journey Name</label>
        <input class="form-control" name="name" value="${journey.name || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Origin</label>
        <input class="form-control" name="origin" value="${journey.origin || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Destination</label>
        <input class="form-control" name="destination" value="${journey.destination || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Stages</label>
        <div id="stages-list"></div>
        <button type="button" class="btn btn-sm btn-outline-primary mt-2" id="add-stage-btn">Add Stage</button>
      </div>
      <div class="d-flex gap-2">
        <button type="submit" class="btn btn-success">Save</button>
        <button type="button" class="btn btn-secondary" id="cancel-travel-btn">Cancel</button>
      </div>
    </form>`;
    document.getElementById('travel-form-area').innerHTML = html;
    // Render stages
    const renderStages = () => {
      const list = document.getElementById('stages-list');
      if (!journey.stages) journey.stages = [];
      let sHtml = '';
      journey.stages.forEach((stage, i) => {
        sHtml += `<div class="card card-body mb-2">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <strong>Stage ${i+1}</strong>
            <button type="button" class="btn btn-outline-danger btn-sm" data-remove-stage="${i}">Remove</button>
          </div>
          <div class="mb-1"><label class="form-label">Start</label><input class="form-control" name="start" value="${stage.start || ''}" /></div>
          <div class="mb-1"><label class="form-label">End</label><input class="form-control" name="end" value="${stage.end || ''}" /></div>
          <div class="mb-1"><label class="form-label">Distance</label><input class="form-control" name="distance" value="${stage.distance || ''}" /></div>
          <div class="mb-1"><label class="form-label">Terrain</label><input class="form-control" name="terrain" value="${stage.terrain || ''}" /></div>
          <div class="mb-1"><label class="form-label">Weather</label><input class="form-control" name="weather" value="${stage.weather || ''}" /></div>
          <div class="mb-1"><label class="form-label">Pace</label>
            <select class="form-select" name="pace">
              <option value="Fast"${stage.pace==="Fast"?" selected":""}>Fast</option>
              <option value="Normal"${stage.pace==="Normal"?" selected":""}>Normal</option>
              <option value="Slow"${stage.pace==="Slow"?" selected":""}>Slow</option>
            </select>
          </div>
          <div class="mb-1"><label class="form-label">Travel Time</label><input class="form-control" name="travelTime" value="${stage.travelTime || ''}" placeholder="e.g. 3" />
            <select class="form-select mt-1" name="travelTimeUnit">
              <option value="days"${stage.travelTimeUnit==="days"?" selected":""}>days</option>
              <option value="hrs"${stage.travelTimeUnit==="hrs"?" selected":""}>hrs</option>
            </select>
          </div>
          <div class="mb-1"><label class="form-label">Narrative Notes</label><textarea class="form-control" name="narrative">${stage.narrative || ''}</textarea></div>
          <div class="mb-1"><label class="form-label">Challenges</label><textarea class="form-control" name="challenges">${stage.challenges || ''}</textarea></div>
          <div class="mb-1"><label class="form-label">Elapsed Time</label><input class="form-control" name="elapsedTime" value="${stage.elapsedTime || ''}" /></div>
        </div>`;
      });
      list.innerHTML = sHtml;
      list.querySelectorAll('[data-remove-stage]').forEach(btn => {
        btn.onclick = () => {
          journey.stages.splice(parseInt(btn.getAttribute('data-remove-stage')), 1);
          renderStages();
        };
      });
      // Update stage values on input
      list.querySelectorAll('.card').forEach((card, i) => {
        card.querySelector('input[name="start"]').oninput = e => { journey.stages[i].start = e.target.value; };
        card.querySelector('input[name="end"]').oninput = e => { journey.stages[i].end = e.target.value; };
        card.querySelector('input[name="distance"]').oninput = e => { journey.stages[i].distance = e.target.value; };
        card.querySelector('input[name="terrain"]').oninput = e => { journey.stages[i].terrain = e.target.value; };
        card.querySelector('input[name="weather"]').oninput = e => { journey.stages[i].weather = e.target.value; };
        card.querySelector('select[name="pace"]').onchange = e => { journey.stages[i].pace = e.target.value; };
        card.querySelector('input[name="travelTime"]').oninput = e => { journey.stages[i].travelTime = e.target.value; };
        card.querySelector('select[name="travelTimeUnit"]').onchange = e => { journey.stages[i].travelTimeUnit = e.target.value; };
        card.querySelector('textarea[name="narrative"]').oninput = e => { journey.stages[i].narrative = e.target.value; };
        card.querySelector('textarea[name="challenges"]').oninput = e => { journey.stages[i].challenges = e.target.value; };
        card.querySelector('input[name="elapsedTime"]').oninput = e => { journey.stages[i].elapsedTime = e.target.value; };
      });
    };
    renderStages();
    document.getElementById('add-stage-btn').onclick = () => {
      journey.stages.push({ start: '', end: '', distance: '', terrain: '', weather: '', pace: 'Normal', travelTime: '', travelTimeUnit: 'days', narrative: '', challenges: '', elapsedTime: '' });
      renderStages();
    };
    document.getElementById('cancel-travel-btn').onclick = () => {
      this.renderTravelList(container, campaign);
    };
    document.getElementById('travel-form').onsubmit = (e) => {
      e.preventDefault();
      const form = e.target;
      const newJourney = {
        name: form.name.value,
        origin: form.origin.value,
        destination: form.destination.value,
        stages: journey.stages
      };
      if (idx != null) {
        entries[idx] = newJourney;
      } else {
        entries.push(newJourney);
      };
      this.saveEntries(campaign, entries);
      this.renderTravelList(container, campaign);
    };
  },
  renderTravelPlannerListView: function(container, campaign) {
    const entries = this.getEntries(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Travel Planner</h2>
      <button class="btn btn-primary" id="add-travel-btn">Add Journey</button>
    </div>`;
    if (entries.length === 0) {
      html += '<div class="alert alert-info">No journeys yet.</div>';
    } else {
      html += '<div class="list-group mb-3">';
      entries.forEach((journey, idx) => {
        html += `<div class="list-group-item">
          <div class="d-flex justify-content-between align-items-center">
            <div><strong>${escapeHtml(journey.name) || '(No Name)'}</strong> <span class="text-muted small">${escapeHtml(journey.origin) || ''} → ${escapeHtml(journey.destination) || ''}</span></div>
            <div>
              <button class="btn btn-sm btn-info me-2" data-view="${idx}">View Details</button>
              <button class="btn btn-sm btn-danger" data-delete="${idx}">Delete</button>
            </div>
          </div>
          <div class="small text-muted">Stages: ${journey.stages ? journey.stages.length : 0}</div>
        </div>`;
      });
      html += '</div>';
    }
    container.innerHTML = html;
    document.getElementById('add-travel-btn').onclick = () => this.renderTravelPlannerFormModal(campaign, null);
    container.querySelectorAll('[data-view]').forEach(btn => {
      btn.onclick = () => this.renderTravelPlannerEntryView(entries[parseInt(btn.getAttribute('data-view'))], campaign, parseInt(btn.getAttribute('data-view')));
    });
    container.querySelectorAll('[data-delete]').forEach(btn => {
      btn.onclick = () => {
        if (confirm('Delete this journey?')) {
          entries.splice(parseInt(btn.getAttribute('data-delete')), 1);
          this.saveEntries(campaign, entries);
          this.renderTravelPlannerListView(container, campaign);
        }
      };
    });
  },
  renderTravelPlannerEntryView: function(journey, campaign, idx) {
    let html = `<dl class="row">
      <dt class="col-sm-4">Journey Name:</dt><dd class="col-sm-8">${escapeHtml(journey.name) || 'N/A'}</dd>
      <dt class="col-sm-4">Origin:</dt><dd class="col-sm-8">${escapeHtml(journey.origin) || 'N/A'}</dd>
      <dt class="col-sm-4">Destination:</dt><dd class="col-sm-8">${escapeHtml(journey.destination) || 'N/A'}</dd>
      <dt class="col-sm-4">Stages:</dt><dd class="col-sm-8">`;
    if (journey.stages && journey.stages.length) {
      html += '<ol>' + journey.stages.map((stage, i) => `
        <li>
          <strong>Stage ${i+1}</strong><br/>
          Start: ${escapeHtml(stage.start) || 'N/A'}<br/>
          End: ${escapeHtml(stage.end) || 'N/A'}<br/>
          Distance: ${escapeHtml(stage.distance) || 'N/A'}<br/>
          Terrain: ${escapeHtml(stage.terrain) || 'N/A'}<br/>
          Weather: ${escapeHtml(stage.weather) || 'N/A'}<br/>
          Pace: ${escapeHtml(stage.pace) || 'N/A'}<br/>
          Travel Time: ${escapeHtml(stage.travelTime) || ''} ${escapeHtml(stage.travelTimeUnit) || ''}<br/>
          Narrative Notes: <pre>${escapeHtml(stage.narrative) || ''}</pre>
          Challenges: <pre>${escapeHtml(stage.challenges) || ''}</pre>
          Elapsed Time: ${escapeHtml(stage.elapsedTime) || 'N/A'}
        </li>`).join('') + '</ol>';
    } else {
      html += 'N/A';
    }
    html += `</dd></dl>`;
    let footer = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editTravelFromViewBtn">Edit</button>`;
    window.modalUtils.showModal(`View Journey: ${escapeHtml(journey.name)}`, html, footer);
    document.getElementById('editTravelFromViewBtn').onclick = () => {
      window.travelPlanner.renderTravelPlannerFormModal(campaign, idx, true);
    };
  },
  renderTravelPlannerFormModal: function(campaign, idx, isEditFromView = false) {
    const entries = this.getEntries(campaign);
    const journey = idx != null ? {...entries[idx], stages: [...(entries[idx].stages||[])]} : {
      name: '', origin: '', destination: '', stages: []
    };
    let html = `<form id="travel-form-modal">
      <div class="mb-2">
        <label class="form-label">Journey Name</label>
        <input class="form-control" name="name" value="${escapeHtml(journey.name) || ''}" required />
      </div>
      <div class="mb-2">
        <label class="form-label">Origin</label>
        <input class="form-control" name="origin" value="${escapeHtml(journey.origin) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Destination</label>
        <input class="form-control" name="destination" value="${escapeHtml(journey.destination) || ''}" />
      </div>
      <div class="mb-2">
        <label class="form-label">Stages</label>
        <div id="stages-list-modal"></div>
        <button type="button" class="btn btn-sm btn-outline-primary mt-2" id="add-stage-btn-modal">Add Stage</button>
      </div>
    </form>`;
    let footer = `<button type="button" class="btn btn-secondary" id="cancelTravelFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveTravelFormBtn">Save</button>`;
    window.modalUtils.showModal(idx != null ? `Edit Journey: ${escapeHtml(journey.name)}` : 'Add Journey', html, footer);
    // Stages logic
    function renderStages() {
      const list = document.getElementById('stages-list-modal');
      if (!journey.stages) journey.stages = [];
      let sHtml = '';
      journey.stages.forEach((stage, i) => {
        sHtml += `<div class="card card-body mb-2">
          <div class="d-flex justify-content-between align-items-center mb-1">
            <strong>Stage ${i+1}</strong>
            <button type="button" class="btn btn-outline-danger btn-sm" data-remove-stage="${i}">Remove</button>
          </div>
          <div class="mb-1"><label class="form-label">Start</label><input class="form-control" name="start" value="${escapeHtml(stage.start) || ''}" /></div>
          <div class="mb-1"><label class="form-label">End</label><input class="form-control" name="end" value="${escapeHtml(stage.end) || ''}" /></div>
          <div class="mb-1"><label class="form-label">Distance</label><input class="form-control" name="distance" value="${escapeHtml(stage.distance) || ''}" /></div>
          <div class="mb-1"><label class="form-label">Terrain</label><input class="form-control" name="terrain" value="${escapeHtml(stage.terrain) || ''}" /></div>
          <div class="mb-1"><label class="form-label">Weather</label><input class="form-control" name="weather" value="${escapeHtml(stage.weather) || ''}" /></div>
          <div class="mb-1"><label class="form-label">Pace</label>
            <select class="form-select" name="pace">
              <option value="Fast"${stage.pace==="Fast"?" selected":""}>Fast</option>
              <option value="Normal"${stage.pace==="Normal"?" selected":""}>Normal</option>
              <option value="Slow"${stage.pace==="Slow"?" selected":""}>Slow</option>
            </select>
          </div>
          <div class="mb-1"><label class="form-label">Travel Time</label><input class="form-control" name="travelTime" value="${escapeHtml(stage.travelTime) || ''}" placeholder="e.g. 3" />
            <select class="form-select mt-1" name="travelTimeUnit">
              <option value="days"${stage.travelTimeUnit==="days"?" selected":""}>days</option>
              <option value="hrs"${stage.travelTimeUnit==="hrs"?" selected":""}>hrs</option>
            </select>
          </div>
          <div class="mb-1"><label class="form-label">Narrative Notes</label><textarea class="form-control" name="narrative">${escapeHtml(stage.narrative) || ''}</textarea></div>
          <div class="mb-1"><label class="form-label">Challenges</label><textarea class="form-control" name="challenges">${escapeHtml(stage.challenges) || ''}</textarea></div>
          <div class="mb-1"><label class="form-label">Elapsed Time</label><input class="form-control" name="elapsedTime" value="${escapeHtml(stage.elapsedTime) || ''}" /></div>
        </div>`;
      });
      list.innerHTML = sHtml;
      list.querySelectorAll('[data-remove-stage]').forEach(btn => {
        btn.onclick = () => {
          journey.stages.splice(parseInt(btn.getAttribute('data-remove-stage')), 1);
          renderStages();
        };
      });
      // Update stage values on input
      list.querySelectorAll('.card').forEach((card, i) => {
        card.querySelector('input[name="start"]').oninput = e => { journey.stages[i].start = e.target.value; };
        card.querySelector('input[name="end"]').oninput = e => { journey.stages[i].end = e.target.value; };
        card.querySelector('input[name="distance"]').oninput = e => { journey.stages[i].distance = e.target.value; };
        card.querySelector('input[name="terrain"]').oninput = e => { journey.stages[i].terrain = e.target.value; };
        card.querySelector('input[name="weather"]').oninput = e => { journey.stages[i].weather = e.target.value; };
        card.querySelector('select[name="pace"]').onchange = e => { journey.stages[i].pace = e.target.value; };
        card.querySelector('input[name="travelTime"]').oninput = e => { journey.stages[i].travelTime = e.target.value; };
        card.querySelector('select[name="travelTimeUnit"]').onchange = e => { journey.stages[i].travelTimeUnit = e.target.value; };
        card.querySelector('textarea[name="narrative"]').oninput = e => { journey.stages[i].narrative = e.target.value; };
        card.querySelector('textarea[name="challenges"]').oninput = e => { journey.stages[i].challenges = e.target.value; };
        card.querySelector('input[name="elapsedTime"]').oninput = e => { journey.stages[i].elapsedTime = e.target.value; };
      });
    }
    renderStages();
    document.getElementById('add-stage-btn-modal').onclick = () => {
      journey.stages.push({ start: '', end: '', distance: '', terrain: '', weather: '', pace: 'Normal', travelTime: '', travelTimeUnit: 'days', narrative: '', challenges: '', elapsedTime: '' });
      renderStages();
    };
    document.getElementById('cancelTravelFormBtn').onclick = () => {
      if (isEditFromView && idx != null) {
        window.travelPlanner.renderTravelPlannerEntryView(entries[idx], campaign, idx);
      } else {
        window.modalUtils.hideModal();
      }
    };
    document.getElementById('saveTravelFormBtn').onclick = () => {
      const form = document.getElementById('travel-form-modal');
      const newJourney = {
        name: form.name.value.trim(),
        origin: form.origin.value.trim(),
        destination: form.destination.value.trim(),
        stages: journey.stages
      };
      if (!newJourney.name) {
        alert('Journey Name is required.');
        return;
      }
      if (idx != null) {
        entries[idx] = newJourney;
      } else {
        entries.push(newJourney);
      }
      window.travelPlanner.saveEntries(campaign, entries);
      window.modalUtils.hideModal();
      // Refresh list view
      const mainContent = document.getElementById('main-content');
      if (mainContent) {
        window.travelPlanner.renderTravelPlannerListView(mainContent, campaign);
      }
    };
  }
};