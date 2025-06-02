from typing import Optional, List, Any
from PySide6.QtWidgets import (
    QTableWidgetItem, QHeaderView, QMessageBox, QDialog
)
from PySide6.QtCore import Qt

from src.data_models import BastionEntry, Campaign # For type hinting
from src.trackers.bastion_tracker_dialog import BastionEntryDialog
from src.trackers.base_tracker_ui import BaseTrackerWidget

class BastionTrackerWidget(BaseTrackerWidget):
    def _get_entity_name(self) -> str:
        return "Bastion"

    def _get_entity_name_plural(self) -> str:
        return "Bastions"

    def _configure_table_columns(self):
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Bastion Name", "Character Name", "Level"])
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)

    def _get_item_data_for_display(self, campaign: Campaign) -> List[BastionEntry]:
        if not campaign.bastions:
            return []
        # Sort by bastion name for display consistency
        return sorted(list(campaign.bastions.values()), key=lambda b: b.bastion_name.lower())

    def _populate_table_row(self, row: int, bastion_entry: BastionEntry):
        name_item = self._create_table_item(bastion_entry.bastion_name, bastion_entry.entry_id)
        self.table_widget.setItem(row, 0, name_item)
        self.table_widget.setItem(row, 1, self._create_table_item(bastion_entry.character_name))
        level_item = self._create_table_item(str(bastion_entry.level), alignment=Qt.AlignmentFlag.AlignCenter)
        self.table_widget.setItem(row, 2, level_item)

    def _get_dialog_for_add(self) -> Optional[QDialog]:
        # The campaign object is implicitly handled by the base class calling _perform_add_item
        return BastionEntryDialog(self) # Parent is this widget

    def _get_dialog_for_edit(self, item_id: str, campaign: Campaign) -> Optional[QDialog]:
        bastion_to_edit = campaign.bastions.get(item_id)
        if not bastion_to_edit:
            QMessageBox.critical(self, "Error", f"Bastion with ID '{item_id}' not found.")
            # self.refresh_display() # Data might be out of sync - refresh is handled by base if dialog fails
            return None
        return BastionEntryDialog(self, bastion_entry=bastion_to_edit)

    def _get_selected_item_id(self) -> Optional[str]:
        # ID is stored in the first column (index 0)
        return self._get_id_from_selected_row(column_with_id=0)

    def _get_item_name_for_confirmation(self, item_id: str, campaign: Campaign) -> Optional[str]:
        bastion = campaign.bastions.get(item_id)
        return bastion.bastion_name if bastion else None

    def _perform_add_item(self, dialog_data: BastionEntry, campaign: Campaign) -> None:
        # dialog_data is a BastionEntry object from BastionEntryDialog.get_data()
        # The base class's _on_add_item_triggered method will pass the result of dialog.get_data()
        # which is new_item_data in that context.
        campaign.bastions[dialog_data.entry_id] = dialog_data

    def _perform_edit_item(self, item_id: str, dialog_data: BastionEntry, campaign: Campaign) -> None:
        # BastionEntryDialog updates the passed bastion_entry in place.
        # dialog_data is the result of dialog.get_data(). In BastionEntryDialog, get_data
        # returns self.bastion_entry, which is the (potentially modified) instance.
        # So, the object in campaign.bastions should already be updated if it was passed to the dialog.
        if item_id not in campaign.bastions:
            # This case should ideally be caught by _get_dialog_for_edit or if ID changed.
            raise ValueError(f"Bastion with ID {item_id} not found for editing.")
        # If the dialog modified the entry_id itself, we might need to adjust the dictionary key.
        # Assuming entry_id is immutable or the dialog handles this correctly by updating the original dict key.
        # For now, we assume the object identified by item_id in campaign.bastions is the one updated.
        campaign.bastions[item_id] = dialog_data # Ensure the (potentially new) object from get_data is in the dict


    def _perform_delete_item(self, item_id: str, campaign: Campaign) -> bool:
        if campaign.bastions and item_id in campaign.bastions:
            del campaign.bastions[item_id]
            return True
        return False

# Keep the existing __main__ block for testing this widget independently
if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    # Assuming ApplicationData and Campaign are correctly imported for type hinting
    # For the test block, explicit import if not found by the linter/runtime
    from src.data_models import ApplicationData #, Campaign # Campaign already imported

    class MockMainWindow(QMainWindow): # Mock for testing the widget
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "bastion_test_camp"
            # Initialize ApplicationData if it's not done elsewhere for the test
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="Bastion Test Campaign")

            # Initialize bastions for the test campaign
            b1 = BastionEntry(bastion_name="Northwatch Keep", character_name="Gardner", level=3)
            b2 = BastionEntry(bastion_name="The Lonely Tower", character_name="Wizard Zed", level=5)
            campaign.bastions = {b1.entry_id: b1, b2.entry_id: b2}

            self.application_data.campaigns[self.current_campaign_id] = campaign
            self.setStatusBar(QStatusBar(self)) # Important for status messages

        def _save_app_data(self):
            """Mock save method."""
            print(f"MockMainWindow: _save_app_data called for campaign: {self.current_campaign_id}")
            # In a real app, this would serialize self.application_data
            # For testing, we can inspect campaign.bastions directly or print
            current_campaign = self.application_data.campaigns.get(self.current_campaign_id)
            if current_campaign:
                print("Current bastions in mock data:")
                for bastion_id, bastion in current_campaign.bastions.items():
                    print(f"  ID: {bastion_id}, Name: {bastion.bastion_name}, Level: {bastion.level}")


        # statusBar method is inherited from QMainWindow and available
        # def statusBar(self):
        # return self._status_bar # if you were manually managing it.

    app = QApplication(sys.argv)
    mock_main_win = MockMainWindow() # Create the mock main window instance

    # Pass the mock main window to the BastionTrackerWidget
    bastion_widget = BastionTrackerWidget(mock_main_win)

    mock_main_win.setCentralWidget(bastion_widget)
    mock_main_win.setWindowTitle("Bastion Tracker Widget Test")
    mock_main_win.setGeometry(100, 100, 700, 500)

    # The refresh_display is automatically called in BaseTrackerWidget's __init__
    # So, no need to call it explicitly here unless a specific re-trigger is needed.
    # bastion_widget.refresh_display()

    mock_main_win.show()
    sys.exit(app.exec())
