from typing import Optional, List, Any
from PySide6.QtWidgets import (
    QPushButton, QHeaderView, QMessageBox, QDialog, QWidget, QHBoxLayout, QTableWidgetItem, QAbstractItemView
)
from PySide6.QtCore import Qt, Slot

from src.data_models import NPCEntry, Campaign # For type hinting
from src.trackers.npc_tracker_dialog import NPCEntryDialog
from src.trackers.base_tracker_ui import BaseTrackerWidget

class NPCTrackerWidget(BaseTrackerWidget):
    def _get_entity_name(self) -> str:
        return "NPC"

    def _get_entity_name_plural(self) -> str:
        return "NPCs"

    def _get_add_button_text(self) -> str:
        return "Add New NPC"

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
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Name", "Stat Block", "Alignment", "Actions"])
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.table_widget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        # Corrected Enum for EditTriggers
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        try:
            self.table_widget.itemDoubleClicked.disconnect(self._on_edit_item_triggered)
        except RuntimeError:
            pass # Not connected

    def _get_item_data_for_display(self, campaign: Campaign) -> List[NPCEntry]:
        if not campaign.npcs:
            return []
        # Sort by NPC name for consistency
        return sorted(list(campaign.npcs.values()), key=lambda x: x.name.lower())

    def _populate_table_row(self, row: int, entry: NPCEntry):
        # Store entry_id in the first column's item (UserRole)
        name_item = self._create_table_item(entry.name, data_role_value=entry.entry_id)
        self.table_widget.setItem(row, 0, name_item)
        self.table_widget.setItem(row, 1, self._create_table_item(entry.stat_block_source))
        self.table_widget.setItem(row, 2, self._create_table_item(entry.alignment))

        edit_btn = QPushButton("Edit")
        delete_btn = QPushButton("Delete")

        edit_btn.clicked.connect(lambda checked=False, bound_id=entry.entry_id: self._on_edit_entry_row(bound_id))
        delete_btn.clicked.connect(lambda checked=False, bound_id=entry.entry_id: self._on_delete_entry_row(bound_id))

        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        self.table_widget.setCellWidget(row, 3, actions_widget)

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
        return NPCEntryDialog(self.main_window)

    def _get_dialog_for_edit(self, item_id: str, campaign: Campaign) -> Optional[QDialog]:
        if not campaign.npcs:
            QMessageBox.critical(self, "Error", "NPCs data structure not found.")
            return None
        entry_to_edit = campaign.npcs.get(item_id)
        if not entry_to_edit:
            QMessageBox.critical(self, "Error", f"{self._entity_name} with ID '{item_id}' not found.")
            # self.refresh_display() # Base class handles refresh
            return None
        return NPCEntryDialog(self.main_window, npc_entry=entry_to_edit)

    def _get_selected_item_id(self) -> Optional[str]:
        # Not applicable for top-bar edit/delete as they don't exist.
        return None

    def _get_item_name_for_confirmation(self, item_id: str, campaign: Campaign) -> Optional[str]:
        if not campaign.npcs:
            return f"the selected {self._get_entity_name().lower()}"
        entry = campaign.npcs.get(item_id)
        if entry:
            return entry.name
        return f"the selected {self._get_entity_name().lower()}"


    def _perform_add_item(self, dialog_data: Any, campaign: Campaign) -> None:
        # Dialog handles saving
        pass

    def _perform_edit_item(self, item_id: str, dialog_data: Any, campaign: Campaign) -> None:
        # Dialog handles saving
        pass

    def _perform_delete_item(self, item_id: str, campaign: Campaign) -> bool:
        if campaign.npcs and item_id in campaign.npcs:
            del campaign.npcs[item_id]
            # Saving is handled by the calling slot (_on_delete_entry_row)
            return True
        return False

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    from src.data_models import ApplicationData

    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "test_campaign"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id="test_campaign", name="Test Campaign")

            # Ensure npcs is initialized as a dict
            campaign.npcs = {}
            npc1 = NPCEntry(name="Gorok", stat_block_source="MM", alignment="CE")
            npc2 = NPCEntry(name="Elara", stat_block_source="VGM", alignment="NG")
            campaign.npcs[npc1.entry_id] = npc1
            campaign.npcs[npc2.entry_id] = npc2

            self.application_data.campaigns["test_campaign"] = campaign
            self.setStatusBar(QStatusBar(self))

        def _save_app_data(self):
            print(f"MockMainWindow: _save_app_data called for campaign {self.current_campaign_id}")
            current_campaign = self.application_data.campaigns.get(self.current_campaign_id)
            if current_campaign and current_campaign.npcs:
                print("Current NPCs in mock data:")
                for entry_id, entry in current_campaign.npcs.items():
                    print(f"  ID: {entry_id}, Name: {entry.name}, Alignment: {entry.alignment}")

        # statusBar inherited

    app = QApplication(sys.argv)
    mock_main_win = MockMainWindow()
    npc_tracker_widget = NPCTrackerWidget(mock_main_win)

    mock_main_win.setCentralWidget(npc_tracker_widget)
    mock_main_win.setWindowTitle("NPC Tracker Widget Test")
    mock_main_win.setGeometry(100, 100, 700, 500)

    mock_main_win.show()
    sys.exit(app.exec())
