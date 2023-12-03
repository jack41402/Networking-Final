# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project
import logging
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget


class LoginPanel(QWidget):
    login_signal = pyqtSignal(int)

    def __init__(self, api):
        super().__init__()
        loadUi("UI/login.ui", self)
        self.api = api
        self.logger = logging.getLogger(__name__)

        self.Login_button.clicked.connect(self.login)

    def login(self):
        try:
            username = self.Username_lineEdit.text()
            password = self.Password_lineEdit.text()
            login_status = self.api.login(username, password)
            self.login_signal.emit(login_status)
            # you can use login_status to determine the message box
        except Exception as e:
            self.logger.error(f'Other exception in LoginPanel.login: {e}')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.Login_button.click()
