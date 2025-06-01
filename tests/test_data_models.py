import unittest
import uuid
from src.data_models import (
    ApplicationData, Campaign, NPCEntry, GameExpectationsEntry, SensitiveElement,
    TravelPlanEntry, TravelStage, SettlementEntry, CampaignJournalEntry,
    DMCharacterEntry, Conflict, CampaignConflictEntry, MagicItemTierData,
    MagicItemTrackerData, BastionFacility, BastionEntry
)

class TestDataModels(unittest.TestCase):

    def test_campaign_creation(self):
        """Test Campaign model creation and default values."""
        campaign_id = str(uuid.uuid4())
        campaign = Campaign(campaign_id=campaign_id, name="Test Campaign")
        self.assertEqual(campaign.campaign_id, campaign_id)
        self.assertEqual(campaign.name, "Test Campaign")
        self.assertEqual(campaign.game_expectations, {})
        self.assertEqual(campaign.travel_plans, {})
        self.assertEqual(campaign.npcs, {})
        self.assertEqual(campaign.settlements, {})
        self.assertEqual(campaign.campaign_journal, {})
        self.assertEqual(campaign.dm_characters, {})
        self.assertIsInstance(campaign.campaign_conflicts, CampaignConflictEntry)
        self.assertEqual(campaign.campaign_conflicts.conflicts, [])
        self.assertIsInstance(campaign.magic_item_tracker, MagicItemTrackerData)
        self.assertEqual(campaign.bastions, {})
        self.assertEqual(campaign.dm_name_global, "")

    def test_npc_entry_creation(self):
        """Test NPCEntry creation and ID generation."""
        npc1 = NPCEntry(name="Goblin")
        npc2 = NPCEntry(name="Orc")
        self.assertIsNotNone(npc1.entry_id)
        self.assertTrue(npc1.entry_id.startswith("npc_"))
        self.assertNotEqual(npc1.entry_id, npc2.entry_id)
        self.assertEqual(npc1.name, "Goblin")
        self.assertEqual(npc1.stat_block_source, "")

    def test_game_expectations_entry(self):
        """Test GameExpectationsEntry and nested SensitiveElement."""
        ge = GameExpectationsEntry(player_name="Player1")
        self.assertEqual(ge.player_name, "Player1")
        self.assertEqual(ge.sensitive_elements, [])

        se1 = SensitiveElement(name="Spiders", hard_limit=True)
        ge.sensitive_elements.append(se1)
        self.assertEqual(len(ge.sensitive_elements), 1)
        self.assertEqual(ge.sensitive_elements[0].name, "Spiders")
        self.assertTrue(ge.sensitive_elements[0].hard_limit)

    def test_travel_plan_and_stages(self):
        """Test TravelPlanEntry and adding TravelStage."""
        tp = TravelPlanEntry(journey_name="To the Mountains")
        self.assertEqual(tp.journey_name, "To the Mountains")
        self.assertEqual(tp.stages, [])

        stage1 = TravelStage(start_location="Town", end_location="Foothills")
        tp.stages.append(stage1)
        self.assertEqual(len(tp.stages), 1)
        self.assertEqual(tp.stages[0].start_location, "Town")
        self.assertTrue(stage1.stage_id.startswith("ts_"))

    def test_settlement_entry(self):
        """Test SettlementEntry creation."""
        settlement = SettlementEntry(name="Oakhaven", size="Village")
        self.assertEqual(settlement.name, "Oakhaven")
        self.assertEqual(settlement.size, "Village")
        self.assertTrue(settlement.entry_id.startswith("set_"))

    def test_campaign_journal_entry(self):
        """Test CampaignJournalEntry creation."""
        entry = CampaignJournalEntry(session_number=1, session_title="First Steps")
        self.assertEqual(entry.session_number, 1)
        self.assertEqual(entry.session_title, "First Steps")
        self.assertTrue(entry.entry_id.startswith("cj_"))

    def test_dm_character_entry(self):
        """Test DMCharacterEntry creation."""
        dmc = DMCharacterEntry(character_name="Gandalf", level=15)
        self.assertEqual(dmc.character_name, "Gandalf")
        self.assertEqual(dmc.level, 15)
        self.assertTrue(dmc.entry_id.startswith("dmc_"))
        self.assertEqual(dmc.player_motivations, [])

    def test_conflict_and_campaign_conflict_entry(self):
        """Test Conflict and CampaignConflictEntry."""
        campaign_conflicts_container = CampaignConflictEntry()
        self.assertEqual(campaign_conflicts_container.conflicts, [])

        conflict1 = Conflict(title_identifier="Goblin War", antagonist_situation="Goblins")
        campaign_conflicts_container.conflicts.append(conflict1)

        self.assertEqual(len(campaign_conflicts_container.conflicts), 1)
        self.assertEqual(campaign_conflicts_container.conflicts[0].title_identifier, "Goblin War")
        self.assertTrue(conflict1.conflict_id.startswith("conf_"))

        # Test adding to Campaign
        campaign = Campaign(name="Conflict Campaign")
        campaign.campaign_conflicts.conflicts.append(conflict1)
        self.assertEqual(len(campaign.campaign_conflicts.conflicts), 1)
        self.assertEqual(campaign.campaign_conflicts.conflicts[0].antagonist_situation, "Goblins")

    def test_magic_item_tracker(self):
        """Test MagicItemTrackerData and MagicItemTierData."""
        mit_data = MagicItemTrackerData()
        self.assertIsInstance(mit_data.level_tier_1_4, MagicItemTierData)
        self.assertEqual(mit_data.level_tier_1_4.common_items, [])

        mit_data.level_tier_5_10.uncommon_items.append("Bag of Holding")
        self.assertEqual(len(mit_data.level_tier_5_10.uncommon_items), 1)
        self.assertEqual(mit_data.level_tier_5_10.uncommon_items[0], "Bag of Holding")

        # Test adding to Campaign
        campaign = Campaign(name="Magic Campaign")
        campaign.magic_item_tracker.level_tier_1_4.rare_items.append("Amulet of Health")
        self.assertIn("Amulet of Health", campaign.magic_item_tracker.level_tier_1_4.rare_items)

    def test_bastion_and_facility(self):
        """Test BastionEntry and BastionFacility."""
        facility = BastionFacility(facility_type_name="Library", space="10 units")
        self.assertEqual(facility.facility_type_name, "Library")
        self.assertTrue(facility.facility_id.startswith("bf_"))

        bastion = BastionEntry(bastion_name="North Keep", level=3)
        self.assertEqual(bastion.bastion_name, "North Keep")
        self.assertTrue(bastion.entry_id.startswith("bas_"))
        self.assertEqual(bastion.special_facilities, [])

        bastion.special_facilities.append(facility)
        self.assertEqual(len(bastion.special_facilities), 1)
        self.assertEqual(bastion.special_facilities[0].space, "10 units")

        # Test adding to Campaign (bastions is a dict)
        campaign = Campaign(name="Bastion Campaign")
        campaign.bastions[bastion.entry_id] = bastion
        self.assertIn(bastion.entry_id, campaign.bastions)
        self.assertEqual(campaign.bastions[bastion.entry_id].character_name, "")


    def test_application_data(self):
        """Test ApplicationData creation."""
        app_data = ApplicationData()
        self.assertEqual(app_data.campaigns, {})
        self.assertEqual(app_data.active_campaign_id, "")

        campaign1 = Campaign(campaign_id="camp1", name="Campaign One")
        app_data.campaigns["camp1"] = campaign1
        self.assertEqual(len(app_data.campaigns), 1)


if __name__ == '__main__':
    unittest.main()
