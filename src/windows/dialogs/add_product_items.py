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


class ComboVariantAddDialog(QDialog):
    def __init__(self, session, combos: list, variants: list, parent=None):
        super().__init__(parent)

        self.session = session 
        
        # Lấy danh sách các combo / variant đã tạo trong database
        self.available_combos = combos
        self.available_variants = variants

        # Lấy key của combo / variant đã chọn
        self.selected_combo_key = None
        self.selected_variant_key = None
        
        self.setWindowTitle("Thêm nhóm combo mới")

        layout = QVBoxLayout()

        self.setMinimumWidth(500)

        layout.addWidget(QLabel("Tên combo")) 
        plus_icon = QIcon("D:\Projects\order-processing-app\src\static\plus.png")

        # Layout dành cho tên combo và nút thêm combo
        self.combo_input = QLineEdit()
        self.combo_add_btn = QPushButton()
        self.combo_add_btn.setIcon(plus_icon)

        combo_layout = QHBoxLayout()
        combo_layout.addWidget(self.combo_input) 
        combo_layout.addWidget(self.combo_add_btn)
        layout.addLayout(combo_layout)

        layout.addWidget(QLabel("Loại combo"))
    
        # Layout dành cho loại combo và nút thêm loại combo
        self.variant_input = QLineEdit()
        self.variant_add_btn = QPushButton()
        self.variant_add_btn.setIcon(plus_icon)

        self.combo_input.textChanged.connect(self.combo_text_changed)
        self.variant_input.textChanged.connect(self.variant_text_changed)

        self.input_suggest()

        variant_layout = QHBoxLayout()
        variant_layout.addWidget(self.variant_input)
        variant_layout.addWidget(self.variant_add_btn)
        layout.addLayout(variant_layout)

        cfm_buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(cfm_buttons)
        layout.addWidget(self.button_box)
        
        self.setLayout(layout)

    def combo_text_changed(self, current_text):
        self.selected_combo_key = None

        for c in self.available_combos:
            if c["combo_name"] == current_text:
                self.selected_combo_key = c["combo_key"]
                break
    
    def variant_text_changed(self, current_text):
        self.selected_variant_key = None

        for v in self.available_variants:
            if v["varinant_name"] == current_text:
                self.selected_variant_key = v["variant_key"]
                break

    def input_suggest(self):
        combo_strings = [c["combo_name"] for c in self.available_combos]
        self.combo_completer = QCompleter(combo_strings, self)
        self.combo_completer.setFilterMode(Qt.MatchFlag.MatchContains) # Tìm chữ ở bất kỳ vị trí nào
        self.combo_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive) # Không phân biệt hoa/thường
        
        self.combo_input.setCompleter(self.combo_completer)
        
        self.combo_completer.activated.connect(self.on_combo_selected)

        variant_strings = [v["variant_name"] for v in self.available_variants]
        
        self.variant_completer = QCompleter(variant_strings, self)
        self.variant_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.variant_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.variant_input.setCompleter(self.variant_completer)
        self.variant_completer.activated.connect(self.on_variant_selected)
    
    def on_combo_selected(self, text):
        # Duyệt qua danh sách RAM để tìm id gốc của Database
        for c in self.available_combos:
            if c["combo_name"] == text:
                self.selected_combo_key = c["combo_key"]
                print(f"Đã bắt được Combo ID thực tế: {self.selected_combo_key}")
                break

    def on_variant_selected(self, text):
        for v in self.available_variants:
            if v["variant_name"] == text:
                self.selected_variant_key = v["variant_key"]
                print(f"Đã bắt được Variant ID thực tế: {self.selected_variant_key}")
                break