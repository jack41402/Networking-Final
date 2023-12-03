# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project

import random
import socket
import logging
import threading
from LibraryX import TCP_Networking, Utils


# This is an self designed VoIP-like module, using UDP to handle data transmit
class VoIP:
	def __init__(self, local_ip):
		self.logger = logging.getLogger(__name__)
		self.local_ip = local_ip
		self.speak_socket = None
		self.listen_socket = None
		self.remote_listen_port = None # remote audio listen port
		self.local_listen_port = None # local audio listen port
		self.ringtone_port = random.randint(8000, 9000) # ringtone server port
		self.ringtone_thread = threading.Thread(target=self.__ringtone_detector, args=(self._ringtone_callback,))
		self.speak_thread = None
		self.listen_thread = None


	# non-stop thread worker for checking if got incomming call, trigger callback when got call
	def __ringtone_detector(self, callback_func):
		# if got incomming call, trigger function call to _ringtone_callback()
		# pass data (caller_ip, caller_listen_port)
		while True:
			# create server and start listening for call
			ringtone_socket = TCP_Networking.SimpleServer('0.0.0.0', self.ringtone_port)
			ringtone_socket.start()
			caller_detail = ringtone_socket.receive()

			# trigger the callback
			callback_func(caller_detail[1])

			# discard server after use
			ringtone_socket.close()

		pass


	# callback for __ringtone_detector to display the caller, meant to be subclass for implement
	def _ringtone_callback(self, caller_info):
		self.logger(f"Incomming call from: {caller_info}")
		pass


	# auto obtain one port as the listening port, and return (IP, Listen_Port) to user
	def setup(self):
		# start local non-stop incomming call checking thread, worker: __ringtone_detector / args: _ringtone_callback
		self.ringtone_thread.daemon = True
		self.ringtone_thread.start()
		self.logger.info(f"Started the ringtone server on port: {self.ringtone_port}")

		# register out ringtone port to forum server
		return


	# double connection to establish phone call
	def dial(self, remote_ip, ringtone_port):
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

		# generate the local answer port
		self.local_listen_port = random.randint(9000, 10000)

		# connect to the receiver's ringtone server
		self.client = TCP_Networking.SimpleClient(remote_ip, ringtone_port)
		self.client.send(f"{local_ip}:{self.local_listen_port}")
		reply = self.client.receive()

		# determine call status based on reply
		
		pass


	# answer an incomming phone call, based on callback function _ringtone_callback's data
	def answer(self, remote_ip, remote_port):
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
		pass


	# reject an incomming phone call
	def reject(self, remote_ip):
		# send a custom message to indicate call rejected
		pass


	# hangup an phone call:
	def hangup(self):
		# join the two thread of listen and sending audio
		pass