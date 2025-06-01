from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, Slot

from src.data_models import DMCharacterEntry # For type hinting
from src.trackers.dm_character_tracker_dialog import DMCharacterEntryDialog

class DMCharacterWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        action_bar_layout = QHBoxLayout()
        self.add_entry_btn = QPushButton("Add New PC Entry")
        action_bar_layout.addWidget(self.add_entry_btn)
        action_bar_layout.addStretch()
        layout.addLayout(action_bar_layout)

        self.pc_table = QTableWidget()
        # Columns: Character Name, Player Name, Class, Level, Actions
        self.pc_table.setColumnCount(5)
        self.pc_table.setHorizontalHeaderLabels(["Character Name", "Player Name", "Class", "Level", "Actions"])
        self.pc_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.pc_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.pc_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.pc_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.pc_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.pc_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.pc_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.pc_table)

        self.placeholder_label = QLabel("No PC entries found. Click 'Add New PC Entry' to create one.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setVisible(False)
        layout.addWidget(self.placeholder_label)
        self.pc_table.setVisible(True)

        self.add_entry_btn.clicked.connect(self._on_add_entry)

    def refresh_display(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            self.pc_table.setRowCount(0)
            self.show_placeholder(True, "No campaign selected.")
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign or not campaign.dm_characters:
            self.pc_table.setRowCount(0)
            self.show_placeholder(True, "No PC entries found. Click 'Add New PC Entry' to create one.")
            return

        self.show_placeholder(False)
        entries_data = campaign.dm_characters
        sorted_entry_ids = list(entries_data.keys()) # Could sort by char name

        self.pc_table.setRowCount(len(sorted_entry_ids))

        for row, entry_id in enumerate(sorted_entry_ids):
            entry = entries_data[entry_id]

            self.pc_table.setItem(row, 0, QTableWidgetItem(entry.character_name))
            self.pc_table.setItem(row, 1, QTableWidgetItem(entry.player_name))
            self.pc_table.setItem(row, 2, QTableWidgetItem(entry.char_class))

            level_item = QTableWidgetItem(str(entry.level))
            level_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.pc_table.setItem(row, 3, level_item)

            edit_btn = QPushButton("Edit")
            delete_btn = QPushButton("Delete")

            edit_btn.clicked.connect(lambda checked=False, bound_id=entry_id: self._on_edit_entry(bound_id))
            delete_btn.clicked.connect(lambda checked=False, bound_id=entry_id: self._on_delete_entry(bound_id))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self.pc_table.setCellWidget(row, 4, actions_widget)

        self.pc_table.resizeRowsToContents()

    def show_placeholder(self, show: bool, text: Optional[str] = None):
        if show:
            if text:
                self.placeholder_label.setText(text)
            self.pc_table.setVisible(False)
            self.placeholder_label.setVisible(True)
        else:
            self.pc_table.setVisible(True)
            self.placeholder_label.setVisible(False)

    @Slot()
    def _on_add_entry(self):
        if not self.main_window.current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "Please select or create a campaign first.")
            return

        dialog = DMCharacterEntryDialog(self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_display()
            self.main_window.statusBar().showMessage("New PC entry added.", 3000)

    @Slot()
    def _on_edit_entry(self, entry_id: str):
        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign: return

        entry_to_edit = campaign.dm_characters.get(entry_id)
        if not entry_to_edit:
            QMessageBox.critical(self, "Error", f"PC entry with ID '{entry_id}' not found.")
            self.refresh_display()
            return

        dialog = DMCharacterEntryDialog(self.main_window, entry=entry_to_edit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"PC entry '{entry_to_edit.character_name}' updated.", 3000)

    @Slot()
    def _on_delete_entry(self, entry_id: str):
        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign: return

        entry_to_delete = campaign.dm_characters.get(entry_id)
        if not entry_to_delete:
            QMessageBox.critical(self, "Error", f"PC entry ID '{entry_id}' not found for deletion.")
            self.refresh_display()
            return

        reply = QMessageBox.question(self, "Delete PC Entry",
                                     f"Are you sure you want to delete entry for PC: '{entry_to_delete.character_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del campaign.dm_characters[entry_id]
            self.main_window._save_app_data()
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"PC entry '{entry_to_delete.character_name}' deleted.", 3000)

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    from src.data_models import ApplicationData, Campaign

    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "dmc_test_camp"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="DMC Test Campaign")

            pc1 = DMCharacterEntry(character_name="Valerius", player_name="Alex", char_class="Paladin", level=3)
            pc2 = DMCharacterEntry(character_name="Lyra", player_name="Sam", char_class="Sorcerer", level=3)
            campaign.dm_characters = {pc1.entry_id: pc1, pc2.entry_id: pc2}
            self.application_data.campaigns[self.current_campaign_id] = campaign
            self.setStatusBar(QStatusBar(self))

        def _save_app_data(self):
            print("MockMainWindow: _save_app_data called")

        def statusBar(self):
            return super().statusBar()

    app = QApplication(sys.argv)
    mock_main = MockMainWindow()
    dmc_widget = DMCharacterWidget(mock_main)

    mock_main.setCentralWidget(dmc_widget)
    mock_main.setWindowTitle("DM's Character Tracker Widget Test")
    mock_main.setGeometry(100, 100, 800, 500)

    dmc_widget.refresh_display()
    mock_main.show()
    sys.exit(app.exec())
