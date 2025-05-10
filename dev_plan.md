# Development Guidelines: TTRPG Campaign Tracker

## 1. Introduction

This document provides development guidelines for an LLM (e.g., GitHub Copilot Agent Mode) tasked with building the TTRPG Campaign Tracker application. It should be used in conjunction with the `PRD.md` (Product Requirements Document), which details the features and functionalities required.

The primary goal is to create a simple, maintainable, and functional web application using HTML, CSS, and JavaScript, with data persisted locally.

## 2. Technology Stack

* **Frontend:** HTML, CSS, JavaScript (ES6+ features are acceptable).
* **Styling:**
  * Plain CSS.
  * Alternatively, Tailwind CSS can be used if the LLM is proficient with its setup and usage via a CDN link. If using Tailwind, ensure all styling is done through its utility classes.
  * Load Tailwind (if used): `<script src="https://cdn.tailwindcss.com"></script>` in the `<head>` of `index.html`.
  * Font: Use "Inter" as the primary font. Include it via Google Fonts or a similar CDN.
* **Data Persistence:**
  * **Primary:** Browser `localStorage` for storing all campaign data. Data should be structured logically, likely as a JSON string representing an object where keys are campaign IDs/names.
  * **Secondary:** Implement functionality to export all campaign data to a JSON file and import from a JSON file. This serves as a backup and data transfer mechanism.
* **JavaScript Libraries:**
  * No complex frameworks (like React, Vue, Angular) are required for this project to maintain simplicity for LLM generation.
  * Utility libraries (like Lodash or date-fns) can be considered if they significantly simplify a specific task, but vanilla JavaScript should be prioritized.

## 3. Code Organization & Folder Structure

Adherence to a modular structure is crucial for maintainability and for the LLM to develop features incrementally.

### 3.1. Proposed Folder Structure:

/ttrpg-campaign-tracker/
|-- index.html                   # Main HTML file (application shell)
|-- PRD.md                       # Product Requirements Document
|-- DEVELOPMENT_GUIDELINES.md    # This file
|-- css/
|   |-- style.css                # Main CSS file
|-- js/
|   |-- main.js                  # Core app logic, campaign management, navigation
|   |-- ui.js                    # DOM manipulation, general UI updates, rendering views
|   |-- dataManager.js           # Handles all localStorage and JSON import/export logic
|   |-- trackers/                # Folder for all tracker-specific modules
|   |   |-- gameExpectations/
|   |   |   |-- gameExpectations.js  # Logic for Game Expectations tracker
|   |   |   |-- gameExpectations.html# Optional: HTML template for this tracker's UI
|   |   |-- travelPlanner/
|   |   |   |-- travelPlanner.js
|   |   |   |-- travelPlanner.html   # Optional HTML template
|   |   |-- npcTracker/
|   |   |   |-- npcTracker.js
|   |   |   |-- npcTracker.html      # Optional HTML template
|   |   |-- settlementTracker/
|   |   |   |-- settlementTracker.js
|   |   |   |-- settlementTracker.html # Optional HTML template
|   |   |-- campaignJournal/
|   |   |   |-- campaignJournal.js
|   |   |   |-- campaignJournal.html # Optional HTML template
|   |   |-- dmCharacterTracker/
|   |   |   |-- dmCharacterTracker.js
|   |   |   |-- dmCharacterTracker.html# Optional HTML template
|   |   |-- campaignConflicts/
|   |   |   |-- campaignConflicts.js
|   |   |   |-- campaignConflicts.html # Optional HTML template
|   |   |-- magicItemTracker/
|   |   |   |-- magicItemTracker.js
|   |   |   |-- magicItemTracker.html  # Optional HTML template
|   |   |-- bastionTracker/
|   |   |   |-- bastionTracker.js
|   |   |   |-- bastionTracker.html    # Optional HTML template
|-- assets/                      # Optional: For any images or static assets (if any)
|   |-- icons/                   # SVG icons etc.
|-- README.md                    # Basic project information

### 3.2. File Content Guidelines:

* **`index.html`**:
  * Should be the main application shell.
  * Include necessary meta tags (viewport, charset).
  * Link to `css/style.css`.
  * Include script tags for JavaScript files at the end of the `<body>`. Order might matter: `dataManager.js`, `ui.js`, then `main.js`, followed by tracker-specific JS files or load them dynamically.
  * Define main layout areas (e.g., a header for campaign selection/app title, a navigation sidebar for trackers, and a main content area where tracker UIs will be rendered).
* **`js/main.js`**:
  * Initialize the application on DOMContentLoaded.
  * Handle campaign creation, selection, loading, and saving (delegating to `dataManager.js`).
  * Manage navigation between different trackers (e.g., by listening to clicks on nav links and calling functions in `ui.js` to render the appropriate tracker).
  * Store the currently active campaign's data in a JavaScript variable.
* **`js/ui.js`**:
  * Contain functions to render different parts of the UI.
  * Example: `renderCampaignSelector(campaigns)`, `renderTrackerNavigation(trackers)`, `displayTrackerView(trackerName, campaignData)`.
  * If using the optional HTML template approach (see below), this file would also handle fetching and injecting those templates.
* **`js/dataManager.js`**:
  * Encapsulate all logic for interacting with `localStorage` (e.g., `saveCampaignsToLocalStorage(allCampaignData)`, `loadCampaignsFromLocalStorage()`).
  * Handle JSON export (`exportDataAsJSON(allCampaignData)`) and import (`handleJSONFileImport(file)`).
* **`js/trackers/[trackerName]/[trackerName].js`**:
  * Each tracker module should be self-contained as much as possible.
  * Export functions to:
    * `render[TrackerName]Form(data)`: To show a form for creating/editing an entry.
    * `render[TrackerName]View(data)`: To display existing entries.
    * `handleSave[TrackerName](formData)`: To process form data and update the campaign data.
    * `handleDelete[TrackerName]Entry(entryId)`: (If applicable).
  * These functions will be called by `main.js` or `ui.js` when the user navigates to that tracker.
  * The data specific to a tracker within a campaign should be passed to these functions.
* **Optional HTML Templates (`js/trackers/[trackerName]/[trackerName].html`)**:
  * To keep `index.html` clean and make tracker UI development more modular, each tracker can have its own HTML snippet file.
  * This file would contain *only* the HTML structure for that tracker's form and display area.
  * `ui.js` or the tracker's own JS can fetch this HTML (e.g., using `fetch()`) and inject it into the main content area of `index.html` when the tracker is selected.
* **CSS (`css/style.css`)**:
  * Organize CSS rules logically.
  * Use classes for styling; avoid inline styles in HTML as much as possible.
  * Ensure basic responsiveness.

## 4. User Experience (UX) Guidelines

* **Clarity and Simplicity:** The UI should be intuitive. Users should easily understand how to create campaigns, switch between them, navigate trackers, and manage data.
* **Feedback:** Provide visual feedback for actions (e.g., "Campaign saved," "NPC added," "Data exported").
* **Error Handling:** Implement basic error handling and display user-friendly messages (e.g., for invalid form inputs, issues with file import/export). Avoid using `alert()`; use a less intrusive on-page message display.
* **Responsiveness:** While complex responsive design isn't the primary goal for a personal tool, the layout should be usable on typical desktop/laptop screen sizes and not break completely on slightly smaller views. Avoid fixed widths that cause horizontal scrolling.

## 5. Step-by-Step Development Plan

This plan outlines a phased approach to developing the application, allowing for iterative development and testing. The LLM should focus on one phase at a time.

1. **Phase 1: Core Application Shell & Campaign Management**

   * **Objective:** Basic HTML structure, main navigation, and functionality to create, select, save, and load campaigns (using `localStorage` and JSON file export/import for all campaign data). No individual trackers yet.
   * **Files to create/edit:** `index.html`, `css/style.css`, `js/main.js`, `js/dataManager.js`, `js/ui.js`.
   * **Details:**
     * `index.html`: Basic page layout (header for app title/campaign management, sidebar for tracker navigation placeholders, main content area placeholder).
     * `js/dataManager.js`: Implement functions to:
       * Load all campaigns from `localStorage`.
       * Save all campaigns to `localStorage`.
       * Trigger JSON file download for export.
       * Handle JSON file upload for import.
     * `js/main.js`:
       * On load, initialize `dataManager` to get campaigns.
       * Implement logic for creating a new campaign (prompt for name, add to data structure, save).
       * Implement logic for selecting an active campaign.
       * Implement logic for deleting a campaign.
       * Connect UI elements (buttons/dropdowns) for these actions.
     * `js/ui.js`: Functions to render the campaign selection UI (e.g., a dropdown list of campaigns) and update it when campaigns are added/deleted.
   * **Testing:** Verify campaign creation, selection, deletion, persistence across page reloads, JSON export, and JSON import.
2. **Phase 2: Implement First Tracker - Game Expectations Tracker**

   * **Objective:** Integrate the "Game Expectations Tracker" into the selected campaign.
   * **Files to create/edit:** `js/trackers/gameExpectations/gameExpectations.js`, (optionally `js/trackers/gameExpectations/gameExpectations.html`), update `js/main.js` and `js/ui.js`.
   * **Details:**
     * `gameExpectations.js`:
       * Define data structure for a Game Expectations entry.
       * Function to render the form for adding/editing an entry (either by generating HTML strings or using the `.html` template).
       * Function to display a list of existing Game Expectations entries for the current campaign.
       * Logic to add a new entry to the current campaign's data, save (via `dataManager`).
       * Logic to edit an existing entry.
       * Logic to delete an entry.
       * Handle the dynamic list for "Potentially Sensitive Elements".
     * `js/main.js` & `js/ui.js`:
       * Add "Game Expectations" to the tracker navigation.
       * When selected, call functions in `ui.js` / `gameExpectations.js` to render its view in the main content area, passing the relevant data from the active campaign.
   * **Testing:** Add, view, edit, and delete Game Expectations entries. Ensure data persists within the correct campaign.
3. **Phase 3: Implement Second Tracker - NPC Tracker**

   * **Objective:** Integrate the "NPC Tracker".
   * **Files to create/edit:** `js/trackers/npcTracker/npcTracker.js`, (optionally `js/trackers/npcTracker/npcTracker.html`), update `js/main.js` and `js/ui.js`.
   * **Details:** Similar structure and logic as Phase 2, but for NPC data.
   * **Testing:** Add, view, edit, delete NPCs. Data persistence.
4. **Phase 4: Implement Third Tracker - Travel Planner**

   * **Objective:** Integrate the "Travel Planner", including multi-stage functionality.
   * **Files to create/edit:** `js/trackers/travelPlanner/travelPlanner.js`, (optionally `js/trackers/travelPlanner/travelPlanner.html`), update `js/main.js` and `js/ui.js`.
   * **Details:**
     * Handle overall journey details and a dynamic list of "Stages" within each travel plan.
     * Each stage will have its own set of fields.
   * **Testing:** Create travel plans, add/edit/delete multiple stages within a plan. Data persistence.
5. **Phase 5: Implement Remaining Trackers (Iteratively)**

   * **Objective:** Add each subsequent tracker one by one, following the pattern from Phases 2-4.
     * Settlement Tracker (`js/trackers/settlementTracker/`)
     * Campaign Journal (`js/trackers/campaignJournal/`)
     * DM's Character Tracker (`js/trackers/dmCharacterTracker/`)
     * Campaign Conflicts (`js/trackers/campaignConflicts/`)
     * Magic Item Tracker (`js/trackers/magicItemTracker/`)
     * Bastion Tracker (`js/trackers/bastionTracker/`)
   * For each tracker:
     * Create its specific JavaScript module and optional HTML template in its dedicated folder.
     * Define data structures as per the PRD.
     * Implement form rendering, display logic, and CRUD operations (Create, Read, Update, Delete) or just Update for singular trackers (like Magic Item Tracker if it's a single entity per campaign).
     * Update main navigation in `js/main.js` / `js/ui.js`.
   * **Testing:** Thoroughly test each tracker's functionality as it's implemented.
6. **Phase 6: UI/UX Refinement & Final Testing**

   * **Objective:** Improve overall usability, styling, and test thoroughly.
   * **Details:**
     * Review all trackers for consistency in UI and behavior.
     * Enhance `css/style.css` for better visual appeal, readability, and basic responsiveness.
     * Test all functionalities across multiple campaigns: campaign management, data persistence (localStorage and JSON import/export), adding/editing/deleting entries in all trackers.
     * Ensure user feedback messages are clear and helpful.
     * Verify basic error handling (e.g., for missing required fields in forms).
     * Cross-browser check on modern browsers (Chrome, Firefox, Edge).

This document should provide a solid foundation for the LLM to build the application in a structured manner.
