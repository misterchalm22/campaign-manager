import unittest
from src.data_models import Campaign, BastionEntry, BastionFacility

class TestBastionTrackerData(unittest.TestCase):

    def setUp(self):
        self.campaign = Campaign(campaign_id="bastion_test_camp", name="Test Campaign for Bastions")

    def test_add_bastion_entry(self):
        """Test adding a bastion entry to the campaign."""
        bastion_data = BastionEntry(bastion_name="Northwatch Keep", character_name="Sir Reginald", level=5)
        # Bastions are stored in a dict, keyed by bastion_data.entry_id
        self.campaign.bastions[bastion_data.entry_id] = bastion_data

        self.assertIn(bastion_data.entry_id, self.campaign.bastions)
        self.assertEqual(self.campaign.bastions[bastion_data.entry_id].bastion_name, "Northwatch Keep")
        self.assertEqual(len(self.campaign.bastions), 1)

    def test_edit_bastion_entry(self):
        """Test editing an existing bastion entry."""
        bastion_data = BastionEntry(bastion_name="The Lonely Tower", basic_facilities_desc="Just a tower.")
        self.campaign.bastions[bastion_data.entry_id] = bastion_data

        entry_to_edit = self.campaign.bastions[bastion_data.entry_id]
        entry_to_edit.bastion_name = "The Really Lonely Tower"
        entry_to_edit.level = 7
        entry_to_edit.bastion_defenders_desc = "One grumpy wizard."

        self.assertEqual(self.campaign.bastions[bastion_data.entry_id].bastion_name, "The Really Lonely Tower")
        self.assertEqual(self.campaign.bastions[bastion_data.entry_id].level, 7)
        self.assertEqual(self.campaign.bastions[bastion_data.entry_id].bastion_defenders_desc, "One grumpy wizard.")

    def test_delete_bastion_entry(self):
        """Test deleting a bastion entry."""
        b1 = BastionEntry(bastion_name="Bastion A")
        b2 = BastionEntry(bastion_name="Bastion B")
        self.campaign.bastions[b1.entry_id] = b1
        self.campaign.bastions[b2.entry_id] = b2

        self.assertEqual(len(self.campaign.bastions), 2)

        del self.campaign.bastions[b1.entry_id]

        self.assertEqual(len(self.campaign.bastions), 1)
        self.assertNotIn(b1.entry_id, self.campaign.bastions)
        self.assertIn(b2.entry_id, self.campaign.bastions)

    def test_add_special_facility_to_bastion(self):
        """Test adding a special facility to a bastion entry."""
        bastion_data = BastionEntry(bastion_name="The Workshop")
        self.campaign.bastions[bastion_data.entry_id] = bastion_data

        bastion = self.campaign.bastions[bastion_data.entry_id]
        self.assertEqual(len(bastion.special_facilities), 0)

        facility_data = BastionFacility(facility_type_name="Alchemy Lab", space="1 room", notes="Explosive!")
        bastion.special_facilities.append(facility_data)

        self.assertEqual(len(self.campaign.bastions[bastion_data.entry_id].special_facilities), 1)
        self.assertEqual(self.campaign.bastions[bastion_data.entry_id].special_facilities[0].facility_type_name, "Alchemy Lab")

    def test_remove_special_facility_from_bastion(self):
        """Test removing a special facility from a bastion entry."""
        bastion_data = BastionEntry(bastion_name="The Stronghold")
        fac1 = BastionFacility(facility_type_name="Barracks", facility_id="fac1_id") # Explicit ID for test
        fac2 = BastionFacility(facility_type_name="Armory", facility_id="fac2_id")
        bastion_data.special_facilities.extend([fac1, fac2])
        self.campaign.bastions[bastion_data.entry_id] = bastion_data

        bastion = self.campaign.bastions[bastion_data.entry_id]
        self.assertEqual(len(bastion.special_facilities), 2)

        # Remove by object identity or by iterating and matching facility_id
        bastion.special_facilities = [f for f in bastion.special_facilities if f.facility_id != fac1.facility_id]

        self.assertEqual(len(self.campaign.bastions[bastion_data.entry_id].special_facilities), 1)
        self.assertEqual(self.campaign.bastions[bastion_data.entry_id].special_facilities[0].facility_type_name, "Armory")

if __name__ == '__main__':
    unittest.main()
