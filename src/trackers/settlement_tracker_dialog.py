from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QDialogButtonBox, QComboBox
)
from src.data_models import SettlementEntry

SETTLEMENT_SIZE_OPTIONS = [
    "Village (Pop up to 500)",
    "Town (Pop. 501-5,000)",
    "City (Pop. 5,001+)"
]

class SettlementEntryDialog(QDialog):
    def __init__(self, parent_window, settlement_entry: Optional[SettlementEntry] = None):
        super().__init__(parent_window)

        self.parent_main_window = parent_window
        self.settlement_entry_to_edit = settlement_entry

        if self.settlement_entry_to_edit:
            self.setWindowTitle("Edit Settlement")
        else:
            self.setWindowTitle("Add New Settlement")

        self.setModal(True)
        self.setMinimumWidth(500) # Increased width for QTextEdit fields

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.size_combo = QComboBox()
        self.size_combo.addItems(SETTLEMENT_SIZE_OPTIONS)

        self.defining_trait_edit = QTextEdit()
        self.claim_to_fame_edit = QTextEdit()
        self.current_calamity_edit = QTextEdit()
        self.local_leader_edit = QLineEdit()
        self.noteworthy_people_edit = QTextEdit()
        self.noteworthy_places_edit = QTextEdit()
        self.gp_value_edit = QLineEdit() # Gold piece value

        form_layout.addRow("Name*:", self.name_edit)
        form_layout.addRow("Size:", self.size_combo)
        form_layout.addRow("Defining Trait:", self.defining_trait_edit)
        form_layout.addRow("Claim to Fame:", self.claim_to_fame_edit)
        form_layout.addRow("Current Calamity:", self.current_calamity_edit)
        form_layout.addRow("Local Leader:", self.local_leader_edit)
        form_layout.addRow("Noteworthy People:", self.noteworthy_people_edit)
        form_layout.addRow("Noteworthy Places:", self.noteworthy_places_edit)
        form_layout.addRow("GP Value of Most Expensive Item:", self.gp_value_edit)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_save)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        if self.settlement_entry_to_edit:
            self._load_settlement_data()
        else:
            # Set default size for new entries if needed, though QComboBox defaults to first item
            self.size_combo.setCurrentIndex(0)


    def _load_settlement_data(self):
        if self.settlement_entry_to_edit:
            self.name_edit.setText(self.settlement_entry_to_edit.name)

            if self.settlement_entry_to_edit.size in SETTLEMENT_SIZE_OPTIONS:
                self.size_combo.setCurrentText(self.settlement_entry_to_edit.size)
            else: # Fallback if data is inconsistent, or use first option
                self.size_combo.setCurrentIndex(0)

            self.defining_trait_edit.setPlainText(self.settlement_entry_to_edit.defining_trait)
            self.claim_to_fame_edit.setPlainText(self.settlement_entry_to_edit.claim_to_fame)
            self.current_calamity_edit.setPlainText(self.settlement_entry_to_edit.current_calamity)
            self.local_leader_edit.setText(self.settlement_entry_to_edit.local_leader)
            self.noteworthy_people_edit.setPlainText(self.settlement_entry_to_edit.noteworthy_people)
            self.noteworthy_places_edit.setPlainText(self.settlement_entry_to_edit.noteworthy_places)
            self.gp_value_edit.setText(self.settlement_entry_to_edit.gp_value_most_expensive_item)

    def _on_save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Settlement Name cannot be empty.")
            return

        size = self.size_combo.currentText()
        defining_trait = self.defining_trait_edit.toPlainText().strip()
        claim_to_fame = self.claim_to_fame_edit.toPlainText().strip()
        current_calamity = self.current_calamity_edit.toPlainText().strip()
        local_leader = self.local_leader_edit.text().strip()
        noteworthy_people = self.noteworthy_people_edit.toPlainText().strip()
        noteworthy_places = self.noteworthy_places_edit.toPlainText().strip()
        gp_value = self.gp_value_edit.text().strip()

        active_campaign_id = self.parent_main_window.current_campaign_id
        if not active_campaign_id:
            QMessageBox.critical(self, "Error", "No active campaign selected.")
            return

        campaign_data = self.parent_main_window.application_data.campaigns.get(active_campaign_id)
        if not campaign_data:
            QMessageBox.critical(self, "Error", "Could not find active campaign data.")
            return

        if self.settlement_entry_to_edit:
            self.settlement_entry_to_edit.name = name
            self.settlement_entry_to_edit.size = size
            self.settlement_entry_to_edit.defining_trait = defining_trait
            self.settlement_entry_to_edit.claim_to_fame = claim_to_fame
            self.settlement_entry_to_edit.current_calamity = current_calamity
            self.settlement_entry_to_edit.local_leader = local_leader
            self.settlement_entry_to_edit.noteworthy_people = noteworthy_people
            self.settlement_entry_to_edit.noteworthy_places = noteworthy_places
            self.settlement_entry_to_edit.gp_value_most_expensive_item = gp_value
        else:
            new_settlement_entry = SettlementEntry(
                name=name,
                size=size,
                defining_trait=defining_trait,
                claim_to_fame=claim_to_fame,
                current_calamity=current_calamity,
                local_leader=local_leader,
                noteworthy_people=noteworthy_people,
                noteworthy_places=noteworthy_places,
                gp_value_most_expensive_item=gp_value
            )
            campaign_data.settlements[new_settlement_entry.entry_id] = new_settlement_entry
            self.settlement_entry_to_edit = new_settlement_entry

        self.parent_main_window._save_app_data()
        super().accept()

    def get_settlement_data(self) -> Optional[SettlementEntry]:
        if self.result() == QDialog.DialogCode.Accepted:
            return self.settlement_entry_to_edit
        return None

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    from src.data_models import ApplicationData, Campaign

    class MockMainWindow:
        def __init__(self):
            self.current_campaign_id = "test_settlement_campaign"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="Settlement Test Campaign")
            self.application_data.campaigns[self.current_campaign_id] = campaign

        def _save_app_data(self):
            print(f"Mock save_app_data called for campaign: {self.current_campaign_id}")

    app = QApplication([])
    mock_parent = MockMainWindow()

    dialog_add = SettlementEntryDialog(mock_parent)
    if dialog_add.exec() == QDialog.DialogCode.Accepted:
        print("Add Settlement dialog accepted. Data:", dialog_add.get_settlement_data())
        if dialog_add.get_settlement_data():
            entry_id = dialog_add.get_settlement_data().entry_id
            print(f"Entry in mock data: {mock_parent.application_data.campaigns[mock_parent.current_campaign_id].settlements.get(entry_id)}")

    # Test editing
    existing_entry_data = SettlementEntry(name="Old Town", size=SETTLEMENT_SIZE_OPTIONS[1])
    mock_parent.application_data.campaigns[mock_parent.current_campaign_id].settlements[existing_entry_data.entry_id] = existing_entry_data

    dialog_edit = SettlementEntryDialog(mock_parent, settlement_entry=existing_entry_data)
    if dialog_edit.exec() == QDialog.DialogCode.Accepted:
        print("Edit Settlement dialog accepted. Data:", dialog_edit.get_settlement_data())
        print(f"Updated entry in mock data: {mock_parent.application_data.campaigns[mock_parent.current_campaign_id].settlements.get(existing_entry_data.entry_id)}")

    del app
