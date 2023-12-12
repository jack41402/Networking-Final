# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project
import logging
import sys
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QApplication, QMainWindow
from LibraryX.GUI import Login, Register, Home
from LibraryX.API import RPC

SERVER_IP = "127.0.0.1"
SERVER_PORT = 6666


# DESC: The all-in-one class that handles everything
class MainWindow(QMainWindow):
    pageflip_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.api = RPC.Client(SERVER_IP, SERVER_PORT)
        self.api.start()

        self.display_panel = None  # reference to avoid instance deletion
        self.register_panel = Register.RegisterPanel(self.api)
        self.login_panel = Login.LoginPanel(self.api)
        self.home_panel = Home.HomePanel(self.api)

        # connect signal
        self.login_panel.Login_button.clicked.connect(self.goto_home)
        self.register_panel.Login_label.linkActivated.connect(self.goto_login)
        self.login_panel.Register_label.linkActivated.connect(self.goto_register)

        # default invoke
        self.goto_login()

    # display manager
    def __swicth_panel(self, panel, size):
        # hide previous widget
        if self.display_panel:
            self.display_panel.hide()

        # display new
        self.display_panel = panel
        self.display_panel.show()
        self.display_panel.setFixedSize(*size)
        return

    # page flip
    def goto_login(self):
        self.__swicth_panel(self.login_panel, (400, 300))
        return

    # page flip
    def goto_register(self):
        self.__swicth_panel(self.register_panel, (400, 350))
        return

    # page flip
    def goto_home(self):
        self.__swicth_panel(self.home_panel, (1000, 600))
        # self.api.insert_directory()
        self.home_panel.friend_list()
        self.home_panel.voip.setup()
        self.home_panel.Username_label.setText(self.api.username)
        return


def main():
    # configure the root logger
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] - %(message)s (%(name)s / %(funcName)s:%(lineno)d)',
    )

    # start application
    app = QApplication([])
    window = MainWindow()
    window.hide()
    sys.exit(app.exec())
    return


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    main()
