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
import threading
from PyQt6 import QtGui
from PyQt6.QtGui import QIcon, QPixmap, QImage, QMovie
from PyQt6.uic import loadUi
from PyQt6.QtCore import Qt, QSize, QEvent, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QMessageBox, QSpacerItem, QSizePolicy, QListWidgetItem, \
    QFileDialog, QApplication, QHBoxLayout, QPushButton, QLabel
from LibraryX.Extra import Audio, VoIP
from LibraryX.GUI import Comment, File, Friend

temp_path = r"D:\GitHub\Networking-Final\File\temp"
max_width = 400
max_height = 300

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
            user_request, friend_request = self.api.get_friend_request(self.api.user_id)
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
            self.send_audio_message(self.temporary_record_audiofile)
            return

    # send the audio message to server
    def send_audio_message(self, audio_file_path):
        try:
            if self.current_item is not None:
                friend = self.current_item.data(Qt.ItemDataRole.UserRole)
                author_id = self.api.username
                reply_id = friend["user_id"]
                if os.path.exists(audio_file_path):
                    self.api.send_file(audio_file_path, author_id, reply_id)
                else:
                    self.logger.error(f"CAN'T FIND FILE PATH OF {audio_file_path}")
                self.render_message(self.current_item)
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f'Other exception in Home.send_audio_message: {e}')

    # play a received audio message
    def play_audio_message(self):
        button = self.app.sender()
        file_path = button.property("file_path")
        play_audio_thread = threading.Thread(target=self.audio_agent.play, args=(file_path,))
        play_audio_thread.start()
        # self.audio_agent.play(file_path)

    # embed a file to message in order to send to the receiver
    def send_file(self):
        try:
            self.logger.info("User trying to embed an external file to the message")
            if self.current_item is not None:
                file_paths, filetype = QFileDialog.getOpenFileNames()
                self.logger.info(f"Open filename {file_paths}, filetype {filetype}.")
                friend = self.current_item.data(Qt.ItemDataRole.UserRole)
                author_id = self.api.user_id
                reply_id = friend["user_id"]

                for file_path in file_paths:
                    if os.path.exists(file_path):
                        self.api.send_file(file_path, author_id, reply_id)
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
            button = self.app.sender()
            file_id = button.property("file_id")
            filename = button.property("filename")
            file_path, extension = QFileDialog.getSaveFileName(self, "Save File", filename)
            if file_path:
                self.logger.info(f"File path selected: {file_path}")

                self.api.receive_file(file_path, file_id)
        except Exception as e:
            self.logger.error(f'Other exception in Home.receive_file: {e}')

    # send the text message to server
    def send_message(self):
        try:
            self.logger.info("Trying to send the message to server")
            if self.current_item is not None:
                friend = self.current_item.data(Qt.ItemDataRole.UserRole)
                content = self.Comment_textEdit.toPlainText().strip()
                reply_id = friend["user_id"]
                author_id = self.api.user_id
                self.Comment_textEdit.clear()

                self.api.comment({"content": content, "author_id": author_id, "reply_id": reply_id})

                self.render_message(self.current_item)
                return True
            else:
                self.logger.error(f'CURRENT ITEM IS NONE.')
                return False
        except Exception as e:
            self.logger.error(f'Other exception in Home.send_message: {e}')

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
            files = self.api.get_file(self.api.user_id, friend_id)
            messages = self.message_list(comments, files)

            for message in messages:
                font = QtGui.QFont()
                today = datetime.date.today()
                time_delta = datetime.timedelta(days=1)

                message_author = self.api.username if message.author_id == self.api.user_id else friend_name
                message_time = message.time
                if message_time.date() == today:
                    message_time = message_time.strftime("Today %H:%M")
                elif message_time.date() == today - time_delta:
                    message_time = message_time.strftime("Yesterday %H:%M")
                else:
                    message_time = message_time.strftime("%Y/%m/%d %H:%M")

                if message.is_file:
                    file_id = message.file_id
                    filename = message.name
                    file_type = message.type
                    save_filename = str(file_id) + '.' + file_type
                    match file_type:
                        case "wav":
                            form = File.FilePanel(message_author, message_time, "")
                            form.File_Button.setIcon(QIcon(r".\UI\play.png"))
                            form.File_Button.setIconSize(form.File_Button.sizeHint())
                            file_path = os.path.join(temp_path, save_filename)
                            if not os.path.exists(file_path):
                                self.api.receive_file(file_path, file_id)
                            font.setPointSize(12)
                            form.File_Button.setFlat(True)
                            form.File_Button.setFont(font)
                            form.File_Button.setProperty("file_path", file_path)
                            form.File_Button.clicked.connect(self.play_audio_message)
                            form.Image_label.deleteLater()
                        case "jpg" | "jpeg" | "png":
                            form = File.FilePanel(message_author, message_time, "")
                            file_path = os.path.join(temp_path, save_filename)
                            if not os.path.exists(file_path):
                                self.api.receive_file(file_path, file_id)
                            image = QImage(file_path)

                            # Scale the image to fit within a maximum size while maintaining its aspect ratio

                            scaled_image = image.scaled(max_width, max_height,
                                                        aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                                                        transformMode=Qt.TransformationMode.SmoothTransformation)

                            form.Image_label.setPixmap(QPixmap.fromImage(scaled_image))
                            form.Image_label.setMaximumSize(max_width, max_height)

                            form.File_Button.deleteLater()
                        case "gif":
                            form = File.FilePanel(message_author, message_time, "")
                            file_path = os.path.join(temp_path, save_filename)
                            if not os.path.exists(file_path):
                                self.api.receive_file(file_path, file_id)
                            movie = QMovie(file_path)
                            # movie.setScaledSize(form.Image_label.size())
                            form.Image_label.setScaledContents(True)
                            form.Image_label.setMovie(movie)
                            movie.jumpToFrame(0)
                            original_size = movie.currentPixmap().size()
                            form.Image_label.setFixedSize(original_size)
                            movie.start()
                            form.File_Button.deleteLater()
                        case _:
                            form = File.FilePanel(message_author, message_time, filename)
                            form.File_Button.setIcon(QIcon(r".\UI\file.png"))
                            form.File_Button.setIconSize(form.File_Button.sizeHint())
                            font.setPointSize(12)
                            form.File_Button.setFont(font)
                            form.File_Button.setProperty("file_id", file_id)
                            form.File_Button.setProperty("filename", filename)
                            form.File_Button.clicked.connect(self.receive_file)
                            form.Image_label.deleteLater()
                else:
                    comment_id = message.comment_id
                    message_content = message.content
                    form = Comment.CommentPanel(message_author, message_time, message_content)
                    form.Comment_label.setFont(font)
                font.setPointSize(9)
                form.Time_label.setFont(font)
                font.setBold(True)
                form.Author_label.setFont(font)

                self.scroll_area_layout.addWidget(form)

            self.scroll_area_layout.addStretch()
            self.scroll_area_widget.setLayout(self.scroll_area_layout)
            self.scrollArea.setWidget(self.scroll_area_widget)

            scrollbar = self.scrollArea.verticalScrollBar()
            if scrollbar.minimum() != scrollbar.maximum():
                scrollbar.setValue(scrollbar.maximum())
            return
        except Exception as e:
            self.logger.error(f'Other exception in Home.render_message: {e}')

    def message_list(self, comments, files):
        try:
            messages = []
            if len(comments):
                for i in range(len(comments)):
                    comments[i] = Message(comments[i], False)
            if len(files):
                for i in range(len(files)):
                    files[i] = Message(files[i], True)
            messages = comments + files
            messages.sort()
            return messages
        except Exception as e:
            self.logger.error(f'Other exception in Home.message_list: {e}')

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


class Message:
    def __init__(self, message, is_file):
        self.reply_id = None
        self.author_id = None
        self.time = None
        self.is_file = is_file
        self.file(message) if is_file else self.comment(message)

    def comment(self, message):
        self.comment_id = message[0]
        self.content = message[1]
        self.time = datetime.datetime.strptime(str(message[2]), '%Y%m%dT%H:%M:%S')
        self.author_id = message[3]
        self.reply_id = message[4]

    def file(self, message):
        self.file_id = message[0]
        self.name = message[1]
        self.type = message[2]
        self.data = message[3]
        self.time = datetime.datetime.strptime(str(message[4]), '%Y%m%dT%H:%M:%S')
        self.author_id = message[5]
        self.reply_id = message[6]

    def __lt__(self, other):
        return self.time < other.time
