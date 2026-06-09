from PySide6.QtCore import QAbstractTableModel, Qt
from jedi.inference.compiled import value
from sqlalchemy import inspect

class ViewModel(QAbstractTableModel):
    def __init__(self, data, column_names, headers):
        super().__init__()
        self._data = data
        self._column_names = column_names
        self._headers = headers

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            row = self._data[index.row()]
            col = self._column_names[index.column()]
            val = row.get(col, "")
            return str(val)

    def rowCount(self, /, parent = ...):
        return len(self._data)

    def columnCount(self, /, parent = ...):
        return len(self._column_names)

    def headerData(self, section, orientation, role = Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return str(self._column_names[section])

        if orientation == Qt.Orientation.Vertical:
            return str(section + 1)

        return None