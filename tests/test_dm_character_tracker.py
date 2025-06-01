import unittest
from src.data_models import Campaign, DMCharacterEntry

class TestDMCharacterTrackerData(unittest.TestCase):

    def setUp(self):
        self.campaign = Campaign(campaign_id="dmc_test_camp", name="Test Campaign for DM Characters")

    def test_add_dm_character(self):
        """Test adding a DM character entry."""
        dmc_data = DMCharacterEntry(character_name="Elminster", player_name="DM", char_class="Wizard", level=20)
        self.campaign.dm_characters[dmc_data.entry_id] = dmc_data

        self.assertIn(dmc_data.entry_id, self.campaign.dm_characters)
        self.assertEqual(self.campaign.dm_characters[dmc_data.entry_id].character_name, "Elminster")
        self.assertEqual(len(self.campaign.dm_characters), 1)

    def test_edit_dm_character(self):
        """Test editing an existing DM character entry."""
        dmc_data = DMCharacterEntry(character_name="Shadowheart", level=3)
        self.campaign.dm_characters[dmc_data.entry_id] = dmc_data

        entry_to_edit = self.campaign.dm_characters[dmc_data.entry_id]
        entry_to_edit.level = 4
        entry_to_edit.goals_ambitions = "Uncover her past."
        entry_to_edit.player_motivations.append("Storytelling")

        self.assertEqual(self.campaign.dm_characters[dmc_data.entry_id].level, 4)
        self.assertEqual(self.campaign.dm_characters[dmc_data.entry_id].goals_ambitions, "Uncover her past.")
        self.assertIn("Storytelling", self.campaign.dm_characters[dmc_data.entry_id].player_motivations)

    def test_delete_dm_character(self):
        """Test deleting a DM character entry."""
        dmc1 = DMCharacterEntry(character_name="Astarion")
        dmc2 = DMCharacterEntry(character_name="Gale")
        self.campaign.dm_characters[dmc1.entry_id] = dmc1
        self.campaign.dm_characters[dmc2.entry_id] = dmc2

        self.assertEqual(len(self.campaign.dm_characters), 2)

        del self.campaign.dm_characters[dmc1.entry_id]

        self.assertEqual(len(self.campaign.dm_characters), 1)
        self.assertNotIn(dmc1.entry_id, self.campaign.dm_characters)
        self.assertIn(dmc2.entry_id, self.campaign.dm_characters)

if __name__ == '__main__':
    unittest.main()
