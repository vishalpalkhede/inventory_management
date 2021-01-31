################################################################################
##
## BY: WANDERSON M.PIMENTA
## PROJECT MADE WITH: Qt Designer and PySide2
## V: 1.0.0
##
## This project can be used freely for all uses, as long as they maintain the
## respective credits only in the Python scripts, any information in the visual
## interface (GUI) can be modified without any implication.
##
## There are limitations on Qt licenses if you want to use your products
## commercially, I recommend reading them on the official website:
## https://doc.qt.io/qtforpython/licenses.html
##
################################################################################

import sys
import platform
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PySide2.QtWidgets import *
import sqlite3
import re

# GUI FILE
from app_modules import *


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.database_connection()

        print('System: ' + platform.system())
        print('Version: ' + platform.release())

        UIFunctions.removeTitleBar(True)

        self.setWindowTitle('Main Window - D.S. Bakers')
        UIFunctions.labelTitle(self, 'Main Window - D.S. Bakers')
        UIFunctions.labelDescription(self, 'Page')

        startSize = QSize(1000, 720)
        self.resize(startSize)
        self.setMinimumSize(startSize)
        # UIFunctions.enableMaximumSize(self, 500, 720)

        self.ui.btn_toggle_menu.clicked.connect(lambda: UIFunctions.toggleMenu(self, 220, True))

        self.ui.stackedWidget.setMinimumWidth(20)
        UIFunctions.addNewMenu(self, "Sales", "btn_sales", "url(:/16x16/icons/16x16/cil-cart.png)", True)
        UIFunctions.addNewMenu(self, "Items", "btn_items", "url(:/16x16/icons/16x16/cil-notes.png)", True)
        UIFunctions.addNewMenu(self, "Stock", "btn_stock", "url(:/16x16/icons/16x16/cil-layers.png)", True)
        UIFunctions.addNewMenu(self, "History", "btn_history", "url(:/16x16/icons/16x16/cil-history.png)", True)

        UIFunctions.selectStandardMenu(self, "btn_sales")

        self.ui.stackedWidget.setCurrentWidget(self.ui.page_sales)
        self.ui.pushButton_submit.clicked.connect(lambda: self.to_database("sales"))
        self.ui.pushButton_search.clicked.connect(lambda: self.to_database("history"))
        self.ui.pushButton_add.clicked.connect(lambda: self.render_page("add_item"))
        self.ui.listWidget_products.itemDoubleClicked.connect(lambda: self.render_page("stock"))
        self.params = []
        self.ui.pushButton_updateStock.clicked.connect(lambda: self.to_database("update_stock", self.params))
        self.update_product_list()
        self.ui.pushButton_addItem.clicked.connect(lambda: self.to_database("add_item"))

        UIFunctions.userIcon(self, "DS", "", True)

        def moveWindow(event):
            # IF MAXIMIZED CHANGE TO NORMAL
            if UIFunctions.returStatus() == 1:
                UIFunctions.maximize_restore(self)

            # MOVE WINDOW
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        self.ui.frame_label_top_btns.mouseMoveEvent = moveWindow

        UIFunctions.uiDefinitions(self)

        self.ui.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.show()

    def Button(self):
        # GET BT CLICKED
        btnWidget = self.sender()

        if btnWidget.objectName() == "btn_sales":
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_sales)
            UIFunctions.resetStyle(self, "btn_sales")
            UIFunctions.labelPage(self, "Sales")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

        if btnWidget.objectName() == "btn_items":
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_items)
            UIFunctions.resetStyle(self, "btn_items")
            UIFunctions.labelPage(self, "Products")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

        if btnWidget.objectName() == "btn_stock":
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_stock)
            UIFunctions.resetStyle(self, "btn_stock")
            UIFunctions.labelPage(self, "Stocks")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

        if btnWidget.objectName() == "btn_history":
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_history)
            UIFunctions.resetStyle(self, "btn_history")
            UIFunctions.labelPage(self, "History")
            btnWidget.setStyleSheet(UIFunctions.selectMenu(btnWidget.styleSheet()))

    def update_product_list(self):
        product_list = self.to_database("get_products")
        self.ui.listWidget_products.clear()
        self.ui.comboBox_product.clear()

        for product in product_list:
            self.ui.comboBox_product.addItem(str(product[0]))
        for product in product_list:
            item = QListWidgetItem("Product: " + product[0] + "\nStock: " + str(product[1]))
            self.ui.listWidget_products.addItem(item)
            item.setData(1, product[0] + ":" + str(product[1]))
        self.ui.listWidget_products.clearSelection()


    ## ==> END ##
    def to_database(self, type1, params=None):
        if type1 == "sales":

            product = self.ui.comboBox_product.currentText()
            quantity = self.ui.lineEdit_quantity.text()
            price = self.ui.lineEdit_price.text()
            date = self.ui.dateEdit_sales.text()
            date = re.split("/", date)
            date = date[2]+"-"+date[1]+"-"+date[0]
            measure = self.ui.comboBox_measure1.currentText()
            msg = QMessageBox()
            msg.setWindowTitle("Confirmation")
            msg.setText("Add Product:"+product+" Quantity:"+quantity+" "+ measure + "Price:"+price+" Date:"+date+" to database?")
            msg.setStandardButtons(QMessageBox.Cancel|QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)
            if product=="Products":
                msg = QMessageBox()
                msg.setWindowTitle("Error")
                msg.setText("Please select product")
                x = msg.exec_()
                return 0
            def button_clicked(i):
                print(i.text())
                if i.text() == "OK":
                    sold_item = (str(product), quantity, price, measure)
                    query = "INSERT INTO sales VALUES(?, ?, ?, date('"+date+"'), ?)"
                    self.cursor.execute(query, sold_item)
                    query = "SELECT stock FROM products WHERE product='"+str(product)+"'"
                    stock = self.cursor.execute(query).fetchall()
                    remaining_stock = stock[0][0] - int(quantity)
                    query = "UPDATE products SET stock="+str(remaining_stock)+" WHERE product='"+str(product)+"'"
                    self.cursor.execute(query)
                    self.update_product_list()
                    self.conn.commit()
                    msg = QMessageBox()
                    msg.setWindowTitle("Stock Remained")
                    msg.setText("Remaining Stock of Product:"+str(product)+" is "+str(remaining_stock))
                    x = msg.exec_()
                if i.text() == "&Cancel":
                    msg = QMessageBox()
                    msg.setWindowTitle("Operation Canceled")
                    msg.setText("Operation Canceled")
                    x = msg.exec_()

            msg.buttonClicked.connect(button_clicked)
            x = msg.exec_()
        if type1 == "history":
            fromDate = self.ui.dateEdit_fromDate.text()
            toDate = self.ui.dateEdit_toDate.text()
            fromDate = re.split("/", fromDate)
            toDate = re.split("/", toDate)
            fromDate = fromDate[2]+"-"+fromDate[1]+"-"+fromDate[0]
            toDate = toDate[2]+"-"+toDate[1]+"-"+toDate[0]
            query = "SELECT * FROM sales WHERE date BETWEEN date('"+fromDate+"') AND date('"+toDate+"')"
            data = self.cursor.execute(query).fetchall()
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_historyResult)
            UIFunctions.labelPage(self, "History->Result")
            self.ui.page_historyResult.setStyleSheet(UIFunctions.selectMenu(self.ui.page_historyResult.styleSheet()))
            count = len(data)
            self.ui.tableWidget_history
            total = ["TOTAL",0,0,0,""]
            self.ui.tableWidget_history.clear()
            for i in range(count+1):
                self.ui.tableWidget_history.insertRow(i)
                for j in range(5):
                    if i < count:
                        if j == 1:
                            if data[i][4] == 'Kilogram':
                                total[1] = total[1] + data[i][j]
                                item = QTableWidgetItem(str(data[i][j])+' kg')
                                self.ui.tableWidget_history.setItem(i, j, item)
                            if data[i][4] == 'Pieces':
                                total[2] = total[2] + data[i][j]
                                item = QTableWidgetItem(str(data[i][j])+' pics')
                                self.ui.tableWidget_history.setItem(i, j+1, item)
                        if j == 2:
                            total[3] = total[3] + data[i][j]
                            item = QTableWidgetItem('Rs.'+str(data[i][j]))
                            self.ui.tableWidget_history.setItem(i, j + 1, item)
                        if j > 2:
                            item = QTableWidgetItem(str(data[i][j]))
                            self.ui.tableWidget_history.setItem(i, j+1, item)
                        if j < 1:
                            item = QTableWidgetItem(str(data[i][j]))
                            self.ui.tableWidget_history.setItem(i, j, item)
                    if i == count:
                        if j == 1:
                            item = QTableWidgetItem(str(total[j])+' kg')
                            self.ui.tableWidget_history.setItem(i, j, item)
                        elif j == 2:
                            item = QTableWidgetItem(str(total[j]) + ' pics')
                            self.ui.tableWidget_history.setItem(i, j, item)
                        elif j == 3:
                            item = QTableWidgetItem('Rs.'+str(total[j]))
                            self.ui.tableWidget_history.setItem(i, j, item)
                        else:
                            item = QTableWidgetItem(str(total[j]))
                            self.ui.tableWidget_history.setItem(i, j, item)
        if type1 == "add_item":
            msg = QMessageBox()
            msg.setWindowTitle("Add Item")
            try:
                item = (str(self.ui.lineEdit_itemName.text()), 0, str(self.ui.comboBox_measure.currentText()))
                query = "INSERT INTO products VALUES(?, ?, ?)"
                self.cursor.execute(query, item)
                self.conn.commit()
                msg.setText("Item successfully added")
                msg.setStandardButtons(QMessageBox.Ok)
                self.update_product_list()
                x = msg.exec_()
            except:
                msg.setText("Item Already exist")
                msg.setStandardButtons(QMessageBox.Ok)
                x = msg.exec_()
        if type1 == "get_products":
            query = "SELECT * from products"
            return self.cursor.execute(query).fetchall()
        if type1 == "update_stock":
            stock = int(params[1]) + int(self.ui.lineEdit_updateStock.text())
            msg = QMessageBox()
            msg.setWindowTitle("Update Stock")
            msg.setText("Update Product:"+params[0]+" stock to Stock:"+str(stock)+"?")
            msg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)

            def clicked_button(i):
                print(i.text())
                if i.text()=="OK":
                    query = "update products set stock=" + str(stock) + " where product='" + params[0] + "'"
                    self.cursor.execute(query)
                    self.conn.commit()
                    self.update_product_list()
                    msg = QMessageBox()
                    msg.setWindowTitle("Stock Updated")
                    msg.setText("Stock updated successfully")
                    x = msg.exec_()
                else:
                    msg = QMessageBox()
                    msg.setWindowTitle("Operation Canceled")
                    msg.setText("Operation is canceled")
                    x = msg.exec_()
            msg.buttonClicked.connect(clicked_button)
            x = msg.exec_()

    def render_page(self, page):
        if page == "add_item":
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_addItem)
            UIFunctions.labelPage(self, "Product->Add")
            self.ui.page_addItem.setStyleSheet(UIFunctions.selectMenu(self.ui.page_addItem.styleSheet()))
            
        if page == "stock":
            data = self.ui.listWidget_products.currentItem().data(1)
            data = re.split(":", data)
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_stockUpdate)
            UIFunctions.labelPage(self, "Stocks->Update")
            self.ui.label_currentStock.setText("Current Stock:  " + str(data[1]))
            self.ui.label_stockProduct.setText("Product:  " + data[0])
            self.params = []
            self.params.append(data[0])
            self.params.append(data[1])

    def database_connection(self):
        self.conn = sqlite3.connect("bakery.db")
        products_table = "CREATE TABLE IF NOT EXISTS products('product' TEXT, 'stock' INT, measure TEXT, PRIMARY KEY(product))"
        sales_table = "CREATE TABLE IF NOT EXISTS sales('product' TEXT REFERENCES products(product), 'quantity' INT, 'amount' INT, 'date' DATE, measure TEXT)"
        self.cursor = self.conn.cursor()
        self.cursor.execute(products_table)
        self.cursor.execute(sales_table)

    ########################################################################
    ## START ==> APP EVENTS
    ########################################################################

    ## EVENT ==> MOUSE DOUBLE CLICK
    ########################################################################
    def eventFilter(self, watched, event):
        if watched == self.le and event.type() == QtCore.QEvent.MouseButtonDblClick:
            print("pos: ", event.pos())
    ## ==> END ##

    ## EVENT ==> MOUSE CLICK
    ########################################################################
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()
        if event.buttons() == Qt.LeftButton:
            print('Mouse click: LEFT CLICK')
        if event.buttons() == Qt.RightButton:
            print('Mouse click: RIGHT CLICK')
        if event.buttons() == Qt.MidButton:
            print('Mouse click: MIDDLE BUTTON')
    ## ==> END ##

    ## EVENT ==> KEY PRESSED
    ########################################################################
    def keyPressEvent(self, event):
        print('Key: ' + str(event.key()) + ' | Text Press: ' + str(event.text()))
    ## ==> END ##

    ## EVENT ==> RESIZE EVENT
    ########################################################################
    def resizeEvent(self, event):
        self.resizeFunction()
        return super(MainWindow, self).resizeEvent(event)

    def resizeFunction(self):
        print('Height: ' + str(self.height()) + ' | Width: ' + str(self.width()))
    ## ==> END ##

    ########################################################################
    ## END ==> APP EVENTS
    ############################## ---/--/--- ##############################

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeui.ttf')
    QtGui.QFontDatabase.addApplicationFont('fonts/segoeuib.ttf')
    window = MainWindow()
    sys.exit(app.exec_())
