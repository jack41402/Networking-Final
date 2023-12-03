# Coded by Eric Chen, D1172271 / Jack Zhou, D1166506
# ISTM Purdue
#
# @All right reserved
# DESC: Final Project

from LibraryX import Utils


# This is an self designed VoIP-like module, using UDP to handle data transmit
class VoIP:
	def __init__(self, thread):
		self.remote_listen_port = None # remote audio listen port
		self.local_listen_port = None # local audio listen port


	# non-stop thread worker for checking if got incomming call, trigger callback when got call
	def __ringtone_detector(self, callback_func):
		# if got incomming call, trigger function call to _ringtone_callback()
		# pass data (caller_ip, caller_listen_port)
		pass


	# callback for __ringtone_detector to display the caller, meant to be subclass for implement
	def _ringtone_callback(self):
		pass


	# auto obtain one port as the listening port, and return (IP, Listen_Port) to user
	def setup(self):
		# start local non-stop incomming call checking thread, worker: __ringtone_detector / args: _ringtone_callback

		# return local ip, random local port
		pass


	# double connection to establish phone call
	def dial(self, remote_ip, remote_port):
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