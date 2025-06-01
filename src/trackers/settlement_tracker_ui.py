from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, Slot

from src.data_models import SettlementEntry # For type hinting
from src.trackers.settlement_tracker_dialog import SettlementEntryDialog

class SettlementTrackerWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        action_bar_layout = QHBoxLayout()
        self.add_entry_btn = QPushButton("Add New Settlement")
        action_bar_layout.addWidget(self.add_entry_btn)
        action_bar_layout.addStretch()
        layout.addLayout(action_bar_layout)

        self.settlement_table = QTableWidget()
        # Columns: Name, Size, Defining Trait (partial), Actions
        self.settlement_table.setColumnCount(4)
        self.settlement_table.setHorizontalHeaderLabels(["Name", "Size", "Defining Trait", "Actions"])
        self.settlement_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Name
        self.settlement_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive) # Size
        self.settlement_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Defining Trait
        self.settlement_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Actions
        self.settlement_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.settlement_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # self.settlement_table.setSortingEnabled(True) # Can enable if desired
        layout.addWidget(self.settlement_table)

        self.placeholder_label = QLabel("No settlements found. Click 'Add New Settlement' to create one.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setVisible(False)
        layout.addWidget(self.placeholder_label)
        self.settlement_table.setVisible(True)

        self.add_entry_btn.clicked.connect(self._on_add_entry)

    def refresh_display(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            self.settlement_table.setRowCount(0)
            self.show_placeholder(True, "No campaign selected.")
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign or not campaign.settlements:
            self.settlement_table.setRowCount(0)
            self.show_placeholder(True, "No settlements found. Click 'Add New Settlement' to create one.")
            return

        self.show_placeholder(False)
        settlements_data = campaign.settlements

        # Could sort by name if desired, e.g.:
        # sorted_entry_ids = sorted(settlements_data.keys(), key=lambda entry_id: settlements_data[entry_id].name.lower())
        sorted_entry_ids = list(settlements_data.keys()) # Or keep insertion order / rely on dict order (Python 3.7+)


        # self.settlement_table.setSortingEnabled(False)
        self.settlement_table.setRowCount(len(sorted_entry_ids))

        for row, entry_id in enumerate(sorted_entry_ids):
            settlement_entry = settlements_data[entry_id]

            self.settlement_table.setItem(row, 0, QTableWidgetItem(settlement_entry.name))
            self.settlement_table.setItem(row, 1, QTableWidgetItem(settlement_entry.size))

            # Show a snippet of defining trait
            trait_snippet = settlement_entry.defining_trait
            if len(trait_snippet) > 75: # Max length for snippet
                trait_snippet = trait_snippet[:72] + "..."
            self.settlement_table.setItem(row, 2, QTableWidgetItem(trait_snippet))


            edit_btn = QPushButton("Edit")
            delete_btn = QPushButton("Delete")

            edit_btn.clicked.connect(lambda checked=False, bound_id=entry_id: self._on_edit_entry(bound_id))
            delete_btn.clicked.connect(lambda checked=False, bound_id=entry_id: self._on_delete_entry(bound_id))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self.settlement_table.setCellWidget(row, 3, actions_widget)

        self.settlement_table.resizeRowsToContents()
        # self.settlement_table.setSortingEnabled(True)

    def show_placeholder(self, show: bool, text: Optional[str] = None):
        if show:
            if text:
                self.placeholder_label.setText(text)
            self.settlement_table.setVisible(False)
            self.placeholder_label.setVisible(True)
        else:
            self.settlement_table.setVisible(True)
            self.placeholder_label.setVisible(False)

    @Slot()
    def _on_add_entry(self):
        if not self.main_window.current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "Please select or create a campaign first.")
            return

        dialog = SettlementEntryDialog(self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_display()
            self.main_window.statusBar().showMessage("New settlement added.", 3000)

    @Slot()
    def _on_edit_entry(self, entry_id: str):
        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign: return

        entry_to_edit = campaign.settlements.get(entry_id)
        if not entry_to_edit:
            QMessageBox.critical(self, "Error", f"Settlement with ID '{entry_id}' not found.")
            self.refresh_display()
            return

        dialog = SettlementEntryDialog(self.main_window, settlement_entry=entry_to_edit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"Settlement '{entry_to_edit.name}' updated.", 3000)

    @Slot()
    def _on_delete_entry(self, entry_id: str):
        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign: return

        entry_to_delete = campaign.settlements.get(entry_id)
        if not entry_to_delete:
            QMessageBox.critical(self, "Error", f"Settlement ID '{entry_id}' not found for deletion.")
            self.refresh_display()
            return

        reply = QMessageBox.question(self, "Delete Settlement",
                                     f"Are you sure you want to delete settlement: '{entry_to_delete.name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del campaign.settlements[entry_id]
            self.main_window._save_app_data()
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"Settlement '{entry_to_delete.name}' deleted.", 3000)

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    from src.data_models import ApplicationData, Campaign

    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "settlement_test_camp"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="Settlement Test Campaign")

            s1 = SettlementEntry(name="Oakhaven", size="Village (Pop up to 500)", defining_trait="Old oak tree in center")
            s2 = SettlementEntry(name="Bridgewater", size="Town (Pop. 501-5,000)", defining_trait="Famous for its stone bridge")
            campaign.settlements = {s1.entry_id: s1, s2.entry_id: s2}
            self.application_data.campaigns[self.current_campaign_id] = campaign
            self.setStatusBar(QStatusBar(self))

        def _save_app_data(self):
            print("MockMainWindow: _save_app_data called")

        def statusBar(self):
            return super().statusBar()

    app = QApplication(sys.argv)
    mock_main = MockMainWindow()
    settlement_widget = SettlementTrackerWidget(mock_main)

    mock_main.setCentralWidget(settlement_widget)
    mock_main.setWindowTitle("Settlement Tracker Widget Test")
    mock_main.setGeometry(100, 100, 800, 600)

    settlement_widget.refresh_display()
    mock_main.show()
    sys.exit(app.exec())
