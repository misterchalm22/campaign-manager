import uuid
from typing import Optional

import uuid
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QHBoxLayout, QMessageBox, QDialogButtonBox,
    QSizeGrip, QToolButton, QWidget, QLabel # Added QToolButton, QWidget, QLabel
)
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QTextListFormat # Added imports
from PySide6.QtCore import Qt
from src.data_models import NPCEntry
# Assuming main_window.py contains MainWindow which has application_data and _save_app_data
# To avoid circular import, we might pass main_window and use it, or use signals
# For now, as per prompt, parent_window is the main_window instance

class NPCEntryDialog(QDialog):
    def __init__(self, parent_window, npc_entry: Optional[NPCEntry] = None):
        super().__init__(parent_window) # parent_window here refers to the QWidget parent for dialog

        self.parent_main_window = parent_window # Store the actual main_window instance
        self.npc_entry_to_edit = npc_entry

        if self.npc_entry_to_edit:
            self.setWindowTitle("Edit NPC")
        else:
            self.setWindowTitle("Add New NPC")

        self.setModal(True)
        self.setMinimumWidth(350) # Adjusted minimum width

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.stat_block_source_edit = QLineEdit()
        self.mm_page_edit = QLineEdit()

        self.stat_block_alterations_edit = QTextEdit()
        stat_block_toolbar = self._create_rich_text_toolbar(self.stat_block_alterations_edit)
        stat_block_layout = QVBoxLayout()
        stat_block_layout.setSpacing(2)
        stat_block_layout.addWidget(stat_block_toolbar)
        stat_block_layout.addWidget(self.stat_block_alterations_edit)
        stat_block_widget = QWidget()
        stat_block_widget.setLayout(stat_block_layout)

        self.alignment_edit = QLineEdit()

        self.personality_edit = QTextEdit()
        personality_toolbar = self._create_rich_text_toolbar(self.personality_edit)
        personality_layout = QVBoxLayout()
        personality_layout.setSpacing(2)
        personality_layout.addWidget(personality_toolbar)
        personality_layout.addWidget(self.personality_edit)
        personality_widget = QWidget()
        personality_widget.setLayout(personality_layout)

        self.appearance_edit = QTextEdit()
        appearance_toolbar = self._create_rich_text_toolbar(self.appearance_edit)
        appearance_layout = QVBoxLayout()
        appearance_layout.setSpacing(2)
        appearance_layout.addWidget(appearance_toolbar)
        appearance_layout.addWidget(self.appearance_edit)
        appearance_widget = QWidget()
        appearance_widget.setLayout(appearance_layout)

        self.secret_edit = QTextEdit()
        secret_toolbar = self._create_rich_text_toolbar(self.secret_edit)
        secret_layout = QVBoxLayout()
        secret_layout.setSpacing(2)
        secret_layout.addWidget(secret_toolbar)
        secret_layout.addWidget(self.secret_edit)
        secret_widget = QWidget()
        secret_widget.setLayout(secret_layout)

        form_layout.addRow("Name*:", self.name_edit)
        form_layout.addRow("Stat Block Source:", self.stat_block_source_edit)
        form_layout.addRow("MM Page:", self.mm_page_edit)
        form_layout.addRow(QLabel("Stat Block Alterations:"), stat_block_widget)
        form_layout.addRow("Alignment:", self.alignment_edit)
        form_layout.addRow(QLabel("Personality:"), personality_widget)
        form_layout.addRow(QLabel("Appearance:"), appearance_widget)
        form_layout.addRow(QLabel("Secret:"), secret_widget)

        layout.addLayout(form_layout)

        # Buttons
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

        if self.npc_entry_to_edit:
            self._load_npc_data()

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

    def _load_npc_data(self):
        if self.npc_entry_to_edit:
            self.name_edit.setText(self.npc_entry_to_edit.name)
            self.stat_block_source_edit.setText(self.npc_entry_to_edit.stat_block_source)
            self.mm_page_edit.setText(self.npc_entry_to_edit.mm_page)
            self.stat_block_alterations_edit.setHtml(self.npc_entry_to_edit.stat_block_alterations)
            self.alignment_edit.setText(self.npc_entry_to_edit.alignment)
            self.personality_edit.setHtml(self.npc_entry_to_edit.personality)
            self.appearance_edit.setHtml(self.npc_entry_to_edit.appearance)
            self.secret_edit.setHtml(self.npc_entry_to_edit.secret)

    def _on_save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "NPC Name cannot be empty.")
            return

        stat_block_source = self.stat_block_source_edit.text().strip()
        mm_page = self.mm_page_edit.text().strip()
        stat_block_alterations = self.stat_block_alterations_edit.toHtml().strip()
        alignment = self.alignment_edit.text().strip()
        personality = self.personality_edit.toHtml().strip()
        appearance = self.appearance_edit.toHtml().strip()
        secret = self.secret_edit.toHtml().strip()

        active_campaign_id = self.parent_main_window.current_campaign_id
        if not active_campaign_id:
            QMessageBox.critical(self, "Error", "No active campaign selected.")
            return

        campaign_data = self.parent_main_window.application_data.campaigns.get(active_campaign_id)
        if not campaign_data:
            QMessageBox.critical(self, "Error", "Could not find active campaign data.")
            return

        if self.npc_entry_to_edit:
            # Update existing NPC
            self.npc_entry_to_edit.name = name
            self.npc_entry_to_edit.stat_block_source = stat_block_source
            self.npc_entry_to_edit.mm_page = mm_page
            self.npc_entry_to_edit.stat_block_alterations = stat_block_alterations
            self.npc_entry_to_edit.alignment = alignment
            self.npc_entry_to_edit.personality = personality
            self.npc_entry_to_edit.appearance = appearance
            self.npc_entry_to_edit.secret = secret
            # The object is already in the application_data structure, so changes are direct
        else:
            # Create new NPC - NPCEntry now generates its own ID
            new_npc_entry = NPCEntry(
                name=name,
                stat_block_source=stat_block_source,
                mm_page=mm_page,
                stat_block_alterations=stat_block_alterations,
                alignment=alignment,
                personality=personality,
                appearance=appearance,
                secret=secret
            )
            # The default_factory for entry_id in NPCEntry will handle ID generation.
            campaign_data.npcs[new_npc_entry.entry_id] = new_npc_entry
            self.npc_entry_to_edit = new_npc_entry # Store it in case get_npc_data is called

        self.parent_main_window._save_app_data()
        super().accept() # Close the dialog

    # Optional: if the calling code needs to get the data
    # For this task, saving is done within the dialog.
    def get_npc_data(self) -> Optional[NPCEntry]:
        if self.result() == QDialog.DialogCode.Accepted:
            return self.npc_entry_to_edit
        return None

if __name__ == '__main__': # Basic test for the dialog
    from PySide6.QtWidgets import QApplication
    from src.data_models import ApplicationData, Campaign # For testing

    # Mock parent_main_window and its attributes for testing
    class MockMainWindow:
        def __init__(self):
            self.current_campaign_id = "test_campaign"
            self.application_data = ApplicationData()
            self.application_data.campaigns["test_campaign"] = Campaign(campaign_id="test_campaign", name="Test Campaign")

        def _save_app_data(self):
            print("Mock save_app_data called")

    app = QApplication([])
    mock_parent = MockMainWindow()

    # Test adding a new NPC
    dialog_add = NPCEntryDialog(mock_parent)
    if dialog_add.exec() == QDialog.DialogCode.Accepted:
        print("Add dialog accepted. NPC data:", dialog_add.get_npc_data())
        # Verify it's in the mock data
        if dialog_add.get_npc_data():
             npc_id = dialog_add.get_npc_data().entry_id
             print(f"NPC in mock campaign data: {mock_parent.application_data.campaigns['test_campaign'].npcs.get(npc_id)}")


    # Test editing an existing NPC (first add one)
    existing_npc = NPCEntry(name="Old NPC", stat_block_source="Monster Manual")
    mock_parent.application_data.campaigns["test_campaign"].npcs[existing_npc.entry_id] = existing_npc

    dialog_edit = NPCEntryDialog(mock_parent, npc_entry=existing_npc)
    if dialog_edit.exec() == QDialog.DialogCode.Accepted:
        print("Edit dialog accepted. Updated NPC data:", dialog_edit.get_npc_data())
        print(f"Updated NPC in mock campaign data: {mock_parent.application_data.campaigns['test_campaign'].npcs.get(existing_npc.entry_id)}")

    # Clean up (not strictly necessary for mock)
    del app
