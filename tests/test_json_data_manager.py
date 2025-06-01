import unittest
import os
import tempfile
import uuid
from src.data_models import (
    ApplicationData, Campaign, NPCEntry, GameExpectationsEntry, SensitiveElement,
    TravelPlanEntry, TravelStage, SettlementEntry, CampaignJournalEntry,
    DMCharacterEntry, Conflict, CampaignConflictEntry, MagicItemTierData,
    MagicItemTrackerData, BastionFacility, BastionEntry
)
from src.json_data_manager import save_data, load_data

class TestJsonDataManager(unittest.TestCase):

    def setUp(self):
        # Create a temporary file for saving/loading
        self.temp_fd, self.temp_filepath = tempfile.mkstemp(suffix=".json")
        os.close(self.temp_fd) # Close the file descriptor

    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.temp_filepath):
            os.remove(self.temp_filepath)

    def _create_sample_application_data(self) -> ApplicationData:
        """Helper method to create a complex ApplicationData object for testing."""
        app_data = ApplicationData(active_campaign_id="campaign1")

        # Campaign 1
        campaign1 = Campaign(campaign_id="campaign1", name="The Dragon's Hoard", dm_name_global="AI DM")

        # NPC
        npc1 = NPCEntry(name="Grog", alignment="CN", stat_block_source="Monster Manual")
        campaign1.npcs[npc1.entry_id] = npc1

        # Game Expectations
        ge1 = GameExpectationsEntry(player_name="Alice", dm_name="AI DM")
        ge1.sensitive_elements.append(SensitiveElement(name="Heights", soft_limit=True))
        campaign1.game_expectations[ge1.entry_id] = ge1

        # Travel Plan
        tp1 = TravelPlanEntry(journey_name="Journey to the Peak")
        ts1 = TravelStage(start_location="Base Camp", end_location="Summit", distance="3 days")
        tp1.stages.append(ts1)
        campaign1.travel_plans[tp1.entry_id] = tp1

        # Settlement
        set1 = SettlementEntry(name="Oakhaven", size="Town", defining_trait="Ancient Oak Tree")
        campaign1.settlements[set1.entry_id] = set1

        # Journal
        cj1 = CampaignJournalEntry(session_number=3, session_title="The Plot Thickens", session_date="2024-03-10")
        campaign1.campaign_journal[cj1.entry_id] = cj1

        # DM Character
        dmc1 = DMCharacterEntry(character_name="Elara", player_name="Bob", char_class="Wizard", level=5)
        dmc1.player_motivations.append("Exploring")
        campaign1.dm_characters[dmc1.entry_id] = dmc1

        # Campaign Conflict
        conf1 = Conflict(title_identifier="Orc Raids", antagonist_situation="Orc War Chief Grukk")
        campaign1.campaign_conflicts.conflicts.append(conf1)

        # Magic Items
        campaign1.magic_item_tracker.level_tier_1_4.common_items.append("Potion of Healing")
        campaign1.magic_item_tracker.level_tier_5_10.uncommon_items.append("Bag of Holding")

        # Bastion
        bf1 = BastionFacility(facility_type_name="Watchtower", space="Small", notes="Good view")
        bas1 = BastionEntry(bastion_name="Eagle's Peak", character_name="Elara", level=5)
        bas1.special_facilities.append(bf1)
        campaign1.bastions[bas1.entry_id] = bas1

        app_data.campaigns["campaign1"] = campaign1

        # Campaign 2 (simpler)
        campaign2 = Campaign(campaign_id="campaign2", name="The Lost Mine")
        npc2 = NPCEntry(name="Sildar Hallwinter")
        campaign2.npcs[npc2.entry_id] = npc2
        app_data.campaigns["campaign2"] = campaign2

        return app_data

    def test_save_and_load_data(self):
        """Test saving data to JSON and loading it back."""
        original_app_data = self._create_sample_application_data()

        # Save data
        save_success = save_data(original_app_data, self.temp_filepath)
        self.assertTrue(save_success, "save_data should return True on success")
        self.assertTrue(os.path.exists(self.temp_filepath), "JSON file should be created")

        # Load data
        loaded_app_data = load_data(self.temp_filepath)

        # Assertions
        self.assertIsNotNone(loaded_app_data, "Loaded data should not be None")
        self.assertIsInstance(loaded_app_data, ApplicationData, "Loaded data should be ApplicationData instance")

        # Compare top-level attributes
        self.assertEqual(original_app_data.active_campaign_id, loaded_app_data.active_campaign_id)
        self.assertEqual(len(original_app_data.campaigns), len(loaded_app_data.campaigns))

        # Detailed comparison of campaign data
        for campaign_id, original_campaign in original_app_data.campaigns.items():
            self.assertIn(campaign_id, loaded_app_data.campaigns)
            loaded_campaign = loaded_app_data.campaigns[campaign_id]

            # Using __dict__ for comparison as dataclasses with nested lists/dicts
            # might not compare equal directly if objects are different instances,
            # even if their contents are the same.
            # This is a common way to compare nested dataclasses loaded from JSON.
            self.assertEqual(original_campaign.__dict__, loaded_campaign.__dict__)

    def test_load_non_existent_file(self):
        """Test loading data from a non-existent file."""
        non_existent_filepath = os.path.join(os.path.dirname(self.temp_filepath), "does_not_exist.json")
        loaded_app_data = load_data(non_existent_filepath)

        self.assertIsNotNone(loaded_app_data, "Should return a default ApplicationData object")
        self.assertIsInstance(loaded_app_data, ApplicationData)
        self.assertEqual(len(loaded_app_data.campaigns), 0)
        self.assertEqual(loaded_app_data.active_campaign_id, "")

    def test_load_empty_file(self):
        """Test loading data from an empty JSON file."""
        with open(self.temp_filepath, 'w') as f:
            f.write("") # Empty file

        loaded_app_data = load_data(self.temp_filepath)
        self.assertIsNotNone(loaded_app_data)
        self.assertIsInstance(loaded_app_data, ApplicationData)
        self.assertEqual(len(loaded_app_data.campaigns), 0)

    def test_load_invalid_json_file(self):
        """Test loading data from a file with invalid JSON."""
        with open(self.temp_filepath, 'w') as f:
            f.write("{invalid_json_")

        loaded_app_data = load_data(self.temp_filepath)
        self.assertIsNotNone(loaded_app_data)
        self.assertIsInstance(loaded_app_data, ApplicationData)
        self.assertEqual(len(loaded_app_data.campaigns), 0) # Should return default on parse error

if __name__ == '__main__':
    unittest.main()
