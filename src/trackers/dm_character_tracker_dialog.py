from typing import Optional, List, Dict
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QDialogButtonBox, QSpinBox, QCheckBox,
    QGroupBox, QGridLayout, QScrollArea, QWidget, QSizeGrip, QHBoxLayout,
    QToolButton, QLabel # Added QToolButton, QLabel
)
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QTextListFormat # Added imports
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
        self.setMinimumWidth(450) # Adjusted minimum width

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
        notes_expectations_toolbar = self._create_rich_text_toolbar(self.notes_on_player_expectations_edit)
        notes_expectations_layout = QVBoxLayout()
        notes_expectations_layout.setSpacing(2)
        notes_expectations_layout.addWidget(notes_expectations_toolbar)
        notes_expectations_layout.addWidget(self.notes_on_player_expectations_edit)
        notes_expectations_widget = QWidget()
        notes_expectations_widget.setLayout(notes_expectations_layout)
        form_layout.addRow(QLabel("Notes on Player Expectations:"), notes_expectations_widget)

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
        goals_toolbar = self._create_rich_text_toolbar(self.goals_ambitions_edit)
        goals_layout = QVBoxLayout()
        goals_layout.setSpacing(2)
        goals_layout.addWidget(goals_toolbar)
        goals_layout.addWidget(self.goals_ambitions_edit)
        goals_widget = QWidget()
        goals_widget.setLayout(goals_layout)
        details_layout.addRow(QLabel("Goals & Ambitions:"), goals_widget)

        self.quirks_whims_edit = QTextEdit()
        quirks_toolbar = self._create_rich_text_toolbar(self.quirks_whims_edit)
        quirks_layout = QVBoxLayout()
        quirks_layout.setSpacing(2)
        quirks_layout.addWidget(quirks_toolbar)
        quirks_layout.addWidget(self.quirks_whims_edit)
        quirks_widget = QWidget()
        quirks_widget.setLayout(quirks_layout)
        details_layout.addRow(QLabel("Quirks & Whims:"), quirks_widget)

        self.magic_items_owned_edit = QTextEdit()
        magic_items_toolbar = self._create_rich_text_toolbar(self.magic_items_owned_edit)
        magic_items_layout = QVBoxLayout()
        magic_items_layout.setSpacing(2)
        magic_items_layout.addWidget(magic_items_toolbar)
        magic_items_layout.addWidget(self.magic_items_owned_edit)
        magic_items_widget = QWidget()
        magic_items_widget.setLayout(magic_items_layout)
        details_layout.addRow(QLabel("Magic Items Owned:"), magic_items_widget)

        self.character_details_edit = QTextEdit() # General details
        char_details_toolbar = self._create_rich_text_toolbar(self.character_details_edit)
        char_details_layout = QVBoxLayout()
        char_details_layout.setSpacing(2)
        char_details_layout.addWidget(char_details_toolbar)
        char_details_layout.addWidget(self.character_details_edit)
        char_details_widget = QWidget()
        char_details_widget.setLayout(char_details_layout)
        details_layout.addRow(QLabel("Other Character Details:"), char_details_widget)

        self.family_friends_foes_edit = QTextEdit()
        family_toolbar = self._create_rich_text_toolbar(self.family_friends_foes_edit)
        family_layout = QVBoxLayout()
        family_layout.setSpacing(2)
        family_layout.addWidget(family_toolbar)
        family_layout.addWidget(self.family_friends_foes_edit)
        family_widget = QWidget()
        family_widget.setLayout(family_layout)
        details_layout.addRow(QLabel("Family, Friends, & Foes:"), family_widget)

        self.adventure_ideas_edit = QTextEdit()
        adventure_toolbar = self._create_rich_text_toolbar(self.adventure_ideas_edit)
        adventure_layout = QVBoxLayout()
        adventure_layout.setSpacing(2)
        adventure_layout.addWidget(adventure_toolbar)
        adventure_layout.addWidget(self.adventure_ideas_edit)
        adventure_widget = QWidget()
        adventure_widget.setLayout(adventure_layout)
        details_layout.addRow(QLabel("Adventure Ideas (DM):"), adventure_widget)

        form_layout.addRow(details_groupbox)

        # Dialog Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        main_dialog_layout.addWidget(self.button_box) # Add button box to main dialog layout, not scroll

        # Add QSizeGrip for resizing
        sizegrip_layout = QHBoxLayout()
        sizegrip_layout.addStretch(1)
        self.size_grip = QSizeGrip(self)
        sizegrip_layout.addWidget(self.size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        main_dialog_layout.addLayout(sizegrip_layout)

        # Connect signals
        self.button_box.accepted.connect(self._on_save)
        self.button_box.rejected.connect(self.reject)

        if self.entry_to_edit:
            self._load_entry_data()

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

    def _load_entry_data(self):
        if self.entry_to_edit:
            self.character_name_edit.setText(self.entry_to_edit.character_name)
            self.player_name_edit.setText(self.entry_to_edit.player_name)

            for motivation, checkbox in self.motivation_checkboxes.items():
                checkbox.setChecked(motivation in self.entry_to_edit.player_motivations)

            self.notes_on_player_expectations_edit.setHtml(self.entry_to_edit.notes_on_player_expectations)
            self.char_class_edit.setText(self.entry_to_edit.char_class)
            self.subclass_edit.setText(self.entry_to_edit.subclass)
            self.level_spinbox.setValue(self.entry_to_edit.level)
            self.background_edit.setText(self.entry_to_edit.background)
            self.species_race_edit.setText(self.entry_to_edit.species_race)
            self.alignment_edit.setText(self.entry_to_edit.alignment)
            self.goals_ambitions_edit.setHtml(self.entry_to_edit.goals_ambitions)
            self.quirks_whims_edit.setHtml(self.entry_to_edit.quirks_whims)
            self.magic_items_owned_edit.setHtml(self.entry_to_edit.magic_items_owned)
            self.character_details_edit.setHtml(self.entry_to_edit.character_details)
            self.family_friends_foes_edit.setHtml(self.entry_to_edit.family_friends_foes)
            self.adventure_ideas_edit.setHtml(self.entry_to_edit.adventure_ideas)

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

        notes_on_player_expectations = self.notes_on_player_expectations_edit.toHtml().strip()
        char_class = self.char_class_edit.text().strip()
        subclass = self.subclass_edit.text().strip()
        level = self.level_spinbox.value()
        background = self.background_edit.text().strip()
        species_race = self.species_race_edit.text().strip()
        alignment = self.alignment_edit.text().strip()
        goals_ambitions = self.goals_ambitions_edit.toHtml().strip()
        quirks_whims = self.quirks_whims_edit.toHtml().strip()
        magic_items_owned = self.magic_items_owned_edit.toHtml().strip()
        character_details = self.character_details_edit.toHtml().strip()
        family_friends_foes = self.family_friends_foes_edit.toHtml().strip()
        adventure_ideas = self.adventure_ideas_edit.toHtml().strip()

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
