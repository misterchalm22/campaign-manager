from typing import Optional, List, cast
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QDialogButtonBox, QSpinBox, QComboBox, QDateTimeEdit,
    QTableWidget, QHeaderView, QAbstractItemView, QMessageBox, QLabel, 
    QTableWidgetItem, QGroupBox, QHBoxLayout, QSizeGrip, QWidget  # Added QWidget
)
from PySide6.QtCore import Qt, Slot, QDateTime # Added QDateTime

from src.data_models import TravelPlanEntry, TravelStage
from src.trackers.travel_stage_dialog import TravelStageDialog # For managing individual stages

class TravelPlanEntryDialog(QDialog):
    def __init__(self, parent_window, entry: Optional[TravelPlanEntry] = None):
        super().__init__(parent_window)

        self.parent_main_window = parent_window
        self.entry_to_edit = entry

        # Work with a copy of stages list, commit only on save
        if self.entry_to_edit and self.entry_to_edit.stages:
            self.current_stages: List[TravelStage] = [s for s in self.entry_to_edit.stages]
        else:
            self.current_stages: List[TravelStage] = []

        if self.entry_to_edit:
            self.setWindowTitle("Edit Travel Plan")
        else:
            self.setWindowTitle("Add New Travel Plan")

        self.setModal(True)
        self.setMinimumWidth(550) # Adjusted minimum width

        main_layout = QVBoxLayout(self)

        # Main Plan Details
        details_groupbox = QGroupBox("Overall Journey Details")
        details_form_layout = QFormLayout(details_groupbox)
        self.journey_name_edit = QLineEdit()
        self.origin_edit = QLineEdit()
        self.destination_edit = QLineEdit()
        details_form_layout.addRow("Journey Name*:", self.journey_name_edit)
        details_form_layout.addRow("Overall Origin:", self.origin_edit)
        details_form_layout.addRow("Overall Destination:", self.destination_edit)
        main_layout.addWidget(details_groupbox)

        # Stages Sub-Section
        stages_groupbox = QGroupBox("Travel Stages")
        stages_main_layout = QVBoxLayout(stages_groupbox)

        self.stages_table = QTableWidget()
        self.stages_table.setColumnCount(4) # #, Start, End, Actions
        self.stages_table.setHorizontalHeaderLabels(["#", "Start", "End", "Actions"])
        self.stages_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive) # Stage #
        self.stages_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.stages_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.stages_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.stages_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.stages_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers) # Corrected Enum

        stage_buttons_layout = QHBoxLayout()
        self.add_stage_btn = QPushButton("Add Stage")
        self.edit_stage_btn = QPushButton("Edit Selected Stage")
        self.remove_stage_btn = QPushButton("Remove Selected Stage")
        stage_buttons_layout.addWidget(self.add_stage_btn)
        stage_buttons_layout.addWidget(self.edit_stage_btn)
        stage_buttons_layout.addWidget(self.remove_stage_btn)
        stage_buttons_layout.addStretch()

        stages_main_layout.addLayout(stage_buttons_layout)
        stages_main_layout.addWidget(self.stages_table)
        main_layout.addWidget(stages_groupbox)

        # Dialog Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        main_layout.addWidget(self.button_box)

        # Add QSizeGrip for resizing
        sizegrip_layout = QHBoxLayout()
        sizegrip_layout.addStretch(1)
        self.size_grip = QSizeGrip(self)
        sizegrip_layout.addWidget(self.size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        main_layout.addLayout(sizegrip_layout)

        # Connect signals
        self.add_stage_btn.clicked.connect(self._on_add_stage)
        self.edit_stage_btn.clicked.connect(self._on_edit_selected_stage) # Edit button for selected row
        self.remove_stage_btn.clicked.connect(self._on_remove_selected_stage) # Remove button for selected row
        self.stages_table.itemDoubleClicked.connect(self._on_edit_selected_stage_from_doubleclick)


        self.button_box.accepted.connect(self._on_save)
        self.button_box.rejected.connect(self.reject)

        if self.entry_to_edit:
            self._load_entry_data()

        self._refresh_stages_table()


    def _load_entry_data(self):
        if self.entry_to_edit:
            self.journey_name_edit.setText(self.entry_to_edit.journey_name)
            self.origin_edit.setText(self.entry_to_edit.origin)
            self.destination_edit.setText(self.entry_to_edit.destination)
            # self.current_stages is already loaded in __init__
            self._refresh_stages_table()

    def _refresh_stages_table(self):
        self.stages_table.setRowCount(0) # Clear table
        for idx, stage in enumerate(self.current_stages):
            row_position = self.stages_table.rowCount()
            self.stages_table.insertRow(row_position)

            # Use stage_number_id if present, otherwise use index+1 as fallback display
            stage_display_num = stage.stage_number_id if stage.stage_number_id else str(idx + 1)
            self.stages_table.setItem(row_position, 0, QTableWidgetItem(stage_display_num))
            self.stages_table.setItem(row_position, 1, QTableWidgetItem(stage.start_location))
            self.stages_table.setItem(row_position, 2, QTableWidgetItem(stage.end_location))

            # "View/Edit" and "Delete" buttons for table rows (more compact)
            view_edit_btn = QPushButton("View/Edit")
            # Store index in button property or use lambda with index
            view_edit_btn.clicked.connect(lambda checked=False, r=row_position: self._edit_stage_by_index(r))

            # No direct delete from table row to simplify, use "Remove Selected Stage" button
            # or implement _remove_stage_by_index if preferred.

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.addWidget(view_edit_btn)
            actions_layout.setContentsMargins(0,0,0,0)
            self.stages_table.setCellWidget(row_position, 3, actions_widget)
        self.stages_table.resizeRowsToContents()


    @Slot()
    def _on_add_stage(self):
        stage_dialog = TravelStageDialog(self) # Parent is this dialog
        if stage_dialog.exec() == QDialog.DialogCode.Accepted:
            new_stage_data = stage_dialog.get_data()
            if new_stage_data:
                # Basic validation for the stage
                if not new_stage_data.start_location or not new_stage_data.end_location:
                     QMessageBox.warning(self, "Stage Error", "Stage start and end locations cannot be empty.")
                     return # Keep the add stage dialog open or re-open it? For now, just fail add.
                self.current_stages.append(new_stage_data)
                self._refresh_stages_table()
            else:
                QMessageBox.warning(self, "Stage Error", "Failed to get valid stage data. Please ensure required fields are filled.")


    def _edit_stage_by_index(self, stage_idx: int):
        if 0 <= stage_idx < len(self.current_stages):
            stage_to_edit = self.current_stages[stage_idx]
            stage_dialog = TravelStageDialog(self, stage_data=stage_to_edit)
            if stage_dialog.exec() == QDialog.DialogCode.Accepted:
                updated_stage_data = stage_dialog.get_data()
                if updated_stage_data:
                    if not updated_stage_data.start_location or not updated_stage_data.end_location:
                        QMessageBox.warning(self, "Stage Error", "Stage start and end locations cannot be empty.")
                        return # Similarly, fail edit for now.
                    self.current_stages[stage_idx] = updated_stage_data
                    self._refresh_stages_table()
                else:
                    QMessageBox.warning(self, "Stage Error", "Failed to get valid updated stage data.")
        else:
            QMessageBox.warning(self, "Selection Error", "Invalid stage selected for editing.")


    @Slot()
    def _on_edit_selected_stage(self):
        selected_rows = self.stages_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Selection Error", "Please select a stage from the table to edit.")
            return
        self._edit_stage_by_index(selected_rows[0].row())

    @Slot(QTableWidgetItem)
    def _on_edit_selected_stage_from_doubleclick(self, item: QTableWidgetItem):
        if item:
            self._edit_stage_by_index(item.row())


    @Slot()
    def _on_remove_selected_stage(self):
        selected_rows = self.stages_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Selection Error", "Please select a stage from the table to remove.")
            return

        stage_idx_to_remove = selected_rows[0].row()
        stage_display_num = self.current_stages[stage_idx_to_remove].stage_number_id or str(stage_idx_to_remove + 1)

        reply = QMessageBox.question(self, "Remove Stage",
                                     f"Are you sure you want to remove stage '{stage_display_num}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del self.current_stages[stage_idx_to_remove]
            self._refresh_stages_table()

    def _on_save(self):
        journey_name = self.journey_name_edit.text().strip()
        if not journey_name:
            QMessageBox.warning(self, "Validation Error", "Journey Name cannot be empty.")
            return

        origin = self.origin_edit.text().strip()
        destination = self.destination_edit.text().strip()

        active_campaign_id = self.parent_main_window.current_campaign_id
        if not active_campaign_id:
            QMessageBox.critical(self, "Error", "No active campaign selected.")
            return

        campaign_data = self.parent_main_window.application_data.campaigns.get(active_campaign_id)
        if not campaign_data:
            QMessageBox.critical(self, "Error", "Could not find active campaign data.")
            return

        if self.entry_to_edit:
            self.entry_to_edit.journey_name = journey_name
            self.entry_to_edit.origin = origin
            self.entry_to_edit.destination = destination
            self.entry_to_edit.stages = self.current_stages # Commit the list of stages
        else:
            new_entry = TravelPlanEntry(
                journey_name=journey_name,
                origin=origin,
                destination=destination,
                stages=self.current_stages # Commit the list of stages
            )
            campaign_data.travel_plans[new_entry.entry_id] = new_entry
            self.entry_to_edit = new_entry # So get_entry_data can return it

        self.parent_main_window._save_app_data()
        super().accept()

    def get_entry_data(self) -> Optional[TravelPlanEntry]:
        if self.result() == QDialog.DialogCode.Accepted:
            return self.entry_to_edit
        return None

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    from src.data_models import ApplicationData, Campaign

    class MockMainWindow:
        def __init__(self):
            self.current_campaign_id = "test_tp_campaign"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="TP Test Campaign")
            self.application_data.campaigns[self.current_campaign_id] = campaign

        def _save_app_data(self): print(f"Mock save_app_data for {self.current_campaign_id}")

    app = QApplication([])
    mock_parent_win = MockMainWindow()

    # Test Add Travel Plan
    add_plan_dialog = TravelPlanEntryDialog(mock_parent_win)
    if add_plan_dialog.exec() == QDialog.DialogCode.Accepted:
        new_plan = add_plan_dialog.get_entry_data()
        print("Add Plan Dialog Accepted. Data:", new_plan)
        if new_plan:
            print("Stages:", new_plan.stages)
            entry_id = new_plan.entry_id
            print(f"Entry in mock data: {mock_parent_win.application_data.campaigns[mock_parent_win.current_campaign_id].travel_plans.get(entry_id)}")

    # Test Edit Travel Plan
    stage1 = TravelStage(stage_number_id="1", start_location="A", end_location="B")
    stage2 = TravelStage(stage_number_id="2", start_location="B", end_location="C")
    existing_plan = TravelPlanEntry(journey_name="Old Journey", stages=[stage1, stage2])
    mock_parent_win.application_data.campaigns[mock_parent_win.current_campaign_id].travel_plans[existing_plan.entry_id] = existing_plan

    edit_plan_dialog = TravelPlanEntryDialog(mock_parent_win, entry=existing_plan)
    if edit_plan_dialog.exec() == QDialog.DialogCode.Accepted:
        updated_plan = edit_plan_dialog.get_entry_data()
        print("Edit Plan Dialog Accepted. Data:", updated_plan)
        if updated_plan:
            print("Stages:", updated_plan.stages)
            print(f"Updated entry in mock data: {mock_parent_win.application_data.campaigns[mock_parent_win.current_campaign_id].travel_plans.get(existing_plan.entry_id)}")
            for i, s in enumerate(updated_plan.stages):
                print(f"  Stage {i} ID: {s.stage_id}")


    del app
