from typing import Optional, List
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QDialogButtonBox, QTableWidget,
    QTableWidgetItem, QCheckBox, QHeaderView, QGroupBox, QHBoxLayout,
    QWidget
)
from PySide6.QtCore import Qt
from src.data_models import GameExpectationsEntry, SensitiveElement

class GameExpectationsEntryDialog(QDialog):
    def __init__(self, parent_window, entry: Optional[GameExpectationsEntry] = None):
        super().__init__(parent_window)

        self.parent_main_window = parent_window
        self.entry_to_edit = entry

        if self.entry_to_edit:
            self.setWindowTitle("Edit Player Expectations")
        else:
            self.setWindowTitle("Add New Player Expectations")

        self.setModal(True)
        self.setMinimumWidth(550) # Adjusted for content

        main_layout = QVBoxLayout(self)

        # Main Details Form
        form_layout = QFormLayout()
        self.dm_name_edit = QLineEdit()
        self.player_name_edit = QLineEdit()
        self.game_theme_flavor_edit = QTextEdit()
        self.player_hopes_edit = QTextEdit()
        self.at_table_concerns_edit = QTextEdit()

        form_layout.addRow("DM Name:", self.dm_name_edit)
        form_layout.addRow("Player Name*:", self.player_name_edit)
        form_layout.addRow("Game Theme and Flavor:", self.game_theme_flavor_edit)
        form_layout.addRow("Player's Hopes/Expectations:", self.player_hopes_edit)
        form_layout.addRow("At-the-Table Concerns:", self.at_table_concerns_edit)
        main_layout.addLayout(form_layout)

        # Sensitive Elements Sub-Section
        sensitive_groupbox = QGroupBox("Potentially Sensitive Elements")
        sensitive_layout = QVBoxLayout(sensitive_groupbox)

        self.sensitive_elements_table = QTableWidget()
        self.sensitive_elements_table.setColumnCount(3)
        self.sensitive_elements_table.setHorizontalHeaderLabels(["Element Name/Description", "Hard Limit", "Soft Limit"])
        self.sensitive_elements_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.sensitive_elements_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.sensitive_elements_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        sensitive_buttons_layout = QHBoxLayout()
        self.add_sensitive_btn = QPushButton("Add Element")
        self.remove_sensitive_btn = QPushButton("Remove Selected Element")
        sensitive_buttons_layout.addWidget(self.add_sensitive_btn)
        sensitive_buttons_layout.addWidget(self.remove_sensitive_btn)
        sensitive_buttons_layout.addStretch()

        sensitive_layout.addLayout(sensitive_buttons_layout)
        sensitive_layout.addWidget(self.sensitive_elements_table)
        main_layout.addWidget(sensitive_groupbox)

        # Dialog Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        main_layout.addWidget(self.button_box)

        # Connect signals
        self.add_sensitive_btn.clicked.connect(lambda: self._add_sensitive_element_row())
        self.remove_sensitive_btn.clicked.connect(self._remove_sensitive_element_row)
        self.button_box.accepted.connect(self._on_save)
        self.button_box.rejected.connect(self.reject)

        if self.entry_to_edit:
            self._load_entry_data()
        else:
            # Auto-fill DM name from global campaign setting if available
            if self.parent_main_window.current_campaign_id:
                campaign = self.parent_main_window.application_data.campaigns.get(self.parent_main_window.current_campaign_id)
                if campaign and campaign.dm_name_global:
                    self.dm_name_edit.setText(campaign.dm_name_global)


    def _load_entry_data(self):
        if self.entry_to_edit:
            self.dm_name_edit.setText(self.entry_to_edit.dm_name)
            self.player_name_edit.setText(self.entry_to_edit.player_name)
            self.game_theme_flavor_edit.setPlainText(self.entry_to_edit.game_theme_flavor)
            self.player_hopes_edit.setPlainText(self.entry_to_edit.player_hopes)
            self.at_table_concerns_edit.setPlainText(self.entry_to_edit.at_table_concerns)

            self.sensitive_elements_table.setRowCount(0) # Clear table first
            for element in self.entry_to_edit.sensitive_elements:
                self._add_sensitive_element_row(element)

    def _add_sensitive_element_row(self, element: Optional[SensitiveElement] = None):
        row_position = self.sensitive_elements_table.rowCount()
        self.sensitive_elements_table.insertRow(row_position)

        name_item = QTableWidgetItem(element.name if element else "")
        self.sensitive_elements_table.setItem(row_position, 0, name_item) # Element Name is editable text

        hard_limit_checkbox = QCheckBox()
        hard_limit_checkbox.setChecked(element.hard_limit if element else False)
        hard_limit_widget = QWidget() # Use a widget container for centering
        h_layout = QHBoxLayout(hard_limit_widget)
        h_layout.addWidget(hard_limit_checkbox)
        h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.setContentsMargins(0,0,0,0)
        self.sensitive_elements_table.setCellWidget(row_position, 1, hard_limit_widget)


        soft_limit_checkbox = QCheckBox()
        soft_limit_checkbox.setChecked(element.soft_limit if element else False)
        soft_limit_widget = QWidget()
        s_layout = QHBoxLayout(soft_limit_widget)
        s_layout.addWidget(soft_limit_checkbox)
        s_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s_layout.setContentsMargins(0,0,0,0)
        self.sensitive_elements_table.setCellWidget(row_position, 2, soft_limit_widget)

        # Ensure the table is editable for the name column
        name_item.setFlags(name_item.flags() | Qt.ItemFlag.ItemIsEditable)


    def _remove_sensitive_element_row(self):
        current_row = self.sensitive_elements_table.currentRow()
        if current_row >= 0:
            self.sensitive_elements_table.removeRow(current_row)
        else:
            QMessageBox.information(self, "No Selection", "Please select a sensitive element row to remove.")

    def _on_save(self):
        player_name = self.player_name_edit.text().strip()
        if not player_name:
            QMessageBox.warning(self, "Validation Error", "Player Name cannot be empty.")
            return

        dm_name = self.dm_name_edit.text().strip()
        game_theme_flavor = self.game_theme_flavor_edit.toPlainText().strip()
        player_hopes = self.player_hopes_edit.toPlainText().strip()
        at_table_concerns = self.at_table_concerns_edit.toPlainText().strip()

        collected_sensitive_elements: List[SensitiveElement] = []
        for row in range(self.sensitive_elements_table.rowCount()):
            name_item = self.sensitive_elements_table.item(row, 0)
            name = name_item.text().strip() if name_item else ""

            hard_limit_widget = self.sensitive_elements_table.cellWidget(row, 1)
            hard_limit_checkbox = cast(QCheckBox, hard_limit_widget.layout().itemAt(0).widget()) if hard_limit_widget else None
            hard_limit = hard_limit_checkbox.isChecked() if hard_limit_checkbox else False

            soft_limit_widget = self.sensitive_elements_table.cellWidget(row, 2)
            soft_limit_checkbox = cast(QCheckBox, soft_limit_widget.layout().itemAt(0).widget()) if soft_limit_widget else None
            soft_limit = soft_limit_checkbox.isChecked() if soft_limit_checkbox else False

            if name: # Only add if name is present
                collected_sensitive_elements.append(SensitiveElement(name=name, hard_limit=hard_limit, soft_limit=soft_limit))

        active_campaign_id = self.parent_main_window.current_campaign_id
        if not active_campaign_id:
            QMessageBox.critical(self, "Error", "No active campaign selected.")
            return

        campaign_data = self.parent_main_window.application_data.campaigns.get(active_campaign_id)
        if not campaign_data:
            QMessageBox.critical(self, "Error", "Could not find active campaign data.")
            return

        if self.entry_to_edit:
            self.entry_to_edit.dm_name = dm_name
            self.entry_to_edit.player_name = player_name
            self.entry_to_edit.game_theme_flavor = game_theme_flavor
            self.entry_to_edit.sensitive_elements = collected_sensitive_elements
            self.entry_to_edit.player_hopes = player_hopes
            self.entry_to_edit.at_table_concerns = at_table_concerns
        else:
            new_entry = GameExpectationsEntry(
                dm_name=dm_name,
                player_name=player_name,
                game_theme_flavor=game_theme_flavor,
                sensitive_elements=collected_sensitive_elements,
                player_hopes=player_hopes,
                at_table_concerns=at_table_concerns
            )
            campaign_data.game_expectations[new_entry.entry_id] = new_entry
            self.entry_to_edit = new_entry

        self.parent_main_window._save_app_data()
        super().accept()

    def get_entry_data(self) -> Optional[GameExpectationsEntry]:
        if self.result() == QDialog.DialogCode.Accepted:
            return self.entry_to_edit
        return None

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    from src.data_models import ApplicationData, Campaign
    from typing import cast

    class MockMainWindow:
        def __init__(self):
            self.current_campaign_id = "test_ge_campaign"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="GE Test Campaign", dm_name_global="Test DM")
            self.application_data.campaigns[self.current_campaign_id] = campaign

        def _save_app_data(self):
            print(f"Mock save_app_data called for campaign: {self.current_campaign_id}")

    app = QApplication([])
    mock_parent = MockMainWindow()

    # Test Add
    dialog_add = GameExpectationsEntryDialog(mock_parent)
    if dialog_add.exec() == QDialog.DialogCode.Accepted:
        print("Add GE dialog accepted. Data:", dialog_add.get_entry_data())
        if dialog_add.get_entry_data():
            entry_id = dialog_add.get_entry_data().entry_id
            print(f"Entry in mock data: {mock_parent.application_data.campaigns[mock_parent.current_campaign_id].game_expectations.get(entry_id)}")

    # Test Edit
    existing_se = [SensitiveElement("Spiders", True, False), SensitiveElement("Heights", False, True)]
    existing_entry = GameExpectationsEntry(player_name="Old Player", dm_name="Old DM", sensitive_elements=existing_se)
    mock_parent.application_data.campaigns[mock_parent.current_campaign_id].game_expectations[existing_entry.entry_id] = existing_entry

    dialog_edit = GameExpectationsEntryDialog(mock_parent, entry=existing_entry)
    if dialog_edit.exec() == QDialog.DialogCode.Accepted:
        print("Edit GE dialog accepted. Data:", dialog_edit.get_entry_data())
        updated_entry = mock_parent.application_data.campaigns[mock_parent.current_campaign_id].game_expectations.get(existing_entry.entry_id)
        print(f"Updated entry in mock data: {updated_entry}")
        if updated_entry:
            print(f"Updated sensitive elements: {updated_entry.sensitive_elements}")

    del app
