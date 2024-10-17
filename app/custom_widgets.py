from PyQt5.QtWidgets import QComboBox
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt

class CheckableComboBox(QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

    def addItem(self, item):
        super(CheckableComboBox, self).addItem(item)
        index = self.model().index(self.count() - 1, 0)
        item = self.model().itemFromIndex(index)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Unchecked)

    def getCheckedItems(self):
        checkedItems = []
        for index in range(self.count()):
            item = self.model().item(index)
            if item.checkState() == Qt.Checked:
                checkedItems.append(item.text())
        return checkedItems