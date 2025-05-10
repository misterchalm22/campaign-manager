// Magic Item Tracker

// Utility for escaping HTML (use window.modalUtils.escapeHtml if available)
function escapeHtml(unsafe) {
  if (window.modalUtils && window.modalUtils.escapeHtml) return window.modalUtils.escapeHtml(unsafe);
  if (typeof unsafe !== 'string') return '';
  return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

// Logic for Magic Item Tracker
window.magicItemTracker = {
  getTracker: function(campaign) {
    return (campaign.trackers && campaign.trackers.magicItemTracker) || {
      tiers: [
        { name: 'Levels 1-4', rarities: { Common: [], Uncommon: [], Rare: [], 'Very Rare': [], Legendary: [] } },
        { name: 'Levels 5-10', rarities: { Common: [], Uncommon: [], Rare: [], 'Very Rare': [], Legendary: [] } },
        { name: 'Levels 11-16', rarities: { Common: [], Uncommon: [], Rare: [], 'Very Rare': [], Legendary: [] } },
        { name: 'Levels 17-20', rarities: { Common: [], Uncommon: [], Rare: [], 'Very Rare': [], Legendary: [] } }
      ]
    };
  },
  saveTracker: function(campaign, tracker) {
    campaign.trackers = campaign.trackers || {};
    campaign.trackers.magicItemTracker = tracker;
    window.dataManager.saveCampaignsToLocalStorage(allCampaigns);
  },
  renderMagicItemTracker: function(container, campaign) {
    const tracker = this.getTracker(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Magic Item Tracker</h2>
      <button class="btn btn-primary" id="edit-magic-items-btn">Edit</button>
    </div>`;
    tracker.tiers.forEach((tier, tIdx) => {
      html += `<div class="card card-body mb-3">
        <h4>${tier.name}</h4>`;
      Object.keys(tier.rarities).forEach(rarity => {
        const items = tier.rarities[rarity] || [];
        html += `<div class="mb-2">
          <strong>${rarity}</strong> <span class="text-muted small">(${items.length} item${items.length !== 1 ? 's' : ''})</span>
          <ul class="list-group">`;
        if (items.length === 0) {
          html += `<li class="list-group-item text-muted">No items</li>`;
        } else {
          items.forEach(item => {
            html += `<li class="list-group-item">${item}</li>`;
          });
        }
        html += `</ul></div>`;
      });
      html += `</div>`;
    });
    container.innerHTML = html + `<div id="magic-item-form-area"></div>`;
    document.getElementById('edit-magic-items-btn').onclick = () => this.renderMagicItemForm(container, campaign);
  },
  renderMagicItemForm: function(container, campaign) {
    const tracker = JSON.parse(JSON.stringify(this.getTracker(campaign)));
    let html = `<form class="card card-body mb-3" id="magic-item-form">
      <h3>Edit Magic Item Tracker</h3>`;
    tracker.tiers.forEach((tier, tIdx) => {
      html += `<div class="mb-3 border p-2">
        <h5>${tier.name}</h5>`;
      Object.keys(tier.rarities).forEach(rarity => {
        html += `<div class="mb-2">
          <label class="form-label"><strong>${rarity}</strong></label>
          <div id="tier${tIdx}-rarity-${rarity.replace(/\s/g, '')}-list"></div>
          <button type="button" class="btn btn-sm btn-outline-primary mt-1" data-add="${tIdx}|${rarity}">Add Item</button>
        </div>`;
      });
      html += `</div>`;
    });
    html += `<div class="d-flex gap-2">
      <button type="submit" class="btn btn-success">Save</button>
      <button type="button" class="btn btn-secondary" id="cancel-magic-item-btn">Cancel</button>
    </div></form>`;
    document.getElementById('magic-item-form-area').innerHTML = html;
    // Render item lists
    tracker.tiers.forEach((tier, tIdx) => {
      Object.keys(tier.rarities).forEach(rarity => {
        const listId = `tier${tIdx}-rarity-${rarity.replace(/\s/g, '')}-list`;
        const listDiv = document.getElementById(listId);
        function renderList() {
          let lHtml = '';
          tier.rarities[rarity].forEach((item, i) => {
            lHtml += `<div class="input-group mb-1">
              <input class="form-control" value="${item}" data-item-input="${tIdx}|${rarity}|${i}" />
              <button type="button" class="btn btn-outline-danger btn-sm" data-remove="${tIdx}|${rarity}|${i}">Remove</button>
            </div>`;
          });
          listDiv.innerHTML = lHtml;
          // Remove handlers
          listDiv.querySelectorAll('[data-remove]').forEach(btn => {
            btn.onclick = () => {
              const [tierIdx, rar, idx] = btn.getAttribute('data-remove').split('|');
              tracker.tiers[tierIdx].rarities[rar].splice(idx, 1);
              renderList();
            };
          });
          // Input handlers
          listDiv.querySelectorAll('[data-item-input]').forEach(input => {
            input.oninput = e => {
              const [tierIdx, rar, idx] = input.getAttribute('data-item-input').split('|');
              tracker.tiers[tierIdx].rarities[rar][idx] = e.target.value;
            };
          });
        }
        renderList();
        // Add handler
        const addBtn = container.querySelector(`[data-add="${tIdx}|${rarity}"]`);
        if (addBtn) {
          addBtn.onclick = () => {
            tier.rarities[rarity].push('');
            renderList();
          };
        }
      });
    });
    document.getElementById('cancel-magic-item-btn').onclick = () => {
      this.renderMagicItemTracker(container, campaign);
    };
    document.getElementById('magic-item-form').onsubmit = (e) => {
      e.preventDefault();
      this.saveTracker(campaign, tracker);
      this.renderMagicItemTracker(container, campaign);
    };
  },
  renderMagicItemTrackerListView: function(container, campaign) {
    const tracker = this.getTracker(campaign);
    let html = `<div class="d-flex justify-content-between align-items-center mb-3">
      <h2>Magic Item Tracker</h2>
      <button class="btn btn-primary" id="edit-magic-items-btn">Edit</button>
    </div>`;
    tracker.tiers.forEach((tier, tIdx) => {
      html += `<div class="card card-body mb-3">
        <h4>${escapeHtml(tier.name)}</h4>`;
      Object.keys(tier.rarities).forEach(rarity => {
        const items = tier.rarities[rarity] || [];
        html += `<div class="mb-2">
          <strong>${escapeHtml(rarity)}</strong> <span class="text-muted small">(${items.length} item${items.length !== 1 ? 's' : ''})</span>
          <ul class="list-group">`;
        if (items.length === 0) {
          html += `<li class="list-group-item text-muted">No items</li>`;
        } else {
          items.forEach(item => {
            html += `<li class="list-group-item">${escapeHtml(item)}</li>`;
          });
        }
        html += `</ul></div>`;
      });
      html += `</div>`;
    });
    container.innerHTML = html;
    document.getElementById('edit-magic-items-btn').onclick = () => this.renderMagicItemTrackerFormModal(campaign);
  },
  renderMagicItemTrackerEntryView: function(tracker, campaign) {
    let html = '';
    tracker.tiers.forEach((tier, tIdx) => {
      html += `<div class="mb-3"><h5>${escapeHtml(tier.name)}</h5>`;
      Object.keys(tier.rarities).forEach(rarity => {
        const items = tier.rarities[rarity] || [];
        html += `<div class="mb-2"><strong>${escapeHtml(rarity)}</strong><ul>`;
        if (items.length === 0) {
          html += `<li class="text-muted">No items</li>`;
        } else {
          items.forEach(item => {
            html += `<li>${escapeHtml(item)}</li>`;
          });
        }
        html += `</ul></div>`;
      });
      html += `</div>`;
    });
    let footer = `<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editMagicItemsFromViewBtn">Edit</button>`;
    window.modalUtils.showModal('View Magic Item Tracker', html, footer);
    document.getElementById('editMagicItemsFromViewBtn').onclick = () => {
      window.magicItemTracker.renderMagicItemTrackerFormModal(campaign, true);
    };
  },
  renderMagicItemTrackerFormModal: function(campaign, isEditFromView = false) {
    const tracker = JSON.parse(JSON.stringify(this.getTracker(campaign)));
    let html = `<form id="magic-item-form-modal">
      <h3>Edit Magic Item Tracker</h3>`;
    tracker.tiers.forEach((tier, tIdx) => {
      html += `<div class="mb-3 border p-2">
        <h5>${escapeHtml(tier.name)}</h5>`;
      Object.keys(tier.rarities).forEach(rarity => {
        html += `<div class="mb-2">
          <label class="form-label"><strong>${escapeHtml(rarity)}</strong></label>
          <div id="tier${tIdx}-rarity-${rarity.replace(/\s/g, '')}-list-modal"></div>
          <button type="button" class="btn btn-sm btn-outline-primary mt-1" data-add="${tIdx}|${rarity}">Add Item</button>
        </div>`;
      });
      html += `</div>`;
    });
    html += `</form>`;
    let footer = `<button type="button" class="btn btn-secondary" id="cancelMagicItemFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveMagicItemFormBtn">Save</button>`;
    window.modalUtils.showModal('Edit Magic Item Tracker', html, footer);
    // Render item lists
    tracker.tiers.forEach((tier, tIdx) => {
      Object.keys(tier.rarities).forEach(rarity => {
        const listId = `tier${tIdx}-rarity-${rarity.replace(/\s/g, '')}-list-modal`;
        const listDiv = document.getElementById(listId);
        function renderList() {
          let lHtml = '';
          tier.rarities[rarity].forEach((item, i) => {
            lHtml += `<div class="input-group mb-1">
              <input class="form-control" value="${escapeHtml(item)}" data-item-input="${tIdx}|${rarity}|${i}" />
              <button type="button" class="btn btn-outline-danger btn-sm" data-remove="${tIdx}|${rarity}|${i}">Remove</button>
            </div>`;
          });
          listDiv.innerHTML = lHtml;
          // Remove handlers
          listDiv.querySelectorAll('[data-remove]').forEach(btn => {
            btn.onclick = () => {
              const [tierIdx, rar, idx] = btn.getAttribute('data-remove').split('|');
              tracker.tiers[tierIdx].rarities[rar].splice(idx, 1);
              renderList();
            };
          });
          // Input handlers
          listDiv.querySelectorAll('[data-item-input]').forEach(input => {
            input.oninput = e => {
              const [tierIdx, rar, idx] = input.getAttribute('data-item-input').split('|');
              tracker.tiers[tierIdx].rarities[rar][idx] = e.target.value;
            };
          });
        }
        renderList();
        // Add handler
        const addBtn = document.querySelector(`[data-add="${tIdx}|${rarity}"]`);
        if (addBtn) {
          addBtn.onclick = () => {
            tier.rarities[rarity].push('');
            renderList();
          };
        }
      });
    });
    document.getElementById('cancelMagicItemFormBtn').onclick = () => {
      if (isEditFromView) {
        window.magicItemTracker.renderMagicItemTrackerEntryView(tracker, campaign);
      } else {
        window.modalUtils.hideModal();
      }
    };
    document.getElementById('saveMagicItemFormBtn').onclick = () => {
      window.magicItemTracker.saveTracker(campaign, tracker);
      window.modalUtils.hideModal();
      // Refresh list view
      const mainContent = document.getElementById('main-content');
      if (mainContent) {
        window.magicItemTracker.renderMagicItemTrackerListView(mainContent, campaign);
      }
    };
  }
};