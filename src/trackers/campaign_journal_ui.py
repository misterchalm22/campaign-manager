from typing import Optional, List, Any
from PySide6.QtWidgets import (
    QPushButton, QHeaderView, QMessageBox, QDialog, QWidget, QHBoxLayout, QTableWidgetItem
)
from PySide6.QtCore import Qt, Slot

from src.data_models import CampaignJournalEntry, Campaign # For type hinting
from src.trackers.campaign_journal_dialog import CampaignJournalEntryDialog
from src.trackers.base_tracker_ui import BaseTrackerWidget

class CampaignJournalWidget(BaseTrackerWidget):
    def _get_entity_name(self) -> str:
        return "Session Log"

    def _get_entity_name_plural(self) -> str:
        return "Session Logs"

    def _get_add_button_text(self) -> str:
        return "Add New Session Log"

    def _setup_action_bar(self):
        # Override to only have an "Add" button in the top action bar
        self.action_bar_layout = QHBoxLayout()
        self.add_button = QPushButton(self._get_add_button_text())
        self.add_button.clicked.connect(self._on_add_item_triggered) # Connect to base class slot

        self.action_bar_layout.addWidget(self.add_button)
        self.action_bar_layout.addStretch()
        # Insert layout at index 0 of main_layout (which is a QVBoxLayout)
        self.main_layout.insertLayout(0, self.action_bar_layout)


        # No top edit/delete buttons for this tracker by default
        self.edit_button = None
        self.delete_button = None

    def _set_buttons_enabled(self, enabled: bool):
        # Override to only manage the add button from the top bar
        if hasattr(self, 'add_button') and self.add_button:
             # Add button always enabled if a campaign is selected, regardless of data presence
            self.add_button.setEnabled(bool(self.main_window.current_campaign_id))
        # Edit/Delete buttons are per-row, not global, so base class logic for them is not needed here.


    def _configure_table_columns(self):
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Session #", "Date", "Title", "Actions"])
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table_widget.setSortingEnabled(True)
        # Disable double-click to edit as actions are via buttons
        # Check if connected before disconnecting to avoid errors if not connected by base.
        try:
            self.table_widget.itemDoubleClicked.disconnect(self._on_edit_item_triggered)
        except RuntimeError: # Catches "signal itemDoubleClicked not connected to any slot"
            pass


    def _get_item_data_for_display(self, campaign: Campaign) -> List[CampaignJournalEntry]:
        if not campaign.campaign_journal:
            return []
        # Sort entries by session number for display
        return sorted(list(campaign.campaign_journal.values()), key=lambda entry: entry.session_number)

    def _populate_table_row(self, row: int, journal_entry: CampaignJournalEntry):
        # Session Number (as QTableWidgetItem for sorting)
        session_num_item = QTableWidgetItem()
        session_num_item.setData(Qt.ItemDataRole.EditRole, journal_entry.session_number) # For sorting as number
        # Store unique ID (entry_id) in UserRole of the first item for potential reference, though not used by base selection
        session_num_item.setData(Qt.ItemDataRole.UserRole, journal_entry.entry_id)
        session_num_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table_widget.setItem(row, 0, session_num_item)

        self.table_widget.setItem(row, 1, self._create_table_item(journal_entry.session_date))
        self.table_widget.setItem(row, 2, self._create_table_item(journal_entry.session_title))

        # Action buttons in the row
        edit_btn = QPushButton("Edit")
        delete_btn = QPushButton("Delete")

        # Connect to new specific slots that will call base class logic or handle directly
        edit_btn.clicked.connect(lambda checked=False, bound_id=journal_entry.entry_id: self._on_edit_entry_row(bound_id))
        delete_btn.clicked.connect(lambda checked=False, bound_id=journal_entry.entry_id: self._on_delete_entry_row(bound_id))

        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        self.table_widget.setCellWidget(row, 3, actions_widget)

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
            # CampaignJournalEntryDialog handles its own saving.
            # Base class _perform_edit_item is a no-op.
            # We still call it to allow any future base class logic, though it expects dialog_data.
            self._perform_edit_item(entry_id, None, campaign) # Pass None as dialog_data
            self.main_window._save_app_data() # Dialog should save, but ensure consistency if not.
            self.refresh_display()
            item_name = self._get_item_name_for_confirmation(entry_id, campaign) or self._entity_name
            self.main_window.statusBar().showMessage(f"{item_name} updated.", 3000)
        else:
            # Ensure UI reflects original state if edit is cancelled
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
                    self.main_window._save_app_data() # Deletion is direct, so save here
                    self.refresh_display()
                    self.main_window.statusBar().showMessage(f"{item_name} deleted.", 3000)
                else:
                    QMessageBox.warning(self, "Delete Error", f"{self._entity_name} not found for deletion or already removed.")
                    self.refresh_display()
            except Exception as e: # Catch any errors from _perform_delete_item
                QMessageBox.critical(self, "Error Deleting Item", f"Could not delete {self._entity_name.lower()}: {e}")
                self.main_window.statusBar().showMessage(f"Failed to delete {self._entity_name.lower()}.", 5000)
                self.refresh_display()


    # --- Implementations for BaseTrackerWidget abstract methods ---

    def _get_dialog_for_add(self) -> Optional[QDialog]:
        return CampaignJournalEntryDialog(self.main_window)

    def _get_dialog_for_edit(self, item_id: str, campaign: Campaign) -> Optional[QDialog]:
        if not campaign.campaign_journal: # Check if campaign_journal dict exists
            QMessageBox.critical(self, "Error", f"Journal data structure not found in campaign.")
            return None
        entry_to_edit = campaign.campaign_journal.get(item_id)
        if not entry_to_edit:
            QMessageBox.critical(self, "Error", f"{self._entity_name} with ID '{item_id}' not found.")
            # self.refresh_display() # Base class handles refresh if dialog returns None
            return None
        return CampaignJournalEntryDialog(self.main_window, journal_entry=entry_to_edit)

    def _get_selected_item_id(self) -> Optional[str]:
        # This tracker uses row-specific buttons, so global selection ID is not applicable
        # for edit/delete. Base _on_edit/delete_item_triggered should not be called.
        return None

    def _get_item_name_for_confirmation(self, item_id: str, campaign: Campaign) -> Optional[str]:
        if not campaign.campaign_journal:
             return f"the selected {self._get_entity_name().lower()}"
        entry = campaign.campaign_journal.get(item_id)
        if entry:
            return f"'{entry.session_title}' (Session {entry.session_number})"
        return f"the selected {self._get_entity_name().lower()}"


    def _perform_add_item(self, dialog_data: Any, campaign: Campaign) -> None:
        # Adding is handled by CampaignJournalEntryDialog itself, including saving data via main_window.
        # Base class's _on_add_item_triggered calls this, then refresh_display and status message.
        # No direct data model manipulation needed here from this widget.
        pass

    def _perform_edit_item(self, item_id: str, dialog_data: Any, campaign: Campaign) -> None:
        # Editing is handled by CampaignJournalEntryDialog itself, including saving.
        # _on_edit_entry_row calls this. No direct data model manipulation needed here.
        pass

    def _perform_delete_item(self, item_id: str, campaign: Campaign) -> bool:
        if campaign.campaign_journal and item_id in campaign.campaign_journal:
            del campaign.campaign_journal[item_id]
            # Actual data saving (self.main_window._save_app_data()) is done by the calling slot (_on_delete_entry_row)
            return True
        return False

# Keep the existing __main__ block for testing this widget independently
if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    from src.data_models import ApplicationData # Campaign, CampaignJournalEntry already imported

    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "journal_test_camp"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="Journal Test Campaign")

            # Ensure campaign_journal is initialized as a dict
            campaign.campaign_journal = {}
            entry1 = CampaignJournalEntry(session_number=2, session_date="2023-01-15", session_title="The Old Mill")
            entry2 = CampaignJournalEntry(session_number=1, session_date="2023-01-01", session_title="Village of Barovia")
            campaign.campaign_journal[entry1.entry_id] = entry1
            campaign.campaign_journal[entry2.entry_id] = entry2

            self.application_data.campaigns[self.current_campaign_id] = campaign
            self.setStatusBar(QStatusBar(self))

        def _save_app_data(self):
            print(f"MockMainWindow: _save_app_data called for campaign {self.current_campaign_id}")
            current_campaign = self.application_data.campaigns.get(self.current_campaign_id)
            if current_campaign and current_campaign.campaign_journal:
                print("Current journal entries in mock data:")
                for entry_id, entry in current_campaign.campaign_journal.items():
                    print(f"  ID: {entry_id}, Title: {entry.session_title}, Session: {entry.session_number}")

        # statusBar is inherited

    app = QApplication(sys.argv)
    mock_main = MockMainWindow()
    journal_widget = CampaignJournalWidget(mock_main)

    mock_main.setCentralWidget(journal_widget)
    mock_main.setWindowTitle("Campaign Journal Widget Test")
    mock_main.setGeometry(100, 100, 700, 500)

    mock_main.show()
    sys.exit(app.exec())
