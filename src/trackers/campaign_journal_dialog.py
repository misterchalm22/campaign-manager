from typing import Optional
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QDialogButtonBox, QSpinBox, QDateEdit,
    QSizeGrip, QHBoxLayout, QToolButton, QWidget, QLabel
)
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QTextListFormat
from PySide6.QtCore import QDate, Qt
from src.data_models import CampaignJournalEntry

class CampaignJournalEntryDialog(QDialog):
    def __init__(self, parent_window, journal_entry: Optional[CampaignJournalEntry] = None):
        super().__init__(parent_window)

        self.parent_main_window = parent_window
        self.journal_entry_to_edit = journal_entry

        if self.journal_entry_to_edit:
            self.setWindowTitle("Edit Journal Entry")
        else:
            self.setWindowTitle("Add New Journal Entry")

        self.setModal(True)
        self.setMinimumWidth(400) # Adjusted minimum width

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.session_number_edit = QSpinBox()
        self.session_number_edit.setMinimum(1)
        self.session_number_edit.setMaximum(999)

        self.session_date_edit = QDateEdit(QDate.currentDate())
        self.session_date_edit.setCalendarPopup(True)
        self.session_date_edit.setDisplayFormat("yyyy-MM-dd")

        self.session_title_edit = QLineEdit()

        self.earlier_events_edit = QTextEdit()
        self.earlier_events_toolbar = self._create_rich_text_toolbar(self.earlier_events_edit)
        earlier_events_layout = QVBoxLayout()
        earlier_events_layout.setSpacing(2) # Minimal spacing between toolbar and text edit
        earlier_events_layout.addWidget(self.earlier_events_toolbar)
        earlier_events_layout.addWidget(self.earlier_events_edit)
        earlier_events_widget = QWidget()
        earlier_events_widget.setLayout(earlier_events_layout)

        self.planned_summary_edit = QTextEdit()
        self.planned_summary_toolbar = self._create_rich_text_toolbar(self.planned_summary_edit)
        planned_summary_layout = QVBoxLayout()
        planned_summary_layout.setSpacing(2)
        planned_summary_layout.addWidget(self.planned_summary_toolbar)
        planned_summary_layout.addWidget(self.planned_summary_edit)
        planned_summary_widget = QWidget()
        planned_summary_widget.setLayout(planned_summary_layout)

        self.additional_notes_edit = QTextEdit()
        self.additional_notes_toolbar = self._create_rich_text_toolbar(self.additional_notes_edit)
        additional_notes_layout = QVBoxLayout()
        additional_notes_layout.setSpacing(2)
        additional_notes_layout.addWidget(self.additional_notes_toolbar)
        additional_notes_layout.addWidget(self.additional_notes_edit)
        additional_notes_widget = QWidget()
        additional_notes_widget.setLayout(additional_notes_layout)

        form_layout.addRow("Session Number*:", self.session_number_edit)
        form_layout.addRow("Session Date:", self.session_date_edit)
        form_layout.addRow("Session Title*:", self.session_title_edit)
        form_layout.addRow(QLabel("Important Earlier Events:"), earlier_events_widget)
        form_layout.addRow(QLabel("Planned Summary for Session:"), planned_summary_widget)
        form_layout.addRow(QLabel("Additional Notes/Outcome:"), additional_notes_widget)

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

        if self.journal_entry_to_edit:
            self._load_journal_entry_data()
        elif self.parent_main_window.current_campaign_id: # Auto-increment session number for new entries
            campaign = self.parent_main_window.application_data.campaigns.get(self.parent_main_window.current_campaign_id)
            if campaign and campaign.campaign_journal:
                max_session_num = 0
                for entry in campaign.campaign_journal.values():
                    if entry.session_number > max_session_num:
                        max_session_num = entry.session_number
                self.session_number_edit.setValue(max_session_num + 1)

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

    def _load_journal_entry_data(self):
        if self.journal_entry_to_edit:
            self.session_number_edit.setValue(self.journal_entry_to_edit.session_number)
            if self.journal_entry_to_edit.session_date:
                self.session_date_edit.setDate(QDate.fromString(self.journal_entry_to_edit.session_date, "yyyy-MM-dd"))
            else:
                self.session_date_edit.setDate(QDate.currentDate())
            self.session_title_edit.setText(self.journal_entry_to_edit.session_title)
            self.earlier_events_edit.setHtml(self.journal_entry_to_edit.earlier_events)
            self.planned_summary_edit.setHtml(self.journal_entry_to_edit.planned_summary)
            self.additional_notes_edit.setHtml(self.journal_entry_to_edit.additional_notes)

    def _on_save(self):
        session_number = self.session_number_edit.value()
        session_date_str = self.session_date_edit.date().toString("yyyy-MM-dd")
        session_title = self.session_title_edit.text().strip()

        if not session_title:
            QMessageBox.warning(self, "Validation Error", "Session Title cannot be empty.")
            return

        # It's good practice to ensure session numbers are unique for a campaign if desired,
        # but the prompt doesn't explicitly ask for this validation. For now, we assume it's okay or handled by user.

        earlier_events = self.earlier_events_edit.toHtml().strip()
        planned_summary = self.planned_summary_edit.toHtml().strip()
        additional_notes = self.additional_notes_edit.toHtml().strip()

        active_campaign_id = self.parent_main_window.current_campaign_id
        if not active_campaign_id:
            QMessageBox.critical(self, "Error", "No active campaign selected.")
            return

        campaign_data = self.parent_main_window.application_data.campaigns.get(active_campaign_id)
        if not campaign_data:
            QMessageBox.critical(self, "Error", "Could not find active campaign data.")
            return

        if self.journal_entry_to_edit:
            self.journal_entry_to_edit.session_number = session_number
            self.journal_entry_to_edit.session_date = session_date_str
            self.journal_entry_to_edit.session_title = session_title
            self.journal_entry_to_edit.earlier_events = earlier_events
            self.journal_entry_to_edit.planned_summary = planned_summary
            self.journal_entry_to_edit.additional_notes = additional_notes
        else:
            new_journal_entry = CampaignJournalEntry(
                session_number=session_number,
                session_date=session_date_str,
                session_title=session_title,
                earlier_events=earlier_events,
                planned_summary=planned_summary,
                additional_notes=additional_notes
            )
            # ID is auto-generated by CampaignJournalEntry dataclass
            campaign_data.campaign_journal[new_journal_entry.entry_id] = new_journal_entry
            self.journal_entry_to_edit = new_journal_entry # Store for get_journal_entry_data

        self.parent_main_window._save_app_data()
        super().accept()

    def get_journal_entry_data(self) -> Optional[CampaignJournalEntry]:
        if self.result() == QDialog.DialogCode.Accepted:
            return self.journal_entry_to_edit
        return None

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    from src.data_models import ApplicationData, Campaign # For mock

    class MockMainWindow:
        def __init__(self):
            self.current_campaign_id = "test_campaign_journal"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id="test_campaign_journal", name="Journal Test Campaign")
            # Add a sample journal entry to test auto-increment
            sample_entry = CampaignJournalEntry(session_number=1, session_title="First Session")
            campaign.campaign_journal[sample_entry.entry_id] = sample_entry
            self.sample_entry_id = sample_entry.entry_id
            self.application_data.campaigns[self.current_campaign_id] = campaign

        def _save_app_data(self):
            print(f"Mock save_app_data called for campaign: {self.current_campaign_id}")

    app = QApplication([])
    mock_parent = MockMainWindow()

    dialog_add = CampaignJournalEntryDialog(mock_parent)
    print(f"Dialog add, initial session number: {dialog_add.session_number_edit.value()}") # Should be 2
    if dialog_add.exec() == QDialog.DialogCode.Accepted:
        print("Add Journal dialog accepted. Data:", dialog_add.get_journal_entry_data())
        if dialog_add.get_journal_entry_data():
            entry_id = dialog_add.get_journal_entry_data().entry_id
            print(f"Entry in mock data: {mock_parent.application_data.campaigns[mock_parent.current_campaign_id].campaign_journal.get(entry_id)}")
    existing_entry = mock_parent.application_data.campaigns[mock_parent.current_campaign_id].campaign_journal.get(mock_parent.sample_entry_id)
    if existing_entry:
        dialog_edit = CampaignJournalEntryDialog(mock_parent, journal_entry=existing_entry)
        if dialog_edit.exec() == QDialog.DialogCode.Accepted:
            print("Edit Journal dialog accepted. Data:", dialog_edit.get_journal_entry_data())
            print(f"Updated entry in mock data: {mock_parent.application_data.campaigns[mock_parent.current_campaign_id].campaign_journal.get(existing_entry.entry_id)}")
            print(f"Updated entry in mock data: {mock_parent.application_data.campaigns[mock_parent.current_campaign_id].campaign_journal.get(existing_entry.entry_id)}")

    del app
