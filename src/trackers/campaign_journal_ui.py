from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, Slot

from src.data_models import CampaignJournalEntry # For type hinting
from src.trackers.campaign_journal_dialog import CampaignJournalEntryDialog

class CampaignJournalWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        action_bar_layout = QHBoxLayout()
        self.add_entry_btn = QPushButton("Add New Session Log")
        action_bar_layout.addWidget(self.add_entry_btn)
        action_bar_layout.addStretch()
        layout.addLayout(action_bar_layout)

        self.journal_table = QTableWidget()
        self.journal_table.setColumnCount(4) # Session #, Date, Title, Actions
        self.journal_table.setHorizontalHeaderLabels(["Session #", "Date", "Title", "Actions"])
        self.journal_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive) # Session #
        self.journal_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive) # Date
        self.journal_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Title
        self.journal_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Actions
        self.journal_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.journal_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.journal_table.setSortingEnabled(True) # Allow sorting by columns
        layout.addWidget(self.journal_table)

        self.placeholder_label = QLabel("No journal entries found. Click 'Add New Session Log' to create one.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setVisible(False)
        layout.addWidget(self.placeholder_label)
        self.journal_table.setVisible(True)

        self.add_entry_btn.clicked.connect(self._on_add_entry)

    def refresh_display(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            self.journal_table.setRowCount(0)
            self.show_placeholder(True, "No campaign selected.")
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign or not campaign.campaign_journal:
            self.journal_table.setRowCount(0)
            self.show_placeholder(True, "No journal entries. Click 'Add New Session Log' to create one.")
            return

        self.show_placeholder(False)
        journal_entries = campaign.campaign_journal

        # Sort entries by session number for display (optional, but good for usability)
        # QTableWidget can also sort if items are QTableWidgetItems that can be compared (like numbers)
        # For custom objects or mixed types, manual sort before populating is better.
        sorted_entry_ids = sorted(journal_entries.keys(), key=lambda entry_id: journal_entries[entry_id].session_number)

        self.journal_table.setSortingEnabled(False) # Disable sorting during population
        self.journal_table.setRowCount(len(sorted_entry_ids))

        for row, entry_id in enumerate(sorted_entry_ids):
            journal_entry = journal_entries[entry_id]

            # Session Number (as QTableWidgetItem for sorting)
            session_num_item = QTableWidgetItem()
            session_num_item.setData(Qt.ItemDataRole.EditRole, journal_entry.session_number) # For sorting as number
            session_num_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.journal_table.setItem(row, 0, session_num_item)

            self.journal_table.setItem(row, 1, QTableWidgetItem(journal_entry.session_date))
            self.journal_table.setItem(row, 2, QTableWidgetItem(journal_entry.session_title))

            edit_btn = QPushButton("Edit")
            delete_btn = QPushButton("Delete")

            edit_btn.clicked.connect(lambda checked=False, bound_id=entry_id: self._on_edit_entry(bound_id))
            delete_btn.clicked.connect(lambda checked=False, bound_id=entry_id: self._on_delete_entry(bound_id))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self.journal_table.setCellWidget(row, 3, actions_widget)

        self.journal_table.resizeRowsToContents()
        self.journal_table.setSortingEnabled(True) # Re-enable sorting

    def show_placeholder(self, show: bool, text: Optional[str] = None):
        if show:
            if text:
                self.placeholder_label.setText(text)
            self.journal_table.setVisible(False)
            self.placeholder_label.setVisible(True)
        else:
            self.journal_table.setVisible(True)
            self.placeholder_label.setVisible(False)

    @Slot()
    def _on_add_entry(self):
        if not self.main_window.current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "Please select or create a campaign first.")
            return

        dialog = CampaignJournalEntryDialog(self.main_window)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_display()
            self.main_window.statusBar().showMessage("New journal entry added.", 3000)

    @Slot()
    def _on_edit_entry(self, entry_id: str):
        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign: return

        entry_to_edit = campaign.campaign_journal.get(entry_id)
        if not entry_to_edit:
            QMessageBox.critical(self, "Error", f"Journal entry with ID '{entry_id}' not found.")
            self.refresh_display()
            return

        dialog = CampaignJournalEntryDialog(self.main_window, journal_entry=entry_to_edit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"Journal entry '{entry_to_edit.session_title}' updated.", 3000)

    @Slot()
    def _on_delete_entry(self, entry_id: str):
        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign: return

        entry_to_delete = campaign.campaign_journal.get(entry_id)
        if not entry_to_delete:
            QMessageBox.critical(self, "Error", f"Journal entry ID '{entry_id}' not found for deletion.")
            self.refresh_display()
            return

        reply = QMessageBox.question(self, "Delete Journal Entry",
                                     f"Are you sure you want to delete session log: '{entry_to_delete.session_title}' (Session {entry_to_delete.session_number})?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del campaign.campaign_journal[entry_id]
            self.main_window._save_app_data()
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"Journal entry '{entry_to_delete.session_title}' deleted.", 3000)

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    from src.data_models import ApplicationData, Campaign

    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "journal_test_camp"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="Journal Test Campaign")

            entry1 = CampaignJournalEntry(session_number=2, session_date="2023-01-15", session_title="The Old Mill")
            entry2 = CampaignJournalEntry(session_number=1, session_date="2023-01-01", session_title="Village of Barovia")
            campaign.campaign_journal = {entry1.entry_id: entry1, entry2.entry_id: entry2}
            self.application_data.campaigns[self.current_campaign_id] = campaign
            self.setStatusBar(QStatusBar(self))

        def _save_app_data(self):
            print("MockMainWindow: _save_app_data called")

        def statusBar(self):
            return super().statusBar()

    app = QApplication(sys.argv)
    mock_main = MockMainWindow()
    journal_widget = CampaignJournalWidget(mock_main)

    # For standalone testing, set the central widget on the mock_main window
    mock_main.setCentralWidget(journal_widget)
    mock_main.setWindowTitle("Campaign Journal Widget Test")
    mock_main.setGeometry(100, 100, 700, 500)

    journal_widget.refresh_display()
    mock_main.show()
    sys.exit(app.exec())
