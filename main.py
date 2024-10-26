import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QStackedWidget, QHBoxLayout, QFrame
from PyQt5.QtGui import QPalette, QColor
from screen.initial import WelcomeScreen
from screen.tes.tes import TeSScreen
from screen.elv import ELVScreen

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Thermodynamic Equilibrium Simulation')
        self.setFixedSize(800, 800)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        self.setPalette(palette)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        button_layout = QHBoxLayout()
        
        self.btn_welcome = QPushButton('Initial', self)
        self.btn_tes = QPushButton('TeS', self)
        self.btn_elv = QPushButton('ELV', self)

        self.set_button_style(self.btn_welcome, True)
        self.set_button_style(self.btn_tes, False)
        self.set_button_style(self.btn_elv, False)

        self.btn_welcome.clicked.connect(self.show_welcome_screen)
        self.btn_tes.clicked.connect(self.show_tes_screen)
        self.btn_elv.clicked.connect(self.show_elv_screen)

        button_layout.addWidget(self.btn_welcome)
        button_layout.addWidget(self.btn_tes)
        button_layout.addWidget(self.btn_elv)
        main_layout.addLayout(button_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        self.welcome_screen = WelcomeScreen()
        self.tes_screen = TeSScreen()
        self.elv_screen = ELVScreen()

        self.stacked_widget.addWidget(self.welcome_screen)
        self.stacked_widget.addWidget(self.tes_screen)
        self.stacked_widget.addWidget(self.elv_screen)

        self.show_welcome_screen()

    def set_button_style(self, button, is_selected):
        if is_selected:
            button.setStyleSheet("font-weight: bold;")
        else:
            button.setStyleSheet("font-weight: normal;")

    def show_welcome_screen(self):
        self.stacked_widget.setCurrentIndex(0)
        self.set_button_style(self.btn_welcome, True)
        self.set_button_style(self.btn_tes, False)
        self.set_button_style(self.btn_elv, False)

    def show_tes_screen(self):
        self.stacked_widget.setCurrentIndex(1)
        self.set_button_style(self.btn_welcome, False)
        self.set_button_style(self.btn_tes, True)
        self.set_button_style(self.btn_elv, False)

    def show_elv_screen(self):
        self.stacked_widget.setCurrentIndex(2)
        self.set_button_style(self.btn_welcome, False)
        self.set_button_style(self.btn_tes, False)
        self.set_button_style(self.btn_elv, True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())