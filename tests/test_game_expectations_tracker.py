import unittest
from src.data_models import Campaign, GameExpectationsEntry, SensitiveElement

class TestGameExpectationsTrackerData(unittest.TestCase):

    def setUp(self):
        self.campaign = Campaign(campaign_id="ge_test_camp", name="Test Campaign for Game Expectations")

    def test_add_game_expectations_entry(self):
        """Test adding a game expectations entry."""
        ge_data = GameExpectationsEntry(player_name="Alice", dm_name="Bob", game_theme_flavor="High Fantasy")
        self.campaign.game_expectations[ge_data.entry_id] = ge_data

        self.assertIn(ge_data.entry_id, self.campaign.game_expectations)
        self.assertEqual(self.campaign.game_expectations[ge_data.entry_id].player_name, "Alice")
        self.assertEqual(len(self.campaign.game_expectations), 1)

    def test_edit_game_expectations_entry(self):
        """Test editing an existing game expectations entry."""
        ge_data = GameExpectationsEntry(player_name="Charlie", player_hopes="Lots of treasure")
        self.campaign.game_expectations[ge_data.entry_id] = ge_data

        entry_to_edit = self.campaign.game_expectations[ge_data.entry_id]
        entry_to_edit.player_hopes = "Epic story and character development"
        se = SensitiveElement(name="Snakes", hard_limit=True)
        entry_to_edit.sensitive_elements.append(se)

        self.assertEqual(self.campaign.game_expectations[ge_data.entry_id].player_hopes, "Epic story and character development")
        self.assertEqual(len(self.campaign.game_expectations[ge_data.entry_id].sensitive_elements), 1)
        self.assertEqual(self.campaign.game_expectations[ge_data.entry_id].sensitive_elements[0].name, "Snakes")

    def test_delete_game_expectations_entry(self):
        """Test deleting a game expectations entry."""
        ge1 = GameExpectationsEntry(player_name="Dave")
        ge2 = GameExpectationsEntry(player_name="Eve")
        self.campaign.game_expectations[ge1.entry_id] = ge1
        self.campaign.game_expectations[ge2.entry_id] = ge2

        self.assertEqual(len(self.campaign.game_expectations), 2)

        del self.campaign.game_expectations[ge1.entry_id]

        self.assertEqual(len(self.campaign.game_expectations), 1)
        self.assertNotIn(ge1.entry_id, self.campaign.game_expectations)
        self.assertIn(ge2.entry_id, self.campaign.game_expectations)

    def test_add_sensitive_element(self):
        """Test adding a sensitive element to an entry."""
        ge_data = GameExpectationsEntry(player_name="Frank")
        self.campaign.game_expectations[ge_data.entry_id] = ge_data

        entry = self.campaign.game_expectations[ge_data.entry_id]
        self.assertEqual(len(entry.sensitive_elements), 0)

        se_data = SensitiveElement(name="Gore", soft_limit=True)
        entry.sensitive_elements.append(se_data)

        self.assertEqual(len(self.campaign.game_expectations[ge_data.entry_id].sensitive_elements), 1)
        self.assertEqual(self.campaign.game_expectations[ge_data.entry_id].sensitive_elements[0].name, "Gore")

if __name__ == '__main__':
    unittest.main()
