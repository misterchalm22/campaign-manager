import unittest
from src.data_models import Campaign, MagicItemTrackerData, MagicItemTierData

class TestMagicItemTrackerData(unittest.TestCase):

    def setUp(self):
        self.campaign = Campaign(campaign_id="magic_item_test_camp", name="Test Campaign for Magic Items")
        # Ensure magic_item_tracker is initialized (as in Campaign.__post_init__)
        if self.campaign.magic_item_tracker is None:
            self.campaign.magic_item_tracker = MagicItemTrackerData()

    def test_add_common_item_tier_1_4(self):
        """Test adding a common item to Tier 1-4."""
        item_name = "Potion of Healing"
        # The UI would directly append to the list
        self.campaign.magic_item_tracker.level_tier_1_4.common_items.append(item_name)

        self.assertIn(item_name, self.campaign.magic_item_tracker.level_tier_1_4.common_items)
        self.assertEqual(len(self.campaign.magic_item_tracker.level_tier_1_4.common_items), 1)

    def test_add_legendary_item_tier_17_20(self):
        """Test adding a legendary item to Tier 17-20."""
        item_name = "Vorpal Sword"
        self.campaign.magic_item_tracker.level_tier_17_20.legendary_items.append(item_name)

        self.assertIn(item_name, self.campaign.magic_item_tracker.level_tier_17_20.legendary_items)

    def test_remove_uncommon_item_tier_5_10(self):
        """Test removing an uncommon item from Tier 5-10."""
        item1 = "Bag of Holding"
        item2 = "Gauntlets of Ogre Power"
        tier_data = self.campaign.magic_item_tracker.level_tier_5_10
        tier_data.uncommon_items.extend([item1, item2])

        self.assertEqual(len(tier_data.uncommon_items), 2)

        # Simulate removal
        tier_data.uncommon_items.remove(item1)

        self.assertEqual(len(tier_data.uncommon_items), 1)
        self.assertNotIn(item1, tier_data.uncommon_items)
        self.assertIn(item2, tier_data.uncommon_items)

    def test_data_persistence_across_tiers_and_rarities(self):
        """Test that data in one list doesn't affect another."""
        self.campaign.magic_item_tracker.level_tier_1_4.common_items.append("Scroll of Protection")
        self.campaign.magic_item_tracker.level_tier_1_4.rare_items.append("Amulet of Health")
        self.campaign.magic_item_tracker.level_tier_11_16.very_rare_items.append("Staff of Power")

        self.assertIn("Scroll of Protection", self.campaign.magic_item_tracker.level_tier_1_4.common_items)
        self.assertEqual(len(self.campaign.magic_item_tracker.level_tier_1_4.rare_items), 1)
        self.assertNotIn("Amulet of Health", self.campaign.magic_item_tracker.level_tier_11_16.very_rare_items)

if __name__ == '__main__':
    unittest.main()
