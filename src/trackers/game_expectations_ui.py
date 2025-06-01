from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, Slot

from src.data_models import GameExpectationsEntry # For type hinting
from src.trackers.game_expectations_dialog import GameExpectationsEntryDialog

class GameExpectationsWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        action_bar_layout = QHBoxLayout()
        self.add_entry_btn = QPushButton("Add Player Expectations")
        action_bar_layout.addWidget(self.add_entry_btn)
        action_bar_layout.addStretch()
        layout.addLayout(action_bar_layout)

        self.expectations_table = QTableWidget()
        # Columns: Player Name, DM Name, Actions
        self.expectations_table.setColumnCount(3)
        self.expectations_table.setHorizontalHeaderLabels(["Player Name", "DM Name", "Actions"])
        self.expectations_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Player Name
        self.expectations_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # DM Name
        self.expectations_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) # Actions
        self.expectations_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.expectations_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.expectations_table)

        self.placeholder_label = QLabel("No game expectations entries found. Click 'Add Player Expectations' to create one.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setVisible(False)
        layout.addWidget(self.placeholder_label)
        self.expectations_table.setVisible(True)

        self.add_entry_btn.clicked.connect(self._on_add_entry)

    def refresh_display(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            self.expectations_table.setRowCount(0)
            self.show_placeholder(True, "No campaign selected.")
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign or not campaign.game_expectations:
            self.expectations_table.setRowCount(0)
            self.show_placeholder(True, "No game expectations entries found. Click 'Add Player Expectations' to create one.")
            return

        self.show_placeholder(False)
        entries_data = campaign.game_expectations
        sorted_entry_ids = list(entries_data.keys()) # Could sort by player name if desired

        self.expectations_table.setRowCount(len(sorted_entry_ids))

        for row, entry_id in enumerate(sorted_entry_ids):
            entry = entries_data[entry_id]

            self.expectations_table.setItem(row, 0, QTableWidgetItem(entry.player_name))
            self.expectations_table.setItem(row, 1, QTableWidgetItem(entry.dm_name))

            edit_btn = QPushButton("Edit")
            delete_btn = QPushButton("Delete")

            edit_btn.clicked.connect(lambda checked=False, bound_id=entry_id: self._on_edit_entry(bound_id))
            delete_btn.clicked.connect(lambda checked=False, bound_id=entry_id: self._on_delete_entry(bound_id))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self.expectations_table.setCellWidget(row, 2, actions_widget)

        self.expectations_table.resizeRowsToContents()

    def show_placeholder(self, show: bool, text: Optional[str] = None):
        if show:
            if text:
                self.placeholder_label.setText(text)
            self.expectations_table.setVisible(False)
            self.placeholder_label.setVisible(True)
        else:
            self.expectations_table.setVisible(True)
            self.placeholder_label.setVisible(False)

    @Slot()
    def _on_add_entry(self):
        if not self.main_window.current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "Please select or create a campaign first.")
            return

        dialog = GameExpectationsEntryDialog(self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_display()
            self.main_window.statusBar().showMessage("New game expectations entry added.", 3000)

    @Slot()
    def _on_edit_entry(self, entry_id: str):
        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign: return

        entry_to_edit = campaign.game_expectations.get(entry_id)
        if not entry_to_edit:
            QMessageBox.critical(self, "Error", f"Game Expectations entry with ID '{entry_id}' not found.")
            self.refresh_display()
            return

        dialog = GameExpectationsEntryDialog(self.main_window, entry=entry_to_edit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"Expectations for '{entry_to_edit.player_name}' updated.", 3000)

    @Slot()
    def _on_delete_entry(self, entry_id: str):
        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign: return

        entry_to_delete = campaign.game_expectations.get(entry_id)
        if not entry_to_delete:
            QMessageBox.critical(self, "Error", f"Game Expectations entry ID '{entry_id}' not found for deletion.")
            self.refresh_display()
            return

        reply = QMessageBox.question(self, "Delete Entry",
                                     f"Are you sure you want to delete expectations for player: '{entry_to_delete.player_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del campaign.game_expectations[entry_id]
            self.main_window._save_app_data()
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"Expectations for '{entry_to_delete.player_name}' deleted.", 3000)

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    from src.data_models import ApplicationData, Campaign, SensitiveElement

    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "ge_test_camp"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="GE Test Campaign", dm_name_global="Global DM")

            ge1 = GameExpectationsEntry(player_name="Alice", dm_name="Global DM", sensitive_elements=[SensitiveElement("Snakes", hard_limit=True)])
            ge2 = GameExpectationsEntry(player_name="Bob", dm_name="Global DM")
            campaign.game_expectations = {ge1.entry_id: ge1, ge2.entry_id: ge2}
            self.application_data.campaigns[self.current_campaign_id] = campaign
            self.setStatusBar(QStatusBar(self))

        def _save_app_data(self):
            print("MockMainWindow: _save_app_data called")

        def statusBar(self):
            return super().statusBar()

    app = QApplication(sys.argv)
    mock_main = MockMainWindow()
    ge_widget = GameExpectationsWidget(mock_main)

    mock_main.setCentralWidget(ge_widget)
    mock_main.setWindowTitle("Game Expectations Widget Test")
    mock_main.setGeometry(100, 100, 700, 500)

    ge_widget.refresh_display()
    mock_main.show()
    sys.exit(app.exec())
