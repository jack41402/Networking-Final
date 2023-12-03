# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QWidget


class FriendPanel(QWidget):
    friend_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        loadUi("UI/friend.ui", self)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.friend_signal.emit()