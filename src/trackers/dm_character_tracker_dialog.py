from typing import Optional, List, Dict
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QDialogButtonBox, QSpinBox, QCheckBox,
    QGroupBox, QGridLayout, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from src.data_models import DMCharacterEntry

PLAYER_MOTIVATION_OPTIONS = [
    "Acting", "Exploring", "Fighting", "Instigating",
    "Optimizing", "Problem-Solving", "Socializing", "Storytelling"
]

class DMCharacterEntryDialog(QDialog):
    def __init__(self, parent_window, entry: Optional[DMCharacterEntry] = None):
        super().__init__(parent_window)

        self.parent_main_window = parent_window
        self.entry_to_edit = entry

        if self.entry_to_edit:
            self.setWindowTitle(f"Edit PC: {self.entry_to_edit.character_name}")
        else:
            self.setWindowTitle("Add New Player Character (PC)")

        self.setModal(True)
        self.setMinimumWidth(500) # Good starting width

        # Main layout for the dialog
        main_dialog_layout = QVBoxLayout(self)

        # Scroll Area for potentially long content
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        main_dialog_layout.addWidget(scroll_area)

        scroll_content_widget = QWidget()
        scroll_area.setWidget(scroll_content_widget)

        form_layout = QFormLayout(scroll_content_widget) # Layout inside scroll area

        # Character and Player Info
        self.character_name_edit = QLineEdit()
        self.player_name_edit = QLineEdit()
        form_layout.addRow("Character's Name*:", self.character_name_edit)
        form_layout.addRow("Player's Name:", self.player_name_edit)

        # Player Motivations Section
        motivations_groupbox = QGroupBox("Player Motivations")
        motivations_grid_layout = QGridLayout(motivations_groupbox)
        self.motivation_checkboxes: Dict[str, QCheckBox] = {}
        cols = 2 # Number of columns for checkboxes
        for i, motivation_text in enumerate(PLAYER_MOTIVATION_OPTIONS):
            checkbox = QCheckBox(motivation_text)
            self.motivation_checkboxes[motivation_text] = checkbox
            motivations_grid_layout.addWidget(checkbox, i // cols, i % cols)
        form_layout.addRow(motivations_groupbox)

        self.notes_on_player_expectations_edit = QTextEdit()
        form_layout.addRow("Notes on Player Expectations:", self.notes_on_player_expectations_edit)

        # Character Stats
        stats_groupbox = QGroupBox("Character Stats")
        stats_layout = QFormLayout(stats_groupbox)
        self.char_class_edit = QLineEdit()
        self.subclass_edit = QLineEdit()
        self.level_spinbox = QSpinBox()
        self.level_spinbox.setMinimum(1)
        self.level_spinbox.setMaximum(20) # Or higher if your game supports it
        self.background_edit = QLineEdit()
        self.species_race_edit = QLineEdit()
        self.alignment_edit = QLineEdit()
        stats_layout.addRow("Class:", self.char_class_edit)
        stats_layout.addRow("Subclass:", self.subclass_edit)
        stats_layout.addRow("Level:", self.level_spinbox)
        stats_layout.addRow("Background:", self.background_edit)
        stats_layout.addRow("Species/Race:", self.species_race_edit)
        stats_layout.addRow("Alignment:", self.alignment_edit)
        form_layout.addRow(stats_groupbox)

        # Character Details
        details_groupbox = QGroupBox("Character Details")
        details_layout = QFormLayout(details_groupbox)
        self.goals_ambitions_edit = QTextEdit()
        self.quirks_whims_edit = QTextEdit()
        self.magic_items_owned_edit = QTextEdit()
        self.character_details_edit = QTextEdit() # General details
        self.family_friends_foes_edit = QTextEdit()
        self.adventure_ideas_edit = QTextEdit()
        details_layout.addRow("Goals & Ambitions:", self.goals_ambitions_edit)
        details_layout.addRow("Quirks & Whims:", self.quirks_whims_edit)
        details_layout.addRow("Magic Items Owned:", self.magic_items_owned_edit)
        details_layout.addRow("Other Character Details:", self.character_details_edit)
        details_layout.addRow("Family, Friends, & Foes:", self.family_friends_foes_edit)
        details_layout.addRow("Adventure Ideas (DM):", self.adventure_ideas_edit)
        form_layout.addRow(details_groupbox)

        # Dialog Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        main_dialog_layout.addWidget(self.button_box) # Add button box to main dialog layout, not scroll

        # Connect signals
        self.button_box.accepted.connect(self._on_save)
        self.button_box.rejected.connect(self.reject)

        if self.entry_to_edit:
            self._load_entry_data()

    def _load_entry_data(self):
        if self.entry_to_edit:
            self.character_name_edit.setText(self.entry_to_edit.character_name)
            self.player_name_edit.setText(self.entry_to_edit.player_name)

            for motivation, checkbox in self.motivation_checkboxes.items():
                checkbox.setChecked(motivation in self.entry_to_edit.player_motivations)

            self.notes_on_player_expectations_edit.setPlainText(self.entry_to_edit.notes_on_player_expectations)
            self.char_class_edit.setText(self.entry_to_edit.char_class)
            self.subclass_edit.setText(self.entry_to_edit.subclass)
            self.level_spinbox.setValue(self.entry_to_edit.level)
            self.background_edit.setText(self.entry_to_edit.background)
            self.species_race_edit.setText(self.entry_to_edit.species_race)
            self.alignment_edit.setText(self.entry_to_edit.alignment)
            self.goals_ambitions_edit.setPlainText(self.entry_to_edit.goals_ambitions)
            self.quirks_whims_edit.setPlainText(self.entry_to_edit.quirks_whims)
            self.magic_items_owned_edit.setPlainText(self.entry_to_edit.magic_items_owned)
            self.character_details_edit.setPlainText(self.entry_to_edit.character_details)
            self.family_friends_foes_edit.setPlainText(self.entry_to_edit.family_friends_foes)
            self.adventure_ideas_edit.setPlainText(self.entry_to_edit.adventure_ideas)

    def _on_save(self):
        character_name = self.character_name_edit.text().strip()
        if not character_name:
            QMessageBox.warning(self, "Validation Error", "Character's Name cannot be empty.")
            return

        player_name = self.player_name_edit.text().strip()

        selected_motivations: List[str] = []
        for motivation, checkbox in self.motivation_checkboxes.items():
            if checkbox.isChecked():
                selected_motivations.append(motivation)

        notes_on_player_expectations = self.notes_on_player_expectations_edit.toPlainText().strip()
        char_class = self.char_class_edit.text().strip()
        subclass = self.subclass_edit.text().strip()
        level = self.level_spinbox.value()
        background = self.background_edit.text().strip()
        species_race = self.species_race_edit.text().strip()
        alignment = self.alignment_edit.text().strip()
        goals_ambitions = self.goals_ambitions_edit.toPlainText().strip()
        quirks_whims = self.quirks_whims_edit.toPlainText().strip()
        magic_items_owned = self.magic_items_owned_edit.toPlainText().strip()
        character_details = self.character_details_edit.toPlainText().strip()
        family_friends_foes = self.family_friends_foes_edit.toPlainText().strip()
        adventure_ideas = self.adventure_ideas_edit.toPlainText().strip()

        active_campaign_id = self.parent_main_window.current_campaign_id
        if not active_campaign_id:
            QMessageBox.critical(self, "Error", "No active campaign selected.")
            return

        campaign_data = self.parent_main_window.application_data.campaigns.get(active_campaign_id)
        if not campaign_data:
            QMessageBox.critical(self, "Error", "Could not find active campaign data.")
            return

        if self.entry_to_edit:
            entry = self.entry_to_edit
        else:
            entry = DMCharacterEntry() # ID will be auto-generated

        entry.character_name = character_name
        entry.player_name = player_name
        entry.player_motivations = selected_motivations
        entry.notes_on_player_expectations = notes_on_player_expectations
        entry.char_class = char_class
        entry.subclass = subclass
        entry.level = level
        entry.background = background
        entry.species_race = species_race
        entry.alignment = alignment
        entry.goals_ambitions = goals_ambitions
        entry.quirks_whims = quirks_whims
        entry.magic_items_owned = magic_items_owned
        entry.character_details = character_details
        entry.family_friends_foes = family_friends_foes
        entry.adventure_ideas = adventure_ideas

        if not self.entry_to_edit: # If new, add to campaign data
            campaign_data.dm_characters[entry.entry_id] = entry
            self.entry_to_edit = entry # So get_entry_data can return it

        self.parent_main_window._save_app_data()
        super().accept()

    def get_entry_data(self) -> Optional[DMCharacterEntry]:
        if self.result() == QDialog.DialogCode.Accepted:
            return self.entry_to_edit
        return None

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    from src.data_models import ApplicationData, Campaign

    class MockMainWindow:
        def __init__(self):
            self.current_campaign_id = "test_dmc_campaign"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="DMC Test Campaign")
            self.application_data.campaigns[self.current_campaign_id] = campaign

        def _save_app_data(self): print(f"Mock save_app_data for {self.current_campaign_id}")

    app = QApplication([])
    mock_parent_win = MockMainWindow()

    # Test Add
    add_dialog = DMCharacterEntryDialog(mock_parent_win)
    if add_dialog.exec() == QDialog.DialogCode.Accepted:
        new_char = add_dialog.get_entry_data()
        print("Add DMC Dialog Accepted. Data:", new_char)
        if new_char:
            print("Motivations:", new_char.player_motivations)
            entry_id = new_char.entry_id
            print(f"Entry in mock data: {mock_parent_win.application_data.campaigns[mock_parent_win.current_campaign_id].dm_characters.get(entry_id)}")

    # Test Edit
    existing_char = DMCharacterEntry(character_name="Old Hero", player_name="Old Player", level=5, player_motivations=["Exploring", "Fighting"])
    mock_parent_win.application_data.campaigns[mock_parent_win.current_campaign_id].dm_characters[existing_char.entry_id] = existing_char

    edit_dialog = DMCharacterEntryDialog(mock_parent_win, entry=existing_char)
    if edit_dialog.exec() == QDialog.DialogCode.Accepted:
        updated_char = edit_dialog.get_entry_data()
        print("Edit DMC Dialog Accepted. Data:", updated_char)
        if updated_char:
            print("Motivations:", updated_char.player_motivations)
            print(f"Updated entry in mock data: {mock_parent_win.application_data.campaigns[mock_parent_win.current_campaign_id].dm_characters.get(existing_char.entry_id)}")

    del app
