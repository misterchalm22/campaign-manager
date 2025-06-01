import sys
import os
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QListWidget, QListWidgetItem,
    QStackedWidget, QMenuBar, QStatusBar, QFileDialog, QMessageBox,
    QSplitter
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QCloseEvent

from PySide6.QtGui import QAction, QCloseEvent

from PySide6.QtGui import QAction, QCloseEvent

from src.data_models import ApplicationData, Campaign, NPCEntry # NPCEntry might be useful
from PySide6.QtGui import QAction, QCloseEvent

from src.data_models import ApplicationData, Campaign, NPCEntry # NPCEntry might be useful
from src.json_data_manager import load_data, save_data
from PySide6.QtGui import QAction, QCloseEvent

from src.data_models import ApplicationData, Campaign, NPCEntry # NPCEntry might be useful
from src.json_data_manager import load_data, save_data
from src.trackers.npc_tracker_ui import NPCTrackerWidget
from src.trackers.campaign_journal_ui import CampaignJournalWidget
from PySide6.QtGui import QAction, QCloseEvent

from src.data_models import ApplicationData, Campaign, NPCEntry # NPCEntry might be useful
from src.json_data_manager import load_data, save_data
from src.trackers.npc_tracker_ui import NPCTrackerWidget
from src.trackers.campaign_journal_ui import CampaignJournalWidget
from src.trackers.settlement_tracker_ui import SettlementTrackerWidget
from src.trackers.game_expectations_ui import GameExpectationsWidget
from src.trackers.travel_planner_ui import TravelPlannerWidget
from src.trackers.dm_character_tracker_ui import DMCharacterWidget
from src.trackers.campaign_conflicts_ui import CampaignConflictsWidget
from src.trackers.magic_item_tracker_ui import MagicItemTrackerWidget
from src.trackers.bastion_tracker_ui import BastionTrackerWidget

# Define tracker names as they appear in the UI - matches PRD for consistency
TRACKER_NAMES = [
    "Game Expectations", "Travel Planner", "NPC Tracker", "Settlement Tracker",
    "Campaign Journal", "DM's Character Tracker", "Campaign Conflicts",
    "Magic Item Tracker", "Bastion Tracker"
]

DATA_FILE_NAME = "ttrpg_campaign_data.json"

class MainWindow(QMainWindow):
    def __init__(self, app_data_path: Optional[str] = None):
        super().__init__()
        self.setWindowTitle("TTRPG Campaign Tracker")
        self.setGeometry(100, 100, 1200, 800)

        self.data_file_path = app_data_path if app_data_path else DATA_FILE_NAME
        self.application_data: ApplicationData = ApplicationData()
        self.current_campaign_id: Optional[str] = None
        self.current_tracker_name: Optional[str] = None

        self.tracker_widgets: dict[str, QWidget] = {} # To store instances of tracker widgets

        self._init_ui()
        self._load_app_data() # Load data and populate campaign selector
        self._connect_signals()
        self._update_tracker_nav_status() # Initial status update

    def _init_ui(self):
        # Central Widget and Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Campaign Management Area
        campaign_management_layout = QHBoxLayout()
        campaign_management_layout.addWidget(QLabel("Campaign:"))
        self.campaign_selector = QComboBox()
        self.campaign_selector.setPlaceholderText("No campaigns loaded")
        campaign_management_layout.addWidget(self.campaign_selector, 1) # Stretch combo box

        self.create_campaign_btn = QPushButton("New Campaign")
        campaign_management_layout.addWidget(self.create_campaign_btn)
        self.delete_campaign_btn = QPushButton("Delete Selected Campaign")
        campaign_management_layout.addWidget(self.delete_campaign_btn)
        # Import/Export individual campaigns might be complex, focusing on all data for now
        # self.import_campaign_btn = QPushButton("Import Campaign") # Future
        # self.export_campaign_btn = QPushButton("Export Campaign") # Future

        main_layout.addLayout(campaign_management_layout)

        # Main Content Area (Splitter)
        main_content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Tracker Navigation
        self.tracker_nav_list = QListWidget()
        for name in TRACKER_NAMES:
            self.tracker_nav_list.addItem(QListWidgetItem(name))
        main_content_splitter.addWidget(self.tracker_nav_list)

        # Tracker Display Area
        self.tracker_display_area = QStackedWidget()

        # Default placeholder if no tracker is selected or no campaign
        self.no_tracker_placeholder = QLabel("Select a campaign and then a tracker to view details.")
        self.no_tracker_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.tracker_display_area.addWidget(self.no_tracker_placeholder) # Will be added as default if no other widgets

        # Initialize actual tracker widgets and add them to the QStackedWidget
        self.npc_tracker_widget = NPCTrackerWidget(self)
        self.tracker_display_area.addWidget(self.npc_tracker_widget)
        self.tracker_widgets["NPC Tracker"] = self.npc_tracker_widget

        self.campaign_journal_widget = CampaignJournalWidget(self)
        self.tracker_display_area.addWidget(self.campaign_journal_widget)
        self.tracker_widgets["Campaign Journal"] = self.campaign_journal_widget

        self.settlement_tracker_widget = SettlementTrackerWidget(self)
        self.tracker_display_area.addWidget(self.settlement_tracker_widget)
        self.tracker_widgets["Settlement Tracker"] = self.settlement_tracker_widget

        self.game_expectations_widget = GameExpectationsWidget(self)
        self.tracker_display_area.addWidget(self.game_expectations_widget)
        self.tracker_widgets["Game Expectations"] = self.game_expectations_widget

        self.travel_planner_widget = TravelPlannerWidget(self)
        self.tracker_display_area.addWidget(self.travel_planner_widget)
        self.tracker_widgets["Travel Planner"] = self.travel_planner_widget

        self.dm_character_widget = DMCharacterWidget(self)
        self.tracker_display_area.addWidget(self.dm_character_widget)
        self.tracker_widgets["DM's Character Tracker"] = self.dm_character_widget

        self.campaign_conflicts_widget = CampaignConflictsWidget(self)
        self.tracker_display_area.addWidget(self.campaign_conflicts_widget)
        self.tracker_widgets["Campaign Conflicts"] = self.campaign_conflicts_widget

        self.magic_item_tracker_widget = MagicItemTrackerWidget(self)
        self.tracker_display_area.addWidget(self.magic_item_tracker_widget)
        self.tracker_widgets["Magic Item Tracker"] = self.magic_item_tracker_widget

        self.bastion_tracker_widget = BastionTrackerWidget(self)
        self.tracker_display_area.addWidget(self.bastion_tracker_widget)
        self.tracker_widgets["Bastion Tracker"] = self.bastion_tracker_widget

        # Add placeholder widgets for other trackers
        for name in TRACKER_NAMES:
            if name not in self.tracker_widgets: # If not already specifically added
                placeholder_widget = QLabel(f"Content for {name} will appear here.")
                placeholder_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tracker_display_area.addWidget(placeholder_widget)
                self.tracker_widgets[name] = placeholder_widget

        # Set initial widget (placeholder or specific if needed)
        if self.tracker_display_area.count() > 0:
             # Check if no_tracker_placeholder needs to be the default visible one
            current_widget_to_set = self.tracker_widgets.get("NPC Tracker") # Default to NPC for now or a generic one
            if not current_widget_to_set: # Should not happen if NPC tracker is there
                current_widget_to_set = self.no_tracker_placeholder
                if self.no_tracker_placeholder not in [self.tracker_display_area.widget(i) for i in range(self.tracker_display_area.count())]:
                    self.tracker_display_area.addWidget(self.no_tracker_placeholder)

            self.tracker_display_area.setCurrentWidget(self.no_tracker_placeholder \
                if self.no_tracker_placeholder in [self.tracker_display_area.widget(i) for i in range(self.tracker_display_area.count())] \
                else self.tracker_display_area.widget(0) )
        else: # Fallback if somehow no widgets were added (e.g. TRACKER_NAMES is empty)
            self.tracker_display_area.addWidget(self.no_tracker_placeholder)
            self.tracker_display_area.setCurrentWidget(self.no_tracker_placeholder)


        main_content_splitter.addWidget(self.tracker_display_area)
        main_content_splitter.setStretchFactor(0, 1) # Tracker nav proportion
        main_content_splitter.setStretchFactor(1, 3) # Tracker display proportion

        main_layout.addWidget(main_content_splitter, 1) # Stretch splitter

        # Menu Bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        import_all_action = QAction("Import All Data...", self)
        file_menu.addAction(import_all_action)

        export_all_action = QAction("Export All Data...", self)
        file_menu.addAction(export_all_action)

        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        file_menu.addAction(exit_action)

        # Status Bar
        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Ready.")

    def _connect_signals(self):
        # Campaign buttons
        self.create_campaign_btn.clicked.connect(self._on_create_campaign)
        self.delete_campaign_btn.clicked.connect(self._on_delete_campaign)
        self.campaign_selector.currentIndexChanged.connect(self._on_campaign_selected)

        # Tracker list
        self.tracker_nav_list.currentItemChanged.connect(self._on_tracker_selected)

        # Menu actions
        # Assuming import_all_action and export_all_action are attributes if connected here
        # Or connect them directly:
        file_menu = self.menuBar().actions()[0].menu() # Get the File menu
        import_all_action = file_menu.actions()[0]
        export_all_action = file_menu.actions()[1]
        exit_action = file_menu.actions()[3]

        import_all_action.triggered.connect(self._on_import_all_data)
        export_all_action.triggered.connect(self._on_export_all_data)
        exit_action.triggered.connect(self.close)


    def _populate_campaign_selector(self):
        self.campaign_selector.blockSignals(True)
        self.campaign_selector.clear()
        if not self.application_data or not self.application_data.campaigns:
            self.campaign_selector.setPlaceholderText("No campaigns - Create or Import one")
            self.current_campaign_id = None
        else:
            self.campaign_selector.setPlaceholderText("Select a campaign")
            for campaign_id, campaign in self.application_data.campaigns.items():
                self.campaign_selector.addItem(campaign.name, userData=campaign_id)

            if self.current_campaign_id and self.current_campaign_id in self.application_data.campaigns:
                for i in range(self.campaign_selector.count()):
                    if self.campaign_selector.itemData(i) == self.current_campaign_id:
                        self.campaign_selector.setCurrentIndex(i)
                        break
            elif self.campaign_selector.count() > 0:
                 self.campaign_selector.setCurrentIndex(0) # Select first one if current is invalid
                 self.current_campaign_id = self.campaign_selector.itemData(0)
            else: # No campaigns left
                self.current_campaign_id = None

        self.campaign_selector.blockSignals(False)
        self._on_campaign_selected(self.campaign_selector.currentIndex()) # Ensure UI updates based on selection


    def _update_tracker_nav_status(self):
        campaign_exists_and_selected = bool(self.current_campaign_id and self.application_data.campaigns.get(self.current_campaign_id))

        self.tracker_nav_list.setEnabled(campaign_exists_and_selected)
        self.delete_campaign_btn.setEnabled(campaign_exists_and_selected)

        if campaign_exists_and_selected:
            if self.current_tracker_name:
                items = self.tracker_nav_list.findItems(self.current_tracker_name, Qt.MatchFlag.MatchExactly)
                if items:
                    self.tracker_nav_list.setCurrentItem(items[0]) # This should trigger _on_tracker_selected
                else: # current_tracker_name is invalid, reset
                    self.tracker_nav_list.clearSelection() # This also triggers _on_tracker_selected with None
                    self.tracker_display_area.setCurrentWidget(self.no_tracker_placeholder)
            else: # No tracker yet selected for this campaign
                self.tracker_nav_list.clearSelection()
                self.tracker_display_area.setCurrentWidget(self.no_tracker_placeholder)
        else: # No campaign selected or exists
            self.tracker_nav_list.clearSelection()
            self.tracker_display_area.setCurrentWidget(self.no_tracker_placeholder)
            self.current_tracker_name = None

    @Slot()
    def _on_create_campaign(self):
        # Simple dialog for campaign name
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "New Campaign", "Enter campaign name:")
        if ok and name:
            # Check for duplicate names
            if any(c.name == name for c in self.application_data.campaigns.values()):
                QMessageBox.warning(self, "Duplicate Name", "A campaign with this name already exists.")
                return

            import uuid
            campaign_id = str(uuid.uuid4())
            new_campaign = Campaign(campaign_id=campaign_id, name=name)
            self.application_data.campaigns[campaign_id] = new_campaign
            self.current_campaign_id = campaign_id
            self._populate_campaign_selector() # Will select the new campaign
            self._save_app_data()
            self.statusBar().showMessage(f"Campaign '{name}' created.")
        self._update_tracker_nav_status()

    @Slot()
    def _on_delete_campaign(self):
        if not self.current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "No campaign selected to delete.")
            return

        campaign_to_delete = self.application_data.campaigns.get(self.current_campaign_id)
        if not campaign_to_delete: # Should not happen if current_campaign_id is set
            QMessageBox.critical(self, "Error", "Selected campaign not found in data.")
            return

        reply = QMessageBox.question(self, "Delete Campaign",
                                     f"Are you sure you want to delete campaign '{campaign_to_delete.name}'?\nThis action cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            del self.application_data.campaigns[self.current_campaign_id]
            self.current_campaign_id = None # Reset current campaign
            self._save_app_data()
            self._populate_campaign_selector() # Repopulate and select default if any
            self.statusBar().showMessage(f"Campaign '{campaign_to_delete.name}' deleted.")
        self._update_tracker_nav_status()


    @Slot()
    def _on_import_all_data(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Import Data File", "", "JSON files (*.json)")
        if filepath:
            original_data_path = self.data_file_path
            self.data_file_path = filepath # Temporarily change path for loading
            self._load_app_data() # This calls populate_campaign_selector and update_tracker_nav
            self.data_file_path = original_data_path # Revert to original if it's different (or decide to adopt new path)
            # To make the change permanent, one might uncomment:
            # self.data_file_path = filepath
            self._save_app_data() # Save the newly imported data to the standard/new location
            self.statusBar().showMessage(f"Data imported from {filepath}.")


    @Slot()
    def _on_export_all_data(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Export All Data", "", "JSON files (*.json)")
        if filepath:
            if save_data(self.application_data, filepath):
                self.statusBar().showMessage(f"All data exported to {filepath}.")
            else:
                QMessageBox.critical(self, "Export Error", f"Failed to export data to {filepath}.")


    @Slot(int)
    def _on_campaign_selected(self, index: int):
        if index < 0 or self.campaign_selector.count() == 0: # No item selected or no items
            self.current_campaign_id = None
        else:
            self.current_campaign_id = self.campaign_selector.itemData(index)

        # When campaign changes, reset current tracker selection logic
        self.current_tracker_name = None # Reset tracker name
        self.tracker_nav_list.clearSelection() # Clear visual selection
        self.tracker_display_area.setCurrentWidget(self.no_tracker_placeholder) # Show placeholder

        self._update_tracker_nav_status()
        if self.current_campaign_id:
            campaign = self.application_data.campaigns.get(self.current_campaign_id)
            if campaign:
                 self.statusBar().showMessage(f"Campaign '{campaign.name}' selected.")
        else:
            self.statusBar().showMessage("No campaign selected.")


    @Slot(QListWidgetItem, QListWidgetItem)
    def _on_tracker_selected(self, current_item: QListWidgetItem, previous_item: Optional[QListWidgetItem]):
        if current_item:
            self.current_tracker_name = current_item.text()

            # Switch to the correct widget in QStackedWidget
            widget_to_display = self.tracker_widgets.get(self.current_tracker_name)
            if widget_to_display:
                self.tracker_display_area.setCurrentWidget(widget_to_display)
                if self.current_tracker_name == "NPC Tracker":
                    self.npc_tracker_widget.refresh_display()
                elif self.current_tracker_name == "Campaign Journal":
                    self.campaign_journal_widget.refresh_display()
                elif self.current_tracker_name == "Settlement Tracker":
                    self.settlement_tracker_widget.refresh_display()
                elif self.current_tracker_name == "Game Expectations":
                    self.game_expectations_widget.refresh_display()
                elif self.current_tracker_name == "Travel Planner":
                    self.travel_planner_widget.refresh_display()
                elif self.current_tracker_name == "DM's Character Tracker":
                    self.dm_character_widget.refresh_display()
                elif self.current_tracker_name == "Campaign Conflicts":
                    self.campaign_conflicts_widget.refresh_display()
                elif self.current_tracker_name == "Magic Item Tracker":
                    self.magic_item_tracker_widget.refresh_display()
                elif self.current_tracker_name == "Bastion Tracker":
                    self.bastion_tracker_widget.refresh_display()
                # Add elif for other actual tracker widgets and their refresh methods
                self.statusBar().showMessage(f"Tracker '{self.current_tracker_name}' selected.")
            else: # Should not happen if TRACKER_NAMES and tracker_widgets are in sync
                self.tracker_display_area.setCurrentWidget(self.no_tracker_placeholder)
                self.statusBar().showMessage(f"Tracker '{self.current_tracker_name}' not found.", 3000)
        else:
            self.current_tracker_name = None
            self.tracker_display_area.setCurrentWidget(self.no_tracker_placeholder)
            self.statusBar().showMessage("No tracker selected.")


    def _save_app_data(self):
        if save_data(self.application_data, self.data_file_path):
            self.statusBar().showMessage(f"Data saved to {self.data_file_path}.")
        else:
            QMessageBox.critical(self, "Save Error", f"Failed to save data to {self.data_file_path}.")
            self.statusBar().showMessage(f"Error saving data to {self.data_file_path}.")


    def _load_app_data(self):
        self.application_data = load_data(self.data_file_path)
        # Ensure current_campaign_id is valid after loading
        if self.application_data.active_campaign_id and \
           self.application_data.active_campaign_id in self.application_data.campaigns:
            self.current_campaign_id = self.application_data.active_campaign_id
        elif self.application_data.campaigns: # if active_id is invalid, pick first one
            self.current_campaign_id = list(self.application_data.campaigns.keys())[0]
            self.application_data.active_campaign_id = self.current_campaign_id
        else: # No campaigns
             self.current_campaign_id = None
             self.application_data.active_campaign_id = ""

        self._populate_campaign_selector() # This will also trigger _on_campaign_selected
        # _update_tracker_nav_status() is called by _populate_campaign_selector via _on_campaign_selected
        self.statusBar().showMessage(f"Data loaded from {self.data_file_path}.")


    def closeEvent(self, event: QCloseEvent):
        # Save data on close
        if self.current_campaign_id: # Save active campaign ID
            self.application_data.active_campaign_id = self.current_campaign_id
        else:
            self.application_data.active_campaign_id = ""

        self._save_app_data()
        super().closeEvent(event)

if __name__ == '__main__': # Basic test
    # This is for direct testing of main_window.py. app.py is the main entry point.
    app = QApplication(sys.argv)
    # You can create a temporary test data file here if needed
    # For example:
    # test_data_path = "temp_test_data.json"
    # initial_test_data = ApplicationData()
    # save_data(initial_test_data, test_data_path)

    main_win = MainWindow() # MainWindow(app_data_path=test_data_path)
    main_win.show()
    exit_code = app.exec()

    # Clean up temporary test file
    # if os.path.exists(test_data_path):
    #    os.remove(test_data_path)
    sys.exit(exit_code)
