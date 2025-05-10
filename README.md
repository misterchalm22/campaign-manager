# TTRPG Campaign Tracker

A web application for tabletop role-playing game masters to organize and manage campaign information, digitizing the functionality of traditional PDF tracking sheets.

## Features
- Manage multiple campaigns, each with its own trackers and data
- Trackers for:
  - Game Expectations (per player)
  - NPC Tracker (multiple NPCs per campaign)
  - Travel Planner (multi-stage journeys)
  - Settlement Tracker
  - Campaign Journal
  - DM's Character Tracker
  - Campaign Conflicts
  - Magic Item Tracker
  - Bastion Tracker
- Add, edit, and delete entries for each tracker
- Data is saved in browser localStorage for persistence
- Export and import all campaign data as JSON files
- Simple, intuitive UI with navigation between campaigns and trackers

## Technology Stack
- HTML, CSS (with Bootstrap for layout), and JavaScript (ES6+)
- No frameworks required; all logic is in vanilla JS
- Data persistence via browser localStorage

## Folder Structure
```
index.html                # Main HTML file
css/
  style.css               # Main stylesheet
js/
  dataManager.js          # Handles localStorage and import/export
  ui.js                   # UI rendering and DOM manipulation
  main.js                 # App logic, campaign management, navigation
  trackers/
    gameExpectations/     # Game Expectations tracker module
    npcTracker/           # NPC Tracker module
    travelPlanner/        # Travel Planner module
    settlementTracker/    # Settlement Tracker module
    campaignJournal/      # Campaign Journal module
    dmCharacterTracker/   # DM's Character Tracker module
    campaignConflicts/    # Campaign Conflicts module
    magicItemTracker/     # Magic Item Tracker module
    bastionTracker/       # Bastion Tracker module
assets/
  icons/                  # (Optional) SVG icons and images
prd.md                    # Product Requirements Document
LICENSE.md                # License (MIT)
README.md                 # This file
```

## Usage
1. Open `index.html` in your browser.
2. Create a new campaign or select an existing one.
3. Use the sidebar to navigate between different trackers.
4. Add, edit, or delete entries as needed for your campaign.
5. Export your data for backup, or import it to restore campaigns.

## Development & Contribution
- All code is modular and organized by tracker.
- See `dev_plan.md` and `prd.md` for detailed requirements and development guidelines.
- Contributions are welcome via pull requests.

## License
MIT License. See `LICENSE.md` for details.
