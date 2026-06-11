from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QVBoxLayout, QDialogButtonBox, QPushButton, QHBoxLayout, QCompleter
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt, Signal
from src.database.model import Product, ProductType

class ProductAddDialog(QDialog):
    product_added = Signal()
    
    def __init__(self, session, parent=None):
        super().__init__()
        
        self.session = session

        self.setWindowTitle("Thêm sản phẩm mới")

        layout = QVBoxLayout()
        
        self.setMinimumWidth(300)

        layout.addWidget(QLabel("Mã sản phẩm:"))
        self.code_input = QLineEdit()
        layout.addWidget(self.code_input)

        layout.addWidget(QLabel("Tên sản phẩm"))
        self.name_input = QLineEdit()
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel("Loại sản phẩm"))
        self.type_input = QComboBox()
        layout.addWidget(self.type_input)
        self.load_product_type()

        cfm_buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(cfm_buttons)
        layout.addWidget(self.button_box)

        self.setLayout(layout)
        self.init_signal()

    def init_signal(self):
        self.button_box.accepted.connect(self.save_data)

    def load_product_type(self):
        try:
            product_type = self.session.query(ProductType).all()
            for type in product_type:
                self.type_input.addItem(type.product_type_name, type.product_type_key)
        except Exception as e:
            print(e)

    def save_data(self):
        product_code = self.code_input.text().strip()
        product_name = self.name_input.text().strip()
        product_type_key = self.type_input.currentData()

        product_insert = Product(
            product_code = product_code,
            product_name = product_name,
            product_type_key = product_type_key 
        )

        try:
            self.session.add(product_insert)
            self.session.commit()
            self.product_added.emit()
            self.code_input.clear()
            self.name_input.clear()
        
        except Exception as e:
            print(e)
            self.session.rollback()