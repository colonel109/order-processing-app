from PySide6.QtWidgets import QMainWindow, QWidget, QTableView, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import QSize

from database.model import ComboDetail
from src.models.product_model import ViewModel
from src.database.model import Product, ProductType, Combo, Variant, ComboVariant

class DatabaseWindow(QMainWindow):
    def __init__(self, session):
        super().__init__()

        self.session= session
        self.setWindowTitle("Cơ sở dữ liệu")
        self.setMinimumSize(QSize(600, 400))

        product_query = (
            session.query(Product, ProductType)
            .join(ProductType, Product.product_type_key == ProductType.product_type_key)
            .all()
        )

        product_data = []
        for product_obj, type_obj in product_query:
            product_data.append({
                "product_code": product_obj.product_code,
                "product_name": product_obj.product_name,
                "product_type_name": type_obj.product_type_name
            })

        product_headers = {"product_code", "product_name", "product_type_name"}

        # 4. Truyền vào Model vạn năng
        self.model_product = ViewModel(
            data=product_data,
            column_names=["product_code", "product_name", "product_type_name"],
            headers=product_headers
        )

        combo_query = (
            session.query(Combo, Variant, ComboVariant)
            .join(Combo, ComboVariant.combo_key == Combo.combo_key)
            .join(Variant, ComboVariant.variant_key == Variant.variant_key)
            .all()
        )

        combo_data = []
        for combo_obj, variant_obj, combo_variant_obj in combo_query:
            combo_data.append({
                "combo_variant_key": combo_variant_obj.combo_variant_key,
                "combo_name": combo_obj.combo_name,
                "variant_name": variant_obj.variant_name
            })

        combo_headers = {
            "combo_variant_key",
            "combo_name",
            "variant_name"
        }

        self.model_combo = ViewModel(
            data=combo_data,
            column_names=["combo_variant_key", "combo_name", "variant_name"],
            headers=combo_headers
        )

        combo_detail_query = (
            session.query(ComboDetail, ComboVariant, Combo, Variant, Product, ProductType)
            .join(ComboVariant, ComboDetail.combo_variant_key == ComboVariant.combo_variant_key)
            .join(Combo, ComboVariant.combo_key == Combo.combo_key)
            .join(Variant, ComboVariant.variant_key == Variant.variant_key)
            .join(Product, ComboDetail.product_code == Product.product_code)
            .join(ProductType, Product.product_type_key == ProductType.product_type_key)
            .all()
        )

        formatted_combo_details = []

        for detail, cv, combo, variant, product, p_type in combo_detail_query:
            formatted_combo_details.append({
                # Từ bảng ComboDetail (Bảng gốc của dòng)
                "combo_detail_key": detail.combo_detail_key,
                "quantity": detail.quantity,  # Số lượng sản phẩm này trong combo

                # Từ bảng Combo và Variant (Thông tin định danh Combo)
                "combo_name": combo.combo_name,
                "variant_name": variant.variant_name,

                # Từ bảng Product và ProductType (Thông tin sản phẩm nằm TRONG combo)
                "product_code": product.product_code,
                "product_name": product.product_name,
                "product_type_name": p_type.product_type_name
            })

        # 3. Định nghĩa danh sách các cột bạn muốn hiển thị trên lưới giao diện (Theo thứ tự từ trái sang phải)
        column_names = [
            "combo_detail_key",
            "combo_name",
            "variant_name",
            "product_code",
            "product_name",
            "product_type_name",
            "quantity"
        ]

        # 4. Định nghĩa từ điển tiêu đề tiếng Việt để "Việt hóa" cái bảng
        headers = {
            "combo_detail_key": "ID Chi Tiết",
            "combo_name": "Tên Combo Gốc",
            "variant_name": "Biến Thể Combo",
            "product_code": "Mã Sản Phẩm Con",
            "product_name": "Tên Sản Phẩm Con",
            "product_type_name": "Loại Sản Phẩm",
            "quantity": "Số Lượng Thành Phần"
        }

        # 5. Đút toàn bộ nguyên liệu sạch này vào Model vạn năng của bạn!
        self.model_combo_detail = ViewModel(
            data=formatted_combo_details,
            column_names=column_names,
            headers=headers
        )


        main_layout = QVBoxLayout()
        upper_layout = QHBoxLayout()

        self.product_view = QTableView()
        self.combo_view = QTableView()
        self.combo_details_view = QTableView()

        upper_layout.addWidget(self.product_view)
        upper_layout.addWidget(self.combo_view)
        main_layout.addLayout(upper_layout)
        main_layout.addWidget(self.combo_details_view)

        self.combo_view.setModel(self.model_combo)
        self.product_view.setModel(self.model_product)
        self.combo_details_view.setModel(self.model_combo_detail)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)