# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project


from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QWidget
import logging


class RegisterPanel(QWidget):
	def __init__(self, api):
		super().__init__()
		loadUi("UI/register.ui", self)
		self.api = api
		self.logger = logging.getLogger(__name__)
