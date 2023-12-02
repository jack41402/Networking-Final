# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project
import datetime
import logging

from PyQt6 import QtGui
from PyQt6.QtCore import Qt, QSize
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidgetItem

from LibraryX.GUI import Comment


class HomePanel(QWidget):
    def __init__(self, api):
        super().__init__()
        loadUi("UI/home.ui", self)
        self.api = api
        self.logger = logging.getLogger(__name__)

        # connect signal
        self.Setting_Button.clicked.connect(self.goto_setting)
        self.Send_Button.clicked.connect(self.post_message)
        self.EmbedFile_Button.clicked.connect(self.embed_file)
        self.VoiceCall_Button.clicked.connect(self.voice_call)
        self.VideoCall_Button.clicked.connect(self.video_call)
        self.Friend_listWidget.itemClicked.connect(self.render_message)

        # Widget setup
        self.scroll_area_widget = None
        self.scroll_area_layout = None

    # maybe implement a user setting panel if we have time
    def goto_setting(self):
        return

    # embed a file to message in order to send to the receiver
    def embed_file(self):
        self.logger.info("User trying to embed an external file to the message")

        # I dont know how in detail but try to create a drag and drop area

        # then send that file via binary to the receiver
        return

    # send the message to server
    def post_message(self):
        self.logger.info("Trying to post the message to server")

        # make a request to server, sending the data in comment box

        # trigger the re-render of previous conversation
        self.render_message()
        return

    # re-render all the msg in a chat
    def render_message(self, item):
        try:
            self.logger.info("Trying to re-render all message from a chat")
            self.scroll_area_widget = QWidget()
            self.scroll_area_layout = QVBoxLayout()
            self.scroll_area_layout.setSpacing(0)

            friend = item.data(Qt.ItemDataRole.UserRole)
            comments = self.api.get_comment(self.api.user_id, friend["user_id"])
            for comment in comments:
                form_widget = QWidget()
                form = comment.Ui_Form()
                form.setupUi(form_widget)
                font = QtGui.QFont()

                comment_author = self.api.username if comment[3] == self.api.user_id else friend["username"]
                comment_content = comment[1]
                comment_time = datetime.datetime.strptime(str(comment[2]), '%Y%m%dT%H:%M:%S')

                form.Author_label.setText(comment_author)
                form.Comment_label.setText(comment_content)
                form.Time_label.setText(comment_time)

                font.setPointSize(9)
                form.Comment_label.setFont(font)
                font.setBold(True)
                form.Author_label.setFont(font)

                self.scroll_area_layout.addWidget(form_widget)

            self.scroll_area_layout.addStretch()
            self.scroll_area_widget.setLayout(self.scroll_area_layout)
            self.scrollArea.setWidget(self.scroll_area_widget)
            return
        except Exception as e:
            self.logger.error(f'Other exception in Home.render_message: {e}')

    def friend_list(self):
        try:
            friends = self.api.get_friend(self.api.user_id)
            if friends is not None:
                for friend in friends:
                    item = QListWidgetItem(friend["username"])
                    item.setData(Qt.ItemDataRole.UserRole, friend)
                    item.setFont(QtGui.QFont("Arial", 12))  # Set font and size
                    item.setSizeHint(QSize(100, 25))
                    self.Friend_listWidget.addItem(item)
        except Exception as e:
            self.logger.error(f'Other exception in Home.friend_list: {e}')

    # user attempt to make a video call
    def video_call(self):
        self.logger.info("User attempt to make a video call to receiver")

        # I have no fucking clue of how to do it
        return

    # user attempt to make a audio call
    def voice_call(self):
        self.logger.info("User attempt to make an audio call")

        # I have no idea of the implmentation of this too
        return
