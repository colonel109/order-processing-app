from PySide6.QtSql import QSqlQuery

def execute_query(sql):
    query = QSqlQuery()
    query.exec(sql)