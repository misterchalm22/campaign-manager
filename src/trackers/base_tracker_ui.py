from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QAbstractItemView, QHeaderView, QMessageBox, QMenu, QDialog, QHBoxLayout, QLabel, QTableWidgetItem # Added QHBoxLayout, QLabel, QTableWidgetItem
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Slot
from PySide6.QtGui import QAction
from abc import ABC, ABCMeta, abstractmethod
from typing import List, Any, Optional, TypeVar, Generic

# Combine metaclasses to resolve conflict
class CombinedMeta(type(QWidget), ABCMeta):
    pass

class BaseTrackerWidget(QWidget, ABC, metaclass=CombinedMeta):
    def __init__(self, main_window, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.main_window = main_window # Instance of MainWindow
        self._entity_name = self._get_entity_name()
        self._entity_name_plural = self._get_entity_name_plural()

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Action buttons (optional, can be overridden)
        self._setup_action_bar()

        # Table for items
        self.table_widget = QTableWidget() # Changed from QTableView to QTableWidget
        self._configure_table_columns() # Call abstract method for column setup
        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_widget.doubleClicked.connect(self._on_edit_item_triggered) # Default double-click action
        self.main_layout.addWidget(self.table_widget)

        # Placeholder label
        self.placeholder_label = QLabel(f"No {self._entity_name_plural.lower()} defined. Click '{self._get_add_button_text()}' to create one.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setVisible(False)
        self.main_layout.addWidget(self.placeholder_label)
        self.table_widget.setVisible(True)

        # Initial state
        self.refresh_display()

    def _setup_action_bar(self):
        '''Sets up the default top action bar with Add, Edit, Delete buttons.'''
        self.action_bar_layout = QHBoxLayout()
        self.add_button = QPushButton(self._get_add_button_text())
        self.edit_button = QPushButton(self._get_edit_button_text())
        self.delete_button = QPushButton(self._get_delete_button_text())

        self.add_button.clicked.connect(self._on_add_item_triggered)
        self.edit_button.clicked.connect(self._on_edit_item_triggered)
        self.delete_button.clicked.connect(self._on_delete_item_triggered)

        self.action_bar_layout.addWidget(self.add_button)
        self.action_bar_layout.addWidget(self.edit_button)
        self.action_bar_layout.addWidget(self.delete_button)
        self.action_bar_layout.addStretch()
        self.main_layout.addLayout(self.action_bar_layout)

    def refresh_display(self):
        '''
        Main method to refresh the entire display.
        Handles campaign checks, data fetching, table population, and placeholder visibility.
        '''
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            self._handle_no_campaign()
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign:
            # This case should ideally not happen if current_campaign_id is set
            # but the campaign object is missing.
            self.show_placeholder(True, f"Error: Campaign data for ID '{current_campaign_id}' not found.")
            self._set_buttons_enabled(False)
            return

        item_data_list = self._get_item_data_for_display(campaign)

        if not item_data_list:
            self._handle_no_data()
            return

        self.show_placeholder(False)
        self.table_widget.setSortingEnabled(False) # Disable sorting during population
        self.table_widget.setRowCount(len(item_data_list))

        for row, item_data in enumerate(item_data_list):
            self._populate_table_row(row, item_data)

        self.table_widget.resizeRowsToContents()
        self.table_widget.setSortingEnabled(True) # Re-enable sorting
        self._set_buttons_enabled(True)


    def show_placeholder(self, show: bool, text: Optional[str] = None):
        '''Shows or hides the placeholder label.'''
        if show:
            if text:
                self.placeholder_label.setText(text)
            self.table_widget.setVisible(False)
            self.placeholder_label.setVisible(True)
        else:
            self.table_widget.setVisible(True)
            self.placeholder_label.setVisible(False)

    def _set_buttons_enabled(self, enabled: bool):
        '''Enables or disables action buttons. Assumes buttons exist.'''
        if hasattr(self, 'add_button'): # Check if buttons were created
            self.add_button.setEnabled(True) # Add button usually always enabled if campaign exists
        if hasattr(self, 'edit_button'):
            self.edit_button.setEnabled(enabled)
        if hasattr(self, 'delete_button'):
            self.delete_button.setEnabled(enabled)


    @Slot()
    def _on_add_item_triggered(self):
        if not self.main_window.current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "Please select or create a campaign first.")
            return

        dialog = self._get_dialog_for_add()
        if dialog is None: # Subclass might not support adding this way
            return

        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                new_item_data = dialog.get_data() # Dialogs should have a get_data() method
                if new_item_data:
                    # Get campaign object and pass to _perform_add_item
                    campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
                    self._perform_add_item(new_item_data, campaign)
                    self.main_window._save_app_data()
                    self.refresh_display()
                    self.main_window.statusBar().showMessage(f"New {self._entity_name.lower()} added.", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error Adding Item", f"Could not add {self._entity_name.lower()}: {e}")
                self.main_window.statusBar().showMessage(f"Failed to add {self._entity_name.lower()}.", 5000)


    @Slot()
    def _on_edit_item_triggered(self):
        if not self.main_window.current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "No campaign selected.")
            return

        item_id_to_edit = self._get_selected_item_id()
        if item_id_to_edit is None:
            QMessageBox.information(self, "No Selection", f"Please select a {self._entity_name.lower()} to edit.")
            return

        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign:
             QMessageBox.critical(self, "Error", "Campaign data not found.")
             return

        dialog = self._get_dialog_for_edit(item_id_to_edit, campaign)
        if dialog is None: # Subclass might not support editing or item not found
            return

        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                updated_item_data = dialog.get_data() # Dialog might update in place or return data
                self._perform_edit_item(item_id_to_edit, updated_item_data, campaign)
                self.main_window._save_app_data()
                self.refresh_display()
                item_name = self._get_item_name_for_confirmation(item_id_to_edit, campaign) or self._entity_name
                self.main_window.statusBar().showMessage(f"{item_name} updated.", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error Editing Item", f"Could not update {self._entity_name.lower()}: {e}")
                self.main_window.statusBar().showMessage(f"Failed to update {self._entity_name.lower()}.", 5000)

    @Slot()
    def _on_delete_item_triggered(self):
        if not self.main_window.current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "No campaign selected.")
            return

        item_id_to_delete = self._get_selected_item_id()
        if item_id_to_delete is None:
            QMessageBox.information(self, "No Selection", f"Please select a {self._entity_name.lower()} to delete.")
            return

        campaign = self.main_window.application_data.campaigns.get(self.main_window.current_campaign_id)
        if not campaign:
             QMessageBox.critical(self, "Error", "Campaign data not found.")
             return

        item_name = self._get_item_name_for_confirmation(item_id_to_delete, campaign) or f"the selected {self._entity_name.lower()}"

        reply = QMessageBox.question(self, f"Delete {self._entity_name}",
                                     f"Are you sure you want to delete {item_name}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                deleted = self._perform_delete_item(item_id_to_delete, campaign)
                if deleted:
                    self.main_window._save_app_data()
                    self.refresh_display()
                    self.main_window.statusBar().showMessage(f"{item_name} deleted.", 3000)
                else:
                    QMessageBox.warning(self, "Delete Error", f"{self._entity_name} not found for deletion or already removed.")
                    self.refresh_display()
            except Exception as e:
                QMessageBox.critical(self, "Error Deleting Item", f"Could not delete {self._entity_name.lower()}: {e}")
                self.main_window.statusBar().showMessage(f"Failed to delete {self._entity_name.lower()}.", 5000)

    # --- Abstract methods to be implemented by subclasses ---

    @abstractmethod
    def _get_entity_name(self) -> str:
        '''Return the singular name of the entity (e.g., "Bastion").'''
        pass

    @abstractmethod
    def _get_entity_name_plural(self) -> str:
        '''Return the plural name of the entity (e.g., "Bastions").'''
        pass

    def _get_add_button_text(self) -> str:
        '''Return text for the add button.'''
        return f"Add {self._get_entity_name()}"

    def _get_edit_button_text(self) -> str:
        '''Return text for the edit button.'''
        return f"Edit Selected {self._get_entity_name()}"

    def _get_delete_button_text(self) -> str:
        '''Return text for the delete button.'''
        return f"Delete Selected {self._get_entity_name()}"

    @abstractmethod
    def _configure_table_columns(self):
        '''Set up table column labels, widths, and other properties.'''
        pass

    @abstractmethod
    def _get_item_data_for_display(self, campaign) -> List[Any]:
        '''Fetch and return a list of items (e.g., model instances) to be displayed in the table.'''
        pass

    @abstractmethod
    def _populate_table_row(self, row: int, item_data: Any):
        '''Populate a single row in the QTableWidget using the provided item_data.'''
        # Remember to store unique ID for the item in the row, e.g., using:
        # name_item.setData(Qt.ItemDataRole.UserRole, item_data.entry_id)
        pass

    @abstractmethod
    def _get_dialog_for_add(self) -> Optional[QDialog]:
        '''Return a new instance of the QDialog used for adding an item.
           The dialog should have a `get_data()` method.
        '''
        pass

    @abstractmethod
    def _get_dialog_for_edit(self, item_id: str, campaign) -> Optional[QDialog]:
        '''Return a new instance of the QDialog used for editing, pre-filled with item_id's data.
           The dialog should have a `get_data()` method.
           Return None if item not found.
        '''
        pass

    @abstractmethod
    def _get_selected_item_id(self) -> Optional[str]:
        '''Return the unique ID of the currently selected item in the table.
           Typically retrieved from item's UserRole data.
        '''
        pass

    @abstractmethod
    def _get_item_name_for_confirmation(self, item_id: str, campaign) -> Optional[str]:
        '''Return a display name for the item (used in delete confirmation).'''
        pass

    @abstractmethod
    def _perform_add_item(self, dialog_data: Any, campaign) -> None:
        '''Add the item (from dialog_data) to the campaign's data model.'''
        pass

    @abstractmethod
    def _perform_edit_item(self, item_id: str, dialog_data: Any, campaign) -> None:
        '''Update the item (identified by item_id) in the campaign's data model using dialog_data.'''
        pass

    @abstractmethod
    def _perform_delete_item(self, item_id: str, campaign) -> bool:
        '''Delete the item (identified by item_id) from the campaign's data model.
           Return True if deletion was successful, False otherwise.
        '''
        pass

    def _handle_no_campaign(self):
        '''Default behavior when no campaign is selected.'''
        self.table_widget.setRowCount(0)
        self.show_placeholder(True, "No campaign selected. Please select or create one from the File menu.")
        self._set_buttons_enabled(False)
        if hasattr(self, 'add_button'): # Add button should also be disabled if no campaign
            self.add_button.setEnabled(False)


    def _handle_no_data(self):
        '''Default behavior when campaign has no data for this tracker.'''
        self.table_widget.setRowCount(0)
        self.show_placeholder(True, f"No {self._entity_name_plural.lower()} defined for this campaign. Click '{self._get_add_button_text()}' to create one.")
        self._set_buttons_enabled(False) # Edit/Delete disabled
        if hasattr(self, 'add_button'):
            self.add_button.setEnabled(True) # Add button can be enabled

    # --- Helper methods for subclasses (optional to use) ---
    def _create_table_item(self, text: str, data_role_value: Optional[Any] = None, alignment: Optional[Qt.AlignmentFlag] = None) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        if data_role_value is not None:
            item.setData(Qt.ItemDataRole.UserRole, data_role_value)
        if alignment is not None:
            item.setTextAlignment(alignment)
        return item

    def _get_id_from_selected_row(self, column_with_id: int = 0) -> Optional[str]:
        '''Helper to get ID from a specific column in the selected row.'''
        selected_items = self.table_widget.selectedItems()
        if not selected_items:
            return None
        selected_row = self.table_widget.row(selected_items[0]) # Get row index from any selected item
        id_item = self.table_widget.item(selected_row, column_with_id)
        if id_item:
            return id_item.data(Qt.ItemDataRole.UserRole)
        return None
