from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QDialogButtonBox, QPushButton, QHBoxLayout, QTableView
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

# Import model hiển thị vạn năng của bạn để nuôi 2 cái bảng TableView nhỏ này
from src.models.view_only_model import UniveralViewModel
import src.resources.resources_rc

class ComboVariantAddDialog(QDialog):
    def __init__(self, session, added_combo_variant: set, combos: list, variants: list, parent=None):
        super().__init__(parent)

        # Thiết lập session để fetch data
        self.session = session 

        # Lưu trữ lại các thông tin được lấy từ database
        self.added_combo_variant = added_combo_variant
        self.available_combos = combos
        self.available_variants = variants

        # Tạo 2 biến lưu lại key mà người dùng chọn để lưu vào database
        self.selected_combo_key = None
        self.selected_variant_key = None

        # Tạo biến lưu các cặp combo - variant đang chọn để so sánh
        self.current_selected_pair = (self.selected_combo_key, self.selected_variant_key)

        self.setWindowTitle("Thêm nhóm combo mới")
        self.setMinimumWidth(1300)
        self.setMinimumHeight(550)

        plus_icon = QIcon(":/my_icons/icons/plus.svg")

        self.combo_add_btn = QPushButton()
        self.combo_add_btn.setIcon(plus_icon)
        self.combo_add_btn.setFixedWidth(30) 

        combo_button_layout = QHBoxLayout()
        combo_button_layout.addWidget(QLabel("<b>Tên combo</b>"), alignment=Qt.AlignmentFlag.AlignLeft) 
        combo_button_layout.addWidget(self.combo_add_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.combo_filter = QLineEdit()
        self.combo_filter.setPlaceholderText("Lọc các combo đã tạo...")
        
        self.combo_list_view = QTableView()
        self.combo_list_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.combo_list_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)

        combo_layout = QVBoxLayout()
        combo_layout.addLayout(combo_button_layout)
        combo_layout.addWidget(self.combo_filter)
        combo_layout.addWidget(self.combo_list_view)

        self.variant_add_btn = QPushButton()
        self.variant_add_btn.setIcon(plus_icon)
        self.variant_add_btn.setFixedWidth(30)

        variant_button_layout = QHBoxLayout()
        variant_button_layout.addWidget(QLabel("<b>Loại combo (Variant)</b>"), alignment=Qt.AlignmentFlag.AlignLeft)
        variant_button_layout.addWidget(self.variant_add_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.variant_filter = QLineEdit()
        self.variant_filter.setPlaceholderText("Lọc các loại combo...")

        self.variant_list_view = QTableView()
        self.variant_list_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.variant_list_view.setSelectionMode(QTableView.SelectionMode.SingleSelection)

        variant_layout = QVBoxLayout()
        variant_layout.addLayout(variant_button_layout)
        variant_layout.addWidget(self.variant_filter)
        variant_layout.addWidget(self.variant_list_view)

        self.model_dialog_combo = UniveralViewModel(data=self.available_combos, column_names=["combo_name"])
        self.model_dialog_variant = UniveralViewModel(data=self.available_variants, column_names=["variant_name"])
        
        self.combo_list_view.setModel(self.model_dialog_combo)
        self.variant_list_view.setModel(self.model_dialog_variant)

        self.combo_list_view.horizontalHeader().setStretchLastSection(True)
        self.variant_list_view.horizontalHeader().setStretchLastSection(True)

        input_layout = QHBoxLayout()
        input_layout.addLayout(combo_layout)
        input_layout.addLayout(variant_layout) 

        result_layout = QVBoxLayout()
        self.combo_displayer = QLabel("<i><span style='color: red'>Chưa chọn combo</span></i>")
        self.variant_displayer = QLabel("<i><span style='color: yellow'>Chưa chọn loại combo (Có thể bỏ trống)</span></i>")
        result_layout.addWidget(QLabel("Cặp combo và loại combo được chọn:"))
        result_layout.addWidget(self.combo_displayer)
        result_layout.addWidget(self.variant_displayer)
        self.cv_dup_indicator = QLabel()
        self.cv_dup_indicator.setVisible(False)
        result_layout.addWidget(self.cv_dup_indicator)

        cfm_buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(cfm_buttons)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(result_layout)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

        # Thiết lập kết nối
        self.init_signal()
    
    def init_signal(self):
        self.combo_list_view.clicked.connect(self.show_selected_combo)
        self.combo_list_view.clicked.connect(self.duplicated_cv_indicator)
        self.variant_list_view.clicked.connect(self.show_selected_variant)
        self.variant_list_view.clicked.connect(self.duplicated_cv_indicator)
        self.combo_filter.textChanged.connect(self.combo_filter_refresh_view)
        self.variant_filter.textChanged.connect(self.variant_filter_refresh_view)

    def duplicated_cv_indicator(self):
        current_pair = (self.selected_combo_key, self.selected_variant_key)
        if current_pair in self.added_combo_variant:
            self.cv_dup_indicator.setVisible(True)
            self.cv_dup_indicator.setText(f"<b>\u274c Combo này đã được tạo trong cơ sở dữ liệu</b>")
        elif not self.selected_combo_key:
            self.cv_dup_indicator.setVisible(True)
            self.cv_dup_indicator.setText(f"<b>\u274c Tên combo không được để trống!</b>")
        else:
            self.cv_dup_indicator.setVisible(True )
            self.cv_dup_indicator.setText(f"<b>\u2705 Có thể tạo combo này!</b>")

    def combo_filter_refresh_view(self, text):
        search_text = text.strip().lower()
        filtered_combo = [
            combo for combo in self.available_combos
            if search_text in combo["combo_name"].lower()
        ]
        self.model_dialog_combo.refresh_data(filtered_combo)

    def variant_filter_refresh_view(self, text):
        search_text = text.strip().lower()
        filtered_variant = [
            variant for variant in self.available_variants
            if search_text in variant["variant_name"].lower()
        ]
        self.model_dialog_variant.refresh_data(filtered_variant)

    def show_selected_combo(self, index):
        index_num = index.row()
        combo_data = self.model_dialog_combo._data

        selected_combo = combo_data[index_num]

        # Lưu combo đã click vào một biến
        clicked_key = selected_combo.get("combo_key") 
        if self.selected_combo_key == clicked_key:
            self.selected_combo_key = None
            self.combo_displayer.setText("<i><span style='color: red'>Chưa chọn combo</span></i>")
            self.combo_list_view.clearSelection()
        else:
            self.selected_combo_key = clicked_key
            name = selected_combo.get("combo_name")
            self.combo_displayer.setText(f"<b><span style='color: green'>Tên combo: </span></b> {name}")

    def show_selected_variant(self, index):
        index_num = index.row()
        variant_data = self.model_dialog_variant._data

        selected_variant = variant_data[index_num]
        # Lưu variant đã click vào một biến
        clicked_key = selected_variant.get("variant_key") 
        if self.selected_variant_key == clicked_key:
            self.selected_variant_key = None
            self.variant_displayer.setText("<i><span style='color: yellow'>Chưa chọn loại combo (Có thể bỏ trống)</span></i>")
            self.variant_list_view.clearSelection()
        else:
            self.selected_variant_key = clicked_key
            name = selected_variant.get("variant_name")
            self.variant_displayer.setText(f"<b><span style='color: green'>Phân loại combo:</span></b> {name}")