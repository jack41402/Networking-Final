# Coded by Eric Chen, D1172271
# ISTM Purdue
#
# @Copyright /  All right reserved
# DESC: For handling UDP client, server connection in a custom way

import time
import select
import socket
import threading
from LibraryX.Utils import Encode


BUFFER_SIZE = 2048

# DESC: Single-thread server implementation, with simplicity & robustness in mind
class SimpleServer:
	def __init__(self, bind_interface, bind_port, buffer_size=BUFFER_SIZE):
		self.buffer_size = buffer_size
		self.interface = bind_interface
		self.port = bind_port

		# init udp server socket
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind((self.interface, self.port))


	# if specify the datatype as None, it wont pack data for you, but process it as raw data
	def send(self, client_info, data, datatype=None):
		status = False

		try:
			if datatype: # packing data in custom convention automatically
				packed_data = Encode.Convert.pack(datatype, data)
				encoded_data = Encode.Convert.hex_encode(packed_data)

			else: # sending the data as rawdata, won't help you pack
				encoded_data = data

			# attempt send if buffer not empty
			if (encoded_data):
				self.socket.sendto(encoded_data, client_info)
				status = True

		except OSError as ex:
			print("[ERROR] Send Failed ! Socket Error: \"{}\"\n".format(ex))

		except Exception as ex:
			print("[ERROR] Send Failed ! \"{}\"\n".format(ex))

		finally:
			return status


	def receive(self, timeout, autoparse=True):
		try:
			readable, _, _ = select.select([self.socket], [], [], timeout) # non blocking client handling
			
			# if socket is ready and got incomming data
			if self.socket in readable:
				raw_data, client_info = self.socket.recvfrom(self.buffer_size)

				# parse the received data if needed
				if (autoparse):
					decoded_data = Encode.Convert.hex_decode(raw_data)
					unpacked_data = Encode.Convert.unpack(decoded_data)
					return (client_info, unpacked_data)

				else:
					return (client_info, raw_data)

			else: # no data was received during the receiving time duration
				return None, None


		except OSError as ex:
			print("[ERROR] Receive Failed ! Socket Error: \"{}\"".format(ex))
			return None, None

		except Exception as ex:
			print("[ERROR] Receive Failed ! \"{}\"".format(ex))
			return None, None


	def close(self):
		self.socket.close()
		return



# DESC: Single-thread client implementation, with simplicity & robustness in mind
class SimpleClient:
	def __init__(self, server_address, server_port, buffer_size=BUFFER_SIZE):
		self.buffer_size = buffer_size
		self.server_ip = server_address
		self.server_port = server_port
		self.server_info = (self.server_ip, self.server_port)

		# create socket, since UDP doesn't have concept of connecttion, so we cont need to establish connection
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


	def send(self, data, datatype=None):
		status = False

		try:
			if datatype: # packing data in custom convention
				packed_data = Encode.Convert.pack(datatype, data)
				encoded_data = Encode.Convert.hex_encode(packed_data)

			else: # sending the data as rawdata, won't help you pack
				encoded_data = data

			# send encoded data if var not empty
			if (encoded_data):
				self.socket.sendto(encoded_data, self.server_info)
				status = True

		except OSError as ex:
			print("[ERROR] Send Failed ! Socket Error: \"{}\"".format(ex))

		except Exception as ex:
			print("[ERROR] Send Failed ! \"{}\"".format(ex))

		finally:
			return status


	def receive(self, timeout, autoparse=True):
		try:
			readable, _, _ = select.select([self.socket], [], [], timeout)

			# if socket is ready and got incomming data
			if self.socket in readable:
				raw_data, server_info = self.socket.recvfrom(self.buffer_size)

				# parse received data if needed
				if (autoparse):
					decoded_data = Encode.Convert.hex_decode(raw_data)
					unpacked_data = Encode.Convert.unpack(decoded_data)
					return (server_info, unpacked_data)

				else:
					return (server_info, raw_data)

			else:
				return None, None


		except OSError as ex:
			print("[ERROR] Receive Failed ! Socket Error: \"{}\"\n".format(ex))
			return None, None

		except Exception as ex:
			print("[ERROR] Receive Failed ! \"{}\"\n".format(ex))
			return None, None


	def close(self):
		self.socket.close()
		return



