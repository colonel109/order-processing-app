from pathlib import Path

from PySide6.QtWidgets import QWidget, QMainWindow, QFileDialog, QTableView, QVBoxLayout, QStatusBar, QToolBar, QAbstractItemView
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QSize
from PySide6.QtSql import QSqlTableModel

from src.order_processor import OrderProcessor
from src.config_loader import ConfigLoader
from src.database.connector import connector
from src.execute_query import execute_query
from src.windows.database.database_window import DatabaseWindow
import src.resources.resources_rc

class MainWindow(QMainWindow):
    def __init__(self, db_path, base_dir):
        super().__init__()
        self.base_dir = base_dir
        self.db_path = db_path

        # Kết nối tới database
        self.connector = connector(db_path=db_path)

        # Cửa sổ database
        self.db_window = None

        self.setMinimumSize(QSize(900, 500))
        self.setWindowTitle("Prototype 01")

        self.config = ConfigLoader(base_dir / "config_shopee.json")
        self.processor = OrderProcessor(
            rename_dict= self.config.get_rename_dict(),
            dtype_dict= self.config.get_dtype_dict(),
            db_path = db_path
        )

        # Thiết lập thanh menu
        menu = self.menuBar()
        file_menu = menu.addMenu("Tệp")
        data_menu = menu.addMenu("Cơ sở dữ liệu")

        # Nút mở đơn hàng
        self.open_file_act = QAction(
            QIcon(":/my_icons/icons/file.svg"),
            "Mở tệp đơn hàng",
            self
        )
        self.open_file_act.setStatusTip("Mở một (hoặc nhiều) tệp chứa đơn hàng và nạp tất cả vào cơ sở dữ liệu")
        file_menu.addAction(self.open_file_act)

        # Nút mở thư mục chứa đơn hàng
        self.open_folder_act = QAction(
            QIcon(":/my_icons/icons/folder.svg"),
            "Mở thư mục đơn hàng",
            self
        )
        self.open_folder_act.setStatusTip("Mở thư mục chứa đơn hàng và nạp tất cả vào cơ sở dữ liệu")
        file_menu.addAction(self.open_folder_act)

        # Nút mở file cấu hình
        self.open_config_act = QAction(
            QIcon(":/my_icons/icons/file-braces-corner.svg"),
            "Mở file cấu hình",
            self
        )
        file_menu.addAction(self.open_config_act)

        # Nút mở cơ sở dữ liệu
        self.open_database_act = QAction(
            QIcon(":/my_icons/icons/database-search.svg"),
            "Mở cơ sở dữ liệu",
            self
        )
        data_menu.addAction(self.open_database_act)

        # Bảng hiển thị đơn hàng
        self.table = QTableView()
        self.model = QSqlTableModel(self)
        self.table.setModel(self.model)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        main_container = QWidget()
        main_container.setLayout(layout)

        # Thanh công cụ
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        self.fetch_order_act = QAction("Lấy dữ liệu", self)
        self.fetch_order_act.setStatusTip("Lấy toàn bộ dữ liệu đơn hàng đã lưu trong cơ sở dữ liệu")
        toolbar.addAction(self.fetch_order_act)

        self.remove_orders_act = QAction("Xoá dữ liệu", self)
        self.remove_orders_act.setStatusTip("Xoá toàn bộ dữ liệu đơn hàng đã lưu trong cơ sở dữ liệu")
        toolbar.addAction(self.remove_orders_act)

        # Thanh trạng thái
        self.setStatusBar(QStatusBar(self))
        self.setCentralWidget(main_container)

        # Kết nối widget tới các hàm
        self.init_signals()

    def init_signals(self):
        self.open_file_act.triggered.connect(self.get_order_file)
        self.open_folder_act.triggered.connect(self.get_folder)
        self.open_config_act.triggered.connect(self.get_config)
        self.fetch_order_act.triggered.connect(self.fetch_order_data)
        self.remove_orders_act.triggered.connect(self.delete_order_data)
        self.open_database_act.triggered.connect(self.open_db_window)

    def get_order_file(self):
        filters = "Tệp Excel (*.xlsx; *.xls);; Tệp Csv (*.csv);; Tất cả các tệp (*)"
        selected_files = QFileDialog.getOpenFileNames(
            self,
            caption="Chọn tệp",
            dir=str(self.base_dir),
            filter=filters
        )
        file_list = selected_files[0]
        self.processor.order_processor(file_list)
        self.processor.import_data()

        self.model.setTable("shopee_orders")
        self.model.select()

    def get_folder(self):
        selected_folder = QFileDialog.getExistingDirectory(
            self,
            caption="Chọn thư mục",
            dir=str(self.base_dir)
        )

        if Path(selected_folder).is_dir:
            file_list = [file for file in Path(selected_folder).glob("*")]
            self.processor.order_processor(file_list)
            self.processor.import_data()
            self.model.setTable("shopee_orders")
            self.model.select()

    def get_config(self):
        QFileDialog.getOpenFileNames(
            self,
            caption="Mở tệp cấu hình",
            dir=str(self.base_dir),
            filter="Tệp JSON (config*.json)"
        )

    def fetch_order_data(self):
        self.model.setTable("shopee_orders")
        self.table.setModel(self.model)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.model.select()

    def delete_order_data(self):
        execute_query(
            """
                DELETE FROM shopee_orders WHERE order_id IS NOT NULL
            """
        )
        self.model.select()

    def open_db_window(self):
        self.db_window = DatabaseWindow(session=self.connector)
        self.db_window.show()