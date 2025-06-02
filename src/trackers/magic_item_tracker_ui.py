from functools import partial
from typing import List, cast, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QTabWidget, QGroupBox, QLabel,
    QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Slot

from src.data_models import MagicItemTierData, MagicItemTrackerData # Assuming these are defined

class MagicItemTrackerWidget(QWidget):
    RARITY_LEVELS = ["common", "uncommon", "rare", "very_rare", "legendary"]
    TIER_LEVEL_MAP = {
        "Levels 1-4": "level_tier_1_4",
        "Levels 5-10": "level_tier_5_10",
        "Levels 11-16": "level_tier_11_16",
        "Levels 17-20": "level_tier_17_20"
    }
    RARITY_FIELD_MAP = {
        "Common": "common_items",
        "Uncommon": "uncommon_items",
        "Rare": "rare_items",
        "Very Rare": "very_rare_items",
        "Legendary": "legendary_items"
    }

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.ui_elements: dict = {} # To store lists, lineedits, etc. for easy access

        main_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        for tab_title, tier_attr_name in self.TIER_LEVEL_MAP.items():
            tier_tab_widget = self._create_tier_tab(tier_attr_name)
            self.tab_widget.addTab(tier_tab_widget, tab_title)

        self.setLayout(main_layout)

    def _create_tier_tab(self, tier_attr_name: str) -> QWidget:
        tier_widget = QWidget()
        tier_layout = QVBoxLayout(tier_widget)
        tier_layout.setContentsMargins(5,5,5,5) # Small margins for tab content

        self.ui_elements[tier_attr_name] = {}

        for rarity_display_name, rarity_field_name in self.RARITY_FIELD_MAP.items():
            group_box = QGroupBox(rarity_display_name)
            group_layout = QVBoxLayout(group_box)

            list_widget = QListWidget()
            list_widget.setAlternatingRowColors(True)

            input_layout = QHBoxLayout()
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"New {rarity_display_name.lower()} item name...")
            add_button = QPushButton("Add Item")

            input_layout.addWidget(line_edit)
            input_layout.addWidget(add_button)

            remove_button = QPushButton("Remove Selected Item")

            group_layout.addLayout(input_layout)
            group_layout.addWidget(list_widget)
            group_layout.addWidget(remove_button)

            tier_layout.addWidget(group_box)

            # Store references for easy access later
            self.ui_elements[tier_attr_name][rarity_field_name] = {
                "list": list_widget,
                "line_edit": line_edit,
                "add_button": add_button,
                "remove_button": remove_button
            }

            # Connect signals
            add_button.clicked.connect(
                partial(self._on_add_item, tier_attr_name, rarity_field_name)
            )
            remove_button.clicked.connect(
                partial(self._on_remove_item, tier_attr_name, rarity_field_name)
            )
            # Allow adding by pressing Enter in LineEdit
            line_edit.returnPressed.connect(add_button.click)


        tier_widget.setLayout(tier_layout)
        return tier_widget

    def refresh_display(self):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            # Clear all lists if no campaign is selected
            for tier_attr_name in self.TIER_LEVEL_MAP.values():
                if tier_attr_name in self.ui_elements:
                    for rarity_field_name in self.RARITY_FIELD_MAP.values():
                        if rarity_field_name in self.ui_elements[tier_attr_name]:
                            self.ui_elements[tier_attr_name][rarity_field_name]["list"].clear()
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign or not campaign.magic_item_tracker:
            # Should not happen if __post_init__ works in Campaign model
            QMessageBox.critical(self, "Error", "Magic Item Tracker data not found for this campaign.")
            return

        tracker_data: MagicItemTrackerData = campaign.magic_item_tracker

        for tier_attr_name in self.TIER_LEVEL_MAP.values():
            tier_data_object: Optional[MagicItemTierData] = getattr(tracker_data, tier_attr_name, None)
            if not tier_data_object: continue # Should not happen

            for rarity_field_name in self.RARITY_FIELD_MAP.values():
                ui_group = self.ui_elements.get(tier_attr_name, {}).get(rarity_field_name)
                if not ui_group: continue

                list_widget: QListWidget = ui_group["list"]
                list_widget.clear()

                items_list: List[str] = getattr(tier_data_object, rarity_field_name, [])
                for item_name in items_list:
                    list_widget.addItem(QListWidgetItem(item_name))

    def _on_add_item(self, tier_attr_name: str, rarity_field_name: str):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "Cannot add item: No campaign selected.")
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign or not campaign.magic_item_tracker:
            QMessageBox.critical(self, "Error", "Magic Item Tracker data not found.")
            return

        ui_group = self.ui_elements[tier_attr_name][rarity_field_name]
        line_edit: QLineEdit = ui_group["line_edit"]
        list_widget: QListWidget = ui_group["list"]
        item_name = line_edit.text().strip()

        if not item_name:
            QMessageBox.warning(self, "Input Error", "Item name cannot be empty.")
            return

        tier_data_object: MagicItemTierData = getattr(campaign.magic_item_tracker, tier_attr_name)
        items_list: List[str] = getattr(tier_data_object, rarity_field_name)

        # Check for duplicates
        if item_name in items_list:
            QMessageBox.information(self, "Duplicate Item", f"'{item_name}' already exists in this list.")
            return

        items_list.append(item_name)
        # Sort the list alphabetically after adding - optional, but good for consistency
        items_list.sort()

        self.main_window._save_app_data()

        # Refresh only the specific list widget
        list_widget.clear()
        for name_in_list in items_list:
            list_widget.addItem(QListWidgetItem(name_in_list))

        line_edit.clear()
        self.main_window.statusBar().showMessage(f"Item '{item_name}' added.", 2000)


    def _on_remove_item(self, tier_attr_name: str, rarity_field_name: str):
        current_campaign_id = self.main_window.current_campaign_id
        if not current_campaign_id:
            QMessageBox.warning(self, "No Campaign", "Cannot remove item: No campaign selected.")
            return

        campaign = self.main_window.application_data.campaigns.get(current_campaign_id)
        if not campaign or not campaign.magic_item_tracker:
            QMessageBox.critical(self, "Error", "Magic Item Tracker data not found.")
            return

        ui_group = self.ui_elements[tier_attr_name][rarity_field_name]
        list_widget: QListWidget = ui_group["list"]

        selected_list_items = list_widget.selectedItems()
        if not selected_list_items:
            QMessageBox.information(self, "No Selection", "Please select an item to remove.")
            return

        item_to_remove_name = selected_list_items[0].text()

        reply = QMessageBox.question(self, "Remove Item",
                                     f"Are you sure you want to remove '{item_to_remove_name}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return

        tier_data_object: MagicItemTierData = getattr(campaign.magic_item_tracker, tier_attr_name)
        items_list: List[str] = getattr(tier_data_object, rarity_field_name)

        if item_to_remove_name in items_list:
            items_list.remove(item_to_remove_name)
            self.main_window._save_app_data()
            # Refresh specific list
            list_widget.takeItem(list_widget.row(selected_list_items[0])) # More efficient than clear + repopulate
            self.main_window.statusBar().showMessage(f"Item '{item_to_remove_name}' removed.", 2000)

        else: # Should not happen if UI is in sync with data
            QMessageBox.warning(self, "Error", f"Item '{item_to_remove_name}' not found in data model.")
            self.refresh_display() # Full refresh to ensure sync

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QStatusBar
    from src.data_models import ApplicationData, Campaign # For mock

    class MockMainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.current_campaign_id = "mit_test_camp"
            self.application_data = ApplicationData()
            campaign = Campaign(campaign_id=self.current_campaign_id, name="Magic Item Test Campaign")
            # Pre-populate some data for testing refresh
            campaign.magic_item_tracker.level_tier_1_4.common_items.append("Potion of Healing")
            campaign.magic_item_tracker.level_tier_1_4.uncommon_items.append("Bag of Holding")
            campaign.magic_item_tracker.level_tier_5_10.rare_items.append("Flame Tongue")
            self.application_data.campaigns[self.current_campaign_id] = campaign
            self.setStatusBar(QStatusBar(self))

        def _save_app_data(self):
            print(f"MockMainWindow: _save_app_data called for campaign: {self.current_campaign_id}")
            # print(self.application_data.campaigns[self.current_campaign_id].magic_item_tracker)


        def statusBar(self):
            return super().statusBar()

    app = QApplication(sys.argv)
    mock_main = MockMainWindow()
    mit_widget = MagicItemTrackerWidget(mock_main)

    mock_main.setCentralWidget(mit_widget)
    mock_main.setWindowTitle("Magic Item Tracker Widget Test")
    mock_main.setGeometry(100, 100, 800, 600)

    mit_widget.refresh_display() # Initial population
    mock_main.show()
    sys.exit(app.exec())
