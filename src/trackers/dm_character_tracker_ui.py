from typing import Optional, List, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QHeaderView, QMessageBox, QDialog, QAbstractItemView, QHBoxLayout
)
from PySide6.QtCore import Qt, Slot

from src.data_models import DMCharacterEntry, Campaign # For type hinting
from src.trackers.dm_character_tracker_dialog import DMCharacterEntryDialog
from src.trackers.base_tracker_ui import BaseTrackerWidget

class DMCharacterWidget(BaseTrackerWidget):
    def _get_entity_name(self) -> str:
        return "PC Entry"

    def _get_entity_name_plural(self) -> str:
        return "PC Entries"

    def _get_add_button_text(self) -> str:
        return "Add New PC Entry"

    def _setup_action_bar(self):
        # Override to only have an "Add" button in the top action bar
        self.action_bar_layout = QHBoxLayout()
        self.add_button = QPushButton(self._get_add_button_text())
        self.add_button.clicked.connect(self._on_add_item_triggered)

        self.action_bar_layout.addWidget(self.add_button)
        self.action_bar_layout.addStretch()
        self.main_layout.insertLayout(0, self.action_bar_layout) # Insert at the top

        self.edit_button = None # No global edit button
        self.delete_button = None # No global delete button

    def _set_buttons_enabled(self, enabled: bool):
        if hasattr(self, 'add_button') and self.add_button:
            self.add_button.setEnabled(bool(self.main_window.current_campaign_id))
        # Edit/Delete buttons are per-row, their state is managed implicitly by their existence.

    def _configure_table_columns(self):
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(["Character Name", "Player Name", "Class", "Level", "Actions"])
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table_widget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # self.table_widget.setSortingEnabled(True) # Optional: enable if sorting is desired

        # Disconnect double-click if connected by base, to prevent issues
        try:
            self.table_widget.itemDoubleClicked.disconnect(self._on_edit_item_triggered)
        except RuntimeError: # Catches "signal itemDoubleClicked not connected to any slot"
            pass


    def _get_item_data_for_display(self, campaign: Campaign) -> List[DMCharacterEntry]:
        if not campaign.dm_characters:
            return []
        # Sort by character name for consistent display order
        return sorted(list(campaign.dm_characters.values()), key=lambda x: x.character_name.lower())


    def _populate_table_row(self, row: int, entry: DMCharacterEntry):
        # Store entry_id in the first column's item (UserRole)
        char_name_item = self._create_table_item(entry.character_name, data_role_value=entry.entry_id)
        self.table_widget.setItem(row, 0, char_name_item)
        self.table_widget.setItem(row, 1, self._create_table_item(entry.player_name))
        self.table_widget.setItem(row, 2, self._create_table_item(entry.char_class))

        level_item = self._create_table_item(str(entry.level), alignment=Qt.AlignmentFlag.AlignCenter)
        self.table_widget.setItem(row, 3, level_item)

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

    # --- Row-specific action handlers ---
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
            # DMCharacterEntryDialog is expected to handle its own saving via main_window.
            # Calling _perform_edit_item is for consistency if base class needs it.
            self._perform_edit_item(entry_id, None, campaign) # Pass None as dialog_data
            self.main_window._save_app_data() # Ensure data is saved, as dialog might not always
            self.refresh_display()
            entry_name = self._get_item_name_for_confirmation(entry_id, campaign) or self._entity_name
            self.main_window.statusBar().showMessage(f"{entry_name} updated.", 3000)
        else:
            self.refresh_display() # Refresh if cancelled to revert any potential optimistic UI changes

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
                    self.main_window._save_app_data() # Deletion is direct, so save here
                    self.refresh_display()
                    self.main_window.statusBar().showMessage(f"{item_name} deleted.", 3000)
                else:
                    QMessageBox.warning(self, "Delete Error", f"{self._entity_name} not found for deletion or already removed.")
                    self.refresh_display()
            except Exception as e:
                QMessageBox.critical(self, "Error Deleting Item", f"Could not delete {self._entity_name.lower()}: {e}")
                self.main_window.statusBar().showMessage(f"Failed to delete {self._entity_name.lower()}.", 5000)
                self.refresh_display()


    # --- Implementations for BaseTrackerWidget abstract methods ---

    def _get_dialog_for_add(self) -> Optional[QDialog]:
        # This dialog takes main_window as parent and handles its own saving.
        return DMCharacterEntryDialog(self.main_window)

    def _get_dialog_for_edit(self, item_id: str, campaign: Campaign) -> Optional[QDialog]:
        if not campaign.dm_characters:
            QMessageBox.critical(self, "Error", "DM Characters data structure not found.")
            return None
        entry_to_edit = campaign.dm_characters.get(item_id)
        if not entry_to_edit:
            QMessageBox.critical(self, "Error", f"{self._entity_name} with ID '{item_id}' not found.")
            # self.refresh_display() # Base class handles refresh
            return None
        return DMCharacterEntryDialog(self.main_window, entry=entry_to_edit)

    def _get_selected_item_id(self) -> Optional[str]:
        # Not applicable for top-bar edit/delete as they don't exist for this tracker.
        return None

    def _get_item_name_for_confirmation(self, item_id: str, campaign: Campaign) -> Optional[str]:
        if not campaign.dm_characters:
            return f"the selected {self._get_entity_name().lower()}"
        entry = campaign.dm_characters.get(item_id)
        if entry:
            return entry.character_name
        return f"the selected {self._get_entity_name().lower()}"


    def _perform_add_item(self, dialog_data: Any, campaign: Campaign) -> None:
        # Add is handled by DMCharacterEntryDialog itself, including saving.
        pass

    def _perform_edit_item(self, item_id: str, dialog_data: Any, campaign: Campaign) -> None:
        # Edit is handled by DMCharacterEntryDialog itself, including saving.
        pass

    def _perform_delete_item(self, item_id: str, campaign: Campaign) -> bool:
        if campaign.dm_characters and item_id in campaign.dm_characters:
            del campaign.dm_characters[item_id]
            # Actual data saving is handled by the calling slot (_on_delete_entry_row)
            return True
        return False

# Keep the existing __main__ block for testing
if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    from src.data_models import ApplicationData # Campaign, DMCharacterEntry already imported

    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "dmc_test_camp"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="DMC Test Campaign")

            # Ensure dm_characters is initialized as a dict
            campaign.dm_characters = {}
            pc1 = DMCharacterEntry(character_name="Valerius", player_name="Alex", char_class="Paladin", level=3)
            pc2 = DMCharacterEntry(character_name="Lyra", player_name="Sam", char_class="Sorcerer", level=3)
            campaign.dm_characters[pc1.entry_id] = pc1
            campaign.dm_characters[pc2.entry_id] = pc2

            self.application_data.campaigns[self.current_campaign_id] = campaign
            self.setStatusBar(QStatusBar(self))

        def _save_app_data(self):
            print(f"MockMainWindow: _save_app_data called for campaign {self.current_campaign_id}")
            current_campaign = self.application_data.campaigns.get(self.current_campaign_id)
            if current_campaign and current_campaign.dm_characters:
                print("Current DM characters in mock data:")
                for entry_id, entry in current_campaign.dm_characters.items():
                    print(f"  ID: {entry_id}, Name: {entry.character_name}, Player: {entry.player_name}")


        # statusBar is inherited

    app = QApplication(sys.argv)
    mock_main = MockMainWindow()
    dmc_widget = DMCharacterWidget(mock_main)

    mock_main.setCentralWidget(dmc_widget)
    mock_main.setWindowTitle("DM's Character Tracker Widget Test")
    mock_main.setGeometry(100, 100, 800, 500)

    # refresh_display is called by BaseTrackerWidget constructor
    mock_main.show()
    sys.exit(app.exec())
