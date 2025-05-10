# UX Refinement Plan: TTRPG Campaign Tracker

## 1. Introduction

This document provides a step-by-step plan for developers to enhance the User Experience (UX) of the TTRPG Campaign Tracker. The primary goal is to improve the way users view and edit data within the various trackers, making the application more intuitive and user-friendly. This plan also addresses strategies for maintaining a manageable codebase, particularly concerning JavaScript file sizes, and promotes code reusability.

The core idea is to separate the "viewing" of data from the "editing" of data more clearly. Currently, most trackers directly present an editable form or a list that leads directly to an editable form. We will introduce a dedicated "read-only" view for individual entries.

## 2. General Principles for UX Refinement

* **Clear Read-Only View:** Each tracker entry should have a well-formatted, read-only display mode. This allows users to quickly review information without the visual clutter of form fields.
* **Explicit View/Edit States:** Users should be able to explicitly switch between viewing an entry's details and editing it.
* **Consistent UI for Actions:** Actions like "View Details," "Edit," "Delete," "Save," and "Cancel" should be presented consistently across all trackers in terms of naming, placement, and appearance.
* **Improved Visual Hierarchy:** Information within read-only views should be organized logically with clear labels and formatting to enhance scannability.
* **Modals for Editing/Viewing (Recommended):** To provide a focused experience and manage screen real estate, using modals for both viewing detailed entries and editing them is recommended. This can also help in creating reusable modal components.
* **Code Reusability:** Develop generic functions or components (e.g., for modals, rendering field-value pairs) wherever feasible.

## 3. Refactoring for Clarity and Maintainability

To prevent JavaScript files for individual trackers from becoming too large and to improve organization:

* **Dedicated Rendering Functions:** Each tracker's JavaScript file (e.g., `js/trackers/campaignConflicts/campaignConflicts.js`) should evolve to include:
  * `render[TrackerName]ListView(container, campaignData)`: Renders the list of entries (as currently, but will link to a detailed view).
  * `render[TrackerName]EntryView(targetElementOrModalContentArea, entryData, campaignData, entryIndex)`: A **new function** to render a single entry in a read-only, well-formatted view. This function will be responsible for displaying all fields of an entry.
  * `render[TrackerName]Form(targetElementOrModalContentArea, campaignData, entryData, entryIndex)`: The existing function for rendering the creation/editing form. This will be invoked when a user chooses to edit an entry from the `EntryView` or add a new entry from the `ListView`.
* **Centralized Modal Logic (If Using Modals):**
  * Create a new utility file, e.g., `js/modalUtils.js`.
  * This file would contain functions like `showModal(title, contentHtml, footerButtonsHtml)` and `closeModal()`. Tracker-specific JS would generate the HTML for the content and buttons.
* **Event Delegation:** Continue using event delegation within list views to handle actions, minimizing the number of direct event listeners.

## 4. Step-by-Step Implementation Plan

This plan will first focus on the **Campaign Conflicts Tracker** as an initial example. The principles and steps can then be applied to other trackers.

### Phase 1: Enhance `campaignConflicts.js` for Read-Only View and Modal Integration

**Step 1.1: Prepare `index.html` for a Generic Modal**

* **File:** `index.html`
* **Action:** Add a basic, hidden modal structure at the end of the `<body>`. This modal will be populated and shown by JavaScript.
  ```html
  <div id="genericModal" class="modal fade" tabindex="-1" aria-labelledby="genericModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg"> <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="genericModalLabel">Modal Title</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body" id="genericModalBody">
          </div>
        <div class="modal-footer" id="genericModalFooter">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        </div>
      </div>
    </div>
  </div>
  ```
* Ensure Bootstrap's JavaScript is correctly loaded in `index.html` for modal functionality.

**Step 1.2: Create `js/modalUtils.js` (New File)**

* **File:** `js/modalUtils.js` (create this file)
* **Location:** `js/modalUtils.js`
* **Action:** Implement basic functions to control the generic modal.
  ```javascript
  // js/modalUtils.js
  window.modalUtils = {
    modalInstance: null,

    initModal: function() {
      const modalElement = document.getElementById('genericModal');
      if (modalElement && typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        this.modalInstance = new bootstrap.Modal(modalElement);
      } else {
        console.error('Modal element not found or Bootstrap Modal class not available at init.');
      }
    },

    showModal: function(title, bodyContent, footerContent = '') {
      if (!this.modalInstance) {
        // Attempt to initialize if it wasn't ready during DOMContentLoaded
        this.initModal(); 
        if (!this.modalInstance) { // If still not initialized, log error and return
           console.error('Modal instance could not be initialized for showModal.');
           return;
        }
      }

      document.getElementById('genericModalLabel').textContent = title;
      document.getElementById('genericModalBody').innerHTML = bodyContent;
      document.getElementById('genericModalFooter').innerHTML = footerContent || '<button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>';
      this.modalInstance.show();
    },

    hideModal: function() {
      if (this.modalInstance) {
        this.modalInstance.hide();
      }
    },
    // Helper to escape HTML content before injecting
    escapeHtml: function(unsafe) {
      if (typeof unsafe !== 'string') return '';
      return unsafe
           .replace(/&/g, "&")
           .replace(/</g, "<")
           .replace(/>/g, ">")
           .replace(/"/g, """)
           .replace(/'/g, "'");
    }
  };
  ```
* **Action:** Include this new script in `index.html` *before* `js/main.js` and other tracker-specific scripts:
  `<script src="js/modalUtils.js"></script>`

**Step 1.3: Initialize Modal System in `main.js`**

* **File:** `js/main.js`
* **Action:** Ensure `modalUtils.initModal()` is called after the DOM is loaded and Bootstrap's JS has likely initialized.
  ```javascript
  // Inside document.addEventListener('DOMContentLoaded', () => { ... }); in main.js
  // ... existing initializations ...
  if (window.modalUtils) { 
    window.modalUtils.initModal(); // Bootstrap should be loaded by now
  } else {
    console.warn('modalUtils not ready for initModal in main.js');
  }
  // ... rest of the DOMContentLoaded logic ...
  ```

**Step 1.4: Modify `renderCampaignConflictsList` in `campaignConflicts.js`**

* **File:** `js/trackers/campaignConflicts/campaignConflicts.js`
* **Action:**
  * Change list items to display a summary.
  * Replace "Edit" button with a "View Details" button. The "Delete" button can remain.
  * The "Add Conflict" button's action will now be to open the form in a modal.
  * Add `escapeHtml` helper or ensure `modalUtils.escapeHtml` is accessible if not already part of this object.
* **Example Snippet (Illustrative changes):**
  ```javascript
  // js/trackers/campaignConflicts/campaignConflicts.js

  window.campaignConflicts = {
    // ... (getConflicts, saveConflicts remain the same) ...

    // Helper for escaping HTML, or use window.modalUtils.escapeHtml
    escapeHtml: function(unsafe) {
      if (typeof unsafe !== 'string') return '';
      return unsafe
           .replace(/&/g, "&")
           .replace(/</g, "<")
           .replace(/>/g, ">")
           .replace(/"/g, """)
           .replace(/'/g, "'");
    },

    renderCampaignConflictsList: function(container, campaign) {
      const conflicts = this.getConflicts(campaign); // Renamed from 'entries' for clarity
      let html = `<div class="d-flex justify-content-between align-items-center mb-3">
        <h2>Campaign Conflicts</h2>
        <button class="btn btn-primary" id="add-conflict-btn">Add Conflict</button>
      </div>`;

      if (conflicts.length === 0) {
        html += '<div class="alert alert-info">No campaign conflicts yet.</div>';
      } else {
        html += '<div class="list-group mb-3">';
        conflicts.forEach((conflict, idx) => {
          html += `<div class="list-group-item">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <strong>${this.escapeHtml(conflict.title) || '(No Title)'}</strong>
                <span class="text-muted small d-block">vs. ${this.escapeHtml(conflict.antagonist) || 'N/A'}</span>
              </div>
              <div>
                <button class="btn btn-sm btn-info me-2" data-view-conflict="${idx}">View Details</button>
                <button class="btn btn-sm btn-danger" data-delete-conflict="${idx}">Delete</button>
              </div>
            </div>
          </div>`;
        });
        html += '</div>';
      }
      container.innerHTML = html + `<div id="conflict-form-area-placeholder"></div>`; // Form area might not be needed here anymore

      document.getElementById('add-conflict-btn').onclick = () => {
        this.renderCampaignConflictsForm(campaign, null); // Pass null for idx for new entry
      };

      container.querySelectorAll('[data-view-conflict]').forEach(btn => {
        btn.onclick = () => {
          const index = parseInt(btn.getAttribute('data-view-conflict'));
          this.renderCampaignConflictEntryView(conflicts[index], campaign, index);
        };
      });

      container.querySelectorAll('[data-delete-conflict]').forEach(btn => {
        btn.onclick = () => {
          if (confirm('Delete this conflict?')) {
            const index = parseInt(btn.getAttribute('data-delete-conflict'));
            conflicts.splice(index, 1);
            this.saveConflicts(campaign, conflicts);
            this.renderCampaignConflictsList(container, campaign); // Re-render the list
          }
        };
      });
    },

    // ... (renderCampaignConflictEntryView and renderCampaignConflictsForm to be added/modified next) ...
  };
  ```

**Step 1.5: Create `renderCampaignConflictEntryView` in `campaignConflicts.js`**

* **File:** `js/trackers/campaignConflicts/campaignConflicts.js`
* **Action:** This new function will render the conflict's details in a read-only format within the modal.
  ```javascript
  // Add this new function to window.campaignConflicts
  renderCampaignConflictEntryView: function(conflictData, campaign, index) {
    // Use this.escapeHtml or window.modalUtils.escapeHtml
    const esc = this.escapeHtml || window.modalUtils.escapeHtml;

    let viewHtml = `
      <dl class="row">
        <dt class="col-sm-3">Conflict Title:</dt>
        <dd class="col-sm-9">${esc(conflictData.title) || 'N/A'}</dd>

        <dt class="col-sm-3">Antagonist/Situation:</dt>
        <dd class="col-sm-9">${esc(conflictData.antagonist) || 'N/A'}</dd>

        <dt class="col-sm-3">Notes:</dt>
        <dd class="col-sm-9"><pre style="white-space: pre-wrap; word-wrap: break-word;">${esc(conflictData.notes) || 'N/A'}</pre></dd>
      </dl>
    `;

    let footerHtml = `
      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
      <button type="button" class="btn btn-primary" id="editConflictFromViewBtn">Edit</button>
    `;

    window.modalUtils.showModal(`View Conflict: ${esc(conflictData.title)}`, viewHtml, footerHtml);

    document.getElementById('editConflictFromViewBtn').onclick = () => {
      this.renderCampaignConflictsForm(campaign, index, true); // true indicates it's an edit from view
    };
  },
  ```

**Step 1.6: Modify `renderCampaignConflictsForm` in `campaignConflicts.js`**

* **File:** `js/trackers/campaignConflicts/campaignConflicts.js`
* **Action:**
  * Adapt the function to render its content into the modal body.
  * Update "Save" and "Cancel" button logic for modal context.

  ```javascript
  // Modify renderCampaignConflictsForm in window.campaignConflicts:
  renderCampaignConflictsForm: function(campaign, idx, isEditFromView = false) {
    const conflicts = this.getConflicts(campaign);
    const conflict = idx != null ? {...conflicts[idx]} : { title: '', antagonist: '', notes: '' };
    const esc = this.escapeHtml || window.modalUtils.escapeHtml;

    // Form HTML for the modal body
    let formHtml = `<form id="conflict-form-modal"> 
      <div class="mb-3">
        <label for="conflict-title-modal" class="form-label">Conflict Title/Identifier</label>
        <input class="form-control" id="conflict-title-modal" name="title" value="${esc(conflict.title)}" required />
      </div>
      <div class="mb-3">
        <label for="conflict-antagonist-modal" class="form-label">Adventurers vs. (Antagonist/Situation)</label>
        <input class="form-control" id="conflict-antagonist-modal" name="antagonist" value="${esc(conflict.antagonist)}" />
      </div>
      <div class="mb-3">
        <label for="conflict-notes-modal" class="form-label">Notes</label>
        <textarea class="form-control" id="conflict-notes-modal" name="notes" rows="5">${esc(conflict.notes)}</textarea>
      </div>
    </form>`;

    // Footer HTML for the modal
    let footerHtml = `
      <button type="button" class="btn btn-secondary" id="cancelConflictFormBtn">Cancel</button>
      <button type="button" class="btn btn-success" id="saveConflictFormBtn">Save</button>
    `;

    const modalTitle = idx != null ? `Edit Conflict: ${esc(conflict.title)}` : 'Add New Conflict';
    window.modalUtils.showModal(modalTitle, formHtml, footerHtml);

    // Event listener for Cancel button in modal
    document.getElementById('cancelConflictFormBtn').onclick = () => {
      if (isEditFromView && idx != null) {
        this.renderCampaignConflictEntryView(conflicts[idx], campaign, idx); // Go back to view mode
      } else {
        window.modalUtils.hideModal();
      }
    };

    // Event listener for Save button in modal
    document.getElementById('saveConflictFormBtn').onclick = () => {
      const form = document.getElementById('conflict-form-modal');
      const newConflictData = {
        title: form.title.value.trim(), // Use .trim() for basic cleanup
        antagonist: form.antagonist.value.trim(),
        notes: form.notes.value.trim()
      };

      if (!newConflictData.title) {
          // Simple validation - consider a more robust approach later
          alert("Title is required."); 
          return;
      }

      if (idx != null) { // Editing existing
        conflicts[idx] = newConflictData;
      } else { // Adding new
        conflicts.push(newConflictData);
      }
      this.saveConflicts(campaign, conflicts);

      window.modalUtils.hideModal();
      // Re-render the main list view to reflect changes
      // Assuming 'main-content' is the ID of your main display area
      const mainContentContainer = document.getElementById('main-content'); 
      if (mainContentContainer) {
          this.renderCampaignConflictsList(mainContentContainer, campaign);
      } else {
          console.error("Main content container not found for list refresh.");
      }
    };
  },
  ```

**Step 1.7: Update `ui.js` `displayTrackerView`**

* **File:** `js/ui.js`
* **Action:** No major change is strictly needed here initially for Campaign Conflicts, as `displayTrackerView` calls `window.campaignConflicts.renderCampaignConflictsList`, which now handles the new modal flow internally. However, ensure the `main` container passed to `renderCampaignConflictsList` is correct.
  ```javascript
  // js/ui.js
  // ...
  displayTrackerView: function(trackerName, campaignData) {
    const main = document.getElementById('main-content');
    // ...
    if (trackerName === 'Campaign Conflicts') {
      window.campaignConflicts.renderCampaignConflictsList(main, campaignData);
    } 
    // ...
  }
  // ...
  ```

### Phase 2: Apply the Pattern to Other Trackers

Iterate through each remaining tracker module (e.g., `npcTracker.js`, `gameExpectations.js`, etc.) and apply a similar refinement process:

1. **Add `escapeHtml`:** Ensure each tracker module has access to an `escapeHtml` function (either its own, or by using `window.modalUtils.escapeHtml`).
2. **Modify `render[TrackerName]List` (or equivalent like `renderMagicItemTracker`):**
   * Update list items to be summaries, using `escapeHtml` for all displayed data.
   * Add "View Details" buttons/links for each entry. These will call the new `render[TrackerName]EntryView`.
   * The "Add New" button will call `render[TrackerName]Form` to open the form in the modal.
   * Ensure delete buttons are specific (e.g., `data-delete-[trackerName]="${idx}"`) and correctly re-render the list.
3. **Create `render[TrackerName]EntryView(entryData, campaignData, entryIndex)`:**
   * This function will generate HTML to display all fields of a single `entryData` object in a read-only format within the modal, using `escapeHtml` for all data.
   * Use `<dl>`, `<dt>`, `<dd>` for structured data and `<pre>` for multi-line text to preserve formatting.
   * Include an "Edit" button in the modal footer that calls `render[TrackerName]Form` for that specific entry, also in the modal.
4. **Modify `render[TrackerName]Form(campaignData, entryDataOrIndex, isEditFromView = false)`:**
   * Adapt it to render inside the modal. Use `escapeHtml` when populating form fields with existing `entryData`.
   * Ensure "Save" persists data (after trimming inputs) and then either closes the modal and refreshes the main list, or switches the modal to the read-only view of the saved/updated item.
   * Ensure "Cancel" closes the modal or returns to the read-only view if `isEditFromView` is true.
5. **Handle Complex Fields:** For trackers with dynamic lists (e.g., "Potentially Sensitive Elements" in Game Expectations, "Stages" in Travel Planner):
   * **Read-Only View:** Display these as formatted lists or tables (e.g., `<ul>` or a simple Bootstrap table), ensuring all user-generated content within them is also escaped.
   * **Form View:** The existing dynamic list management in forms should continue to work within the modal. Ensure data loaded into these sub-forms is also escaped.

**Example: Adapting `gameExpectations.js`**

* `renderGameExpectationsView` (current list view) would change:
  * Each list item for a player would have a "View Player Expectations" button. Player names and other summary data escaped.
  * "Add Entry" button would call `renderGameExpectationsForm` to open in a modal.
* New `renderGameExpectationEntryView(entryData, campaignData, index)`:
  * Displays DM Name, Player Name, Theme, Hopes, Concerns as text, all escaped.
  * Displays "Potentially Sensitive Elements" as a list (e.g., `<ul><li>Element: ${esc(el.desc)}, Limit: ${el.hardLimit ? 'Hard' : ''} ${el.softLimit ? 'Soft' : ''}</li>...</ul>`).
  * Modal footer has "Close" and "Edit" buttons. Edit calls `renderGameExpectationsForm`.
* `renderGameExpectationsForm` adapted for modal:
  * The form, including the dynamic list for sensitive elements, renders in the modal. Values loaded into fields are escaped.
  * Save/Cancel logic updated for modal context.

### Phase 3: Styling and Consistency

* **File:** `css/style.css`
* **Actions:**
  * Add styles for the read-only views within modals (`dl`, `dt`, `dd`, `pre` tags used in examples) to ensure they are legible and well-spaced.
    ```css
    /* Example styles for modal read-only views */
    #genericModalBody dl.row dt {
      font-weight: bold;
    }
    #genericModalBody dl.row dd pre {
      background-color: #f8f9fa; /* Light background for preformatted text */
      padding: 0.5rem;
      border-radius: 0.25rem;
      border: 1px solid #dee2e6;
      font-size: 0.9em;
      white-space: pre-wrap; /* Ensures long lines wrap */
      word-wrap: break-word; /* Breaks long words if necessary */
    }
    ```
  * Review Bootstrap modal default styling; customize if necessary for better theme cohesion.
  * Ensure all buttons ("View Details", "Edit", "Delete", "Save", "Cancel", "Add New") have a consistent look and feel (e.g., using Bootstrap button classes appropriately: `btn-primary`, `btn-secondary`, `btn-success`, `btn-danger`, `btn-info`).
  * Improve overall page layout if side effects from modal integration occur.

### Phase 4: Advanced - Reusable View Components (Optional)

* For very common patterns, like displaying a list of key-value pairs, consider creating helper functions in `js/ui.js` or a new `js/viewUtils.js`.
  * Example: `createKeyValueListHtml(dataObject, fieldOrderAndLabels)` that returns an HTML string for a `<dl>` list, ensuring values are escaped.

## 5. File Structure Summary of Changes

* **New File:**
  * `js/modalUtils.js` (for generic modal control functions and `escapeHtml` utility)
* **Modified Files:**
  * `index.html` (to include the generic modal structure and `modalUtils.js` script tag).
  * `js/main.js` (to initialize the modal system).
  * `js/trackers/[all_tracker_names]/[tracker_name].js` (significant changes to rendering logic for lists, entry views, and forms; addition/use of `escapeHtml`).
  * `css/style.css` (for styling new read-only views and potentially modal adjustments).
  * `js/ui.js` (likely minor or no changes, as tracker-specific JS will handle most new view logic).

## 6. Conclusion

By implementing these changes, the TTRPG Campaign Tracker will offer a significantly improved user experience. Separating read and edit states, using modals for focused interaction, and standardizing UI elements will make the application more intuitive to use. The phased approach, starting with one tracker and then applying the pattern, allows for incremental development and testing. This refactoring also sets a better foundation for future enhancements by emphasizing data sanitization (via `escapeHtml`) and structured UI presentation.
