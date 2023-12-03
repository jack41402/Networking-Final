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
from LibraryX import TCP_Networking, Utils


# This is an self designed VoIP-like module, using UDP to handle data transmit
class VoIP:
	FORMAT = pyaudio.paInt16
	CHANNEL = 1
	RATE = 44100
	CHUNK = 1024

	def __init__(self, local_ip):
		self.logger = logging.getLogger(__name__)
		self.audio = pyaudio.PyAudio()
		self.is_hangup = threading.Event() # phone call hangup event
		self.local_ip = local_ip
		self.ringtone_socket = None
		self.speak_socket = None
		self.listen_socket = None
		self.remote_listen_port = None # remote audio listen port
		self.local_listen_port = None # local audio listen port
		self.ringtone_port = random.randint(8000, 9000) # ringtone server port
		self.ringtone_thread = threading.Thread(target=self.__ringtone_detector, args=(self._ringtone_callback,))
		self.speak_thread = threading.Thread(target=self.__audio_send)
		self.listen_thread = threading.Thread(target=self.__audio_receive)


	# non-stop thread worker for checking if got incomming call, trigger callback when got call
	def __ringtone_detector(self, callback_func):
		# if got incomming call, trigger function call to _ringtone_callback()
		# pass data (caller_ip, caller_listen_port)
		self.ringtone_socket = TCP_Networking.SimpleServer('0.0.0.0', self.ringtone_port)
		self.ringtone_socket.start()

		while True:
			# create server and start listening for call
			dailer_detail = self.ringtone_socket.receive()
			dailer_ip, dailer_listen_port = dailer_detail.split(':')

			# trigger the callback to ask if answer or not
			status = callback_func(caller_detail[1])

			# check what the callback function returned
			if (status):
				self.ringtone_socket.send("[OK]", datatype=Encode.EncodeType.STR)
				self.answer(dailer_ip, int(dailer_listen_port))

			else:
				self.ringtone_socket.send("[REJECT]", datatype=Encode.EncodeType.STR)

		return


	# callback for __ringtone_detector to display the caller, meant to be subclass for implement
	def _ringtone_callback(self, caller_info):
		self.logger(f"Incomming call from: {caller_info}")

		# parse data
		self.logger.info("Set to auto accept call")
		return True


	# audio send thread worker
	def __audio_send(self):
		with self.audio.open(format=self.FORMAT, channels=self.CHANNEL, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK) as stream:
			while not self.is_hangup.is_emit():
				data = stream.read(CHUNK)
				self.speak_socket.send(data)

		self.logger("received hangup signal in the audio sending thread")
		return


	# audio receive thread worker
	def __audio_receive(self):
		with self.audio.open(format=self.FORMAT, channels=self.CHANNEL, rate=self.RATE, output=True, frames_per_buffer=self.CHUNK) as stream:
            while not self.is_hangup.is_emit():
				data = listen_socket.receive(0.2, autoparse=False)[1]

				# check if timeout
				if data:
					stream.write(data)

		self.logger("received hangup signal in the audio receving thread")
        return


	# auto obtain one port as the listening port, and return (IP, Listen_Port) to user
	def setup(self):
		# start local non-stop incomming call checking thread, worker: __ringtone_detector / args: _ringtone_callback
		self.ringtone_thread.daemon = True
		self.ringtone_thread.start()
		self.logger.info(f"Started the ringtone server on port: {self.ringtone_port}")

		# register out ringtone port to forum server
		return


	# double connection to establish phone call
	def dial(self, remote_ip, remote_ringtone_port):
		# send my local opening listen port to receiver, trigger remote __ringtone_detector()
		# set an timeout 60 sec
		#
		# if answered:
		# receive the remote listening port of accetper's host
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
		# start another thread for receivng accepter's voice
 
		# setup the local audio listen port
		self.local_listen_port = random.randint(9000, 10000)
		self.listen_socket = UDP_Networking.SimpleServer('0.0.0.0', self.local_listen_port)
		self.logger.info(f"Setting up the local UDP audio listen port on: {self.local_listen_port}")

		# connect to the receiver's ringtone server
		self.logger.info(f"Connecting to the receiver's ringtone server on: {remote_ip}:{remote_ringtone_port}")
		self.client = TCP_Networking.SimpleClient(remote_ip, remote_ringtone_port)
		self.client.send(f"{local_ip}:{self.local_listen_port}", datatype=Encode.EncodeType.STR)
		reply[1] = self.client.receive()
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


	# answer an incomming phone call, based on callback function _ringtone_callback's data
	def answer(self, remote_ip, remote_listen_port):
		# give my local listening port to the dailer's host
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

		# connecting to the dailer's listening socket
		self.logger.info("Answering dailer's incomming phone call")
		self.logger.info("Now swapping listen port details......")
		self.speak_socket = UDP_Networking.SimpleClient(remote_ip, remote_listen_port)
		self.speak_socket.send(self.local_listen_port, datatype=Encode.EncodeType.INT)
		self.logger.info(f"Sending local audio listen port {self.local_listen_port} to dailer")

		# try to receive an ack message from dailer
		self.remote_client_info, data = self.listen_socket.receive(10)
		if data[1] == "[ACK]":
			self.logger("Received an ack message form the dailer's speaking socket")

		# start audio transmission
		self.logger.info("Starting audio transmission......")
		self.audio_stream()
		return


	# audio transmission start
	def audio_stream(self):
		self.speak_thread.start()
		self.listen_thread.start()
		return


	# hangup an phone call:
	def hangup(self):
		# setting signal to halt the send and listen audio thread
		self.is_hangup.emit()

		# join the two thread of listen and sending audio
		self.logger("Waiting for audio listening & sending thread join main thread")
		self.speak_thread.join()
		self.listen_thread.join()
		self.logger("Audio listening & sending thread joined elegently")
		return