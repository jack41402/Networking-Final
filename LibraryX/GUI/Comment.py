# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project


from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QWidget


class CommentPanel(QWidget):
	def __init__(self, author, message, timestamp):
		super().__init__()
		loadUi("UI/comment.ui", self)

		# set data
		self.Author_label.setText(author)
		self.Message_label.setText(message)
		self.Timestamp_label.setText(timestamp)