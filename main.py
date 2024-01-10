import os
import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget, QPushButton, QMessageBox

from UI.addEditCoffeeForm import Ui_MainWindow as addEditCoffeeFormMainWindow
from UI.main import Ui_mainWindow as mainMainWindow


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class AddChangeWindow(QMainWindow, addEditCoffeeFormMainWindow):
    def __init__(self, parent):
        self.parent = parent

        super().__init__()
        self.setupUi(self)

        self.pushButton.clicked.connect(self.add_or_change_table)

    def add_or_change_table(self):
        connect = sqlite3.connect(self.parent.db_file)
        cursor = connect.cursor()
        max_id = max(info[0] for info in cursor.execute("""SELECT * FROM coffee""").fetchall())
        id = self.spinBox_id.value()
        sort = self.lineEdit_sort.text()
        degree = self.lineEdit_degree.text()
        type = self.lineEdit_type.text()
        desc = self.plainTextEdit.toPlainText()
        price = self.spinBox_price.value()
        volume = self.spinBox_volume.value()
        if id == 0:
            # Add coffee.
            cursor.execute("""
                INSERT INTO coffee ("НАЗВАНИЕ СОРТА", "СТЕПЕНЬ ОБЖАРКИ", "МОЛОТЫЙ/В ЗЕРНАХ",
                                   "ОПИСАНИЕ ВКУСА", "ЦЕНА (в рублях)", "ОБЪЕМ УПАКОВКИ (в граммах)")
                VALUES (?, ?, ?, ?, ?, ?)
            """, (sort, degree, type, desc, price, volume))
        elif 0 < id <= max_id:
            # Update coffee.
            cursor.execute("""
                UPDATE coffee
                SET "НАЗВАНИЕ СОРТА" = ?, "СТЕПЕНЬ ОБЖАРКИ" = ?, "МОЛОТЫЙ/В ЗЕРНАХ" = ?,
                    "ОПИСАНИЕ ВКУСА" = ?, "ЦЕНА (в рублях)" = ?, "ОБЪЕМ УПАКОВКИ (в граммах)" = ?
                WHERE ID = ?
            """, (sort, degree, type, desc, price, volume, id))
        elif id > max_id:
            # Show a warning for an incorrect ID.
            QMessageBox.warning(self, "Ошибка", "Неверный ID. Введите корректный ID.")
        connect.commit()
        connect.close()
        self.parent.initLogic()


class CoffeeApp(QMainWindow, mainMainWindow):
    def __init__(self):
        self.connect = self.cursor = None
        self.db_file = self.get_database_path()

        super().__init__()
        self.setupUi(self)

        self.initDB()
        self.initLogic()
        self.add_change_window = AddChangeWindow(self)
        self.pushButton.clicked.connect(self.add_change_window.show)

    def get_database_path(self):
        # Check if running as a PyInstaller executable.
        if getattr(sys, 'frozen', False):
            # Return the path to the bundled database file.
            return os.path.join(os.path.dirname(sys.executable), 'data', 'coffee.sqlite')
        else:
            # Return the path to the database file in the source code.
            return os.path.abspath("data/coffee.sqlite")

    def initDB(self):
        if not os.path.isfile(self.db_file):
            self.connect = sqlite3.connect(self.db_file)
            self.cursor = self.connect.cursor()

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS coffee (
                    ID INTEGER PRIMARY KEY,
                    "НАЗВАНИЕ СОРТА" TEXT,
                    "СТЕПЕНЬ ОБЖАРКИ" TEXT,
                    "МОЛОТЫЙ/В ЗЕРНАХ" TEXT,
                    "ОПИСАНИЕ ВКУСА" TEXT,
                    "ЦЕНА (в рублях)" INTEGER,
                    "ОБЪЕМ УПАКОВКИ (в граммах)" INTEGER
                )
            """)

            self.cursor.execute("""
                INSERT INTO coffee ("НАЗВАНИЕ СОРТА", "СТЕПЕНЬ ОБЖАРКИ", "МОЛОТЫЙ/В ЗЕРНАХ", "ОПИСАНИЕ ВКУСА", "ЦЕНА (в рублях)", "ОБЪЕМ УПАКОВКИ (в граммах)")
                VALUES ('Arabica', 'Средняя', 'Молотый', 'Насыщенный и фруктовый вкус', 500, 250),
                       ('Robusta', 'Темная', 'В зернах', 'Сильный и горький вкус', 300, 500),
                       ('Liberica', 'Светлая', 'Молотый', 'Экзотический и сладкий вкус', 700, 100),
                       ('Ethiopian Yirgacheffe', 'Светлая', 'В зернах', 'Цветочный и фруктовый аромат', 800, 200)
            """)

            self.connect.commit()
            self.connect.close()

    def initLogic(self):
        self.tableWidget: QTableWidget
        self.pushButton: QPushButton

        self.connect = sqlite3.connect(self.db_file)
        self.cursor = self.connect.cursor()
        self.cursor.execute("SELECT * FROM coffee")
        data = self.cursor.fetchall()
        self.connect.close()

        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(len(data[0]))
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderLabels([info[0] for info in self.cursor.description])

        for row_index, row_data in enumerate(data):
            self.tableWidget.insertRow(row_index)
            for col_index, col_data in enumerate(row_data):
                self.tableWidget.setItem(row_index, col_index, QTableWidgetItem(str(col_data)))

        self.tableWidget.setColumnWidth(0, 1)
        self.tableWidget.setColumnWidth(1, 180)
        self.tableWidget.setColumnWidth(2, 160)
        self.tableWidget.setColumnWidth(3, 160)
        self.tableWidget.setColumnWidth(4, 240)
        self.tableWidget.setColumnWidth(5, 130)
        self.tableWidget.setColumnWidth(6, 230)

        self.connect.close()


if __name__ == "__main__":
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = CoffeeApp()
    ex.show()
    sys.exit(app.exec())
