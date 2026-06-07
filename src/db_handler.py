from PySide6.QtSql import QSqlDatabase

def db_connector(db_path):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(str(db_path))
    print(f"Database path: {db_path}")
    if not db.open():
        print("Không thể kết nối tới cơ sở dữ liệu")
        return False

    print("Kết nối tới cơ sở dữ liệu thành công")

    return True