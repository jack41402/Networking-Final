# Coded by Eric Chen, D1172271
# ISTM Purdue
#
# @Copyright /  All right reserved
# DESC: For handling TCP client, server connection in a custom way

import ssl
import time
import select
import socket
import logging
import threading
from LibraryX.Utils import Encode


# DESC: Single-thread server implementation, with simplicity & robustness in mind
# Note: If need TLS/mTLS support, so the SSL context wrapping direclty on the  socket is ok, since it's single threaded
class SimpleServer:
    def __init__(self, bind_interface, bind_port, backlog, server_privatekey=None, server_certificate=None,
                 client_certificate=None):
        self.TLS = False  # TLS / SSL
        self.mTLS = False  # Mutal TLS
        self.port = bind_port
        self.backlog = backlog
        self.interface = bind_interface
        self.client_connection = None

        # create the sever socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # specify tcp transmission
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allow port reusing
        self.socket.bind((self.interface, self.port))  # set port & interface

        # check if the user both specified the server cert and private key, enable ssl mode
        if server_privatekey and server_certificate:
            self.TLS = True

            # check if files exist else raise exception (?

            # create ssl context and load the server cert and pkey
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(certfile=server_certificate, keyfile=server_privatekey)

            # going for mutal TLS, load in client cert for verification
            if client_certificate:
                self.mTLS = True
                ctx.verify_mode = ssl.CERT_REQUIRED  # require client cert by CA
                ctx.load_verify_locations(cafile=client_certificate)

            # perform socket wrapping
            self.socket = ctx.wrap_socket(self.socket, server_side=True)

    def start(self):
        # start listening for incomming client conenction
        self.socket.listen(self.backlog)
        client, addr = self.socket.accept()
        print("[INFO] Receive incomming connection from {ip} via port {port}".format(ip=addr[0], port=addr[1]))
        self.client_connection = client
        return addr

    def send(self, data, datatype=None):
        status = False

        try:
            if datatype:
                # packing data in custom convention
                packed_data = Encode.Convert.pack(datatype, data)
                encoded_data = Encode.Convert.hex_encode(packed_data)

            else:
                encoded_data = data

            # send encoded data if var not empty
            if (encoded_data):
                self.client_connection.sendall(encoded_data)
                status = True

        except OSError as ex:
            print("[ERROR] Send Failed ! Socket Error: \"{}\"".format(ex))

        except Exception as ex:
            print("[ERROR] Send Failed ! \"{}\"".format(ex))

        finally:
            return status

    def receive(self, autoparse=True):
        try:
            raw_data = self.client_connection.recv(2048)

            # empty data received, indicates client closed connection
            if not raw_data:
                return None, None

            # if need the autoparse for data processing
            if (autoparse):
                # normal data received, try to decode it
                decoded_data = Encode.Convert.hex_decode(raw_data)
                unpacked_data = Encode.Convert.unpack(decoded_data)
                return unpacked_data

            else:
                return raw_data

        except OSError as ex:
            print("[ERROR] Send Failed ! Socket Error: \"{}\"".format(ex))
            return None, None

        except Exception as ex:
            print("[ERROR] Send Failed ! \"{}\"".format(ex))
            return None, None

    def close(self):
        try:
            print("[TRACE] Closing server socket......")
            self.client_connection.close()  # cleanup client handle
            self.socket.close()  # cleanup server port binding
            return

        except OSError as ex:
            return


# DESC: Single-thread client implementation, with simplicity & robustness in mind
# Note: If need TLS/mTLS support, so the SSL context wrapping direclty on the client socket
class SimpleClient:
    def __init__(self, server_address, server_port, TLS=None, client_privatekey=None, client_certificate=None,
                 server_certificate=None):
        self.TLS = False
        self.mTLS = False
        self.server_ip = server_address
        self.server_port = server_port

        # create client socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # tcp

        # check if the user both specified the client cert and private key, enable ssl mode
        if TLS:
            if (client_privatekey and client_certificate and server_certificate):  # going for mTLS
                ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=server_certificate)
                ctx.load_cert_chain(certfile=client_certificate, keyfile=client_privatekey)

            else:  # going for TLS
                ctx = ssl._create_unverified_context()

            # wrap the client socket
            self.socket = ctx.wrap_socket(self.socket, server_side=False, server_hostname=self.server_ip)

        # connect to server
        self.socket.connect((self.server_ip, self.server_port))
        return

    def send(self, data, datatype=None):
        status = False

        try:
            if datatype:
                # packing data in custom convention
                packed_data = Encode.Convert.pack(datatype, data)
                encoded_data = Encode.Convert.hex_encode(packed_data)

            else:
                encoded_data = data

            # send encoded data if var not empty
            if (encoded_data):
                self.socket.sendall(encoded_data)
                status = True

        except OSError as ex:
            print("[ERROR] Send Failed ! Socket Error: \"{}\"".format(ex))

        except Exception as ex:
            print("[ERROR] Send Failed ! \"{}\"".format(ex))

        finally:
            return status

    def receive(self, autoparse=True):
        try:
            raw_data = self.socket.recv(2048)

            # empty data received, indicates client closed connection
            if not raw_data:
                return None, None

            if (autoparse):
                decoded_data = Encode.Convert.hex_decode(raw_data)
                unpacked_data = Encode.Convert.unpack(decoded_data)
                return unpacked_data

            else:
                return raw_data

        except OSError as ex:
            print("[ERROR] Receive Failed ! Socket Error: \"{}\"".format(ex))
            return None, None

        except Exception as ex:
            print(raw_data)
            print("[ERROR] Receive Failed ! \"{}\"".format(ex))
            return None, None

    def close(self):
        print("[TRACE] Closing clinet socket......")
        self.socket.close()  # cleanup
        return


# DESC: Muli-thread server daemon implementation, please subclass it to override the trnasmission loop for custom behavior
# Note: If need TLS/mTLS support, do the SSL context wrapping in the conn socket for best flexibility (not implemented)
class ConcurrentServer:
    def __init__(self, bind_interface, bind_port, backlog):
        self.port = bind_port
        self.buffer_size = 2048
        self.backlog = backlog
        self.interface = bind_interface
        self.terminate_signal = threading.Event()  # critical shared signal to kill daemon when set
        self.tracking_lock = threading.Lock()  # thread lock to prevent race condition on connection_list
        self.connection_list = []  # for tracking the client connection handler subthreads
        self.readable_sockets = []  # for efficient server socket tracking via select module
        self.logger = logging.getLogger(__name__)  # the logger for this class

        # start the server in raw socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.interface, self.port))

        # using a seperate thread to handle the forever listening loop
        self.thread = threading.Thread(target=self.__listen, name="<Concurrent TCP Server Daemon>")
        self.thread.daemon = True

    # Forever listening loop
    def __listen(self):
        # start server listen
        readable_sockets = [self.socket]
        self.socket.listen(self.backlog)

        # run until been halt by another thread
        while not self.terminate_signal.is_set():
            # check if there's new data(connection) ready to read in
            readable, _, _ = select.select(readable_sockets, [], [], 5)

            # itterate the readin socket
            for socket in readable:
                if (socket is self.socket):
                    client_connection, client_addr = socket.accept()

                    # create subthread to handle the client
                    client_hdlr = threading.Thread(target=self.__client_wrapper, args=(client_connection, client_addr),
                                                   name="<Client Connection Wrapper>")
                    client_hdlr.daemon = True  # in case the user exit server abruptly

                    # add entry in the connection tracking list
                    with self.tracking_lock:
                        self.connection_list.append(client_hdlr)

                    # start client handling subthread
                    client_hdlr.start()

        self.logger.debug("The concurrent server exited the listening loop elegently.....")
        return

    # DESC: Client connection handling wrapper to track the alive connection, should only be used internally
    def __client_wrapper(self, connection, addr):
        try:
            # invoke the transmission handler which shall be override by user
            self.logger.debug(
                "Client connection wrapper invoking the transmission loop for \'{host}:{port}\'".format(host=addr[0],
                                                                                                        port=addr[1]))
            self.transmission_loop(connection)

        except Exception as ex:
            self.logger.error(
                "[ERROR] Got an unexpected exception in thread \'{thread}\' for host \'{host}:{port}\' !!".format(
                    thread=threading.current_thread().name,
                    host=addr[0],
                    port=addr[1]))
            self.logger.error("[ERROR] Exception: {}".format(str(ex)))

        finally:
            connection.close()

            # remove the client from the active thread list
            with self.tracking_lock:  # prevent race condition on client connection tracking
                self.connection_list.remove(threading.current_thread())
                self.logger.debug(
                    "Transmission with host \'{host}:{port}\' ended elegently.".format(host=addr[0], port=addr[1]))
                self.logger.debug("Removed connection entry from the tracking list !")

        return

    # DESC: The transmission loop meant to be override to have a custom behavior on client transmission handling
    def transmission_loop(self, connection):
        # If the user is using the default transmission loop
        self.logger.warning("You are using the default transmission loop for client handling......")
        self.logger.warning(
            "Please subclass the ConcurrentServer Class and override the transmission_loop(connection) for custom implementation !")

        # warn them by sending a dummy packet to client
        self.send(connection, "Warning !! Default Transmission Loop !!", datatype=Encode.EncodeType.STR)
        return

    # DESC: API for starting server daemon
    def start_service(self):
        self.logger.debug("Now starting the concurrent server daemon......")
        self.thread.start()
        return

    # DESC: API for stopping server daemon elegently, this will signal server & all exisiting client to abort !!
    def stop_service(self):
        # set the terminate signal for all thread
        self.logger.debug("Now shutting down the concurrent server daemon......")
        self.terminate_signal.set()

        # create a shallow copy(reference) for the current connection list
        # since the client_wrapper will use the thread lock when exiting, so we shouldnt be acquiring it
        with self.tracking_lock:
            snapshot_connection_list = self.connection_list.copy()
            self.logger.debug("Created snapshot of current tracking list")

        # recursive wait for all client to stop
        self.logger.debug("Waiting for client handling subthreads to join......")
        for client in snapshot_connection_list:
            client.join()

        # join the main threads
        self.logger.debug("All subthreads joined !")
        self.logger.debug("Waiting for concurrent server main thread to join......")
        self.thread.join()  # join the server listening thread
        self.socket.close()  # close concurrent server socket

        self.logger.debug("Main thread joined !")
        self.logger.debug("The concurrent server daemon has been shutdown elegently !!")
        return

    # DESC: API for sending data to client via a specific connection
    def send(self, connection, data, datatype=None):
        status = False

        try:
            if datatype:
                # packing data in custom convention
                packed_data = Encode.Convert.pack(datatype, data)
                encoded_data = Encode.Convert.hex_encode(packed_data)

            else:
                encoded_data = data

            # send encoded data if var not empty
            # self.logger.debug(f"[TRACE] Encoded {data} to {encoded_data}")
            if (encoded_data):
                connection.sendall(encoded_data)
                status = True

        except OSError as ex:
            self.logger.error("Send Failed ! Socket Error: \"{}\"".format(ex))

        except Exception as ex:
            self.logger.error("Send Failed ! \"{}\"".format(ex))

        finally:
            return status

    # DESC: API for receiving data from client via a specific conenction
    def receive(self, connection, autoparse=True):
        try:
            raw_data = connection.recv(self.buffer_size)

            # check if received empty data, signals connection ends
            if not (raw_data):
                return False

            # handle the parsing of raw data according to user's need
            if (autoparse):
                decoded_data = Encode.Convert.hex_decode(raw_data)
                unpacked_data = Encode.Convert.unpack(decoded_data)
                return unpacked_data

            else:
                return raw_data

        except OSError as ex:
            self.logger.error("Receive Failed ! Socket Error: \"{}\"".format(ex))
            return False

        except Exception as ex:
            self.logger.error("Receive Failed ! \"{}\"".format(ex))
            return False


if __name__ == "__main__":
    pass
