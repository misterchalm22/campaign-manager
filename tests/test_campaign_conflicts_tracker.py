import unittest
from src.data_models import Campaign, Conflict, CampaignConflictEntry

class TestCampaignConflictsTrackerData(unittest.TestCase):

    def setUp(self):
        self.campaign = Campaign(campaign_id="conflict_test_camp", name="Test Campaign for Conflicts")
        # Ensure the campaign_conflicts attribute is initialized (as done in Campaign.__post_init__)
        if self.campaign.campaign_conflicts is None:
             self.campaign.campaign_conflicts = CampaignConflictEntry()


    def test_add_conflict(self):
        """Test adding a conflict."""
        conflict_data = Conflict(title_identifier="War of the Roses", antagonist_situation="House Lancaster vs House York")
        # The UI would append to campaign.campaign_conflicts.conflicts list
        self.campaign.campaign_conflicts.conflicts.append(conflict_data)

        self.assertEqual(len(self.campaign.campaign_conflicts.conflicts), 1)
        self.assertEqual(self.campaign.campaign_conflicts.conflicts[0].title_identifier, "War of the Roses")
        self.assertIsNotNone(self.campaign.campaign_conflicts.conflicts[0].conflict_id)

    def test_edit_conflict(self):
        """Test editing an existing conflict."""
        conflict_data = Conflict(title_identifier="Smuggling Ring", notes="Based in the docks.")
        self.campaign.campaign_conflicts.conflicts.append(conflict_data)

        # To edit, we'd find the conflict in the list and modify its attributes.
        # For this test, assume we have a reference to it (e.g., by iterating and finding by ID).
        conflict_to_edit = self.campaign.campaign_conflicts.conflicts[0]
        conflict_to_edit.title_identifier = "The Serpent's Coil Smuggling Ring"
        conflict_to_edit.notes = "Expanded operations to the upper city."

        self.assertEqual(self.campaign.campaign_conflicts.conflicts[0].title_identifier, "The Serpent's Coil Smuggling Ring")
        self.assertEqual(self.campaign.campaign_conflicts.conflicts[0].notes, "Expanded operations to the upper city.")

    def test_delete_conflict(self):
        """Test deleting a conflict."""
        c1 = Conflict(title_identifier="Conflict A")
        c2 = Conflict(title_identifier="Conflict B")
        self.campaign.campaign_conflicts.conflicts.extend([c1, c2])

        self.assertEqual(len(self.campaign.campaign_conflicts.conflicts), 2)

        # To delete, the UI would remove it from the list, e.g., by ID
        conflict_id_to_delete = c1.conflict_id
        self.campaign.campaign_conflicts.conflicts = [
            c for c in self.campaign.campaign_conflicts.conflicts if c.conflict_id != conflict_id_to_delete
        ]

        self.assertEqual(len(self.campaign.campaign_conflicts.conflicts), 1)
        self.assertEqual(self.campaign.campaign_conflicts.conflicts[0].title_identifier, "Conflict B")

if __name__ == '__main__':
    unittest.main()
