from dataclasses import dataclass, field
from typing import List, Dict, Any

# Forward declaration for Campaign to use in tracker dict value type hint
# This is not strictly necessary for dict values but good practice for complex types.
# However, Python's type hinting handles forward references for strings well.
# For now, we'll use 'Any' for simplicity in the trackers dict,
# as specific tracker types will be handled by application logic.

@dataclass
class SensitiveElement:
    name: str = ""
    hard_limit: bool = False
    soft_limit: bool = False

import uuid

@dataclass
class GameExpectationsEntry:
    entry_id: str = field(default_factory=lambda: f"ge_{uuid.uuid4().hex[:8]}")
    dm_name: str = ""
    player_name: str = ""
    game_theme_flavor: str = ""
    sensitive_elements: List[SensitiveElement] = field(default_factory=list)
    player_hopes: str = ""
    at_table_concerns: str = ""

@dataclass
class TravelStage:
    stage_id: str = field(default_factory=lambda: f"ts_{uuid.uuid4().hex[:8]}")
    stage_number_id: str = "" # User-defined identifier like "Stage 1"
    start_location: str = ""
    end_location: str = ""
    distance: str = ""
    terrain: str = ""
    weather: str = ""
    pace: str = "Normal"  # Options: "Fast", "Normal", "Slow"
    travel_time_value: int = 0
    travel_time_unit: str = "days"  # Options: "days", "hrs"
    narrative_notes: str = ""
    challenges: str = ""
    elapsed_time_total: str = ""

@dataclass
class TravelPlanEntry:
    entry_id: str = field(default_factory=lambda: f"tp_{uuid.uuid4().hex[:8]}")
    journey_name: str = ""
    origin: str = ""
    destination: str = ""
    stages: List[TravelStage] = field(default_factory=list)

@dataclass
class NPCEntry:
    entry_id: str = field(default_factory=lambda: f"npc_{uuid.uuid4().hex[:8]}")
    name: str = ""
    stat_block_source: str = ""
    mm_page: str = ""
    stat_block_alterations: str = ""
    alignment: str = ""
    personality: str = ""
    appearance: str = ""
    secret: str = ""

@dataclass
class SettlementEntry:
    entry_id: str = field(default_factory=lambda: f"set_{uuid.uuid4().hex[:8]}")
    name: str = ""
    size: str = "Village"  # Options: "Village", "Town", "City"
    defining_trait: str = ""
    claim_to_fame: str = ""
    current_calamity: str = ""
    local_leader: str = ""
    noteworthy_people: str = ""
    noteworthy_places: str = ""
    gp_value_most_expensive_item: str = ""

@dataclass
class CampaignJournalEntry:
    entry_id: str = field(default_factory=lambda: f"cj_{uuid.uuid4().hex[:8]}")
    session_number: int = 0
    session_date: str = ""  # Store as ISO date string e.g. "YYYY-MM-DD"
    session_title: str = ""
    earlier_events: str = ""
    planned_summary: str = ""
    additional_notes: str = ""

@dataclass
class DMCharacterEntry:
    entry_id: str = field(default_factory=lambda: f"dmc_{uuid.uuid4().hex[:8]}")
    character_name: str = ""
    player_name: str = ""
    player_motivations: List[str] = field(default_factory=list)
    notes_on_player_expectations: str = ""
    char_class: str = ""
    subclass: str = ""
    level: int = 1
    background: str = ""
    species_race: str = ""
    alignment: str = ""
    goals_ambitions: str = ""
    quirks_whims: str = ""
    magic_items_owned: str = ""
    character_details: str = ""
    family_friends_foes: str = ""
    adventure_ideas: str = ""

@dataclass
class Conflict:
    conflict_id: str = field(default_factory=lambda: f"conf_{uuid.uuid4().hex[:8]}")
    title_identifier: str = ""
    antagonist_situation: str = ""
    notes: str = ""

@dataclass
class CampaignConflictEntry: # Singular per campaign, but holds multiple conflicts
    # This entry itself doesn't need a unique ID if it's always singular and known.
    # If there's a possibility of this structure changing, an ID might be added.
    conflicts: List[Conflict] = field(default_factory=list)

@dataclass
class MagicItemTierData:
    common_items: List[str] = field(default_factory=list)
    uncommon_items: List[str] = field(default_factory=list)
    rare_items: List[str] = field(default_factory=list)
    very_rare_items: List[str] = field(default_factory=list)
    legendary_items: List[str] = field(default_factory=list)

@dataclass
class MagicItemTrackerData: # Singular per campaign
    # Similarly, no explicit ID needed if it's always one per campaign.
    level_tier_1_4: MagicItemTierData = field(default_factory=MagicItemTierData)
    level_tier_5_10: MagicItemTierData = field(default_factory=MagicItemTierData)
    level_tier_11_16: MagicItemTierData = field(default_factory=MagicItemTierData)
    level_tier_17_20: MagicItemTierData = field(default_factory=MagicItemTierData)

@dataclass
class BastionFacility:
    facility_id: str = field(default_factory=lambda: f"bf_{uuid.uuid4().hex[:8]}")
    facility_type_name: str = ""
    space: str = ""
    order_association: str = ""
    hirelings: str = ""
    notes: str = ""

@dataclass
class BastionEntry:
    entry_id: str = field(default_factory=lambda: f"bas_{uuid.uuid4().hex[:8]}")
    bastion_name: str = ""
    character_name: str = ""
    level: int = 0
    special_facilities: List[BastionFacility] = field(default_factory=list)
    basic_facilities_desc: str = ""
    bastion_defenders_desc: str = ""

# Main Campaign class to hold all data
@dataclass
class Campaign:
    campaign_id: str = "" # Unique ID for the campaign
    name: str = ""
    # The trackers dict will store lists of entries or single entry instances.
    # Keys will be tracker type names (e.g., "npc_tracker", "travel_planner").
    # Values will be Dict[str, Any] where str is entry_id and Any is the entry object
    # or for singular trackers, it could be Dict[str, TrackerData] e.g. {"magic_item_tracker": MagicItemTrackerData}
    game_expectations: Dict[str, GameExpectationsEntry] = field(default_factory=dict)
    travel_plans: Dict[str, TravelPlanEntry] = field(default_factory=dict)
    npcs: Dict[str, NPCEntry] = field(default_factory=dict)
    settlements: Dict[str, SettlementEntry] = field(default_factory=dict)
    campaign_journal: Dict[str, CampaignJournalEntry] = field(default_factory=dict)
    dm_characters: Dict[str, DMCharacterEntry] = field(default_factory=dict)
    campaign_conflicts: CampaignConflictEntry = field(default_factory=CampaignConflictEntry) # Singular
    magic_item_tracker: MagicItemTrackerData = field(default_factory=MagicItemTrackerData) # Singular
    bastions: Dict[str, BastionEntry] = field(default_factory=dict)
    # Any other global campaign settings can be added here.
    dm_name_global: str = "" # Example: Global DM name for the campaign

    # Note: The 'trackers: dict' from the prompt is implemented above as specific typed fields
    # for better clarity and type safety, e.g., `npcs: Dict[str, NPCEntry]`.
    # A generic `trackers: Dict[str, Any]` could also be used if dynamic tracker types
    # were a requirement, but explicit fields are generally safer for known types.
    # If a generic dict is strictly needed, it can be added, but the current structure is more robust.

    def __post_init__(self):
        # Ensure default factories are called, though usually dataclasses handle this.
        # This is more for complex initializations if needed.
        if self.campaign_conflicts is None:
            self.campaign_conflicts = CampaignConflictEntry()
        if self.magic_item_tracker is None:
            self.magic_item_tracker = MagicItemTrackerData()

# Example of how you might store all campaigns in an application
@dataclass
class ApplicationData:
    campaigns: Dict[str, Campaign] = field(default_factory=dict)
    # Global application settings can go here
    active_campaign_id: str = ""
