from typing import Optional, List, cast
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QDialogButtonBox, QSpinBox, QGroupBox,
    QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Slot
from src.data_models import BastionEntry, BastionFacility # Use existing models

class SpecialFacilityDialog(QDialog):
    def __init__(self, parent, facility_data: Optional[BastionFacility] = None):
        super().__init__(parent)
        self.facility_to_edit = facility_data

        if self.facility_to_edit:
            self.setWindowTitle("Edit Special Facility")
        else:
            self.setWindowTitle("Add New Special Facility")

        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_edit = QLineEdit() # facility_type_name
        self.space_edit = QLineEdit()
        self.order_edit = QLineEdit() # order_association
        self.hirelings_edit = QTextEdit()
        self.notes_edit = QTextEdit()

        form_layout.addRow("Facility Type/Name*:", self.name_edit)
        form_layout.addRow("Space Requirement:", self.space_edit)
        form_layout.addRow("Order Association:", self.order_edit)
        form_layout.addRow("Hirelings:", self.hirelings_edit)
        form_layout.addRow("Notes:", self.notes_edit)
        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self._on_save)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        if self.facility_to_edit:
            self._load_facility_data()

    def _load_facility_data(self):
        if self.facility_to_edit:
            self.name_edit.setText(self.facility_to_edit.facility_type_name)
            self.space_edit.setText(self.facility_to_edit.space)
            self.order_edit.setText(self.facility_to_edit.order_association)
            self.hirelings_edit.setHtml(self.facility_to_edit.hirelings)
            self.notes_edit.setHtml(self.facility_to_edit.notes)

    def _on_save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Facility Type/Name cannot be empty.")
            return
        self.accept()

    def get_data(self) -> Optional[BastionFacility]:
        if self.result() == QDialog.DialogCode.Accepted:
            name = self.name_edit.text().strip()
            space = self.space_edit.text().strip()
            order = self.order_edit.text().strip()
            hirelings = self.hirelings_edit.toHtml().strip()
            notes = self.notes_edit.toHtml().strip()

            if self.facility_to_edit:
                self.facility_to_edit.facility_type_name = name
                self.facility_to_edit.space = space
                self.facility_to_edit.order_association = order
                self.facility_to_edit.hirelings = hirelings
                self.facility_to_edit.notes = notes
                return self.facility_to_edit
            else:
                return BastionFacility(
                    facility_type_name=name,
                    space=space,
                    order_association=order,
                    hirelings=hirelings,
                    notes=notes
                )
        return None


class BastionEntryDialog(QDialog):
    def __init__(self, parent, bastion_entry: Optional[BastionEntry] = None):
        super().__init__(parent)
        self.parent_main_window = parent.main_window # Access main_window through parent widget
        self.bastion_to_edit = bastion_entry

        # Work with a copy of facilities list, commit only on save
        if self.bastion_to_edit:
            self.current_facilities: List[BastionFacility] = [
                facility for facility in self.bastion_to_edit.special_facilities
            ]
        else:
            self.current_facilities: List[BastionFacility] = []

        if self.bastion_to_edit:
            self.setWindowTitle(f"Edit Bastion: {self.bastion_to_edit.bastion_name}")
        else:
            self.setWindowTitle("Add New Bastion")

        self.setModal(True)
        self.setMinimumWidth(550)

        main_layout = QVBoxLayout(self)

        # Bastion Info
        bastion_info_group = QGroupBox("Bastion Information")
        bastion_info_form = QFormLayout(bastion_info_group)
        self.bastion_name_edit = QLineEdit()
        self.character_name_edit = QLineEdit()
        self.level_spinbox = QSpinBox()
        self.level_spinbox.setMinimum(0)
        self.level_spinbox.setMaximum(20) # Or higher if needed
        bastion_info_form.addRow("Bastion Name*:", self.bastion_name_edit)
        bastion_info_form.addRow("Character's Name:", self.character_name_edit)
        bastion_info_form.addRow("Character Level (at acquisition):", self.level_spinbox)
        main_layout.addWidget(bastion_info_group)

        # Special Facilities
        facilities_group = QGroupBox("Special Facilities")
        facilities_layout = QVBoxLayout(facilities_group)
        self.facilities_list_widget = QListWidget()
        self.facilities_list_widget.setAlternatingRowColors(True)

        facilities_buttons_layout = QHBoxLayout()
        self.add_facility_btn = QPushButton("Add Facility")
        self.edit_facility_btn = QPushButton("Edit Selected")
        self.remove_facility_btn = QPushButton("Remove Selected")
        facilities_buttons_layout.addWidget(self.add_facility_btn)
        facilities_buttons_layout.addWidget(self.edit_facility_btn)
        facilities_buttons_layout.addWidget(self.remove_facility_btn)
        facilities_buttons_layout.addStretch()

        facilities_layout.addLayout(facilities_buttons_layout)
        facilities_layout.addWidget(self.facilities_list_widget)
        main_layout.addWidget(facilities_group)

        # General Details
        general_details_group = QGroupBox("General Bastion Details")
        general_details_form = QFormLayout(general_details_group)
        self.basic_facilities_edit = QTextEdit() # basic_facilities_desc
        self.bastion_defenders_edit = QTextEdit() # bastion_defenders_desc
        general_details_form.addRow("Basic Facilities Description:", self.basic_facilities_edit)
        general_details_form.addRow("Bastion Defenders Description:", self.bastion_defenders_edit)
        main_layout.addWidget(general_details_group)

        # Dialog Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        main_layout.addWidget(self.button_box)

        # Connect signals
        self.add_facility_btn.clicked.connect(self._on_add_facility)
        self.edit_facility_btn.clicked.connect(self._on_edit_facility)
        self.facilities_list_widget.itemDoubleClicked.connect(self._on_edit_facility) # Edit on double click
        self.remove_facility_btn.clicked.connect(self._on_remove_facility)

        self.button_box.accepted.connect(self._on_save)
        self.button_box.rejected.connect(self.reject)

        if self.bastion_to_edit:
            self._load_bastion_data()
        self._refresh_facilities_list()


    def _load_bastion_data(self):
        if self.bastion_to_edit:
            self.bastion_name_edit.setText(self.bastion_to_edit.bastion_name)
            self.character_name_edit.setText(self.bastion_to_edit.character_name)
            self.level_spinbox.setValue(self.bastion_to_edit.level)
            self.basic_facilities_edit.setHtml(self.bastion_to_edit.basic_facilities_desc)
            self.bastion_defenders_edit.setHtml(self.bastion_to_edit.bastion_defenders_desc)
            # self.current_facilities is loaded in __init__
            self._refresh_facilities_list()

    def _refresh_facilities_list(self):
        self.facilities_list_widget.clear()
        for facility in self.current_facilities:
            item = QListWidgetItem(facility.facility_type_name)
            # Store the actual facility object (or its ID) with the item
            item.setData(Qt.ItemDataRole.UserRole, facility.facility_id)
            self.facilities_list_widget.addItem(item)

    @Slot()
    def _on_add_facility(self):
        dialog = SpecialFacilityDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_facility_data = dialog.get_data()
            if new_facility_data: # It's a BastionFacility object with a new ID
                self.current_facilities.append(new_facility_data)
                self._refresh_facilities_list()

    @Slot()
    def _on_edit_facility(self):
        selected_item = self.facilities_list_widget.currentItem()
        if not selected_item:
            QMessageBox.information(self, "Selection Error", "Please select a facility to edit.")
            return

        facility_id_to_edit = selected_item.data(Qt.ItemDataRole.UserRole)
        facility_to_edit = next((f for f in self.current_facilities if f.facility_id == facility_id_to_edit), None)

        if not facility_to_edit:
            QMessageBox.critical(self, "Error", "Facility not found in current list.")
            return

        dialog = SpecialFacilityDialog(self, facility_data=facility_to_edit)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Data is updated in-place by SpecialFacilityDialog's get_data()
            self._refresh_facilities_list()

    @Slot()
    def _on_remove_facility(self):
        selected_item = self.facilities_list_widget.currentItem()
        if not selected_item:
            QMessageBox.information(self, "Selection Error", "Please select a facility to remove.")
            return

        facility_id_to_remove = selected_item.data(Qt.ItemDataRole.UserRole)
        facility_name = selected_item.text()

        reply = QMessageBox.question(self, "Remove Facility",
                                     f"Are you sure you want to remove facility: '{facility_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.current_facilities = [f for f in self.current_facilities if f.facility_id != facility_id_to_remove]
            self._refresh_facilities_list()

    def _on_save(self):
        bastion_name = self.bastion_name_edit.text().strip()
        if not bastion_name:
            QMessageBox.warning(self, "Validation Error", "Bastion Name cannot be empty.")
            return
        self.accept()

    def get_data(self) -> Optional[BastionEntry]:
        if self.result() == QDialog.DialogCode.Accepted:
            bastion_name = self.bastion_name_edit.text().strip()
            character_name = self.character_name_edit.text().strip()
            level = self.level_spinbox.value()
            basic_facilities = self.basic_facilities_edit.toHtml().strip()
            bastion_defenders = self.bastion_defenders_edit.toHtml().strip()

            if self.bastion_to_edit:
                self.bastion_to_edit.bastion_name = bastion_name
                self.bastion_to_edit.character_name = character_name
                self.bastion_to_edit.level = level
                self.bastion_to_edit.special_facilities = self.current_facilities # Commit the list
                self.bastion_to_edit.basic_facilities_desc = basic_facilities
                self.bastion_to_edit.bastion_defenders_desc = bastion_defenders
                return self.bastion_to_edit
            else:
                return BastionEntry(
                    bastion_name=bastion_name,
                    character_name=character_name,
                    level=level,
                    special_facilities=self.current_facilities, # Commit the list
                    basic_facilities_desc=basic_facilities,
                    bastion_defenders_desc=bastion_defenders
                    # entry_id will be auto-generated by BastionEntry dataclass
                )
        return None

if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    # Mock main_window for dialog testing context
    class MockParentWidget(QWidget):
        def __init__(self):
            super().__init__()
            # Mimic main_window structure if dialogs need it (not directly for these dialogs)
            # For BastionEntryDialog, parent is BastionTrackerWidget, which has main_window
            # So, if testing BastionEntryDialog directly, its parent needs a main_window attribute.
            class MockMainWindow:
                pass
            self.main_window = MockMainWindow()


    app = QApplication([])

    # Test SpecialFacilityDialog
    mock_parent = MockParentWidget()
    facility_dialog_add = SpecialFacilityDialog(mock_parent)
    if facility_dialog_add.exec() == QDialog.DialogCode.Accepted:
        new_fac_data = facility_dialog_add.get_data()
        print("New Facility Data:", new_fac_data)
        if new_fac_data: print(f"Facility ID: {new_fac_data.facility_id}")

    existing_facility = BastionFacility(facility_type_name="Old Library", space="1 room")
    facility_dialog_edit = SpecialFacilityDialog(mock_parent, facility_data=existing_facility)
    if facility_dialog_edit.exec() == QDialog.DialogCode.Accepted:
        edited_fac_data = facility_dialog_edit.get_data()
        print("Edited Facility Data:", edited_fac_data)
        assert edited_fac_data is existing_facility

    # Test BastionEntryDialog
    bastion_dialog_add = BastionEntryDialog(mock_parent) # Pass mock_parent as parent
    if bastion_dialog_add.exec() == QDialog.DialogCode.Accepted:
        new_bast_data = bastion_dialog_add.get_data()
        print("New Bastion Data:", new_bast_data)
        if new_bast_data:
            print(f"Bastion ID: {new_bast_data.entry_id}")
            for fac in new_bast_data.special_facilities:
                print(f"  Facility in new bastion: {fac.facility_type_name}, ID: {fac.facility_id}")


    existing_bastion = BastionEntry(bastion_name="Old Keep", character_name="Sir Knight", level=5)
    existing_bastion.special_facilities.append(BastionFacility(facility_type_name="Forge"))
    bastion_dialog_edit = BastionEntryDialog(mock_parent, bastion_entry=existing_bastion)
    if bastion_dialog_edit.exec() == QDialog.DialogCode.Accepted:
        edited_bast_data = bastion_dialog_edit.get_data()
        print("Edited Bastion Data:", edited_bast_data)
        if edited_bast_data:
            print(f"Bastion ID: {edited_bast_data.entry_id}")
            for fac in edited_bast_data.special_facilities:
                print(f"  Facility in edited bastion: {fac.facility_type_name}, ID: {fac.facility_id}")
        assert edited_bast_data is existing_bastion

    del app
