import unittest
from src.data_models import Campaign, TravelPlanEntry, TravelStage

class TestTravelPlannerTrackerData(unittest.TestCase):

    def setUp(self):
        self.campaign = Campaign(campaign_id="tp_test_camp", name="Test Campaign for Travel Plans")

    def test_add_travel_plan(self):
        """Test adding a travel plan."""
        tp_data = TravelPlanEntry(journey_name="To the Coast", origin="Inland City", destination="Port Town")
        self.campaign.travel_plans[tp_data.entry_id] = tp_data

        self.assertIn(tp_data.entry_id, self.campaign.travel_plans)
        self.assertEqual(self.campaign.travel_plans[tp_data.entry_id].journey_name, "To the Coast")
        self.assertEqual(len(self.campaign.travel_plans), 1)

    def test_edit_travel_plan(self):
        """Test editing an existing travel plan."""
        tp_data = TravelPlanEntry(journey_name="Old Road", origin="A", destination="B")
        self.campaign.travel_plans[tp_data.entry_id] = tp_data

        entry_to_edit = self.campaign.travel_plans[tp_data.entry_id]
        entry_to_edit.journey_name = "The Sunken Road"
        entry_to_edit.destination = "New B"

        self.assertEqual(self.campaign.travel_plans[tp_data.entry_id].journey_name, "The Sunken Road")
        self.assertEqual(self.campaign.travel_plans[tp_data.entry_id].destination, "New B")

    def test_delete_travel_plan(self):
        """Test deleting a travel plan."""
        tp1 = TravelPlanEntry(journey_name="Plan A")
        tp2 = TravelPlanEntry(journey_name="Plan B")
        self.campaign.travel_plans[tp1.entry_id] = tp1
        self.campaign.travel_plans[tp2.entry_id] = tp2

        self.assertEqual(len(self.campaign.travel_plans), 2)

        del self.campaign.travel_plans[tp1.entry_id]

        self.assertEqual(len(self.campaign.travel_plans), 1)
        self.assertNotIn(tp1.entry_id, self.campaign.travel_plans)
        self.assertIn(tp2.entry_id, self.campaign.travel_plans)

    def test_add_travel_stage_to_plan(self):
        """Test adding a travel stage to a plan."""
        tp_data = TravelPlanEntry(journey_name="Path of Trials")
        self.campaign.travel_plans[tp_data.entry_id] = tp_data

        plan = self.campaign.travel_plans[tp_data.entry_id]
        self.assertEqual(len(plan.stages), 0)

        stage_data = TravelStage(start_location="Gate", end_location="Checkpoint 1", distance="1 day")
        plan.stages.append(stage_data)

        self.assertEqual(len(self.campaign.travel_plans[tp_data.entry_id].stages), 1)
        self.assertEqual(self.campaign.travel_plans[tp_data.entry_id].stages[0].distance, "1 day")

    def test_remove_travel_stage_from_plan(self):
        """Test removing a travel stage from a plan."""
        tp_data = TravelPlanEntry(journey_name="Long Road")
        stage1 = TravelStage(start_location="X", end_location="Y", stage_number_id="S1")
        stage2 = TravelStage(start_location="Y", end_location="Z", stage_number_id="S2")
        tp_data.stages.extend([stage1, stage2])
        self.campaign.travel_plans[tp_data.entry_id] = tp_data

        plan = self.campaign.travel_plans[tp_data.entry_id]
        self.assertEqual(len(plan.stages), 2)

        # Remove by object identity (or find by ID and remove)
        plan.stages.remove(stage1)
        # Or: plan.stages = [s for s in plan.stages if s.stage_id != stage1.stage_id]

        self.assertEqual(len(self.campaign.travel_plans[tp_data.entry_id].stages), 1)
        self.assertEqual(self.campaign.travel_plans[tp_data.entry_id].stages[0].stage_number_id, "S2")

if __name__ == '__main__':
    unittest.main()
