# PRD: PySide6 TTRPG Campaign Tracker

## 1. Introduction

This document describes the features and specifications of the PySide6 TTRPG Campaign Tracker application as of its current implementation. It is based on an analysis of the application's source code.

## 2. General Application Structure & Features

The application is built using PySide6 and provides a graphical user interface for managing TTRPG campaign data.

*   **Main Window:**
    *   The application presents a main window titled "TTRPG Campaign Tracker".
    *   It includes a Menu Bar and a Status Bar.
    *   The main content area is divided by a splitter into a tracker navigation list on the left and a tracker display area on the right.

*   **Campaign Management:**
    *   **Campaign Selection:** A combo box ("Campaign:") allows users to select from existing campaigns. If no campaigns are loaded, it prompts to create or import one.
    *   **Create Campaign:** A "New Campaign" button opens a dialog prompting for a campaign name. It checks for duplicate names and, upon success, creates a new campaign, making it the active one.
    *   **Delete Campaign:** A "Delete Selected Campaign" button prompts for confirmation before deleting the currently selected campaign and all its associated data.
    *   **Data Import/Export (All Data):**
        *   The "File" menu contains "Import All Data..." which opens a file dialog to load campaign data from a JSON file (defaulting to `ttrpg_campaign_data.json`).
        *   The "File" menu contains "Export All Data..." which opens a file dialog to save all current campaign data to a JSON file.
    *   **Data Persistence:** Application data is automatically saved to a JSON file (default `ttrpg_campaign_data.json`) when changes are made (e.g., creating/deleting campaigns, adding/editing tracker entries) and upon closing the application. The active campaign is also remembered.

*   **Tracker Navigation and Display:**
    *   **Sidebar Navigation:** A list on the left side of the main window (`tracker_nav_list`) displays the names of available trackers. This list is enabled only when a campaign is selected.
    *   **Stacked Widget Display:** Selecting a tracker from the navigation list displays its specific UI in the area to the right (`tracker_display_area`). If no campaign is selected, or no tracker is selected for an active campaign, a placeholder message is shown.

## 3. Detailed Tracker Specifications

The following trackers are currently implemented with dedicated UI and functionality:

### 3.1 Game Expectations

*   **Main Widget (`GameExpectationsWidget`):**
    *   Displays a table of game expectations entries with columns: "Player Name", "DM Name", "Actions".
    *   "Add Player Expectations" button: Opens the `GameExpectationsEntryDialog` to add a new entry.
    *   "Actions" column in the table contains "Edit" and "Delete" buttons for each entry.
        *   "Edit": Opens `GameExpectationsEntryDialog` pre-filled with the entry's data.
        *   "Delete": Prompts for confirmation before removing the entry.
    *   A placeholder message is shown if no campaign is selected or no entries exist.
*   **Dialog (`GameExpectationsEntryDialog`):**
    *   Fields:
        *   DM Name: Text Input (auto-fills from global campaign DM name for new entries)
        *   Player Name: Text Input (mandatory)
        *   Game Theme and Flavor: Text Area
        *   Player's Hopes/Expectations: Text Area
        *   At-the-Table Concerns: Text Area
    *   Potentially Sensitive Elements GroupBox:
        *   Table with columns: "Element Name/Description" (Text Input), "Hard Limit" (Checkbox), "Soft Limit" (Checkbox).
        *   "Add Element" button: Adds a new row to the sensitive elements table.
        *   "Remove Selected Element" button: Removes the selected row from the table.
    *   "Save" button: Validates and saves the entry.
    *   "Cancel" button: Closes the dialog without saving.

### 3.2 Travel Planner

*   **Main Widget (`TravelPlannerWidget`):**
    *   Displays a table of travel plans with columns: "Journey Name", "Origin", "Destination", "# Stages", "Actions".
    *   "Add New Travel Plan" button: Opens `TravelPlanEntryDialog` to create a new travel plan.
    *   "Actions" column in the table contains "Edit" and "Delete" buttons.
        *   "Edit": Opens `TravelPlanEntryDialog` pre-filled with the plan's data.
        *   "Delete": Prompts for confirmation before removing the plan.
    *   A placeholder message is shown if no campaign is selected or no plans exist.
*   **Dialog (`TravelPlanEntryDialog`):**
    *   Overall Journey Details GroupBox:
        *   Journey Name: Text Input (mandatory)
        *   Overall Origin: Text Input
        *   Overall Destination: Text Input
    *   Travel Stages GroupBox:
        *   Table displaying stages with columns: "#" (Identifier), "Start", "End", "Actions" (View/Edit button).
        *   "Add Stage" button: Opens `TravelStageDialog` to add a new stage.
        *   "Edit Selected Stage" button: Opens `TravelStageDialog` for the selected stage.
        *   "Remove Selected Stage" button: Removes the selected stage after confirmation.
        *   Double-clicking a stage also opens it for editing.
    *   "Save" button: Validates and saves the travel plan (including all its stages).
    *   "Cancel" button: Closes the dialog.
*   **Sub-Dialog (`TravelStageDialog`):** Used for adding/editing individual travel stages.
    *   Fields:
        *   Stage Identifier (e.g., Stage 1): Text Input
        *   Start Location: Text Input (mandatory within the dialog logic)
        *   End Location: Text Input (mandatory within the dialog logic)
        *   Distance: Text Input
        *   Terrain: Text Input
        *   Weather: Text Input
        *   Pace: ComboBox (Fast, Normal, Slow)
        *   Travel Time Value: SpinBox
        *   Travel Time Unit: ComboBox (days, hrs)
        *   Narrative Notes: Text Area
        *   Challenges: Text Area
        *   Total Elapsed Time (Journey): Text Input
    *   "Ok" button: Accepts changes (data retrieved by `TravelPlanEntryDialog`).
    *   "Cancel" button: Closes the dialog.

### 3.3 NPC Tracker

*   **Main Widget (`NPCTrackerWidget`):**
    *   Displays a table of NPCs with columns: "Name", "Stat Block", "Alignment", "Actions".
    *   "Add New NPC" button: Opens `NPCEntryDialog` to add a new NPC.
    *   "Actions" column in the table contains "Edit" and "Delete" buttons.
        *   "Edit": Opens `NPCEntryDialog` pre-filled with NPC data.
        *   "Delete": Prompts for confirmation before removing the NPC.
    *   A placeholder message is shown if no campaign or NPCs exist.
*   **Dialog (`NPCEntryDialog`):**
    *   Fields:
        *   Name: Text Input (mandatory)
        *   Stat Block Source: Text Input
        *   MM Page: Text Input
        *   Stat Block Alterations: Text Area
        *   Alignment: Text Input
        *   Personality: Text Area
        *   Appearance: Text Area
        *   Secret: Text Area
    *   "Save" button: Validates and saves NPC data.
    *   "Cancel" button: Closes dialog.

### 3.4 Settlement Tracker

*   **Main Widget (`SettlementTrackerWidget`):**
    *   Displays a table of settlements with columns: "Name", "Size", "Defining Trait" (snippet), "Actions".
    *   "Add New Settlement" button: Opens `SettlementEntryDialog`.
    *   "Actions" column has "Edit" and "Delete" buttons.
    *   A placeholder message is shown if no campaign or settlements exist.
*   **Dialog (`SettlementEntryDialog`):**
    *   Fields:
        *   Name: Text Input (mandatory)
        *   Size: ComboBox (Village, Town, City)
        *   Defining Trait: Text Area
        *   Claim to Fame: Text Area
        *   Current Calamity: Text Area
        *   Local Leader: Text Input
        *   Noteworthy People: Text Area
        *   Noteworthy Places: Text Area
        *   GP Value of Most Expensive Item: Text Input
    *   "Save" button: Validates and saves settlement data.
    *   "Cancel" button: Closes dialog.

### 3.5 Campaign Journal

*   **Main Widget (`CampaignJournalWidget`):**
    *   Displays a table of journal entries with columns: "Session #", "Date", "Title", "Actions". Table is sortable.
    *   "Add New Session Log" button: Opens `CampaignJournalEntryDialog`.
    *   "Actions" column has "Edit" and "Delete" buttons.
    *   A placeholder message is shown if no campaign or entries exist.
*   **Dialog (`CampaignJournalEntryDialog`):**
    *   Fields:
        *   Session Number: SpinBox (min 1, auto-increments for new entries)
        *   Session Date: DateEdit (calendar popup, format yyyy-MM-dd)
        *   Session Title: Text Input (mandatory)
        *   Important Earlier Events: Text Area
        *   Planned Summary for Session: Text Area
        *   Additional Notes/Outcome: Text Area
    *   "Save" button: Validates and saves journal entry.
    *   "Cancel" button: Closes dialog.

### 3.6 DM's Character Tracker

*   **Main Widget (`DMCharacterWidget`):**
    *   Displays a table of Player Characters (PCs) with columns: "Character Name", "Player Name", "Class", "Level", "Actions".
    *   "Add New PC Entry" button: Opens `DMCharacterEntryDialog`.
    *   "Actions" column has "Edit" and "Delete" buttons.
    *   A placeholder message is shown if no campaign or PC entries exist.
*   **Dialog (`DMCharacterEntryDialog`):** (Uses a scroll area for its many fields)
    *   Fields:
        *   Character's Name: Text Input (mandatory)
        *   Player's Name: Text Input
        *   Player Motivations: GroupBox with Checkboxes (Acting, Exploring, Fighting, Instigating, Optimizing, Problem-Solving, Socializing, Storytelling)
        *   Notes on Player Expectations: Text Area
        *   Class: Text Input (Character Stats GroupBox)
        *   Subclass: Text Input (Character Stats GroupBox)
        *   Level: SpinBox (min 1, max 20) (Character Stats GroupBox)
        *   Background: Text Input (Character Stats GroupBox)
        *   Species/Race: Text Input (Character Stats GroupBox)
        *   Alignment: Text Input (Character Stats GroupBox)
        *   Goals & Ambitions: Text Area (Character Details GroupBox)
        *   Quirks & Whims: Text Area (Character Details GroupBox)
        *   Magic Items Owned: Text Area (Character Details GroupBox)
        *   Other Character Details: Text Area (Character Details GroupBox)
        *   Family, Friends, & Foes: Text Area (Character Details GroupBox)
        *   Adventure Ideas (DM): Text Area (Character Details GroupBox)
    *   "Save" button: Validates and saves PC entry data.
    *   "Cancel" button: Closes dialog.

## 4. Unimplemented Trackers

The following trackers are listed in the application's navigation but currently display only a placeholder message indicating that their content will appear there. They do not have dedicated UI or functionality beyond being listed:

*   Campaign Conflicts
*   Magic Item Tracker
*   Bastion Tracker
