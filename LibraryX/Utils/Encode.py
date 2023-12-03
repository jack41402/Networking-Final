# Coded by Eric Chen, D1172271
# ISTM Purdue
#
# @Copyright /  All right reserved
# DESC: Some custom module for data encoding on transmission

import socket
import struct
import logging
import binascii
from enum import IntFlag, auto

LOGGER = logging.getLogger(__name__)
NULL_SEQ_ACK = -999 # the magic number use to indicat the value in data packing is null of protocolX


# DESC: Listing out the supprorted datatype we can handle packing
class EncodeType(IntFlag):
	INT = auto()
	STR = auto()
	CHAR = auto()
	BOOL = auto()
	FLOAT = auto()
	DOUBLE = auto()
	ARRAY = auto()


# DESC: Auto data convertion for network transmission in a custom way
class Convert:
	@staticmethod
	def hex_encode(data):
		return binascii.hexlify(data) # for safe transmission, in case raw byte transmission is not supported


	@staticmethod
	def hex_decode(data):
		return binascii.unhexlify(data)


	@staticmethod
	def pack(datatype, raw_data):
		data = b''

		# check the type it specify before packing
		if (datatype & EncodeType.ARRAY): # array data type
			count =  len(raw_data) # get number of entry
			data += bytes([0x00]) # make a mark that it's an array
			entry_count = len(raw_data)
			data += entry_count.to_bytes(2, 'big', signed=False)

			if (datatype & EncodeType.INT):
				agent = struct.Struct("!{}i".format(entry_count))
				data += bytes([0x01])
				data += agent.pack(*raw_data)

			elif (datatype & EncodeType.STR): # caution !!
				data += bytes([0x02]) # ID 0x02: String

				# itterate throught ther target string list
				for entry in raw_data:
					length = len(entry)
					agent = struct.Struct("!{}s".format(length))
					data += length.to_bytes(4, "big", signed=False) # 4 byte unsigned data length identifier
					data += agent.pack(entry.encode('utf-8')) # append the actual payload

			elif (datatype & EncodeType.CHAR):
				agent = struct.Struct("!{}c".format(entry_count))
				data += bytes([0x03])
				data += agent.pack(*raw_data)

			elif (datatype & EncodeType.BOOL):
				agent = struct.Struct("!{}?".format(entry_count))
				data += bytes([0x04])
				data += agent.pack(*raw_data)

			elif (datatype & EncodeType.FLOAT):
				agent = struct.Struct("!{}f".format(entry_count))
				data += bytes([0x05])
				data += agent.pack(*raw_data)

			elif (datatype & EncodeType.DOUBLE):
				agent = struct.Struct("!{}d".format(entry_count))
				data += bytes([0x06])
				data += agent.pack(*raw_data)
			

		else: # normal data type
			if (datatype & EncodeType.INT):
				agent = struct.Struct("!i")
				data += bytes([0x01])
				data += agent.pack(raw_data)

			elif (datatype & EncodeType.STR):
				length = len(raw_data)
				agent = struct.Struct("!{}s".format(length))
			
				data += bytes([0x02]) # ID 0x02: String
				data += length.to_bytes(4, "big", signed=False) # 4 byte unsigned data length identifier
				data += agent.pack(raw_data.encode('utf-8')) # append the actual payload

			elif (datatype & EncodeType.CHAR):
				agent = struct.Struct("!c")
				data += bytes([0x03])
				data += agent.pack(raw_data)

			elif (datatype & EncodeType.BOOL):
				agent = struct.Struct("!?")
				data += bytes([0x04])
				data += agent.pack(raw_data)

			elif (datatype & EncodeType.FLOAT):
				agent = struct.Struct("!f")
				data += bytes([0x05])
				data += agent.pack(raw_data)

			elif (datatype & EncodeType.DOUBLE):
				agent = struct.Struct("!d")
				data += bytes([0x06])
				data += agent.pack(raw_data)

		return data


	@staticmethod
	def unpack(packed_data):
		step = 0
		data = ""
		datatype = ""
		id = packed_data[0]

		# # check the format it is packed in
		if (id == 0x00): # array data handling
			data = []
			id = packed_data[3]
			count = int.from_bytes(packed_data[1:3], 'big', signed=False)

			if (id == 0x01): # integer format
				LOGGER.debug("Detected Int format encoding, now parsing......")
				agent = struct.Struct("!{}i".format(count))
				data = list(agent.unpack(packed_data[4:]))
				datatype = EncodeType.INT | EncodeType.ARRAY

			elif (id == 0x02): # string format
				LOGGER.debug("Detected String format encoding, now parsing......")
				datatype = EncodeType.STR | EncodeType.ARRAY

				# itterate unpack
				for index in range(0, count):
					length = int.from_bytes(packed_data[4+step:8+step], 'big', signed=False)
					rawdata = packed_data[step+8:step+8+length]
					agent = struct.Struct("!{}s".format(length))
					data.append(agent.unpack(rawdata)[0].decode('utf-8'))

					# counter increase
					step += (length + 4)

			elif (id == 0x03): # raw byte
				LOGGER.debug("Detected Char format encoding, now parsing......")
				agent = struct.Struct("!{}c".format(count))
				data = list(agent.unpack(packed_data[4:]))
				datatype = EncodeType.CHAR | EncodeType.ARRAY

			elif (id == 0x04): # bool
				LOGGER.debug("Detected Bool format encoding, now parsing......")
				agent = struct.Struct("!{}?".format(count))
				data = list(agent.unpack(packed_data[4:]))
				datatype = EncodeType.BOOL | EncodeType.ARRAY

			elif (id == 0x05): # float
				LOGGER.debug("Detected Float format encoding, now parsing......")
				agent = struct.Struct("!{}f".format(count))
				data = list(agent.unpack(packed_data[4:]))
				datatype = EncodeType.FLOAT | EncodeType.ARRAY

			elif (id == 0x06): # double
				LOGGER.debug("Detected Double format encoding, now parsing......")
				agent = struct.Struct("!{}d".format(count))
				data = list(agent.unpack(packed_data[4:]))
				datatype = EncodeType.DOUBLE | EncodeType.ARRAY
			

		else: # normal data handling
			if (id == 0x01): # integer format
				LOGGER.debug("Detected Int format encoding, now parsing......")
				agent = struct.Struct("!i")
				data = agent.unpack(packed_data[1:])[0]
				datatype = EncodeType.INT

			elif (id == 0x02): # string format
				LOGGER.debug("Detected String format encoding, now parsing......")
				length = int.from_bytes(packed_data[1:5], "big", signed=False)
				agent = struct.Struct("!{}s".format(length))
				data = (agent.unpack(packed_data[5:])[0]).decode('utf-8')
				datatype = EncodeType.STR

			elif (id == 0x03): # raw byte
				LOGGER.debug("Detected Char format encoding, now parsing......")
				agent = struct.Struct("!c")
				data = agent.unpack(packed_data[1:])[0]
				datatype = EncodeType.CHAR

			elif (id == 0x04): # bool
				LOGGER.debug("Detected Bool format encoding, now parsing......")
				agent = struct.Struct("!?")
				data = agent.unpack(packed_data[1:])[0]
				datatype = EncodeType.BOOL

			elif (id == 0x05): # float
				LOGGER.debug("Detected Float format encoding, now parsing......")
				agent = struct.Struct("!f")
				data = agent.unpack(packed_data[1:])[0]
				datatype = EncodeType.FLOAT

			elif (id == 0x06): # double
				LOGGER.debug("Detected Double format encoding, now parsing......")
				agent = struct.Struct("!d")
				data = agent.unpack(packed_data[1:])[0]
				datatype = EncodeType.DOUBLE

		
		return datatype, data



# DESC: For some common feautures on validation, like IPV4 address and Port
class Validity:
	
	# check if a string contains a valid number for port
	@staticmethod
	def port(data):
		# If all letters contained are digits
		if (data.isdigit()):
			# then check if it is in range of 1 ~ 65535
			if (1 <= int(data) <= 65535):
				return True

			else:
				print("Data not in range")
				return False

		else:
			print("Not digit")
			return False

	# check if a string contains a valud ip address
	@staticmethod
	def ip(data):
		try:
			socket.inet_aton(data)
			return True

		except OSError:
			return False



# Custom robust self-defined protocol framework, providing flags and other supports
class ProtocolX:
	def __init__(self, SYN=False, ACK=False, PSH=False, URG=False, FIN=False, seq=0, ack=0):
		self.is_embed = False
		self.seq = seq
		self.ack = ack
		self.SYN = SYN
		self.ACK = ACK
		self.PSH = PSH
		self.URG = URG
		self.FIN = FIN
		self.payload = None
		self.datatype = None


	# autoparse the rawdata and load in th
	def parse(self, rawdata):
		unhexed_data = Convert.hex_decode(rawdata)
		id = unhexed_data[0] # the first byte is signature

		# we check signature first, make sure it is an packed ProtocolX
		if (id == 0xFF):
			header_length = int.from_bytes(unhexed_data[1:3], 'big', signed=False) # the folowing 2 bytes is header length
			header_rawdata = unhexed_data[3:3+header_length]
			payload_rawdata = unhexed_data[3+header_length:]

			# debug show
			LOGGER.debug(f"Header Rawdata: {header_rawdata}")
			LOGGER.debug(f"Payload Rawdata: {payload_rawdata}")

			# pasre the header first and perform mapping
			agent = struct.Struct("!5? 2i 1?")
			header = agent.unpack(header_rawdata)
			self.SYN = header[0]
			self.ACK = header[1]
			self.PSH = header[2]
			self.URG = header[3]
			self.FIN = header[4]
			self.seq = None if header[5] == NULL_SEQ_ACK else header[5]
			self.ack = None if header[6] == NULL_SEQ_ACK else header[6]
			self.is_embed = header[7]

			# parse the payload, if it is an embed packet
			if (self.is_embed):
				self.datatype, self.payload = Convert.unpack(payload_rawdata)

		return


	# perfoming the export of the protocolx instance in hex to transmit
	def packup(self):
		data = b''
		data += bytes([0xFF]) # special mark indicating it's a packed protocolx
		data += self._pack_header()

		# if the packet is meant to be embed, append the payload
		if (self.is_embed):
			data += self._pack_payload()

		return Convert.hex_encode(data)


	# for exporting the header 
	def _pack_header(self):
		data = b''

		agent = struct.Struct("!5? 2i 1?")
		header_packed = agent.pack(self.SYN, self.ACK, self.PSH, self.URG, self.FIN, self.seq, self.ack, self.is_embed)
		header_length = len(header_packed)

		# format the data as (header length) + (packed header)
		data += header_length.to_bytes(2, 'big', signed=False)
		data += header_packed
		return data


	# for exporting the embeded data
	def _pack_payload(self):
		return Convert.pack(self.datatype, self.payload)


	# for embeding the payload on the packet
	def embed_payload(self, datatype, data):
		if (datatype and data):
			self.is_embed = True
			self.payload = data
			self.datatype = datatype

		return


	# perfoming header flag manipulation
	def set_flags(self, SYN=False, ACK=False, PSH=False, URG=False, FIN=False):
		self.SYN = SYN
		self.ACK = ACK
		self.PSH = PSH
		self.URG = URG
		self.FIN = FIN
		return


	# set value for the header
	def set_values(self, seq=None, ack=None):
		self.seq = NULL_SEQ_ACK if seq == None else seq
		self.ack = NULL_SEQ_ACK if ack == None else ack
		return



if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)

	# test pack
	encoded = Convert.pack(EncodeType.STR, "[NOT-READY]")
	encoded = Convert.hex_encode(encoded)
	print(Convert.hex_decode(encoded))
	print(Convert.hex_decode(b'02000000055b41434b5d'))

	# debug show
	print(encoded)