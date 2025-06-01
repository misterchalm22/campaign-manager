import unittest
from src.data_models import Campaign, CampaignJournalEntry

class TestCampaignJournalData(unittest.TestCase):

    def setUp(self):
        self.campaign = Campaign(campaign_id="journal_test_camp", name="Test Campaign for Journal")

    def test_add_journal_entry(self):
        """Test adding a journal entry."""
        entry_data = CampaignJournalEntry(session_number=1, session_title="The Beginning", session_date="2024-01-01")
        # Keyed by entry_id
        self.campaign.campaign_journal[entry_data.entry_id] = entry_data

        self.assertIn(entry_data.entry_id, self.campaign.campaign_journal)
        self.assertEqual(self.campaign.campaign_journal[entry_data.entry_id].session_title, "The Beginning")
        self.assertEqual(len(self.campaign.campaign_journal), 1)

    def test_edit_journal_entry(self):
        """Test editing an existing journal entry."""
        entry_data = CampaignJournalEntry(session_number=2, session_title="Old Title")
        self.campaign.campaign_journal[entry_data.entry_id] = entry_data

        entry_to_edit = self.campaign.campaign_journal[entry_data.entry_id]
        entry_to_edit.session_title = "A New Chapter"
        entry_to_edit.additional_notes = "Something important happened."

        self.assertEqual(self.campaign.campaign_journal[entry_data.entry_id].session_title, "A New Chapter")
        self.assertEqual(self.campaign.campaign_journal[entry_data.entry_id].additional_notes, "Something important happened.")

    def test_delete_journal_entry(self):
        """Test deleting a journal entry."""
        entry1 = CampaignJournalEntry(session_number=1, session_title="First Entry")
        entry2 = CampaignJournalEntry(session_number=2, session_title="Second Entry")
        self.campaign.campaign_journal[entry1.entry_id] = entry1
        self.campaign.campaign_journal[entry2.entry_id] = entry2

        self.assertEqual(len(self.campaign.campaign_journal), 2)

        del self.campaign.campaign_journal[entry1.entry_id]

        self.assertEqual(len(self.campaign.campaign_journal), 1)
        self.assertNotIn(entry1.entry_id, self.campaign.campaign_journal)
        self.assertIn(entry2.entry_id, self.campaign.campaign_journal)

if __name__ == '__main__':
    unittest.main()
