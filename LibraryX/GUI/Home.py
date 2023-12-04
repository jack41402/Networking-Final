# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project

import datetime
import logging
import os.path
import re
import sys
from PyQt6 import QtGui
from PyQt6.QtGui import QIcon
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt, QSize, QEvent, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QMessageBox, QSpacerItem, QSizePolicy, QListWidgetItem, \
    QFileDialog, QApplication, QHBoxLayout, QPushButton, QLabel
from LibraryX.Extra import Audio, VoIP
from LibraryX.GUI import Comment, File, Friend


class HomePanel(QWidget):
    pop_msgbox_signal = pyqtSignal(str, str, str)

    def __init__(self, api):
        super().__init__()
        loadUi("UI/home.ui", self)

        self.api = api
        self.current_item = None
        self.app = QApplication(sys.argv)
        self.logger = logging.getLogger(__name__)
        self.is_calling = False
        self.audio_agent = Audio.AudioUtils()  # epic audio recording agent
        self.temporary_received_audiofile = None  # temporary received audio file from friend
        self.temporary_record_audiofile = None  # temporary self recorded audio file
        self.audio_recording = False  # audio recording status

        # Widget setup
        self.Comment_textEdit.installEventFilter(self)
        self.friend_widget = Friend.FriendPanel()
        self.scroll_area_widget = None
        self.scroll_area_layout = None

        # connect signal
        self.pop_msgbox_signal.connect(self.pop_yesnomessagebox)
        self.Friend_Button.clicked.connect(self.goto_friend)
        self.friend_widget.friend_signal.connect(self.search_friend)
        self.friend_widget.Add_Friend_listWidget.itemClicked.connect(self.send_friend_request)
        self.Send_Button.clicked.connect(self.send_message)
        self.EmbedFile_Button.clicked.connect(self.send_file)
        self.VoiceCall_Button.clicked.connect(self.voice_call)
        self.Friend_listWidget.itemClicked.connect(self.render_message)
        self.AudioRecord_Button.clicked.connect(self.record_audio_message)

        # setup the VoIP function
        self.voip = VoIP.VoIP("127.0.0.1", self.api, self.pop_msgbox_signal)  # for local test
        # self.voip = VoIP.VoIP(Identity.local_intranet_ip()) # for intranet
        # connect voip signal


    # Popup a message box with only "OK option"
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

    # Popup a yes/no message box with "Yes / No" option, return True when Yes, False when No
    def pop_yesnomessagebox(self, banner, title, text):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(banner)
        msg_box.setText(title)
        msg_box.setInformativeText(text)
        msg_box.setIcon(QMessageBox.Icon.Information)  # Set an icon
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        # Adjusting the size using QSpacerItem
        spacer = QSpacerItem(200, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout = msg_box.layout()
        layout.addItem(spacer, layout.rowCount(), 0, 1, layout.columnCount())

        result = msg_box.exec()
        if result == QMessageBox.StandardButton.Yes:
            self.is_calling = True
            self.VoiceCall_Button.setText("Hang\nUp !")
            self.logger.info("User pressed True")
            return self.voip.ANSWER_OR_REJECT_SIGNAL.emit(True)

        elif result == QMessageBox.StandardButton.No:
            self.logger.info("User pressed False")
            return self.voip.ANSWER_OR_REJECT_SIGNAL.emit(False)

    # maybe implement a user setting panel if we have time
    def goto_friend(self):
        self.friend_widget.Add_Friend_listWidget.clear()
        self.get_friend_request()
        self.friend_widget.show()
        return

    def search_friend(self):
        try:
            username = self.friend_widget.Search_lineEdit.text()
            self.friend_widget.Search_lineEdit.setText("")
            result = self.api.find_friend(self.api.user_id, username)
            self.logger.info(f"Search user {username} results: {result}")
            for row in result:
                item = QListWidgetItem(row[1])
                item.setData(Qt.ItemDataRole.UserRole, row)
                item.setFont(QtGui.QFont("Arial", 12))  # Set font and size
                item.setSizeHint(QSize(100, 25))
                self.friend_widget.Add_Friend_listWidget.addItem(item)
        except Exception as e:
            self.logger.error(f'Other exception in Home.search_friend: {e}')

    def accept_friend_request(self):
        try:
            button = self.app.sender()
            friend_id = button.property("user_id")
            self.api.send_friend_request(self.api.user_id, friend_id, 'A')
            self.api.send_friend_request(friend_id, self.api.user_id, 'A')
            self.get_friend_request()
            self.friend_list()
        except Exception as e:
            self.logger.error(f'Other exception in Home.accept_friend_request: {e}')

    def reject_friend_request(self):
        try:
            button = self.app.sender()
            friend_id = button.property("user_id")
            self.api.send_friend_request(friend_id, self.api.user_id, 'R')
            self.get_friend_request()
        except Exception as e:
            self.logger.error(f'Other exception in Home.reject_friend_request: {e}')

    def get_friend_request(self):
        try:
            self.friend_widget.Friend_Request_listWidget.clear()
            user_request, friend_request = self.api.find_friend_request(self.api.user_id)
            for request in user_request:
                friend_info = self.api.find_user_id(request[2])[0]
                item = QListWidgetItem(f"{friend_info[1]} (Waiting...)")
                item.setData(Qt.ItemDataRole.UserRole, friend_info)
                item.setFont(QtGui.QFont("Arial", 12))  # Set font and size
                item.setSizeHint(QSize(100, 25))
                self.friend_widget.Friend_Request_listWidget.addItem(item)
            for request in friend_request:
                friend_info = self.api.find_user_id(request[1])[0]

                item = QListWidgetItem()
                item_widget = QWidget()
                line_text = QLabel(friend_info[1])

                accept_button = QPushButton("Accept")
                accept_button.setProperty("user_id", friend_info[0])
                accept_button.clicked.connect(self.accept_friend_request)

                reject_button = QPushButton("Reject")
                reject_button.setProperty("user_id", friend_info[0])
                reject_button.clicked.connect(self.reject_friend_request)

                item_layout = QHBoxLayout()
                item_layout.addWidget(line_text)
                item_layout.addWidget(accept_button)
                item_layout.addWidget(reject_button)
                item_widget.setLayout(item_layout)
                item.setSizeHint(item_widget.sizeHint())
                self.friend_widget.Friend_Request_listWidget.addItem(item)
                self.friend_widget.Friend_Request_listWidget.setItemWidget(item, item_widget)
        except Exception as e:
            self.logger.error(f'Other exception in Home.get_friend_request: {e}')

    def send_friend_request(self, item):
        try:
            friend = item.data(Qt.ItemDataRole.UserRole)
            friend_id = friend[0]
            self.api.send_friend_request(self.api.user_id, friend_id, 'P')
        except Exception as e:
            self.logger.error(f'Other exception in Home.send_friend_request: {e}')

    # start record an audio message
    def record_audio_message(self):
        if not self.audio_recording:  # if not recording now, start recording
            self.audio_recording = True
            self.audio_agent.start_record()

            # change the text on audio icon
            self.AudioRecord_Button.setText("Stop\nRecord")
            return

        else:  # if recording now, stop recording
            self.audio_recording = False
            self.audio_agent.stop_record()

            # save the audio filepath to attribute for further sending
            self.temporary_record_audiofile = self.audio_agent.tempfile
            self.AudioRecord_Button.setText("Audio\nRecord")
            return


    # play a received audio message
    def play_audio_message(self):
        return


    # embed a file to message in order to send to the receiver
    def send_file(self):
        try:
            self.logger.info("User trying to embed an external file to the message")
            if self.current_item is not None:
                file_paths, filetype = QFileDialog.getOpenFileNames()
                self.logger.info(f"Open filename {file_paths}, filetype {filetype}.")
                author = self.api.username
                friend = self.current_item.data(Qt.ItemDataRole.UserRole)
                reply_id = friend["user_id"]

                for file_path in file_paths:
                    if os.path.exists(file_path):
                        content = re.split(r"/", file_path)[-1]
                        self.api.send({"author": author, "content": content, "reply_id": reply_id, "is_file": True})
                        self.api.send_file(file_path)
                    else:
                        self.logger.error(f"CAN'T FIND FILE PATH OF {file_path}")
                self.render_message(self.current_item)
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f'Other exception in Home.send_file: {e}')


    # download file from server
    def receive_file(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "All Files (*);;Text Files (*.txt)")
            if file_path:
                self.logger.info(f"File path selected: {file_path}")
                button = self.app.sender()
                file_id = button.property("comment_id")
                self.api.receive_file(file_path, file_id)
        except Exception as e:
            self.logger.error(f'Other exception in Home.receive_file: {e}')


    # send the text message to server
    def send_message(self, is_file):
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


    # send the audio message to server
    def send_audio_message(self, audio_filepath):
        return

    # re-render all the msg in a chat
    def render_message(self, item):
        try:
            self.current_item = item
            friend = item.data(Qt.ItemDataRole.UserRole)
            friend_name = friend["username"]
            friend_id = friend["user_id"]

            self.ReplyUser_label.setText(friend_name)
            self.VoiceCall_Button.setProperty("user_id", friend_id)
            self.logger.info("Trying to re-render all message from a chat")
            self.scroll_area_widget = QWidget()
            self.scroll_area_layout = QVBoxLayout()
            self.scroll_area_layout.setSpacing(0)

            comments = self.api.get_comment(self.api.user_id, friend_id)
            for comment in comments:
                font = QtGui.QFont()
                today = datetime.date.today()
                time_delta = datetime.timedelta(days=1)

                comment_id = comment[0]
                is_file = comment[3]
                comment_author_id = comment[4]
                comment_author = self.api.username if comment_author_id == self.api.user_id else friend["username"]
                comment_time = datetime.datetime.strptime(str(comment[2]), '%Y%m%dT%H:%M:%S')
                if comment_time.date() == today:
                    comment_time = comment_time.strftime("Today %H:%M")
                elif comment_time.date() == today - time_delta:
                    comment_time = comment_time.strftime("Yesterday %H:%M")
                else:
                    comment_time = comment_time.strftime("%Y/%M/%d %H:%M")

                if is_file:
                    filename = comment[1]
                    form = File.FilePanel(comment_author, comment_time, filename)
                    font.setPointSize(12)
                    form.File_Button.setFont(font)
                    form.File_Button.setProperty("comment_id", comment_id)
                    form.File_Button.clicked.connect(self.receive_file)
                else:
                    comment_content = comment[1]
                    form = Comment.CommentPanel(comment_author, comment_time, comment_content)
                    form.Comment_label.setFont(font)
                font.setPointSize(9)
                form.Time_label.setFont(font)
                font.setBold(True)
                form.Author_label.setFont(font)
                form.setProperty("comment_id", comment_id)

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
            self.Friend_listWidget.clear()
            friends = self.api.get_friend(self.api.user_id)
            self.logger.info(f"Friend List: {friends}")
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

        # giveup
        return

    # user attempt to make a audio call
    def voice_call(self):
        try:
            if not self.is_calling:
                self.is_calling = True
                self.VoiceCall_Button.setText("Hang\nUp !")
                self.logger.info("User attempt to make an audio call")
                button = self.app.sender()
                user_id = button.property("user_id")
                ip, port = self.api.find_directory(user_id)
                # query server for the receiver IP:ringtong_port
                # port can only be int
                self.voip.dial(ip, port)

            else:
                self.is_calling = False
                self.VoiceCall_Button.setText("Voice\nCall !")
                self.voip.hangup()

            return

        except Exception as e:
            print(e.__traceback__.tb_lineno)
            self.logger.error(f'Other exception in Home.voice_call: {e}')

    # bind return and enter key to send button
    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.Type.KeyPress and (
                    event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter):
                if self.Comment_textEdit.hasFocus() and self.Comment_textEdit.toPlainText() != "":
                    self.Send_Button.click()
            return super().eventFilter(obj, event)
        except Exception as e:
            self.logger.error(f'Other exception in Home.eventFilter: {e}')

    def closeEvent(self, event):
        self.api.delete_directory(self.api.user_id)
        event.accept()
