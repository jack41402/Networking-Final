# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project


import logging
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QWidget
from LibraryX.GUI import Comment


class HomePanel(QWidget):
	def __init__(self):
		super().__init__()
		loadUi("UI/home.ui", self)
		self.logger = logging.getLogger(__name__)

		# connect signal
		self.Send_Button.clicked.connect(self.post_comment)


	# send the comment to server
	def post_comment(self):
		self.logger.info("Trying to post the comment to server")

		return