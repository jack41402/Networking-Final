# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project
from PyQt6.uic import loadUi
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QWidget
import logging


class RegisterPanel(QWidget):
    register_signal = pyqtSignal(int)

    def __init__(self, api):
        super().__init__()
        loadUi("UI/register.ui", self)
        self.api = api
        self.logger = logging.getLogger(__name__)

        self.Register_button.clicked.connect(self.register)

    def register(self):
        try:
            username = self.Username_lineEdit.text()
            password = self.Password_lineEdit.text()
            confirm_password = self.Confirm_Password_lineEdit.text()
            register_status = self.api.register(username, password, confirm_password)
            self.register_signal.emit(register_status)
        # you can use register_status to determine the message box
        except Exception as e:
            self.logger.error(f'Other exception in RegisterPanel.register: {e}')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.Register_button.click()