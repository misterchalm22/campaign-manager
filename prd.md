# Product Requirements Document: TTRPG Campaign Tracker

## 1. Introduction

This document outlines the requirements for a personal-use application designed to digitize and manage tracking sheets for tabletop role-playing games (TTRPGs). The goal is to provide a user-friendly interface for Game Masters (GMs) to organize campaign information efficiently, based on the provided PDF tracking sheets.

For implementation details, including technology stack, code organization, folder structure, and a step-by-step development plan, please refer to the `DEVELOPMENT_GUIDELINES.md` document.

## 2. Target User

* Tabletop Role-Playing Game Masters (GMs) for personal campaign management.

## 3. High-Level Goals

* Digitize the functionality of the provided PDF tracking sheets.
* Allow users to create, manage, save, and load multiple distinct campaigns.
* For each campaign, allow users to create and manage various types of tracking entries (e.g., NPCs, Settlements, Travel Plans).
* Ensure data is persistent for the user (e.g., via local storage or file export/import for all campaigns).
* Provide a clear and intuitive user interface.

## 4. General Application Structure & Features

* **Campaign Management:**
  * Ability to create a new campaign. Each campaign should have a unique name or identifier.
  * Ability to list all created campaigns, allowing the user to select one to view/edit.
  * Ability to delete campaigns.
  * **Data Persistence:**
    * Ability to save the current state of *all* campaigns and their associated data (e.g., to a single local file in JSON format, or utilize browser `localStorage` with a clear structure for multiple campaigns).
    * Ability to load campaign data from a previously saved state, restoring all campaigns and their information.
  * Each campaign will serve as a container for all its related tracking sheets/data.
* **Modular Trackers:** The application will be organized around the different types of tracking sheets.
  * Some trackers will allow multiple instances per campaign (e.g., NPC Tracker, Travel Planner, Settlement Tracker, Campaign Journal, DM's Character Tracker, Bastion Tracker).
  * Some trackers will be singular per campaign (e.g., Magic Item Tracker, Campaign Conflicts - *User initial specification for Magic Items was singular, Campaign Conflicts seems singular in its PDF layout but could be multiple if desired by user, for now, keeping it singular per campaign*).
* **User Interface (UI):**
  * A main navigation to switch between different tracker types *within a selected campaign*.
  * A clear way to switch between managing different campaigns.
  * Forms for data entry that mirror the fields in the PDF.
  * Display views for existing entries.
  * Ability to add, edit, and delete entries for multi-instance trackers.

## 5. Detailed Feature Specifications

We will detail each tracking sheet from the PDF as a module/feature of the application.

### 5.1 Game Expectations Tracker

* **Purpose:** To document player and DM expectations, preferences, and boundaries for a campaign.
* **Cardinality:** Multiple instances per campaign (one for each player).
* **Fields:**
  1. **DM Name:**
     * Type: Text Input
     * Description: Name of the Dungeon Master. (This should ideally be a global setting for the *campaign* rather than repeated on each player's expectation sheet).
     * *PRD Note for LLM:* Auto-fill from a general campaign setting if possible. If not, allow input here but consider how it relates to the overall campaign.
  2. **Player Name:**
     * Type: Text Input
     * Description: Name of the player for whom these expectations are being recorded. This will be the primary identifier for this specific Game Expectation entry within the campaign.
  3. **Game Theme and Flavor:**
     * Type: Text Area (multi-line input)
     * Description: Overall theme, tone, and style of the game (as perceived or desired by this player/DM).
  4. **Potentially Sensitive Elements:**
     * Type: Dynamic List of Objects
     * Description: A list of potentially sensitive topics or themes. Each item in the list should have:
       * **Element Name/Description:** Text Input (e.g., "Spiders", "Gore", "Betrayal")
       * **Hard Limit:** Checkbox (Boolean - True/False). Label: "Don't mention or include."
       * **Soft Limit:** Checkbox (Boolean - True/False). Label: "Handle with care or off-camera."
     * *PRD Note for LLM:* User should be able to add multiple sensitive elements and remove them.
  5. **Player's Hopes and Expectations:**
     * Type: Text Area
     * Description: What the player wants to see or experience in the campaign. (Corresponds to "WHAT DO YOU WANT TO SEE IN THIS CAMPAIGN?" on the PDF).
  6. **At-the-Table Concerns:**
     * Type: Text Area
     * Description: Any concerns related to player behavior or the play environment. (Corresponds to "EXAMPLES: SHOUTING, SWEARING, ALCOHOL, SHARING DICE" on the PDF).

### 5.2 Travel Planner

* **Purpose:** To plan and track journeys within the campaign, including stages, duration, and challenges.
* **Cardinality:** Multiple instances per campaign. Each instance represents a distinct journey.
* **Fields (Overall Journey):**

  1. **Journey Name/Identifier:**
     * Type: Text Input
     * Description: A unique name for this travel plan (e.g., "Trip to Oakhaven", "Crossing the Serpent Peaks"). This is for user organization, not on the PDF but highly recommended.
  2. **Origin:**
     * Type: Text Input
     * Description: Starting point of the overall journey.
  3. **Destination:**
     * Type: Text Input
     * Description: Final destination of the overall journey.
* **Fields (Per Stage - A journey can have multiple stages):**

  * *PRD Note for LLM:* The UI should allow adding multiple stages to a single Travel Plan. The PDF shows three stages, but the application should allow for a variable number.

  1. **Stage Number/Identifier:**
     * Type: Auto-generated or Text Input (e.g., "Stage 1", "Leg 1")
  2. **Start (Stage):**
     * Type: Text Input
     * Description: Starting point of this specific stage.
  3. **End (Stage):**
     * Type: Text Input
     * Description: Ending point of this specific stage.
  4. **Distance (Stage):**
     * Type: Text Input (allows numbers and units, e.g., "120 miles", "3 days walk")
     * Description: Distance to be covered in this stage.
  5. **Terrain (Stage):**
     * Type: Text Input (e.g., "Forest", "Mountains", "Swamp")
     * Description: Predominant terrain type for this stage.
  6. **Weather (Stage):**
     * Type: Text Input (e.g., "Sunny", "Rainy with high winds", "Blizzard")
     * Description: Expected or current weather conditions for this stage.
  7. **Pace (Stage):**
     * Type: Radio Buttons or Select Dropdown
     * Options: "Fast", "Normal", "Slow"
     * Description: Chosen travel pace for this stage.
  8. **Travel Time (Stage):**
     * **Value:** Number Input
     * **Unit:** Select Dropdown (Options: "days", "hrs")
     * Description: Estimated or actual time taken for this stage based on pace, distance, etc. (The PDF has "days/hrs" next to each pace option, implying the user fills this in).
  9. **Narrative Notes (Stage):**
     * Type: Text Area
     * Description: Key events, descriptions, or points of interest encountered during this stage.
  10. **Challenges (Stage):**
      * Type: Text Area
      * Description: Obstacles, encounters, or difficulties faced during this stage.
  11. **Elapsed Time (Total for Journey up to this stage):**
      * Type: Text Input (allows numbers and units, e.g., "3 days", "28 hrs")
      * Description: Cumulative travel time for the journey after completing this stage.
      * *PRD Note for LLM:* This could potentially be auto-calculated based on the sum of previous stage travel times, or manually entered.

### 5.3 NPC Tracker

* **Purpose:** To store and manage information about Non-Player Characters (NPCs) in the campaign.
* **Cardinality:** Multiple instances per campaign. Each instance represents a unique NPC.
* **Fields:**
  1. **NPC Name:**
     * Type: Text Input
     * Description: The name of the Non-Player Character. This is the primary identifier.
  2. **Stat Block (Source):**
     * Type: Text Input
     * Description: Reference to the NPC's stat block (e.g., "Goblin", "Veteran", "Archmage").
  3. **MM Page (Monster Manual Page):**
     * Type: Text Input (or Number Input)
     * Description: Page number in the Monster Manual or other sourcebook where the stat block can be found.
  4. **Stat Block Alterations:**
     * Type: Text Area
     * Description: Any modifications or deviations from the standard stat block.
  5. **Alignment:**
     * Type: Text Input (or Select Dropdown with common alignments: LG, NG, CG, LN, N, CN, LE, NE, CE)
     * Description: The NPC's moral and ethical alignment.
  6. **Personality:**
     * Type: Text Area
     * Description: Key personality traits, demeanor, and mannerisms of the NPC.
  7. **Appearance:**
     * Type: Text Area
     * Description: Physical description of the NPC.
  8. **Secret:**
     * Type: Text Area
     * Description: Hidden information, motivations, or background details about the NPC.

### 5.4 Settlement Tracker

* **Purpose:** To detail information about various settlements within the campaign world.
* **Cardinality:** Multiple instances per campaign. Each instance represents a unique settlement.
* **Fields:**
  1. **Settlement Name:**
     * Type: Text Input
     * Description: The name of the settlement. This is the primary identifier.
  2. **Size:**
     * Type: Radio Buttons or Select Dropdown
     * Options:
       * "Village (Pop up to 500)"
       * "Town (Pop. 501-5,000)"
       * "City (Pop. 5,001+)"
     * Description: The general size category of the settlement.
  3. **Defining Trait:**
     * Type: Text Area
     * Description: A key characteristic or feature that makes the settlement unique.
  4. **Claim to Fame:**
     * Type: Text Area
     * Description: What the settlement is known for (e.g., a historical event, a unique export).
  5. **Current Calamity:**
     * Type: Text Area
     * Description: Any ongoing problems, threats, or significant events affecting the settlement.
  6. **Local Leader:**
     * Type: Text Input
     * Description: The name and/or title of the settlement's leader or governing body.
  7. **Noteworthy People:**
     * Type: Text Area
     * Description: A list or description of important or interesting NPCs residing in the settlement.
     * *PRD Note for LLM:* Consider allowing dynamic addition of multiple people, perhaps with a small note for each, or just a free text area.
  8. **Noteworthy Places:**
     * Type: Text Area
     * Description: A list or description of significant locations, landmarks, or businesses within the settlement.
     * *PRD Note for LLM:* Similar to Noteworthy People, consider dynamic list or free text.
  9. **GP Value of the Most Expensive Item for Sale:**
     * Type: Number Input (or Text Input if currency symbols/notes are needed)
     * Description: The approximate gold piece value of the most expensive item generally available for purchase.

### 5.5 Campaign Journal

* **Purpose:** To log session-by-session events, plans, and notes for the campaign.
* **Cardinality:** Multiple instances per campaign. Each instance represents a single game session log.
* **Fields:**
  1. **Session Number:**
     * Type: Number Input
     * Description: A sequential number for the game session.
     * *PRD Note for LLM:* Could auto-increment based on existing journal entries for the campaign.
  2. **Session Date:**
     * Type: Date Input (e.g., YYYY-MM-DD)
     * Description: The real-world date the game session was played.
  3. **Session/Adventure Title:**
     * Type: Text Input
     * Description: A title or brief theme for the session or adventure.
  4. **Important Events from Earlier Sessions:**
     * Type: Text Area
     * Description: Notes on relevant past events that might impact the current session. (Corresponds to "Important events from earlier sessions that might have bearing on this game session:" on the PDF).
  5. **Planned Summary for This Session:**
     * Type: Text Area
     * Description: A brief outline of what the DM plans for the current game session. (Corresponds to "Brief summary of what's planned for this game session:" on the PDF).
  6. **Additional Notes:**
     * Type: Text Area
     * Description: Any other miscellaneous notes, outcomes from the session, or thoughts for future sessions.

### 5.6 DM's Character Tracker

* **Purpose:** For the DM to track key details about each Player Character (PC) in the campaign.
* **Cardinality:** Multiple instances per campaign (one for each PC).
* **Fields:**
  1. **Character's Name:**
     * Type: Text Input
     * Description: The name of the Player Character. This is the primary identifier for this entry.
  2. **Player's Name:**
     * Type: Text Input
     * Description: The name of the player who controls this character.
  3. **Player Motivation:**
     * Type: Set of Checkboxes (allow multiple selections)
     * Options: "Acting", "Exploring", "Fighting", "Instigating", "Optimizing", "Problem-Solving", "Socializing", "Storytelling"
     * Description: Key motivations of the player for this character/game.
  4. **Notes on Player Expectations:**
     * Type: Text Area
     * Description: DM's notes related to this specific player's expectations (could link to or summarize info from the Game Expectations Tracker for this player).
  5. **Class:**
     * Type: Text Input
  6. **Subclass:**
     * Type: Text Input
  7. **Level:**
     * Type: Number Input
  8. **Background:**
     * Type: Text Input
  9. **Species (Race):**
     * Type: Text Input
     * Description: The character's species or race.
  10. **Alignment:**
      * Type: Text Input (or Select Dropdown with common alignments)
  11. **Goals and Ambitions:**
      * Type: Text Area
      * Description: The character's short-term and long-term goals.
  12. **Quirks and Whims:**
      * Type: Text Area
      * Description: Distinctive habits, personality traits, or unusual behaviors.
  13. **Magic Items:**
      * Type: Text Area
      * Description: A list or notes on magic items possessed by the character.
      * *PRD Note for LLM:* Could potentially link to a centralized Magic Item Tracker if one is implemented with individual item details. For now, a text area.
  14. **Character Details:**
      * Type: Text Area
      * Description: Other important details about the character (e.g., appearance, backstory snippets not covered elsewhere).
  15. **Family, Friends, and Foes:**
      * Type: Text Area
      * Description: Key NPCs related to the character.
  16. **Adventure Ideas:**
      * Type: Text Area
      * Description: DM's plot hooks or adventure ideas specifically tied to this character.

### 5.7 Campaign Conflicts Tracker

* **Purpose:** To outline major conflicts or potential conflicts within the campaign.
* **Cardinality:** Singular per campaign (The PDF shows three conflict slots on one page. We can interpret this as one "Campaign Conflicts" tracker that can hold multiple conflict descriptions).
* **Fields (Per Conflict - The tracker should allow for defining multiple conflicts):**

  * *PRD Note for LLM:* The UI should allow adding multiple conflict entries within this single tracker. The PDF shows "Conflict 1", "Conflict 2", "Conflict 3".

  1. **Conflict Title/Identifier:**
     * Type: Text Input
     * Description: A short name for the conflict (e.g., "War with the Orcs", "Guild Rivalry", "Ancient Curse"). (Not explicitly on PDF but good for organization).
  2. **Adventurers vs. (Antagonist/Situation):**
     * Type: Text Input
     * Description: The primary opposing force or situation for this conflict.
  3. **Notes:**
     * Type: Text Area
     * Description: Detailed notes about the conflict, including key players, stakes, potential resolutions, progress, etc.

### 5.8 Magic Item Tracker

* **Purpose:** To list available or planned magic items in the campaign, categorized by rarity and character level tiers.
* **Cardinality:** Singular per campaign (as per user's initial specification and PDF layout).
* **Structure:** The tracker is organized by character level tiers. Within each tier, items are listed under their rarity.
* **Level Tiers:**
  * Levels 1-4
  * Levels 5-10
  * Levels 11-16
  * Levels 17-20
* **Fields (For each Level Tier):**
  * **Rarities and Items:**
    * *PRD Note for LLM:* For each rarity within a tier (Common, Uncommon, Rare, Very Rare, Legendary), the application should allow the user to input a list of item names. The PDF shows a fixed number of items per rarity/tier (e.g., "6 COMMON" for Levels 1-4). The application could either:
      * A) Provide text fields for each item slot shown on the PDF.
      * B) More flexibly, allow the user to add/remove item names under each rarity heading, perhaps with a counter to show how many are listed vs. the PDF's suggestion. Option B is preferred for flexibility.
    * **Common Items:**
      * Type: Dynamic List of Text Inputs (Item Names)
    * **Uncommon Items:**
      * Type: Dynamic List of Text Inputs (Item Names)
    * **Rare Items:**
      * Type: Dynamic List of Text Inputs (Item Names)
    * **Very Rare Items:** (Not present in Levels 1-4 on PDF)
      * Type: Dynamic List of Text Inputs (Item Names)
    * **Legendary Items:** (Not present in Levels 1-4 & 5-10 on PDF)
      * Type: Dynamic List of Text Inputs (Item Names)
* **Example for "Levels 1-4" section:**
  * **Common:** Text Area or list for up to 6 items.
  * **Uncommon:** Text Area or list for up to 4 items.
  * **Rare:** Text Area or list for 1 item.

### 5.9 Bastion Tracker

* **Purpose:** To track details about a player character's bastion (stronghold, base of operations).
* **Cardinality:** Multiple instances per campaign (one for each character who has a bastion, or potentially multiple bastions if the campaign supports it).
* **Fields (Overall Bastion):**

  1. **Bastion's Name:**
     * Type: Text Input
  2. **Character's Name:**
     * Type: Text Input
     * Description: The PC who owns or is associated with this bastion.
  3. **Level:**
     * Type: Number Input
     * Description: Level of the bastion or character level at the time of tracking.
* **Fields (Per Special Facility - A bastion can have multiple special facilities):**

  * *PRD Note for LLM:* The UI should allow adding multiple "Special Facility" sections to a single Bastion Tracker entry. The PDF shows space for six.

  1. **Facility Type/Name:**
     * Type: Text Input (Corresponds to "SPECIAL FACILITY" on PDF)
  2. **Space:**
     * Type: Text Input (e.g., "1 room", "5 units")
     * Description: Space occupied or required by the facility.
  3. **Order:**
     * Type: Text Input
     * Description: Any specific order or group associated with the facility.
  4. **Hirelings:**
     * Type: Text Area
     * Description: Details about hirelings associated with this facility.
  5. **Notes:**
     * Type: Text Area
     * Description: General notes about this specific facility.
* **General Fields (for the Bastion as a whole, if not tied to a specific facility):**

  1. **Basic Facilities:**
     * Type: Text Area
     * Description: Description of the bastion's common or basic facilities.
  2. **Bastion Defenders:**
     * Type: Text Area
     * Description: Details about the general defenders of the bastion.
