from typing import Optional, List, Any
from PySide6.QtWidgets import (
    QHeaderView, QMessageBox, QDialog
)
# QTableWidgetItem is imported via BaseTrackerWidget's _create_table_item if needed directly
# Qt is imported via BaseTrackerWidget if needed directly

from src.data_models import Conflict, Campaign, CampaignConflictEntry as CampaignConflictDataContainer
from src.trackers.campaign_conflicts_dialog import CampaignConflictEntryDialog
from src.trackers.base_tracker_ui import BaseTrackerWidget

class CampaignConflictsWidget(BaseTrackerWidget):
    def _get_entity_name(self) -> str:
        return "Conflict"

    def _get_entity_name_plural(self) -> str:
        return "Conflicts"

    def _configure_table_columns(self):
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Conflict Title/Identifier", "Antagonist/Situation"])
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def _get_item_data_for_display(self, campaign: Campaign) -> List[Conflict]:
        if not campaign.campaign_conflicts or not campaign.campaign_conflicts.conflicts:
            return []
        # Conflicts are stored in a list, no specific sorting by default here, but can be added.
        return campaign.campaign_conflicts.conflicts

    def _populate_table_row(self, row: int, conflict_entry: Conflict):
        # Store the conflict_id in the item for later retrieval
        title_item = self._create_table_item(conflict_entry.title_identifier, conflict_entry.conflict_id)
        self.table_widget.setItem(row, 0, title_item)
        self.table_widget.setItem(row, 1, self._create_table_item(conflict_entry.antagonist_situation))

    def _get_dialog_for_add(self) -> Optional[QDialog]:
        return CampaignConflictEntryDialog(self) # Parent is this widget

    def _get_dialog_for_edit(self, item_id: str, campaign: Campaign) -> Optional[QDialog]:
        if not campaign.campaign_conflicts:
            QMessageBox.critical(self, "Error", "Conflict data structure not found for this campaign.")
            return None

        conflict_to_edit = None
        for conflict in campaign.campaign_conflicts.conflicts:
            if conflict.conflict_id == item_id:
                conflict_to_edit = conflict
                break

        if not conflict_to_edit:
            QMessageBox.critical(self, "Error", f"Conflict with ID '{item_id}' not found.")
            # self.refresh_display() # Base class handles refresh if dialog returns None or on error
            return None
        return CampaignConflictEntryDialog(self, conflict_entry=conflict_to_edit)

    def _get_selected_item_id(self) -> Optional[str]:
        # ID is stored in the first column (index 0)
        return self._get_id_from_selected_row(column_with_id=0)

    def _get_item_name_for_confirmation(self, item_id: str, campaign: Campaign) -> Optional[str]:
        if not campaign.campaign_conflicts:
            return f"the selected {self._get_entity_name().lower()}" # Use dynamic entity name
        for conflict in campaign.campaign_conflicts.conflicts:
            if conflict.conflict_id == item_id:
                return conflict.title_identifier
        return f"the selected {self._get_entity_name().lower()}" # Fallback

    def _perform_add_item(self, dialog_data: Conflict, campaign: Campaign) -> None:
        # dialog_data is a Conflict object from CampaignConflictEntryDialog.get_data()
        if campaign.campaign_conflicts is None:
            # Initialize the container if it's None
            campaign.campaign_conflicts = CampaignConflictDataContainer()
        campaign.campaign_conflicts.conflicts.append(dialog_data)

    def _perform_edit_item(self, item_id: str, dialog_data: Conflict, campaign: Campaign) -> None:
        # CampaignConflictEntryDialog updates the passed conflict_entry in place.
        # dialog_data is the result of dialog.get_data().
        # We need to ensure the list in campaign.campaign_conflicts.conflicts contains the updated object.
        if campaign.campaign_conflicts:
            for i, conflict in enumerate(campaign.campaign_conflicts.conflicts):
                if conflict.conflict_id == item_id:
                    # Assuming dialog_data is the potentially modified object (could be same instance or new)
                    campaign.campaign_conflicts.conflicts[i] = dialog_data
                    return
        # This line would be reached if the item_id was not found, which should ideally be caught earlier.
        raise ValueError(f"Conflict with ID {item_id} not found for editing in perform_edit_item.")


    def _perform_delete_item(self, item_id: str, campaign: Campaign) -> bool:
        if campaign.campaign_conflicts and campaign.campaign_conflicts.conflicts:
            original_len = len(campaign.campaign_conflicts.conflicts)
            campaign.campaign_conflicts.conflicts = [
                c for c in campaign.campaign_conflicts.conflicts if c.conflict_id != item_id
            ]
            return len(campaign.campaign_conflicts.conflicts) < original_len
        return False

# Keep the existing __main__ block for testing this widget independently
if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    from src.data_models import ApplicationData # Campaign, Conflict, CampaignConflictDataContainer already imported

    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "conflict_test_camp"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="Conflict Test Campaign")

            # Initialize CampaignConflictEntry and add some sample conflicts
            campaign.campaign_conflicts = CampaignConflictDataContainer() # Ensure this is initialized
            c1 = Conflict(title_identifier="Goblin Raid", antagonist_situation="Goblins from Misty Caves")
            c2 = Conflict(title_identifier="Missing Artifact", antagonist_situation="Thieves Guild")
            campaign.campaign_conflicts.conflicts.extend([c1, c2])

            self.application_data.campaigns[self.current_campaign_id] = campaign
            self.setStatusBar(QStatusBar(self))

        def _save_app_data(self):
            print(f"MockMainWindow: _save_app_data called for campaign {self.current_campaign_id}")
            current_campaign = self.application_data.campaigns.get(self.current_campaign_id)
            if current_campaign and current_campaign.campaign_conflicts:
                print("Current conflicts in mock data:")
                for conflict in current_campaign.campaign_conflicts.conflicts:
                    print(f"  ID: {conflict.conflict_id}, Title: {conflict.title_identifier}")


        # statusBar method is inherited

    app = QApplication(sys.argv)
    mock_main_win = MockMainWindow()
    conflicts_widget = CampaignConflictsWidget(mock_main_win)

    mock_main_win.setCentralWidget(conflicts_widget)
    mock_main_win.setWindowTitle("Campaign Conflicts Widget Test")
    mock_main_win.setGeometry(100, 100, 700, 500)

    # refresh_display is called by BaseTrackerWidget's __init__
    mock_main_win.show()
    sys.exit(app.exec())
