from pathlib import Path

from windows.main_window import MainWindow
from PySide6.QtWidgets import QApplication
import sys

# Đường dẫn
BASE_DIR = Path(__file__).parent
DB_PATH = Path(BASE_DIR / "database.sqlite3")

app = QApplication(sys.argv)
main_window = MainWindow(db_path=DB_PATH, base_dir=BASE_DIR)
window = main_window
window.show()
sys.exit(app.exec())