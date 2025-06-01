from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QLabel
)
from PySide6.QtCore import Qt, Slot

from src.data_models import BastionEntry # Use existing model
from src.trackers.bastion_tracker_dialog import BastionEntryDialog

class BastionTrackerWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window # Instance of MainWindow

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        # Action buttons
        action_bar_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Bastion")
        self.edit_button = QPushButton("Edit Selected Bastion")
        self.delete_button = QPushButton("Delete Selected Bastion")
        action_bar_layout.addWidget(self.add_button)
        action_bar_layout.addWidget(self.edit_button)
        action_bar_layout.addWidget(self.delete_button)
        action_bar_layout.addStretch()
        layout.addLayout(action_bar_layout)

        # Table for bastions
        self.bastions_table = QTableWidget()
        self.bastions_table.setColumnCount(3) # Bastion Name, Character Name, Level
        self.bastions_table.setHorizontalHeaderLabels(["Bastion Name", "Character Name", "Level"])
        self.bastions_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.bastions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.bastions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.bastions_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.bastions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.bastions_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.bastions_table)

        self.placeholder_label = QLabel("No bastions defined for this campaign. Click 'Add Bastion' to create one.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setVisible(False) # Initially hidden
        layout.addWidget(self.placeholder_label)
        self.bastions_table.setVisible(True)


        # Connect signals
        self.add_button.clicked.connect(self._on_add_bastion)
        self.edit_button.clicked.connect(self._on_edit_bastion)
        self.delete_button.clicked.connect(self._on_delete_bastion)
        self.bastions_table.itemDoubleClicked.connect(self._on_edit_bastion) # Edit on double click

    def refresh_display(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            self.bastions_table.setRowCount(0)
            self.show_placeholder(True, "No campaign selected.")
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        # Data model uses campaign.bastions which is a Dict[str, BastionEntry]
        if not campaign or not campaign.bastions:
            self.bastions_table.setRowCount(0)
            self.show_placeholder(True, "No bastions defined. Click 'Add Bastion' to create one.")
            self.edit_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            return

        self.show_placeholder(False)
        bastions_dict = campaign.bastions # This is a Dict[str, BastionEntry]

        # Sort by bastion name for display consistency
        sorted_bastion_ids = sorted(bastions_dict.keys(), key=lambda bid: bastions_dict[bid].bastion_name.lower())

        self.bastions_table.setRowCount(len(sorted_bastion_ids))
        for row, bastion_id in enumerate(sorted_bastion_ids):
            bastion_entry = bastions_dict[bastion_id]

            name_item = QTableWidgetItem(bastion_entry.bastion_name)
            # Store the bastion_id (which is entry_id) in the item for later retrieval
            name_item.setData(Qt.ItemDataRole.UserRole, bastion_entry.entry_id)

            self.bastions_table.setItem(row, 0, name_item)
            self.bastions_table.setItem(row, 1, QTableWidgetItem(bastion_entry.character_name))

            level_item = QTableWidgetItem(str(bastion_entry.level))
            level_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.bastions_table.setItem(row, 2, level_item)

        self.bastions_table.resizeRowsToContents()
        self.edit_button.setEnabled(self.bastions_table.rowCount() > 0)
        self.delete_button.setEnabled(self.bastions_table.rowCount() > 0)

    def show_placeholder(self, show: bool, text: Optional[str] = None):
        if show:
            if text:
                self.placeholder_label.setText(text)
            self.bastions_table.setVisible(False)
            self.placeholder_label.setVisible(True)
        else:
            self.bastions_table.setVisible(True)
            self.placeholder_label.setVisible(False)

    @Slot()
    def _on_add_bastion(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "Please select or create a campaign first.")
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign:
            QMessageBox.critical(self, "Error", "Campaign data not found.")
            return

        dialog = BastionEntryDialog(self) # Parent is this widget
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_bastion_data = dialog.get_data() # Returns a BastionEntry object
            if new_bastion_data:
                # Add to the campaign.bastions dictionary (ID is auto-generated in BastionEntry)
                campaign.bastions[new_bastion_data.entry_id] = new_bastion_data
                self.main_window._save_app_data()
                self.refresh_display()
                self.main_window.statusBar().showMessage("New bastion added.", 3000)

    @Slot()
    def _on_edit_bastion(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "No campaign selected.")
            return

        selected_items = self.bastions_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a bastion to edit.")
            return

        selected_row = selected_items[0].row()
        # Retrieve the bastion_id (entry_id) stored in the item's UserRole data
        bastion_id_to_edit = self.bastions_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign or not campaign.bastions:
            QMessageBox.critical(self, "Error", "Bastion data not found for this campaign.")
            return

        bastion_to_edit = campaign.bastions.get(bastion_id_to_edit)

        if not bastion_to_edit:
            QMessageBox.critical(self, "Error", f"Bastion with ID '{bastion_id_to_edit}' not found.")
            self.refresh_display()
            return

        dialog = BastionEntryDialog(self, bastion_entry=bastion_to_edit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # The dialog's get_data method updates the bastion_to_edit object in place.
            self.main_window._save_app_data()
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"Bastion '{bastion_to_edit.bastion_name}' updated.", 3000)

    @Slot()
    def _on_delete_bastion(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "No campaign selected.")
            return

        selected_items = self.bastions_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a bastion to delete.")
            return

        selected_row = selected_items[0].row()
        bastion_id_to_delete = self.bastions_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        bastion_name = self.bastions_table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, "Delete Bastion",
                                     f"Are you sure you want to delete the bastion: '{bastion_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
            if campaign and campaign.bastions and bastion_id_to_delete in campaign.bastions:
                del campaign.bastions[bastion_id_to_delete]
                self.main_window._save_app_data()
                self.refresh_display()
                self.main_window.statusBar().showMessage(f"Bastion '{bastion_name}' deleted.", 3000)
            else:
                QMessageBox.warning(self, "Delete Error", "Bastion not found for deletion.")
                self.refresh_display()

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    from src.data_models import ApplicationData, Campaign

    class MockMainWindow(QMainWindow): # Mock for testing the widget
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "bastion_test_camp"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="Bastion Test Campaign")

            b1 = BastionEntry(bastion_name="Northwatch Keep", character_name="Gardner", level=3)
            b2 = BastionEntry(bastion_name="The Lonely Tower", character_name="Wizard Zed", level=5)
            campaign.bastions = {b1.entry_id: b1, b2.entry_id: b2} # Store as dict

            self.application_data.campaigns[self.current_campaign_id] = campaign
            self.setStatusBar(QStatusBar(self))

        def _save_app_data(self):
            print(f"MockMainWindow: _save_app_data called for campaign: {self.current_campaign_id}")

        def statusBar(self):
            return super().statusBar()

    app = QApplication(sys.argv)
    mock_main_win = MockMainWindow()
    bastion_widget = BastionTrackerWidget(mock_main_win)

    mock_main_win.setCentralWidget(bastion_widget)
    mock_main_win.setWindowTitle("Bastion Tracker Widget Test")
    mock_main_win.setGeometry(100, 100, 700, 500)

    bastion_widget.refresh_display()
    mock_main_win.show()
    sys.exit(app.exec())
