from typing import cast, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QHBoxLayout, QLabel, QDialog, QStatusBar
)
from PySide6.QtCore import Qt, Slot

from src.data_models import NPCEntry, Campaign # For type hinting
from src.trackers.npc_tracker_dialog import NPCEntryDialog
# main_window is passed in constructor, so no direct import here

class NPCTrackerWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window # Instance of MainWindow

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0) # Use full space

        # Top bar for actions
        action_bar_layout = QHBoxLayout()
        self.add_npc_btn = QPushButton("Add New NPC")
        action_bar_layout.addWidget(self.add_npc_btn)
        action_bar_layout.addStretch() # Pushes button to the left
        layout.addLayout(action_bar_layout)

        # NPC Table
        self.npc_table = QTableWidget()
        self.npc_table.setColumnCount(4) # Name, Stat Block, Alignment, Actions
        self.npc_table.setHorizontalHeaderLabels(["Name", "Stat Block", "Alignment", "Actions"])
        self.npc_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Name
        self.npc_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Stat Block
        self.npc_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive) # Alignment
        self.npc_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Actions
        self.npc_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Read-only table
        self.npc_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.npc_table)

        # Placeholder for when table is empty
        self.placeholder_label = QLabel("No NPCs found for the current campaign. Click 'Add New NPC' to create one.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setVisible(False) # Initially hidden
        layout.addWidget(self.placeholder_label)
        self.npc_table.setVisible(True)


        # Connect signals
        self.add_npc_btn.clicked.connect(self._on_add_npc)

    def refresh_display(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            self.npc_table.setRowCount(0)
            self.show_placeholder(True, "No campaign selected.")
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign or not campaign.npcs:
            self.npc_table.setRowCount(0)
            self.show_placeholder(True, "No NPCs found. Click 'Add New NPC' to create one.")
            return

        self.show_placeholder(False)
        npcs_data = campaign.npcs

        self.npc_table.setRowCount(len(npcs_data))

        for row, npc_id in enumerate(npcs_data.keys()):
            npc_entry = npcs_data[npc_id]

            self.npc_table.setItem(row, 0, QTableWidgetItem(npc_entry.name))
            self.npc_table.setItem(row, 1, QTableWidgetItem(npc_entry.stat_block_source))
            self.npc_table.setItem(row, 2, QTableWidgetItem(npc_entry.alignment))

            # Actions buttons
            edit_btn = QPushButton("Edit")
            delete_btn = QPushButton("Delete")

            # Use a lambda to capture the correct npc_id for each button
            edit_btn.clicked.connect(lambda checked=False, bound_npc_id=npc_id: self._on_edit_npc(bound_npc_id))
            delete_btn.clicked.connect(lambda checked=False, bound_npc_id=npc_id: self._on_delete_npc(bound_npc_id))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setContentsMargins(0, 0, 0, 0) # Compact layout
            self.npc_table.setCellWidget(row, 3, actions_widget)

        self.npc_table.resizeRowsToContents()

    def show_placeholder(self, show: bool, text: Optional[str] = None):
        if show:
            if text:
                self.placeholder_label.setText(text)
            self.npc_table.setVisible(False)
            self.placeholder_label.setVisible(True)
        else:
            self.npc_table.setVisible(True)
            self.placeholder_label.setVisible(False)


    @Slot()
    def _on_add_npc(self):
        if not self.main_window.current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "Please select or create a campaign first.")
            return

        dialog = NPCEntryDialog(self.main_window) # Pass main_window as parent for data access
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_display()
            self.main_window.statusBar().showMessage("New NPC added successfully.", 3000)

    @Slot()
    def _on_edit_npc(self, npc_id: str):
        if not self.main_window.current_campaign_id: # Should not happen if edit button is visible
            QMessageBox.critical(self, "Error", "No active campaign context.")
            return

        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign: # Should not happen
            QMessageBox.critical(self, "Error", "Active campaign data not found.")
            return

        npc_to_edit = campaign.npcs.get(npc_id)
        if not npc_to_edit:
            QMessageBox.critical(self, "Error", f"NPC with ID '{npc_id}' not found.")
            self.refresh_display() # Data might be out of sync
            return

        dialog = NPCEntryDialog(self.main_window, npc_entry=npc_to_edit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"NPC '{npc_to_edit.name}' updated.", 3000)

    @Slot()
    def _on_delete_npc(self, npc_id: str):
        if not self.main_window.current_campaign_id:
            QMessageBox.critical(self, "Error", "No active campaign context.")
            return

        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign:
            QMessageBox.critical(self, "Error", "Active campaign data not found.")
            return

        npc_to_delete = campaign.npcs.get(npc_id)
        if not npc_to_delete:
            QMessageBox.critical(self, "Error", f"NPC with ID '{npc_id}' not found for deletion.")
            self.refresh_display() # Data might be out of sync
            return

        reply = QMessageBox.question(self, "Delete NPC",
                                     f"Are you sure you want to delete NPC '{npc_to_delete.name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del campaign.npcs[npc_id]
            self.main_window._save_app_data()
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"NPC '{npc_to_delete.name}' deleted.", 3000)

if __name__ == '__main__': # Basic test for the widget
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow
    from src.data_models import ApplicationData # Required for MockMainWindow

    class MockMainWindow(QMainWindow): # Mock a QMainWindow
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "test_campaign"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id="test_campaign", name="Test Campaign")
            # Add some sample NPCs
            npc1 = NPCEntry(name="Test NPC 1", stat_block_source="MM", alignment="LG")
            npc2 = NPCEntry(name="Test NPC 2", stat_block_source="VGM", alignment="CN")
            campaign.npcs = {npc1.entry_id: npc1, npc2.entry_id: npc2}
            self.application_data.campaigns["test_campaign"] = campaign
            self.setStatusBar(QStatusBar(self)) # Important for status messages

        def _save_app_data(self):
            print("MockMainWindow: _save_app_data called")
            # In a real scenario, this would save self.application_data to a file.
            # For the mock, we can just log that it was called.
            # To see changes in the table after dialog operations, we might need to
            # simulate the data change more directly or rely on refresh_display.

        def statusBar(self): # Ensure it returns the status bar
            return super().statusBar()


    app = QApplication(sys.argv)

    mock_main_win = MockMainWindow() # Create the mock main window

    npc_tracker_widget = NPCTrackerWidget(mock_main_win) # Pass the mock

    # To display the widget directly, we need a window
    test_window = QMainWindow() # Or use mock_main_win if it's set up as a full window
    test_window.setCentralWidget(npc_tracker_widget)
    test_window.setWindowTitle("NPC Tracker Widget Test")
    test_window.setGeometry(100, 100, 600, 400)

    # Need to set the mock_main_win as the parent for the dialogs to work correctly if they use it
    # For this test, NPCTrackerWidget uses mock_main_win which is a QMainWindow.

    npc_tracker_widget.refresh_display() # Initial population
    test_window.show()

    sys.exit(app.exec())
