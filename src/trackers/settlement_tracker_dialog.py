from typing import Optional
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QDialogButtonBox, QComboBox,
    QSizeGrip, QHBoxLayout, QToolButton, QWidget, QLabel # Added QToolButton, QWidget, QLabel
)
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QTextListFormat # Added imports
from PySide6.QtCore import Qt
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
        self.setMinimumWidth(450) # Adjusted minimum width

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.size_combo = QComboBox()
        self.size_combo.addItems(SETTLEMENT_SIZE_OPTIONS)

        self.defining_trait_edit = QTextEdit()
        defining_trait_toolbar = self._create_rich_text_toolbar(self.defining_trait_edit)
        defining_trait_layout = QVBoxLayout()
        defining_trait_layout.setSpacing(2)
        defining_trait_layout.addWidget(defining_trait_toolbar)
        defining_trait_layout.addWidget(self.defining_trait_edit)
        defining_trait_widget = QWidget()
        defining_trait_widget.setLayout(defining_trait_layout)

        self.claim_to_fame_edit = QTextEdit()
        claim_to_fame_toolbar = self._create_rich_text_toolbar(self.claim_to_fame_edit)
        claim_to_fame_layout = QVBoxLayout()
        claim_to_fame_layout.setSpacing(2)
        claim_to_fame_layout.addWidget(claim_to_fame_toolbar)
        claim_to_fame_layout.addWidget(self.claim_to_fame_edit)
        claim_to_fame_widget = QWidget()
        claim_to_fame_widget.setLayout(claim_to_fame_layout)

        self.current_calamity_edit = QTextEdit()
        current_calamity_toolbar = self._create_rich_text_toolbar(self.current_calamity_edit)
        current_calamity_layout = QVBoxLayout()
        current_calamity_layout.setSpacing(2)
        current_calamity_layout.addWidget(current_calamity_toolbar)
        current_calamity_layout.addWidget(self.current_calamity_edit)
        current_calamity_widget = QWidget()
        current_calamity_widget.setLayout(current_calamity_layout)

        self.local_leader_edit = QLineEdit()

        self.noteworthy_people_edit = QTextEdit()
        noteworthy_people_toolbar = self._create_rich_text_toolbar(self.noteworthy_people_edit)
        noteworthy_people_layout = QVBoxLayout()
        noteworthy_people_layout.setSpacing(2)
        noteworthy_people_layout.addWidget(noteworthy_people_toolbar)
        noteworthy_people_layout.addWidget(self.noteworthy_people_edit)
        noteworthy_people_widget = QWidget()
        noteworthy_people_widget.setLayout(noteworthy_people_layout)

        self.noteworthy_places_edit = QTextEdit()
        noteworthy_places_toolbar = self._create_rich_text_toolbar(self.noteworthy_places_edit)
        noteworthy_places_layout = QVBoxLayout()
        noteworthy_places_layout.setSpacing(2)
        noteworthy_places_layout.addWidget(noteworthy_places_toolbar)
        noteworthy_places_layout.addWidget(self.noteworthy_places_edit)
        noteworthy_places_widget = QWidget()
        noteworthy_places_widget.setLayout(noteworthy_places_layout)

        self.gp_value_edit = QLineEdit() # Gold piece value

        form_layout.addRow("Name*:", self.name_edit)
        form_layout.addRow("Size:", self.size_combo)
        form_layout.addRow(QLabel("Defining Trait:"), defining_trait_widget)
        form_layout.addRow(QLabel("Claim to Fame:"), claim_to_fame_widget)
        form_layout.addRow(QLabel("Current Calamity:"), current_calamity_widget)
        form_layout.addRow("Local Leader:", self.local_leader_edit)
        form_layout.addRow(QLabel("Noteworthy People:"), noteworthy_people_widget)
        form_layout.addRow(QLabel("Noteworthy Places:"), noteworthy_places_widget)
        form_layout.addRow("GP Value of Most Expensive Item:", self.gp_value_edit)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_save)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        # Add QSizeGrip for resizing
        sizegrip_layout = QHBoxLayout()
        sizegrip_layout.addStretch(1)
        self.size_grip = QSizeGrip(self)
        sizegrip_layout.addWidget(self.size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        layout.addLayout(sizegrip_layout)

        if self.settlement_entry_to_edit:
            self._load_settlement_data()
        else:
            # Set default size for new entries if needed, though QComboBox defaults to first item
            self.size_combo.setCurrentIndex(0)

    def _create_rich_text_toolbar(self, text_edit: QTextEdit) -> QWidget:
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(3)

        # Bold Button
        bold_button = QToolButton()
        bold_button.setText("B")
        font = bold_button.font()
        font.setBold(True)
        bold_button.setFont(font)
        bold_button.setCheckable(True)
        bold_button.clicked.connect(lambda checked: text_edit.setFontWeight(QFont.Bold if checked else QFont.Normal))
        toolbar_layout.addWidget(bold_button)

        # Italic Button
        italic_button = QToolButton()
        italic_button.setText("I")
        font = italic_button.font()
        font.setItalic(True)
        italic_button.setFont(font)
        italic_button.setCheckable(True)
        italic_button.clicked.connect(lambda checked: text_edit.setFontItalic(checked))
        toolbar_layout.addWidget(italic_button)

        # Underline Button
        underline_button = QToolButton()
        underline_button.setText("U")
        font = underline_button.font()
        font.setUnderline(True)
        underline_button.setFont(font)
        underline_button.setCheckable(True)
        underline_button.clicked.connect(lambda checked: text_edit.setFontUnderline(checked))
        toolbar_layout.addWidget(underline_button)

        # Strikethrough Button
        strike_button = QToolButton()
        strike_button.setText("S")
        font = strike_button.font()
        font.setStrikeOut(True) # Visual cue on button
        strike_button.setFont(font)
        strike_button.setCheckable(True)
        def toggle_strike():
            fmt = text_edit.currentCharFormat()
            fmt.setFontStrikeOut(strike_button.isChecked())
            text_edit.setCurrentCharFormat(fmt)
        strike_button.clicked.connect(toggle_strike)
        toolbar_layout.addWidget(strike_button)

        toolbar_layout.addSpacing(10) # Separator

        # Bullet List Button
        bullet_list_button = QToolButton()
        bullet_list_button.setText("• List") # Or use an icon
        bullet_list_button.clicked.connect(lambda: text_edit.textCursor().createList(QTextListFormat.Style.ListDisc))
        toolbar_layout.addWidget(bullet_list_button)

        # Numbered List Button
        numbered_list_button = QToolButton()
        numbered_list_button.setText("1. List") # Or use an icon
        numbered_list_button.clicked.connect(lambda: text_edit.textCursor().createList(QTextListFormat.Style.ListDecimal))
        toolbar_layout.addWidget(numbered_list_button)

        toolbar_layout.addStretch() # Push buttons to the left

        # Update button states based on cursor's current format
        def update_button_states():
            fmt = text_edit.currentCharFormat()
            bold_button.setChecked(fmt.fontWeight() == QFont.Bold)
            italic_button.setChecked(fmt.fontItalic())
            underline_button.setChecked(fmt.fontUnderline())
            strike_button.setChecked(fmt.fontStrikeOut())

        text_edit.currentCharFormatChanged.connect(update_button_states)

        return toolbar_widget

    def _load_settlement_data(self):
        if self.settlement_entry_to_edit:
            self.name_edit.setText(self.settlement_entry_to_edit.name)

            if self.settlement_entry_to_edit.size in SETTLEMENT_SIZE_OPTIONS:
                self.size_combo.setCurrentText(self.settlement_entry_to_edit.size)
            else: # Fallback if data is inconsistent, or use first option
                self.size_combo.setCurrentIndex(0)

            self.defining_trait_edit.setHtml(self.settlement_entry_to_edit.defining_trait)
            self.claim_to_fame_edit.setHtml(self.settlement_entry_to_edit.claim_to_fame)
            self.current_calamity_edit.setHtml(self.settlement_entry_to_edit.current_calamity)
            self.local_leader_edit.setText(self.settlement_entry_to_edit.local_leader)
            self.noteworthy_people_edit.setHtml(self.settlement_entry_to_edit.noteworthy_people)
            self.noteworthy_places_edit.setHtml(self.settlement_entry_to_edit.noteworthy_places)
            self.gp_value_edit.setText(self.settlement_entry_to_edit.gp_value_most_expensive_item)

    def _on_save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Settlement Name cannot be empty.")
            return

        size = self.size_combo.currentText()
        defining_trait = self.defining_trait_edit.toHtml().strip()
        claim_to_fame = self.claim_to_fame_edit.toHtml().strip()
        current_calamity = self.current_calamity_edit.toHtml().strip()
        local_leader = self.local_leader_edit.text().strip()
        noteworthy_people = self.noteworthy_people_edit.toHtml().strip()
        noteworthy_places = self.noteworthy_places_edit.toHtml().strip()
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

    def get_entry_data(self) -> Optional[SettlementEntry]:
        if self.result() == QDialog.DialogCode.Accepted:
            return self.settlement_entry_to_edit
        return None

    def get_data(self):
        """Return the SettlementEntry instance for saving to the campaign."""
        return self.get_settlement_data()

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
