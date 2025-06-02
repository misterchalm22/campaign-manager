from typing import Optional, List, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QHeaderView, QMessageBox, QDialog, QAbstractItemView, QHBoxLayout
)
from PySide6.QtCore import Qt, Slot

from src.data_models import TravelPlanEntry, Campaign # For type hinting
from src.trackers.travel_planner_dialog import TravelPlanEntryDialog
from src.trackers.base_tracker_ui import BaseTrackerWidget

class TravelPlannerWidget(BaseTrackerWidget):
    def _get_entity_name(self) -> str:
        return "Travel Plan"

    def _get_entity_name_plural(self) -> str:
        return "Travel Plans"

    def _get_add_button_text(self) -> str:
        return "Add New Travel Plan"

    def _setup_action_bar(self):
        self.action_bar_layout = QHBoxLayout()
        self.add_button = QPushButton(self._get_add_button_text())
        self.add_button.clicked.connect(self._on_add_item_triggered)

        self.action_bar_layout.addWidget(self.add_button)
        self.action_bar_layout.addStretch()
        self.main_layout.insertLayout(0, self.action_bar_layout) # Insert at the top

        self.edit_button = None
        self.delete_button = None

    def _set_buttons_enabled(self, enabled: bool):
        if hasattr(self, 'add_button') and self.add_button:
            self.add_button.setEnabled(bool(self.main_window.current_campaign_id))
        # Edit/Delete buttons are per-row

    def _configure_table_columns(self):
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["Journey Name", "Origin", "Destination", "No. Stages", "Actions"])
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Corrected Enum
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        # Disconnect default double-click from base if it exists, as edit is per-row button
        try:
            self.table_widget.doubleClicked.disconnect(self._on_edit_item_triggered)
        except RuntimeError:
            pass # Not connected or already disconnected

    def _get_item_data_for_display(self, campaign: Campaign) -> List[TravelPlanEntry]:
        if not campaign.travel_plans:
            return []
        return sorted(list(campaign.travel_plans.values()), key=lambda x: x.journey_name.lower())

    def _populate_table_row(self, row: int, entry: TravelPlanEntry):
        # Store entry_id in the first column's item (UserRole)
        name_item = self._create_table_item(entry.journey_name, data_role_value=entry.entry_id)
        self.table_widget.setItem(row, 0, name_item)
        self.table_widget.setItem(row, 1, self._create_table_item(entry.origin))
        self.table_widget.setItem(row, 2, self._create_table_item(entry.destination))

        num_stages_item = self._create_table_item(str(len(entry.stages)), alignment=Qt.AlignmentFlag.AlignCenter)
        self.table_widget.setItem(row, 3, num_stages_item)

        edit_btn = QPushButton("Edit")
        delete_btn = QPushButton("Delete")

        edit_btn.clicked.connect(lambda checked=False, bound_id=entry.entry_id: self._on_edit_entry_row(bound_id))
        delete_btn.clicked.connect(lambda checked=False, bound_id=entry.entry_id: self._on_delete_entry_row(bound_id))

        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        self.table_widget.setCellWidget(row, 4, actions_widget)

    @Slot()
    def _on_edit_entry_row(self, entry_id: str):
        if not self.main_window.current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "No campaign selected.")
            return
        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign:
             QMessageBox.critical(self, "Error", "Campaign data not found.")
             return
        dialog = self._get_dialog_for_edit(entry_id, campaign)
        if dialog is None: return

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Dialog is expected to handle its own saving.
            self._perform_edit_item(entry_id, None, campaign) # Call for consistency
            self.main_window._save_app_data() # Ensure save consistency
            self.refresh_display()
            entry_name = self._get_item_name_for_confirmation(entry_id, campaign) or self._entity_name
            self.main_window.statusBar().showMessage(f"{entry_name} updated.", 3000)
        else:
            self.refresh_display()

    @Slot()
    def _on_delete_entry_row(self, entry_id: str):
        if not self.main_window.current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "No campaign selected.")
            return
        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign:
             QMessageBox.critical(self, "Error", "Campaign data not found.")
             return
        item_name = self._get_item_name_for_confirmation(entry_id, campaign) or f"the selected {self._entity_name.lower()}"
        reply = QMessageBox.question(self, f"Delete {self._entity_name}",
                                     f"Are you sure you want to delete {item_name}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                deleted = self._perform_delete_item(entry_id, campaign)
                if deleted:
                    self.main_window._save_app_data() # Save after successful deletion
                    self.refresh_display()
                    self.main_window.statusBar().showMessage(f"{item_name} deleted.", 3000)
                else:
                    QMessageBox.warning(self, "Delete Error", f"{self._entity_name} not found for deletion or already removed.")
                    self.refresh_display()
            except Exception as e:
                QMessageBox.critical(self, "Error Deleting Item", f"Could not delete {self._entity_name.lower()}: {e}")
                self.main_window.statusBar().showMessage(f"Failed to delete {self._entity_name.lower()}.", 5000)
                self.refresh_display()

    def _get_dialog_for_add(self) -> Optional[QDialog]:
        # Dialog handles its own saving through main_window
        return TravelPlanEntryDialog(self.main_window)

    def _get_dialog_for_edit(self, item_id: str, campaign: Campaign) -> Optional[QDialog]:
        if not campaign.travel_plans:
            QMessageBox.critical(self, "Error", "Travel Plans data structure not found.")
            return None
        entry_to_edit = campaign.travel_plans.get(item_id)
        if not entry_to_edit:
            QMessageBox.critical(self, "Error", f"{self._entity_name} with ID '{item_id}' not found.")
            # self.refresh_display() # Base class handles refresh
            return None
        return TravelPlanEntryDialog(self.main_window, entry=entry_to_edit)

    def _get_selected_item_id(self) -> Optional[str]:
        # Not applicable for top-bar edit/delete as they don't exist.
        return None

    def _get_item_name_for_confirmation(self, item_id: str, campaign: Campaign) -> Optional[str]:
        if not campaign.travel_plans:
            return f"the selected {self._get_entity_name().lower()}"
        entry = campaign.travel_plans.get(item_id)
        if entry:
            return entry.journey_name
        return f"the selected {self._get_entity_name().lower()}"

    def _perform_add_item(self, dialog_data: Any, campaign: Campaign) -> None:
        # Dialog handles saving
        pass

    def _perform_edit_item(self, item_id: str, dialog_data: Any, campaign: Campaign) -> None:
        # Dialog handles saving
        pass

    def _perform_delete_item(self, item_id: str, campaign: Campaign) -> bool:
        if campaign.travel_plans and item_id in campaign.travel_plans:
            del campaign.travel_plans[item_id]
            # Saving is handled by the calling slot (_on_delete_entry_row)
            return True
        return False

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    from src.data_models import ApplicationData, TravelStage

    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "tp_test_camp"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="TP Test Campaign")

            # Ensure travel_plans is initialized as a dict
            campaign.travel_plans = {}
            ts1 = TravelStage(stage_name="Stage 1", start_location="Town", end_location="Forest", distance="10 miles", duration="1 day", notes="Easy travel")
            tp1 = TravelPlanEntry(journey_name="To the Woods", origin="Town", destination="Deep Forest", stages=[ts1])
            tp2 = TravelPlanEntry(journey_name="Across the Mountains", origin="Valley", destination="Peak", stages=[]) # Ensure stages can be empty

            campaign.travel_plans[tp1.entry_id] = tp1
            campaign.travel_plans[tp2.entry_id] = tp2

            self.application_data.campaigns[self.current_campaign_id] = campaign
            self.setStatusBar(QStatusBar(self))

        def _save_app_data(self):
            print(f"MockMainWindow: _save_app_data called for campaign {self.current_campaign_id}")
            current_campaign = self.application_data.campaigns.get(self.current_campaign_id)
            if current_campaign and current_campaign.travel_plans:
                print("Current travel plans in mock data:")
                for entry_id, entry in current_campaign.travel_plans.items():
                    print(f"  ID: {entry_id}, Journey: {entry.journey_name}, Stages: {len(entry.stages)}")

        # statusBar inherited

    app = QApplication(sys.argv)
    mock_main_win = MockMainWindow()
    tp_widget = TravelPlannerWidget(mock_main_win)
    mock_main_win.setCentralWidget(tp_widget)
    mock_main_win.setWindowTitle("Travel Planner Widget Test")
    mock_main_win.setGeometry(100, 100, 800, 500)
    mock_main_win.show()
    sys.exit(app.exec())
