import unittest
from src.data_models import Campaign, NPCEntry

class TestNPCTrackerData(unittest.TestCase):

    def setUp(self):
        self.campaign = Campaign(campaign_id="test_camp", name="Test Campaign for NPCs")

    def test_add_npc(self):
        """Test adding an NPC to the campaign."""
        npc_data = NPCEntry(name="Gorok", alignment="LE", stat_block_source="Custom")
        # In the actual UI, the widget would add the npc_data to campaign.npcs dictionary
        # using npc_data.entry_id as the key.
        self.campaign.npcs[npc_data.entry_id] = npc_data

        self.assertIn(npc_data.entry_id, self.campaign.npcs)
        self.assertEqual(self.campaign.npcs[npc_data.entry_id].name, "Gorok")
        self.assertEqual(len(self.campaign.npcs), 1)

    def test_edit_npc(self):
        """Test editing an existing NPC in the campaign."""
        npc_data = NPCEntry(name="Lysa", personality="Quiet")
        self.campaign.npcs[npc_data.entry_id] = npc_data

        # Simulate editing: Fetch the object and modify it
        npc_to_edit = self.campaign.npcs[npc_data.entry_id]
        npc_to_edit.name = "Lysandra"
        npc_to_edit.personality = "Brave and outspoken"
        npc_to_edit.alignment = "NG"

        # Re-assigning is not strictly necessary if the object is mutable and modified in place,
        # but if the UI were to replace the entry, this would be the pattern.
        # self.campaign.npcs[npc_data.entry_id] = npc_to_edit
        # For dataclasses, modifications are in-place.

        self.assertEqual(self.campaign.npcs[npc_data.entry_id].name, "Lysandra")
        self.assertEqual(self.campaign.npcs[npc_data.entry_id].personality, "Brave and outspoken")
        self.assertEqual(self.campaign.npcs[npc_data.entry_id].alignment, "NG")

    def test_delete_npc(self):
        """Test deleting an NPC from the campaign."""
        npc1 = NPCEntry(name="ToDelete")
        npc2 = NPCEntry(name="ToKeep")
        self.campaign.npcs[npc1.entry_id] = npc1
        self.campaign.npcs[npc2.entry_id] = npc2

        self.assertEqual(len(self.campaign.npcs), 2)

        # Simulate deletion
        del self.campaign.npcs[npc1.entry_id]

        self.assertEqual(len(self.campaign.npcs), 1)
        self.assertNotIn(npc1.entry_id, self.campaign.npcs)
        self.assertIn(npc2.entry_id, self.campaign.npcs)

if __name__ == '__main__':
    unittest.main()
