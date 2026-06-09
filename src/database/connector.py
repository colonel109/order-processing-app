from PySide6.QtSql import QSqlDatabase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def connector(db_path):
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(str(db_path))
    print(f"Database path: {db_path}")
    if not db.open():
        print("Không thể kết nối tới cơ sở dữ liệu")
        return False

    print("Kết nối tới cơ sở dữ liệu thành công")

    engine = create_engine(f"sqlite:///{db_path}")
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    return session