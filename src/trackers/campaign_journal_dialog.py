from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QDialogButtonBox, QSpinBox, QDateEdit
)
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
        self.setMinimumWidth(450)

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
        self.planned_summary_edit = QTextEdit()
        self.additional_notes_edit = QTextEdit()

        form_layout.addRow("Session Number*:", self.session_number_edit)
        form_layout.addRow("Session Date:", self.session_date_edit)
        form_layout.addRow("Session Title*:", self.session_title_edit)
        form_layout.addRow("Important Earlier Events:", self.earlier_events_edit)
        form_layout.addRow("Planned Summary for Session:", self.planned_summary_edit)
        form_layout.addRow("Additional Notes/Outcome:", self.additional_notes_edit)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_save)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

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

    existing_entry = mock_parent.application_data.campaigns[mock_parent.current_campaign_id].campaign_journal.get(sample_entry.entry_id)
    if existing_entry:
        dialog_edit = CampaignJournalEntryDialog(mock_parent, journal_entry=existing_entry)
        if dialog_edit.exec() == QDialog.DialogCode.Accepted:
            print("Edit Journal dialog accepted. Data:", dialog_edit.get_journal_entry_data())
            print(f"Updated entry in mock data: {mock_parent.application_data.campaigns[mock_parent.current_campaign_id].campaign_journal.get(existing_entry.entry_id)}")

    del app
