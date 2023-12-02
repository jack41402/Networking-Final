# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project


import logging
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QWidget, QVBoxLayout
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
    def render_message(self):
        self.logger.info("Trying to re-render all message from a chat")
        self.scroll_area_widget = QWidget()
        self.scroll_area_layout = QVBoxLayout()
        self.scroll_area_layout.setSpacing(0)


        self.scroll_area_layout.addStretch()
        self.scroll_area_widget.setLayout(self.scroll_area_layout)
        self.scrollArea.setWidget(self.scroll_area_widget)
        # request server to receive previous conversation detail

        # itterate, and render all the received data into the scrollarea

        # lets do a dummy test for render
        return

    def friend_list(self):
        friends = self.api.get_friend()
        if friends is not None:
            for friend in friends:
                post = Post(row[0], row[1], row[2], row[3], row[4], self.client.user(row[4])[0][1])
                item = QListWidgetItem(post.title)
                item.setData(Qt.ItemDataRole.UserRole, post)
                item.setFont(QtGui.QFont("Arial", 12))  # Set font and size
                item.setSizeHint(QSize(100, 25))
                self.ForumWindow.Article_listWidget.addItem(item)


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
