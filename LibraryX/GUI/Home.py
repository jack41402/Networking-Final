# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project

import datetime
import logging
from PyQt6 import QtGui
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt, QSize, QEvent
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QMessageBox, QSpacerItem, QSizePolicy, QListWidgetItem
from LibraryX.Extra import Audio
from LibraryX.GUI import Comment


class HomePanel(QWidget):
    def __init__(self, api):
        super().__init__()
        loadUi("UI/home.ui", self)

        self.api = api
        self.current_item = None
        self.logger = logging.getLogger(__name__)
        self.audio_agent = Audio.AudioUtils()  # epic audio recording agent
        self.temporary_received_audiofile = None  # temporary received audio file from friend
        self.temporary_recored_audiofile = None  # temporary self recorded audio file
        self.audio_recording = False  # audio recording status

        # connect signal
        self.Setting_Button.clicked.connect(self.goto_setting)
        self.Send_Button.clicked.connect(self.send_message)
        self.EmbedFile_Button.clicked.connect(self.embed_file)
        self.VoiceCall_Button.clicked.connect(self.voice_call)
        self.VideoCall_Button.clicked.connect(self.video_call)
        self.Friend_listWidget.itemClicked.connect(self.render_message)
        self.AudioRecord_Button.clicked.connect(self.record_audio_message)

        # Widget setup
        self.Comment_textEdit.installEventFilter(self)
        self.scroll_area_widget = None
        self.scroll_area_layout = None


    # Popup an messgae box with only "OK option"
    def pop_okmessagebox(self, banner, title, text):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(banner)
        msg_box.setText(title)
        msg_box.setInformativeText(text)
        msg_box.setIcon(QMessageBox.Icon.Information)  # Set an icon
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)

        # Adjusting the size using QSpacerItem
        spacer = QSpacerItem(200, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout = msg_box.layout()
        layout.addItem(spacer, layout.rowCount(), 0, 1, layout.columnCount())
        msg_box.exec()
        return

    # maybe implement a user setting panel if we have time
    def goto_setting(self):
        return

    # start record an audio message
    def record_audio_message(self):
        if not self.audio_recording:  # if not recording now, start recording
            self.audio_recording = True
            self.audio_agent.start_record()

            # change the text on audio icon
            self.AudioRecord_Button.setText("Stop\nRecord")
            return

        else:  # if recording now, stop recoridng
            self.audio_recording = False
            self.audio_agent.stop_record()

            # save the audio filepath to attribute for further sending
            self.temporary_recored_audiofile = self.audio_agent.tempfile
            self.AudioRecord_Button.setText("Audio\nRecord")
            return

    # play an received audio message
    def play_audio_message(self):
        return

    # embed a file to message in order to send to the receiver
    def embed_file(self):
        self.logger.info("User trying to embed an external file to the message")

        # I dont know how in detail but try to create a drag and drop area

        # then send that file via binary to the receiver
        return

    # send the text message to server
    def send_message(self):
        try:
            self.logger.info("Trying to send the message to server")
            if self.current_item is not None:
                author = self.api.username
                content = self.Comment_textEdit.toPlainText().strip()
                self.Comment_textEdit.clear()
                friend = self.current_item.data(Qt.ItemDataRole.UserRole)
                reply_id = friend["user_id"]

                self.api.send({"author": author, "content": content, "reply_id": reply_id, "is_file": False})

                self.render_message(self.current_item)
                return True
            else:
                self.logger.error(f'CURRENT ITEM IS NONE.')
                return False
        except Exception as e:
            self.logger.error(f'Other exception in Home.send_message: {e}')

    # send the audio messge to server
    def send_audio_message(self, audio_filepath):
        return

    # re-render all the msg in a chat
    def render_message(self, item):
        try:
            self.current_item = item
            self.logger.info("Trying to re-render all message from a chat")
            self.scroll_area_widget = QWidget()
            self.scroll_area_layout = QVBoxLayout()
            self.scroll_area_layout.setSpacing(0)

            friend = item.data(Qt.ItemDataRole.UserRole)
            comments = self.api.get_comment(self.api.user_id, friend["user_id"])
            for comment in comments:
                form = loadUi("UI/comment.ui")
                font = QtGui.QFont()
                today = datetime.date.today()
                time_delta = datetime.timedelta(days=1)

                comment_author_id = comment[4]
                comment_author = self.api.username if comment_author_id == self.api.user_id else friend["username"]
                comment_content = comment[1]
                comment_time = datetime.datetime.strptime(str(comment[2]), '%Y%m%dT%H:%M:%S')
                if comment_time.date() == today:
                    comment_time = comment_time.strftime("Today %H:%M")
                elif comment_time.date() == today - time_delta:
                    comment_time = comment_time.strftime("Yesterday %H:%M")
                else:
                    comment_time = comment_time.strftime("%Y/%M/%d %H:%M")

                form.Author_label.setText(comment_author)
                form.Time_label.setText(comment_time)
                form.Comment_label.setText(comment_content)

                font.setPointSize(9)
                form.Comment_label.setFont(font)
                font.setBold(True)
                form.Author_label.setFont(font)

                self.scroll_area_layout.addWidget(form)

            self.scroll_area_layout.addStretch()
            self.scroll_area_widget.setLayout(self.scroll_area_layout)
            self.scrollArea.setWidget(self.scroll_area_widget)
            return
        except Exception as e:
            self.logger.error(f'Other exception in Home.render_message: {e}')

    # render friend list
    def friend_list(self):
        try:
            friends = self.api.get_friend(self.api.user_id)
            self.logger.info(f"Friend List: {friends}")
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

    # bind return and enter key to send button
    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.Type.KeyPress and obj is self.Comment_textEdit:
                if (
                        event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter) and self.Comment_textEdit.hasFocus():
                    if self.Comment_textEdit.toPlainText() != "":
                        self.Send_Button.click()
            return super().eventFilter(obj, event)
        except Exception as e:
            self.logger.error(f'Other exception in Home.eventFilter: {e}')