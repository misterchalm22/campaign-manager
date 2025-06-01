from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, Slot

from src.data_models import TravelPlanEntry # For type hinting
from src.trackers.travel_planner_dialog import TravelPlanEntryDialog

class TravelPlannerWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        action_bar_layout = QHBoxLayout()
        self.add_entry_btn = QPushButton("Add New Travel Plan")
        action_bar_layout.addWidget(self.add_entry_btn)
        action_bar_layout.addStretch()
        layout.addLayout(action_bar_layout)

        self.plans_table = QTableWidget()
        # Columns: Journey Name, Origin, Destination, # Stages, Actions
        self.plans_table.setColumnCount(5)
        self.plans_table.setHorizontalHeaderLabels(["Journey Name", "Origin", "Destination", "# Stages", "Actions"])
        self.plans_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # Journey Name
        self.plans_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) # Origin
        self.plans_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Destination
        self.plans_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive) # # Stages
        self.plans_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents) # Actions
        self.plans_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.plans_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.plans_table)

        self.placeholder_label = QLabel("No travel plans found. Click 'Add New Travel Plan' to create one.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setVisible(False)
        layout.addWidget(self.placeholder_label)
        self.plans_table.setVisible(True)

        self.add_entry_btn.clicked.connect(self._on_add_entry)

    def refresh_display(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            self.plans_table.setRowCount(0)
            self.show_placeholder(True, "No campaign selected.")
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign or not campaign.travel_plans:
            self.plans_table.setRowCount(0)
            self.show_placeholder(True, "No travel plans found. Click 'Add New Travel Plan' to create one.")
            return

        self.show_placeholder(False)
        entries_data = campaign.travel_plans
        sorted_entry_ids = list(entries_data.keys()) # Could sort by journey name if desired

        self.plans_table.setRowCount(len(sorted_entry_ids))

        for row, entry_id in enumerate(sorted_entry_ids):
            entry = entries_data[entry_id]

            self.plans_table.setItem(row, 0, QTableWidgetItem(entry.journey_name))
            self.plans_table.setItem(row, 1, QTableWidgetItem(entry.origin))
            self.plans_table.setItem(row, 2, QTableWidgetItem(entry.destination))

            num_stages_item = QTableWidgetItem(str(len(entry.stages)))
            num_stages_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.plans_table.setItem(row, 3, num_stages_item)


            edit_btn = QPushButton("Edit")
            delete_btn = QPushButton("Delete")

            edit_btn.clicked.connect(lambda checked=False, bound_id=entry_id: self._on_edit_entry(bound_id))
            delete_btn.clicked.connect(lambda checked=False, bound_id=entry_id: self._on_delete_entry(bound_id))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self.plans_table.setCellWidget(row, 4, actions_widget)

        self.plans_table.resizeRowsToContents()

    def show_placeholder(self, show: bool, text: Optional[str] = None):
        if show:
            if text:
                self.placeholder_label.setText(text)
            self.plans_table.setVisible(False)
            self.placeholder_label.setVisible(True)
        else:
            self.plans_table.setVisible(True)
            self.placeholder_label.setVisible(False)

    @Slot()
    def _on_add_entry(self):
        if not self.main_window.current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "Please select or create a campaign first.")
            return

        dialog = TravelPlanEntryDialog(self.main_window) # Pass main_window as parent
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_display()
            self.main_window.statusBar().showMessage("New travel plan added.", 3000)

    @Slot()
    def _on_edit_entry(self, entry_id: str):
        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign: return

        entry_to_edit = campaign.travel_plans.get(entry_id)
        if not entry_to_edit:
            QMessageBox.critical(self, "Error", f"Travel Plan with ID '{entry_id}' not found.")
            self.refresh_display()
            return

        dialog = TravelPlanEntryDialog(self.main_window, entry=entry_to_edit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"Travel Plan '{entry_to_edit.journey_name}' updated.", 3000)

    @Slot()
    def _on_delete_entry(self, entry_id: str):
        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign: return

        entry_to_delete = campaign.travel_plans.get(entry_id)
        if not entry_to_delete:
            QMessageBox.critical(self, "Error", f"Travel Plan ID '{entry_id}' not found for deletion.")
            self.refresh_display()
            return

        reply = QMessageBox.question(self, "Delete Travel Plan",
                                     f"Are you sure you want to delete travel plan: '{entry_to_delete.journey_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del campaign.travel_plans[entry_id]
            self.main_window._save_app_data()
            self.refresh_display()
            self.main_window.statusBar().showMessage(f"Travel Plan '{entry_to_delete.journey_name}' deleted.", 3000)

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    from src.data_models import ApplicationData, Campaign, TravelStage

    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "tp_test_camp"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="TP Test Campaign")

            ts1 = TravelStage(start_location="Town", end_location="Forest")
            tp1 = TravelPlanEntry(journey_name="To the Woods", origin="Town", destination="Deep Forest", stages=[ts1])
            tp2 = TravelPlanEntry(journey_name="Across the Mountains", origin="Valley", destination="Peak")
            campaign.travel_plans = {tp1.entry_id: tp1, tp2.entry_id: tp2}
            self.application_data.campaigns[self.current_campaign_id] = campaign
            self.setStatusBar(QStatusBar(self))

        def _save_app_data(self):
            print("MockMainWindow: _save_app_data called")

        def statusBar(self):
            return super().statusBar()

    app = QApplication(sys.argv)
    mock_main = MockMainWindow()
    tp_widget = TravelPlannerWidget(mock_main)

    mock_main.setCentralWidget(tp_widget)
    mock_main.setWindowTitle("Travel Planner Widget Test")
    mock_main.setGeometry(100, 100, 800, 500)

    tp_widget.refresh_display()
    mock_main.show()
    sys.exit(app.exec())
