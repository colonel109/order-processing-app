import pandas as pd
import sqlite3
from pathlib import Path

class OrderProcessor:
    def __init__(self, rename_dict: dict, dtype_dict: dict, db_path: Path):
        self.rename_dict = rename_dict
        self.dtype_dict = dtype_dict
        self.db_path = db_path
        self._data = pd.DataFrame()

    def order_processor(self, file_path: list):
        """
        Hàm này nhận danh sách các tệp được người dùng chọn từ dialog
        """
        dfs = []

        for file in file_path:
            try:
                df = pd.read_excel(file, dtype="str")

                df_rename = df.rename(columns=self.rename_dict)
                # Lấy danh sách tên các cột đã được chuẩn hoá
                expected_cols = [col for col in self.rename_dict.values()]

                if df_rename is not None and not df_rename.empty:

                    # Chỉ lấy những cột nằm trong danh sách tên cột được chọn
                    df_filtered = df_rename[[col for col in expected_cols if col in df_rename.columns]]
                    df_filtered['source_file'] = str(Path(file).stem)
                    dfs.append(df_filtered)

            except Exception as e:
                print(e)
        df_concat = pd.concat(dfs)
        for col, dtype in self.dtype_dict.items():
            if col in df_concat.columns:
                if dtype == "string":
                    df_concat[col] = df_concat[col].astype("string")
                elif dtype == "float":
                    df_concat[col] = pd.to_numeric(df_concat[col], errors="raise")
                elif dtype == "datetime":
                    df_concat[col] = pd.to_datetime(df_concat[col], errors="raise")

        self._data = df_concat
        return self._data

    def import_data(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                self._data.to_sql(
                    con = conn,
                    name="shopee_orders",
                    index=False,
                    if_exists='append'
                )
        except sqlite3.IntegrityError as ie:
            print(f"Xảy ra lỗi khi import {ie}")