import uuid
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QHBoxLayout, QMessageBox, QDialogButtonBox
)

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
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.stat_block_source_edit = QLineEdit()
        self.mm_page_edit = QLineEdit()
        self.stat_block_alterations_edit = QTextEdit()
        self.alignment_edit = QLineEdit()
        self.personality_edit = QTextEdit()
        self.appearance_edit = QTextEdit()
        self.secret_edit = QTextEdit()

        form_layout.addRow("Name*:", self.name_edit)
        form_layout.addRow("Stat Block Source:", self.stat_block_source_edit)
        form_layout.addRow("MM Page:", self.mm_page_edit)
        form_layout.addRow("Stat Block Alterations:", self.stat_block_alterations_edit)
        form_layout.addRow("Alignment:", self.alignment_edit)
        form_layout.addRow("Personality:", self.personality_edit)
        form_layout.addRow("Appearance:", self.appearance_edit)
        form_layout.addRow("Secret:", self.secret_edit)

        layout.addLayout(form_layout)

        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_save)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        if self.npc_entry_to_edit:
            self._load_npc_data()

    def _load_npc_data(self):
        if self.npc_entry_to_edit:
            self.name_edit.setText(self.npc_entry_to_edit.name)
            self.stat_block_source_edit.setText(self.npc_entry_to_edit.stat_block_source)
            self.mm_page_edit.setText(self.npc_entry_to_edit.mm_page)
            self.stat_block_alterations_edit.setPlainText(self.npc_entry_to_edit.stat_block_alterations)
            self.alignment_edit.setText(self.npc_entry_to_edit.alignment)
            self.personality_edit.setPlainText(self.npc_entry_to_edit.personality)
            self.appearance_edit.setPlainText(self.npc_entry_to_edit.appearance)
            self.secret_edit.setPlainText(self.npc_entry_to_edit.secret)

    def _on_save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "NPC Name cannot be empty.")
            return

        stat_block_source = self.stat_block_source_edit.text().strip()
        mm_page = self.mm_page_edit.text().strip()
        stat_block_alterations = self.stat_block_alterations_edit.toPlainText().strip()
        alignment = self.alignment_edit.text().strip()
        personality = self.personality_edit.toPlainText().strip()
        appearance = self.appearance_edit.toPlainText().strip()
        secret = self.secret_edit.toPlainText().strip()

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
