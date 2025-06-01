from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QDialogButtonBox, QComboBox, QSpinBox
)
from PySide6.QtCore import Qt
from src.data_models import TravelStage # Assuming TravelStage dataclass is defined

PACE_OPTIONS = ["Fast", "Normal", "Slow"]
TIME_UNIT_OPTIONS = ["days", "hrs"]

class TravelStageDialog(QDialog):
    def __init__(self, parent_dialog, stage_data: Optional[TravelStage] = None):
        super().__init__(parent_dialog) # Parent is the TravelPlanEntryDialog

        self.stage_data_to_edit = stage_data # Store the original stage data if editing

        if self.stage_data_to_edit:
            self.setWindowTitle("Edit Travel Stage")
        else:
            self.setWindowTitle("Add New Travel Stage")

        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.stage_number_id_edit = QLineEdit()
        self.start_location_edit = QLineEdit()
        self.end_location_edit = QLineEdit()
        self.distance_edit = QLineEdit()
        self.terrain_edit = QLineEdit()
        self.weather_edit = QLineEdit()

        self.pace_combo = QComboBox()
        self.pace_combo.addItems(PACE_OPTIONS)

        self.travel_time_value_spinbox = QSpinBox()
        self.travel_time_value_spinbox.setMinimum(0)
        self.travel_time_value_spinbox.setMaximum(9999) # Arbitrary max

        self.travel_time_unit_combo = QComboBox()
        self.travel_time_unit_combo.addItems(TIME_UNIT_OPTIONS)

        self.narrative_notes_edit = QTextEdit()
        self.challenges_edit = QTextEdit()
        self.elapsed_time_total_edit = QLineEdit() # e.g., "3 days", "28 hrs"

        form_layout.addRow("Stage Identifier (e.g., Stage 1):", self.stage_number_id_edit)
        form_layout.addRow("Start Location*:", self.start_location_edit)
        form_layout.addRow("End Location*:", self.end_location_edit)
        form_layout.addRow("Distance:", self.distance_edit)
        form_layout.addRow("Terrain:", self.terrain_edit)
        form_layout.addRow("Weather:", self.weather_edit)
        form_layout.addRow("Pace:", self.pace_combo)
        form_layout.addRow("Travel Time Value:", self.travel_time_value_spinbox)
        form_layout.addRow("Travel Time Unit:", self.travel_time_unit_combo)
        form_layout.addRow("Narrative Notes:", self.narrative_notes_edit)
        form_layout.addRow("Challenges:", self.challenges_edit)
        form_layout.addRow("Total Elapsed Time (Journey):", self.elapsed_time_total_edit)

        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept) # Use QDialog's accept
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        if self.stage_data_to_edit:
            self._load_stage_data()

    def _load_stage_data(self):
        if self.stage_data_to_edit:
            self.stage_number_id_edit.setText(self.stage_data_to_edit.stage_number_id)
            self.start_location_edit.setText(self.stage_data_to_edit.start_location)
            self.end_location_edit.setText(self.stage_data_to_edit.end_location)
            self.distance_edit.setText(self.stage_data_to_edit.distance)
            self.terrain_edit.setText(self.stage_data_to_edit.terrain)
            self.weather_edit.setText(self.stage_data_to_edit.weather)
            self.pace_combo.setCurrentText(self.stage_data_to_edit.pace)
            self.travel_time_value_spinbox.setValue(self.stage_data_to_edit.travel_time_value)
            self.travel_time_unit_combo.setCurrentText(self.stage_data_to_edit.travel_time_unit)
            self.narrative_notes_edit.setPlainText(self.stage_data_to_edit.narrative_notes)
            self.challenges_edit.setPlainText(self.stage_data_to_edit.challenges)
            self.elapsed_time_total_edit.setText(self.stage_data_to_edit.elapsed_time_total)

    def get_data(self) -> Optional[TravelStage]:
        if self.result() == QDialog.DialogCode.Accepted:
            # Basic validation
            if not self.start_location_edit.text().strip() or not self.end_location_edit.text().strip():
                # In a real app, show QMessageBox here, but for now, let parent dialog handle if needed.
                # For simplicity, this dialog doesn't show its own error message on get_data failure.
                # Parent dialog should validate before proceeding.
                return None

            stage_id_val = self.stage_data_to_edit.stage_id if self.stage_data_to_edit else None # Keep existing ID or let dataclass generate

            # If stage_data_to_edit is None, a new TravelStage is created with a new ID by default_factory.
            # If stage_data_to_edit is provided, we are updating it.
            # The ID should remain the same for an existing stage.

            return TravelStage(
                stage_id=stage_id_val if stage_id_val else TravelStage().stage_id, # Ensure ID is generated if new, or kept if existing
                stage_number_id=self.stage_number_id_edit.text().strip(),
                start_location=self.start_location_edit.text().strip(),
                end_location=self.end_location_edit.text().strip(),
                distance=self.distance_edit.text().strip(),
                terrain=self.terrain_edit.text().strip(),
                weather=self.weather_edit.text().strip(),
                pace=self.pace_combo.currentText(),
                travel_time_value=self.travel_time_value_spinbox.value(),
                travel_time_unit=self.travel_time_unit_combo.currentText(),
                narrative_notes=self.narrative_notes_edit.toPlainText().strip(),
                challenges=self.challenges_edit.toPlainText().strip(),
                elapsed_time_total=self.elapsed_time_total_edit.text().strip()
            )
        return None

if __name__ == '__main__': # Basic test
    from PySide6.QtWidgets import QApplication, QPushButton

    app = QApplication([])

    # Test adding a new stage
    parent_dummy_dialog = QDialog() # Dummy parent for testing
    add_dialog = TravelStageDialog(parent_dummy_dialog)
    if add_dialog.exec() == QDialog.DialogCode.Accepted:
        new_data = add_dialog.get_data()
        print("New stage data (if valid):", new_data)
        if new_data:
             print(f"  Stage ID: {new_data.stage_id}")


    # Test editing an existing stage
    existing_stage = TravelStage(
        stage_number_id="Leg 1",
        start_location="Old Town",
        end_location="Dark Woods",
        distance="3 days",
        pace="Normal"
    )
    print(f"Existing stage ID before edit: {existing_stage.stage_id}")
    edit_dialog = TravelStageDialog(parent_dummy_dialog, stage_data=existing_stage)
    if edit_dialog.exec() == QDialog.DialogCode.Accepted:
        updated_data = edit_dialog.get_data()
        print("Updated stage data (if valid):", updated_data)
        if updated_data:
            print(f"  Updated Stage ID: {updated_data.stage_id}") # Should be same as existing_stage.stage_id
            assert updated_data.stage_id == existing_stage.stage_id # Important check

    del app
