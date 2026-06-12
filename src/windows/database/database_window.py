from PySide6.QtWidgets import QMainWindow, QWidget, QTableView, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from src.models.view_only_model import UniveralViewModel 
from src.database.model import Product, ProductType, Combo, Variant, ComboVariant, ComboDetail
from src.windows.dialogs.add_product_items import ProductAddDialog 
from src.windows.dialogs.add_combo_variant_items import ComboVariantAddDialog
import src.resources.resources_rc

class DatabaseWindow(QMainWindow):
    def __init__(self, session):
        super().__init__()

        self.session = session

        self.setWindowTitle("Cơ sở dữ liệu")
        self.setMinimumSize(QSize(1300, 600))

        # Quản lí data  
        self.product_manager = ProductData(
            session=self.session,
            column_names=["product_code", "product_name", "product_type_name"]
        )

        self.combo_variant_manager = ComboVariantData(
            session=self.session,
            column_names=["combo_variant_key", "combo_name", "variant_name"]
        )
        
        self.combo_detail_manager = ComboDetailData(
            session=self.session,
            column_names=["combo_detail_key", "combo_name", "variant_name", "combo_composition_key", "product_code", "product_name", "product_type_name", "product_price", "product_quantity"]
        )

        # Tạo data model với các data manager
        self.model_product = self.product_manager.create_model()
        self.model_combo_variant = self.combo_variant_manager.create_model()
        self.model_combo_detail = self.combo_detail_manager.create_model()

        # Dialogs
        self.product_add_dlg = None 
        self.combo_variant_add_dlg = None
        self.combo_detail_add_dlg = None

        # Icon
        list_plus_icon = QIcon(":/my_icons/icons/list-plus.svg")

        product_area = QVBoxLayout()
        product_header = QHBoxLayout()
        product_header.addWidget(QLabel("<b>Sản phẩm</b>"), alignment=Qt.AlignmentFlag.AlignLeft)
        self.add_product_btn = QPushButton()
        self.add_product_btn.setIcon(list_plus_icon)
        self.add_product_btn.setFixedWidth(30)
        product_header.addWidget(self.add_product_btn, alignment=Qt.AlignmentFlag.AlignRight)
        self.add_product_btn.pressed.connect(self.add_product)
        
        self.product_view = QTableView()
        product_area.addLayout(product_header)
        product_area.addWidget(self.product_view)
        self.product_view.setModel(self.model_product)
        
        # Vùng hiển thị các combo
        combo_variant_area = QVBoxLayout()
        combo_variant_header = QHBoxLayout()
        combo_variant_header.addWidget(QLabel("<b>Combo</b>"), alignment=Qt.AlignmentFlag.AlignLeft)
        self.add_combo_variant_btn = QPushButton()
        self.add_combo_variant_btn.setIcon(list_plus_icon)
        self.add_combo_variant_btn.setFixedWidth(30)
        combo_variant_header.addWidget(self.add_combo_variant_btn, alignment=Qt.AlignmentFlag.AlignRight)
        self.add_combo_variant_btn.pressed.connect(self.add_combo_variant)
        
        self.combo_view = QTableView()
        combo_variant_area.addLayout(combo_variant_header)
        combo_variant_area.addWidget(self.combo_view)
        self.combo_view.setModel(self.model_combo_variant)

        # Vùng hiển thị các combo
        combo_detail_area = QVBoxLayout()
        self.add_combo_detail_btn = QPushButton()
        self.add_combo_detail_btn.setIcon(list_plus_icon)
        self.add_combo_detail_btn.setFixedWidth(30)

        combo_detail_header = QHBoxLayout()
        combo_detail_header.addWidget(QLabel("<b>Chi tiết combo</b>"), alignment=Qt.AlignmentFlag.AlignLeft)
        combo_detail_header.addWidget(self.add_combo_detail_btn, alignment=Qt.AlignmentFlag.AlignRight)
        # self.add_combo_detail_btn.pressed.connect(self.add_combo_variant)

        self.combo_detail_view = QTableView()
        combo_detail_area.addLayout(combo_detail_header)
        combo_detail_area.addWidget(self.combo_detail_view)
        self.combo_detail_view.setModel(self.model_combo_detail)

        # Layout chính
        main_layout = QVBoxLayout()
        upper_layout = QHBoxLayout()
        upper_layout.addLayout(product_area)
        upper_layout.addLayout(combo_variant_area)

        lower_layout = QHBoxLayout()
        lower_layout.addLayout(combo_detail_area)

        main_layout.addLayout(upper_layout)
        main_layout.addLayout(lower_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def add_product(self):
        self.product_add_dlg = ProductAddDialog(session=self.session)
        self.product_add_dlg.product_added.connect(self.refresh_product_table)
        self.product_add_dlg.exec()  
    
    def add_combo_variant(self):
        self.combo_variant_add_dlg = ComboVariantAddDialog(
            session=self.session,
            added_combo_variant=self.combo_variant_manager.added_combo_variant,
            combos=self.combo_variant_manager._unique_combo,
            variants=self.combo_variant_manager._unique_variant
        )

        self.combo_variant_add_dlg.exec()

    def refresh_product_table(self):
        self.product_manager.refresh_model(self.model_product)

class ProductData:
    def __init__(self, session, column_names : dict):
        self.session = session
        self.product_data = None
        self.column_names= column_names 
        
    def query_data(self):
        product_query = (
            self.session.query(Product, ProductType)
            .join(ProductType, Product.product_type_key == ProductType.product_type_key)
            .all()
        )
        return product_query
    
    def process_data(self):
        result = []

        for product_obj, type_obj in self.query_data():
            result.append({
                "product_code": product_obj.product_code,
                "product_name": product_obj.product_name,
                "product_type_name": type_obj.product_type_name
            })
        
        return result 
    
    def create_model(self):
        processed_data = self.process_data()
        return UniveralViewModel(
            data=processed_data,
            column_names=self.column_names
        )

    def refresh_model(self, current_model):
        new_data = self.process_data()
        current_model.refresh_data(new_data)

class ComboVariantData:
    def __init__(self, session, column_names: list):
        self.session = session
        self.column_names = column_names
        
        # Biến lưu trữ danh sách phẳng Dict sau khi chế biến để truyền sang Dialog
        self._unique_combo = [] 
        self._unique_variant = []
        self.added_combo_variant = []

    def query_data(self):
        return (
            self.session.query(Combo, Variant, ComboVariant)
            .join(Combo, ComboVariant.combo_key == Combo.combo_key)
            .join(Variant, ComboVariant.variant_key == Variant.variant_key)
            .all()
        )

    def update_added_pairs(self):
        return self.session.query(ComboVariant.combo_key, ComboVariant.variant_key).all()

    def query_unique_combos(self):
        """Chỉ query duy nhất bảng Combo từ DB"""
        return self.session.query(Combo).all()

    def query_unique_variants(self):
        """Chỉ query duy nhất bảng Variant từ DB"""
        return self.session.query(Variant).all()

    def process_data(self):
        # 1. Làm sạch bộ đệm cũ trước khi nạp mới (Tránh trùng lặp khi bấm refresh)
        self._unique_combo.clear()
        self._unique_variant.clear()

        self.added_combo_variant =  self.update_added_pairs()

        # 2. Chế biến dữ liệu sạch cho Combo
        for combo in self.query_unique_combos():
            self._unique_combo.append({
                "combo_key": combo.combo_key,
                "combo_name": combo.combo_name
            })

        # 3. Chế biến dữ liệu sạch cho Variant (Đã bổ sung phần bị thiếu của bạn)
        for variant in self.query_unique_variants():
            self._unique_variant.append({
                "variant_key": variant.variant_key,
                "variant_name": variant.variant_name
            })
            
        # 4. Trả về kết quả hiển thị bảng QTableView chính ở ngoài cửa sổ
        result = []
        for combo_obj, variant_obj, combo_variant_obj in self.query_data():
            result.append({
                "combo_variant_key": combo_variant_obj.combo_variant_key,
                "combo_name": combo_obj.combo_name,
                "variant_name": variant_obj.variant_name
            })
        return result

    def create_model(self):
        return UniveralViewModel(data=self.process_data(), column_names=self.column_names)

    def refresh_model(self, current_model):
        current_model.refresh_data(self.process_data())


class ComboDetailData:
    def __init__(self, session, column_names: list):
        self.session = session
        self.column_names = column_names

    def query_data(self):
        return (
            self.session.query(ComboDetail, ComboVariant, Combo, Variant, Product, ProductType)
            .join(ComboVariant, ComboDetail.combo_variant_key == ComboVariant.combo_variant_key)
            .join(Combo, ComboVariant.combo_key == Combo.combo_key)
            .join(Variant, ComboVariant.variant_key == Variant.variant_key)
            .join(Product, ComboDetail.product_key== Product.product_key)
            .join(ProductType, Product.product_type_key == ProductType.product_type_key)
            .all()
        )

    def process_data(self):
        result = []
        for detail, combo_variant, combo, variant, product, p_type in self.query_data():
            result.append({
                "combo_detail_key": detail.combo_detail_key,
                "combo_name": combo.combo_name,
                "variant_name": variant.variant_name,
                "combo_composition_key": detail.combo_composition_key, 
                "product_code": product.product_code,
                "product_name": product.product_name,
                "product_type_name": p_type.product_type_name,
                "product_price": detail.product_price,
                "product_quantity": detail.product_quantity
            })
        return result

    def create_model(self):
        return UniveralViewModel(data=self.process_data(), column_names=self.column_names)

    def refresh_model(self, current_model):
        current_model.refresh_data(self.process_data())