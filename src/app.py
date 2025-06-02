import sys
import os
from PySide6.QtWidgets import QApplication
from src.main_window import MainWindow, DATA_FILE_NAME

# Determine the application data file path.
# This could be in a user-specific directory in a real app.
# For now, it's in the current working directory or alongside the script.
APP_DATA_PATH = DATA_FILE_NAME # Uses the constant from main_window

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Ensure the directory for the data file exists if it's more complex,
    # but for a simple filename, it will be in the CWD.
    # For example, if APP_DATA_PATH was 'data/app_data.json':
    # data_dir = os.path.dirname(APP_DATA_PATH)
    # if data_dir and not os.path.exists(data_dir):
    #     os.makedirs(data_dir)

    main_win = MainWindow(app_data_path=APP_DATA_PATH) # Pass app_data_path only
    main_win.show()

    sys.exit(app.exec())
