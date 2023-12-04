# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project

import time
import pyaudio
import random
import socket
import logging
import threading
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QSpacerItem, QSizePolicy
from LibraryX.Utils import TCP_Networking, UDP_Networking, Encode
from PyQt6.QtWidgets import QWidget, QMessageBox, QSpacerItem, QSizePolicy
from LibraryX.API import SQL


# This is a self designed VoIP-like module, using UDP to handle data transmit
class VoIP(QWidget):
    ANSWER_OR_REJECT_SIGNAL = pyqtSignal(bool)
    FORMAT = pyaudio.paInt16
    CHANNEL = 1
    RATE = 44100
    CHUNK = 1024

    def __init__(self, local_ip, api, pop_msgbox_signal):
        super().__init__()
        self.ANSWER_OR_REJECT_SIGNAL.connect(self._ringtone_handler)
        self.pop_msgbox_signal = pop_msgbox_signal
        self.condition = threading.Condition()
        self.logger = logging.getLogger(__name__)
        self.audio = pyaudio.PyAudio()
        self.is_hangup = threading.Event()  # phone call hangup event
        self.local_ip = local_ip
        self.ringtone_socket = None
        self.speak_socket = None
        self.listen_socket = None
        self.remote_listen_port = None  # remote audio listen port
        self.local_listen_port = None  # local audio listen port
        self.ringtone_port = random.randint(8000, 9000)  # ringtone server port
        self.ringtone_thread = threading.Thread(target=self.__ringtone_detector, args=(self._ringtone_callback,))
        self.speak_thread = None
        self.listen_thread = None
        self.dialer_ip = None
        self.dialer_listen_port = None
        self.api = api

    # non-stop thread worker for checking if got incoming call, trigger callback when got call
    def __ringtone_detector(self, callback_func):
        # if got incoming call, trigger function call to _ringtone_callback()
        # pass data (caller_ip, caller_listen_port)
        while True:
            # we will discard the server everytime
            self.ringtone_socket = TCP_Networking.SimpleServer('0.0.0.0', self.ringtone_port, 5)
            self.ringtone_socket.start()

            # create server and start listening for call
            dialer_detail = self.ringtone_socket.receive()[1]
            dialer_ip, dialer_listen_port = dialer_detail.split(':')

            # trigger the callback to ask if answer or not
            status = callback_func(dialer_detail)

            # close server
            with self.condition:
                self.condition.wait() # wait for user to make desicsion
                self.ringtone_socket.close()

    # callback for __ringtone_detector to display the caller, meant to be subclass for implement
    def _ringtone_callback(self, caller_info):
        self.logger.info(f"Incoming call from: {caller_info}")

        # parse data
        self.dialer_ip, self.dialer_listen_port = caller_info.split(':')

        # pop msgbox in the main thread
        self.pop_msgbox_signal.emit("[Audio Call]", f"Incomming call from {self.dialer_ip} !", "Answer it or not ?")
        return
        # return self.pop_yesnomessagebox("[Audio Call]", f"Incomming call from {dialer_ip} !", "Answer it or not ?")

    # user made choice to answer call or not
    def _ringtone_handler(self, choice):
        # check what the callback function returned
        if choice:
            self.logger.info("Accepting Call")
            self.ringtone_socket.send("[OK]", datatype=Encode.EncodeType.STR)
            self.answer(self.dialer_ip, int(self.dialer_listen_port))

        else:
            self.logger.info("Rejecting Call")
            self.ringtone_socket.send("[REJECT]", datatype=Encode.EncodeType.STR)

        # notify that user had made choice
        with self.condition:
            self.condition.notify()

    # audio send thread worker
    def __audio_send(self):
        stream = self.audio.open(format=self.FORMAT, channels=self.CHANNEL, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        while not self.is_hangup.is_set():
            data = stream.read(self.CHUNK)
            self.speak_socket.send(data)

        self.logger.info("received hangup signal in the audio sending thread")
        return

    # audio receive thread worker
    def __audio_receive(self):
        stream = self.audio.open(format=self.FORMAT, channels=self.CHANNEL, rate=self.RATE, output=True, frames_per_buffer=self.CHUNK)
        while not self.is_hangup.is_set():
            data = self.listen_socket.receive(0.2, autoparse=False)[1]

            # check if timeout
            if data:
                stream.write(data)

        self.logger.info("received hangup signal in the audio receiving thread")
        return

    # auto obtain one port as the listening port, and return (IP, Listen_Port) to user
    def setup(self):
        try:
            # start local non-stop incoming call checking thread, worker: __ringtone_detector / args: _ringtone_callback
            self.ringtone_thread.daemon = True
            self.ringtone_thread.start()
            self.logger.info(f"Started the ringtone server on port: {self.ringtone_port}")

            # register out ringtone port to forum server
            self.api.register_directory(self.api.user_id, self.local_ip, self.ringtone_port)
            return
        except Exception as e:
            self.logger.error(f'Other exception in VoIP.setup: {e}')

    # double connection to establish phone call
    def dial(self, remote_ip, remote_ringtone_port):
        try:
            # send my local opening listen port to receiver, trigger remote __ringtone_detector()
            # set an timeout 60 sec
            #
            # if answered:
            # receive the remote listening port of acceptor's host
            #
            # if reject or timeout:
            # return None
            #
            #
            # double connection establish:
            # {
            # 	dialer ====> receiver's udp audio receive port
            # 	dialer audio receive port <==== receiver
            #                                                 }
            #
            # start one thread for sending my voice
            # start another thread for receiving acceptor's voice

            # setup the local audio listen port
            self.local_listen_port = random.randint(9000, 10000)
            self.listen_socket = UDP_Networking.SimpleServer('0.0.0.0', self.local_listen_port)
            self.logger.info(f"Setting up the local UDP audio listen port on: {self.local_listen_port}")

            # connect to the receiver's ringtone server
            self.logger.info(f"Connecting to the receiver's ringtone server on: {remote_ip}:{remote_ringtone_port}")
            self.client = TCP_Networking.SimpleClient(remote_ip, remote_ringtone_port)
            self.client.send(f"{self.local_ip}:{self.local_listen_port}", datatype=Encode.EncodeType.STR)
            reply = self.client.receive()[1]
            self.client.close()

            # determine call status based on reply
            if reply == "[OK]":
                self.logger.info("Remote host aceepted the phone call")
                self.logger.info("Now swapping listen port details......")
                self.remote_client_info, data = self.listen_socket.receive(10)
                self.remote_listen_port = data[1]
                self.logger.info(f"Received remote listen port: {self.remote_listen_port}")
                self.logger.info("Establishing UDP connection with receiver's audio listen port")
                self.speak_socket = UDP_Networking.SimpleClient(remote_ip, self.remote_listen_port)
                self.logger.info("Giving the receiver's audio listening socket an ack")
                self.speak_socket.send("[ACK]", datatype=Encode.EncodeType.STR)

                # start audio transmission
                self.logger.info("Starting audio transmission......")
                self.audio_stream()

            elif reply == "[REJECT]":
                self.logger.info("Remote host rejected the phone call")
                self.listen_socket.close()

            return
        except Exception as e:
            self.logger.error(f'Other exception in VoIP.dial: {e}')

    # answer an incoming phone call, based on callback function _ringtone_callback's data
    def answer(self, remote_ip, remote_listen_port):
        # give my local listening port to the dialer's host
        #
        # double connection established
        # {
        # 	receiver ====> dialer's udp audio receive port
        # 	receiver audio receive port <==== dialer
        #                                                 }
        #
        # start one thread for sending my voice
        # start another thread for receiving dialer's voice

        # setup the local audio listen port
        self.local_listen_port = random.randint(9000, 10000)
        self.listen_socket = UDP_Networking.SimpleServer('0.0.0.0', self.local_listen_port)
        self.logger.info(f"Setting up the local UDP audio listen port on: {self.local_listen_port}")

        # connecting to the dialer's listening socket
        self.logger.info("Answering dialer's incoming phone call")
        self.logger.info("Now swapping listen port details......")
        self.speak_socket = UDP_Networking.SimpleClient(remote_ip, remote_listen_port)
        self.speak_socket.send(self.local_listen_port, datatype=Encode.EncodeType.INT)
        self.logger.info(f"Sending local audio listen port {self.local_listen_port} to dialer")

        # try to receive an ack message from dialer
        self.remote_client_info, data = self.listen_socket.receive(10)
        if data[1] == "[ACK]":
            self.logger.info("Received an ack message form the dailer's speaking socket")

        # start audio transmission
        self.logger.info("Starting audio transmission......")
        self.audio_stream()
        return

    # audio transmission start
    def audio_stream(self):
        self.speak_thread = threading.Thread(target=self.__audio_send)
        self.listen_thread = threading.Thread(target=self.__audio_receive)
        self.speak_thread.daemon = True
        self.listen_thread.daemon = True
        self.speak_thread.start()
        self.listen_thread.start()
        return

    # hangup a phone call:
    def hangup(self):
        # setting signal to halt the send and listen audio thread
        self.is_hangup.set()

        # join the two thread of listen and sending audio
        self.logger.info("Waiting for audio listening & sending thread join main thread")
        self.speak_thread.join()
        self.listen_thread.join()
        self.logger.info("Audio listening & sending thread joined elegently")

        # reinitialize the voip server
        self.is_hangup.clear()
        self.local_listen_port = None
        self.remote_listen_port = None
        return
