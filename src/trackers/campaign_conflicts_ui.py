from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QLabel
)
from PySide6.QtCore import Qt, Slot

from src.data_models import Conflict # Using the existing Conflict model
from src.trackers.campaign_conflicts_dialog import CampaignConflictEntryDialog

class CampaignConflictsWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window # Instance of MainWindow

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        # Action buttons
        action_bar_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Conflict")
        self.edit_button = QPushButton("Edit Selected Conflict")
        self.delete_button = QPushButton("Delete Selected Conflict")
        action_bar_layout.addWidget(self.add_button)
        action_bar_layout.addWidget(self.edit_button)
        action_bar_layout.addWidget(self.delete_button)
        action_bar_layout.addStretch()
        layout.addLayout(action_bar_layout)

        # Table for conflicts
        self.conflicts_table = QTableWidget()
        self.conflicts_table.setColumnCount(2) # Title, Antagonist
        self.conflicts_table.setHorizontalHeaderLabels(["Conflict Title/Identifier", "Antagonist/Situation"])
        self.conflicts_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.conflicts_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.conflicts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.conflicts_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.conflicts_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.conflicts_table)

        self.placeholder_label = QLabel("No conflicts defined for this campaign. Click 'Add Conflict' to create one.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setVisible(False)
        layout.addWidget(self.placeholder_label)
        self.conflicts_table.setVisible(True)


        # Connect signals
        self.add_button.clicked.connect(self._on_add_conflict)
        self.edit_button.clicked.connect(self._on_edit_conflict)
        self.delete_button.clicked.connect(self._on_delete_conflict)
        self.conflicts_table.itemDoubleClicked.connect(self._on_edit_conflict) # Edit on double click

    def refresh_display(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            self.conflicts_table.setRowCount(0)
            self.show_placeholder(True, "No campaign selected.")
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        # The data model uses campaign.campaign_conflicts which is a CampaignConflictEntry object,
        # and this object has a 'conflicts' list.
        if not campaign or not campaign.campaign_conflicts or not campaign.campaign_conflicts.conflicts:
            self.conflicts_table.setRowCount(0)
            self.show_placeholder(True, "No conflicts defined. Click 'Add Conflict' to create one.")
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return

        self.show_placeholder(False)
        conflicts_list = campaign.campaign_conflicts.conflicts

        self.conflicts_table.setRowCount(len(conflicts_list))
        for row, conflict_entry in enumerate(conflicts_list):
            title_item = QTableWidgetItem(conflict_entry.title_identifier)
            # Store the conflict_id in the item for later retrieval
            title_item.setData(Qt.ItemDataRole.UserRole, conflict_entry.conflict_id)

            self.conflicts_table.setItem(row, 0, title_item)
            self.conflicts_table.setItem(row, 1, QTableWidgetItem(conflict_entry.antagonist_situation))

        self.conflicts_table.resizeRowsToContents()
        self.edit_button.setEnabled(self.conflicts_table.rowCount() > 0)
        self.delete_button.setEnabled(self.conflicts_table.rowCount() > 0)

    def show_placeholder(self, show: bool, text: Optional[str] = None):
        if show:
            if text:
                self.placeholder_label.setText(text)
            self.conflicts_table.setVisible(False)
            self.placeholder_label.setVisible(True)
        else:
            self.conflicts_table.setVisible(True)
            self.placeholder_label.setVisible(False)

    @Slot()
    def _on_add_conflict(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "Please select or create a campaign first.")
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign: # Should not happen if ID is set
            QMessageBox.critical(self, "Error", "Campaign data not found.")
            return

        dialog = CampaignConflictEntryDialog(self) # Parent is this widget
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_conflict_data = dialog.get_data()
            if new_conflict_data: # get_data() returns a Conflict object
                # The Conflict object from get_data() already has a new UUID.
                campaign.campaign_conflicts.conflicts.append(new_conflict_data)
                self.main_window._save_app_data()
                self.refresh_display()
                self.main_window.statusBar().showMessage("New conflict added.", 3000)

    @Slot()
    def _on_edit_conflict(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "No campaign selected.")
            return

        selected_items = self.conflicts_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a conflict to edit.")
            return

        selected_row = selected_items[0].row()
        conflict_id_to_edit = self.conflicts_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign or not campaign.campaign_conflicts:
            QMessageBox.critical(self, "Error", "Conflict data not found for this campaign.")
            return

        conflict_to_edit = None
        for conflict in campaign.campaign_conflicts.conflicts:
            if conflict.conflict_id == conflict_id_to_edit:
                conflict_to_edit = conflict
                break

        if not conflict_to_edit:
            QMessageBox.critical(self, "Error", f"Conflict with ID '{conflict_id_to_edit}' not found.")
            self.refresh_display() # Data might be out of sync
            return

        dialog = CampaignConflictEntryDialog(self, conflict_entry=conflict_to_edit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # The dialog's get_data method updates the conflict_to_edit object in place.
            # So, no need to call dialog.get_data() again unless we want to re-verify.
            self.main_window._save_app_data()
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"Conflict '{conflict_to_edit.title_identifier}' updated.", 3000)

    @Slot()
    def _on_delete_conflict(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "No campaign selected.")
            return

        selected_items = self.conflicts_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a conflict to delete.")
            return

        selected_row = selected_items[0].row()
        conflict_id_to_delete = self.conflicts_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        conflict_title = self.conflicts_table.item(selected_row, 0).text()


        reply = QMessageBox.question(self, "Delete Conflict",
                                     f"Are you sure you want to delete the conflict: '{conflict_title}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
            if campaign and campaign.campaign_conflicts:
                original_len = len(campaign.campaign_conflicts.conflicts)
                campaign.campaign_conflicts.conflicts = [
                    c for c in campaign.campaign_conflicts.conflicts if c.conflict_id != conflict_id_to_delete
                ]
                if len(campaign.campaign_conflicts.conflicts) < original_len:
                    self.main_window._save_app_data()
                    self.refresh_display()
                    self.main_window.statusBar().showMessage(f"Conflict '{conflict_title}' deleted.", 3000)
                else:
                    QMessageBox.warning(self, "Delete Error", "Conflict not found for deletion, it might have been already removed.")
                    self.refresh_display() # Refresh to show current state
            else:
                QMessageBox.critical(self, "Error", "Campaign or conflict data not found.")
                self.refresh_display()

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    from src.data_models import ApplicationData, Campaign, CampaignConflictEntry

    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "conflict_test_camp"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="Conflict Test Campaign")
            # Initialize CampaignConflictEntry and add some sample conflicts
            campaign.campaign_conflicts = CampaignConflictEntry() # Ensure this is initialized
            c1 = Conflict(title_identifier="Goblin Raid", antagonist_situation="Goblins from Misty Caves")
            c2 = Conflict(title_identifier="Missing Artifact", antagonist_situation="Thieves Guild")
            campaign.campaign_conflicts.conflicts.extend([c1, c2])

            self.application_data.campaigns[self.current_campaign_id] = campaign
            self.setStatusBar(QStatusBar(self))

        def _save_app_data(self):
            print("MockMainWindow: _save_app_data called")

        def statusBar(self): # Ensure it returns the status bar
            return super().statusBar()

    app = QApplication(sys.argv)
    mock_main_win = MockMainWindow()
    conflicts_widget = CampaignConflictsWidget(mock_main_win)

    mock_main_win.setCentralWidget(conflicts_widget)
    mock_main_win.setWindowTitle("Campaign Conflicts Widget Test")
    mock_main_win.setGeometry(100, 100, 700, 500)

    conflicts_widget.refresh_display() # Initial population
    mock_main_win.show()
    sys.exit(app.exec())
