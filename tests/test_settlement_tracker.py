import unittest
from src.data_models import Campaign, SettlementEntry

class TestSettlementTrackerData(unittest.TestCase):

    def setUp(self):
        self.campaign = Campaign(campaign_id="settlement_test_camp", name="Test Campaign for Settlements")

    def test_add_settlement(self):
        """Test adding a settlement."""
        settlement_data = SettlementEntry(name="Oakhaven", size="Village", defining_trait="Old Oak")
        self.campaign.settlements[settlement_data.entry_id] = settlement_data

        self.assertIn(settlement_data.entry_id, self.campaign.settlements)
        self.assertEqual(self.campaign.settlements[settlement_data.entry_id].name, "Oakhaven")
        self.assertEqual(len(self.campaign.settlements), 1)

    def test_edit_settlement(self):
        """Test editing an existing settlement."""
        settlement_data = SettlementEntry(name="Bridgewater", size="Town")
        self.campaign.settlements[settlement_data.entry_id] = settlement_data

        entry_to_edit = self.campaign.settlements[settlement_data.entry_id]
        entry_to_edit.name = "Stonebridge"
        entry_to_edit.current_calamity = "Orc raids nearby"

        self.assertEqual(self.campaign.settlements[settlement_data.entry_id].name, "Stonebridge")
        self.assertEqual(self.campaign.settlements[settlement_data.entry_id].current_calamity, "Orc raids nearby")

    def test_delete_settlement(self):
        """Test deleting a settlement."""
        s1 = SettlementEntry(name="ToDelete")
        s2 = SettlementEntry(name="ToKeep")
        self.campaign.settlements[s1.entry_id] = s1
        self.campaign.settlements[s2.entry_id] = s2

        self.assertEqual(len(self.campaign.settlements), 2)

        del self.campaign.settlements[s1.entry_id]

        self.assertEqual(len(self.campaign.settlements), 1)
        self.assertNotIn(s1.entry_id, self.campaign.settlements)
        self.assertIn(s2.entry_id, self.campaign.settlements)

if __name__ == '__main__':
    unittest.main()
