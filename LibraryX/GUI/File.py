# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project


from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QWidget


class FilePanel(QWidget):
    def __init__(self, author, time, filename):
        super().__init__()
        loadUi("UI/file.ui", self)

        # set data
        self.Author_label.setText(author)
        self.Time_label.setText(time)
        self.File_Button.setText(filename)
