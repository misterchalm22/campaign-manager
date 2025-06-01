import json
import logging
import os
from dataclasses import asdict, is_dataclass
from typing import TypeVar, Type, Dict, List, Any

from src.data_models import (
    ApplicationData, Campaign, GameExpectationsEntry, SensitiveElement,
    TravelPlanEntry, TravelStage, NPCEntry, SettlementEntry,
    CampaignJournalEntry, DMCharacterEntry, CampaignConflictEntry, Conflict,
    MagicItemTrackerData, MagicItemTierData, BastionEntry, BastionFacility
)

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

T = TypeVar('T')

def _from_dict(data_class: Type[T], data: Dict[str, Any]) -> T:
    """
    Helper function to recursively convert a dictionary to a dataclass instance.
    Handles nested dataclasses and lists of dataclasses.
    """
    if not isinstance(data, dict):
        # If data is not a dict, it might be a primitive type for a list, or an error
        if data_class in [str, int, bool, float] or data is None:
             return data # type: ignore
        logging.warning(f"Expected a dict for {data_class.__name__}, but got {type(data)}. Returning None or default.")
        # Attempt to return a default instance if possible, otherwise this will likely error upstream
        try:
            return data_class() # type: ignore
        except TypeError: # pragma: no cover
            logging.error(f"Could not create a default instance for {data_class.__name__}")
            return None # type: ignore


    kwargs = {}
    for field_name, field_type in data_class.__annotations__.items():
        field_data = data.get(field_name)
        if field_data is None:
            # If field_data is None, rely on dataclass default_factory or default value
            # Check if field has a default value or factory in the dataclass
            if hasattr(data_class, field_name) and getattr(data_class, field_name) is not None:
                 kwargs[field_name] = getattr(data_class, field_name)
            elif hasattr(data_class.__dataclass_fields__[field_name], 'default_factory') \
                    and data_class.__dataclass_fields__[field_name].default_factory is not None:
                kwargs[field_name] = data_class.__dataclass_fields__[field_name].default_factory()
            else:
                kwargs[field_name] = None # Or some other sensible default if None is not appropriate
            continue

        origin_type = getattr(field_type, '__origin__', None)
        args_type = getattr(field_type, '__args__', ())

        if origin_type is list and args_type and is_dataclass(args_type[0]):
            # List of dataclasses
            kwargs[field_name] = [_from_dict(args_type[0], item) for item in field_data if isinstance(item, dict)]
        elif origin_type is dict and args_type and len(args_type) == 2 and is_dataclass(args_type[1]):
            # Dict of [str, dataclass]
            kwargs[field_name] = {k: _from_dict(args_type[1], v) for k, v in field_data.items() if isinstance(v, dict)}
        elif is_dataclass(field_type):
            # Nested dataclass
            kwargs[field_name] = _from_dict(field_type, field_data)
        else:
            # Primitive type or list of primitives
            kwargs[field_name] = field_data

    try:
        return data_class(**kwargs) # type: ignore
    except TypeError as e: # pragma: no cover
        logging.error(f"TypeError reconstructing {data_class.__name__} with kwargs {kwargs}: {e}")
        logging.error(f"Original data for {data_class.__name__}: {data}")
        # Attempt to return a default instance if construction fails
        try:
            return data_class() # type: ignore
        except TypeError:
            logging.error(f"Could not create a default instance for {data_class.__name__} after TypeError.")
            return None # type: ignore


def save_data(application_data: ApplicationData, filepath: str) -> bool:
    """
    Saves the ApplicationData object to a JSON file.

    Args:
        application_data: The ApplicationData object to save.
        filepath: The path to the file where data should be saved.

    Returns:
        True if saving was successful, False otherwise.
    """
    try:
        data_dict = asdict(application_data)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=4, ensure_ascii=False)
        logging.info(f"Data successfully saved to {filepath}")
        return True
    except IOError as e: # pragma: no cover
        logging.error(f"IOError saving data to {filepath}: {e}")
    except PermissionError as e: # pragma: no cover
        logging.error(f"PermissionError saving data to {filepath}: {e}")
    except TypeError as e: # pragma: no cover
        # This can happen if asdict encounters non-serializable data not caught by dataclass structure
        logging.error(f"TypeError during serialization: {e}. Check data_models for non-serializable types.")
    except Exception as e: # pragma: no cover
        logging.error(f"An unexpected error occurred while saving data to {filepath}: {e}")
    return False

def load_data(filepath: str) -> ApplicationData:
    """
    Loads ApplicationData from a JSON file.

    Args:
        filepath: The path to the file from which to load data.

    Returns:
        An ApplicationData object. If the file doesn't exist or is corrupted,
        a new ApplicationData instance with default values is returned.
    """
    if not os.path.exists(filepath):
        logging.info(f"File {filepath} not found. Returning new ApplicationData instance.")
        return ApplicationData()

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data_dict = json.load(f)

        # Start reconstruction from the top-level ApplicationData
        return _from_dict(ApplicationData, data_dict)

    except IOError as e: # pragma: no cover
        logging.error(f"IOError loading data from {filepath}: {e}. Returning new ApplicationData.")
    except json.JSONDecodeError as e: # pragma: no cover
        logging.error(f"JSONDecodeError loading data from {filepath}: {e}. File might be corrupted. Returning new ApplicationData.")
    except Exception as e: # pragma: no cover
        logging.error(f"An unexpected error occurred while loading data from {filepath}: {e}. Returning new ApplicationData.")

    return ApplicationData()

# Example Usage (for testing purposes, can be removed or commented out)
if __name__ == '__main__': # pragma: no cover
    # Create sample data
    app_data = ApplicationData(active_campaign_id="campaign1")

    campaign1 = Campaign(campaign_id="campaign1", name="Curse of Strahd", dm_name_global="Test DM")

    # Game Expectations
    ge1_sens_el = SensitiveElement(name="Spiders", hard_limit=True)
    ge1 = GameExpectationsEntry(entry_id="ge1", player_name="Alice", game_theme_flavor="Gothic Horror", sensitive_elements=[ge1_sens_el])
    campaign1.game_expectations["ge1"] = ge1

    # Travel Plan
    tp1_stage1 = TravelStage(stage_id="s1", stage_number_id="1", start_location="Village A", end_location="Forest B", distance="10 miles")
    tp1 = TravelPlanEntry(entry_id="tp1", journey_name="To the Woods", stages=[tp1_stage1])
    campaign1.travel_plans["tp1"] = tp1

    # NPC
    npc1 = NPCEntry(entry_id="npc1", name="Ismark Kolyanovich", alignment="LG", personality="Stern but kind")
    campaign1.npcs["npc1"] = npc1

    # Settlement
    settlement1 = SettlementEntry(entry_id="set1", name="Barovia Village", size="Village", defining_trait="Gloomy")
    campaign1.settlements["set1"] = settlement1

    # Journal
    journal1 = CampaignJournalEntry(entry_id="j1", session_number=1, session_title="Arrival in Barovia")
    campaign1.campaign_journal["j1"] = journal1

    # DM Character
    dm_char1 = DMCharacterEntry(entry_id="dmc1", character_name="Ireena Kolyana", player_name="PlayerNPC", char_class="Noble")
    campaign1.dm_characters["dmc1"] = dm_char1

    # Conflicts
    conflict1 = Conflict(conflict_id="conf1", title_identifier="Strahd's Domination", antagonist_situation="Count Strahd von Zarovich")
    campaign1.campaign_conflicts = CampaignConflictEntry(conflicts=[conflict1])

    # Magic Items
    campaign1.magic_item_tracker.level_tier_1_4.common_items.append("Potion of Healing")

    # Bastions
    facility1 = BastionFacility(facility_id="fac1", facility_type_name="Library", space="1 room")
    bastion1 = BastionEntry(entry_id="bas1", bastion_name="Old Mill", character_name="Party", special_facilities=[facility1])
    campaign1.bastions["bas1"] = bastion1

    app_data.campaigns["campaign1"] = campaign1

    # Test save
    FILEPATH = "test_app_data.json"
    if save_data(app_data, FILEPATH):
        logging.info("Sample data saved successfully.")

        # Test load
        loaded_app_data = load_data(FILEPATH)
        if loaded_app_data and loaded_app_data.campaigns:
            logging.info("Sample data loaded successfully.")
            logging.info(f"Loaded active campaign ID: {loaded_app_data.active_campaign_id}")
            if "campaign1" in loaded_app_data.campaigns:
                loaded_campaign1 = loaded_app_data.campaigns["campaign1"]
                logging.info(f"Loaded campaign name: {loaded_campaign1.name}")
                if "ge1" in loaded_campaign1.game_expectations:
                    logging.info(f"Loaded GE Player: {loaded_campaign1.game_expectations['ge1'].player_name}")
                    if loaded_campaign1.game_expectations['ge1'].sensitive_elements:
                         logging.info(f"Loaded Sensitive Element: {loaded_campaign1.game_expectations['ge1'].sensitive_elements[0].name}")
                if "tp1" in loaded_campaign1.travel_plans and loaded_campaign1.travel_plans["tp1"].stages:
                     logging.info(f"Loaded Travel Stage Start: {loaded_campaign1.travel_plans['tp1'].stages[0].start_location}")
                if loaded_campaign1.campaign_conflicts and loaded_campaign1.campaign_conflicts.conflicts:
                    logging.info(f"Loaded Conflict Title: {loaded_campaign1.campaign_conflicts.conflicts[0].title_identifier}")
                if loaded_campaign1.magic_item_tracker.level_tier_1_4.common_items:
                    logging.info(f"Loaded Magic Item: {loaded_campaign1.magic_item_tracker.level_tier_1_4.common_items[0]}")
            # Basic check:
            assert loaded_app_data.campaigns["campaign1"].name == "Curse of Strahd"
            assert loaded_app_data.campaigns["campaign1"].npcs["npc1"].name == "Ismark Kolyanovich"
            assert loaded_app_data.campaigns["campaign1"].game_expectations["ge1"].sensitive_elements[0].name == "Spiders"
            logging.info("Basic assertions passed.")
        else:
            logging.error("Failed to load or parse sample data correctly.")

        # Clean up test file
        # os.remove(FILEPATH) # Comment out to inspect the file
    else:
        logging.error("Failed to save sample data.")
