import sys
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import (QMainWindow, QWidget,
        QPushButton, QLineEdit, QInputDialog, QDialog, QDialogButtonBox, QComboBox, QCalendarWidget,
        QFormLayout, QLabel, QSpinBox, QTreeView, QVBoxLayout, QHBoxLayout)


import myDatabase

class myDialog(QDialog):
    def __init__(self, l, title = "question"):
        super().__init__()
        super().setWindowTitle(title)
        layout = QFormLayout()
        super().setLayout(layout)

        for i, j in l:
            layout.addRow(QLabel(i), j)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        layout.addRow(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)


class MainWindow(QMainWindow):
    def __init__(self, dataBaseName):
        super().__init__()
        self._myDatabase = myDatabase.MyDataBase(dataBaseName)
        self._view = QTreeView()

        self._buttonAdd = QPushButton("Добавление рейтинга")
        self._buttonAdd.clicked.connect(self.addToDatabase)

        self._buttons = [(QPushButton("Запрос 1"), self.on1), (QPushButton("Запрос 2"), self.on2), (QPushButton("Запрос 3"), self.on3)]
        for i, j in self._buttons:
            i.clicked.connect(j)
        
        self.initUi()

    def initUi(self):
        self.setGeometry(300,300,200,200)
        self.setWindowTitle('7 Вариант (Магазины)')

        w = QWidget()

        mainLayout = QVBoxLayout()
        w.setLayout(mainLayout)

        self.setCentralWidget(w)

        mainLayout.addWidget(self._view)

        tmpLayout = QHBoxLayout()
        mainLayout.addLayout(tmpLayout)
        tmpLayout.addWidget(self._buttonAdd)
        for i, _ in self._buttons:
            tmpLayout.addWidget(i)


    def on1(self):
        str_disc = QLabel("Количество товара с наименованием X в поставках")
        l = [("Запрос: ", str_disc), ("Продукт: ", QComboBox())]
        l[1][1].addItems(self._myDatabase.products_in_supply())
        d = myDialog(l, "Первый запрос")
        if d.exec() == QDialog.Accepted:
            model = self._myDatabase.first(l[1][1].currentText())
            self.setModel(model)

    def on2(self):
        str_disc = QLabel("Адреса складов, работающих с магазинами,\n организации которых содержат подстроку X (например, «ИП»),\n отсортированные по цене товара")
        l = [("Запрос", str_disc), ("Подстрока в имени компании", QLineEdit())]
        d = myDialog(l, "Второй запрос")
        if d.exec() == QDialog.Accepted:
            model = self._myDatabase.second(l[1][1].text())
            self.setModel(model)

    def on3(self):
        str_disc = QLabel("Оценка товаров, наименования товаров и адреса магазинов,\n в которых работают кассиры с зарплатой меньше, чем X,\n поставки в которые ожидаются позднее даты Y")
        l = [("Запрос", str_disc), ("Зарплата меньше чем ", QSpinBox()), ("Позже даты", QCalendarWidget())]
        l[1][1].setMaximum(self._myDatabase.max_salary()+1)
        d = myDialog(l, "Третий запрос")
        if d.exec() == QDialog.Accepted:
            model = self._myDatabase.third(l[1][1].value(), l[2][1].selectedDate().toPyDate())
            self.setModel(model)

    def setModel(self, model):
        if model is None:
            return
        self._view.setModel(model)

    def addToDatabase(self):
        num, ok = QInputDialog.getInt(self, "Рейтинг (0-5)", "Введите рейтинг", 0, 0, 5)
        if not ok:
            return None
        l = [("Автор", QLineEdit()), ("Продукт :", QComboBox())]
        l[1][1].addItems(self._myDatabase.products()) 
        d = myDialog(l, "Добавление")
        if d.exec() == QDialog.Accepted:
            self._myDatabase.add(num, l[0][1].text(), l[1][1].currentText())


if __name__ == "__main__":
    app = QApplication(sys.argv)

    w = MainWindow("test.bd")
    w.show()

    sys.exit(app.exec_())