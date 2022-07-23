if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()  # 名字根据.py文件前面的class名字调整
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
