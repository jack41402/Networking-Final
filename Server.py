# Server RPC Function
# Student ID: D1166506
# Name: 周嘉禾
import logging
import os.path
import re
import time
from xmlrpc import client
from LibraryX.API import SQL
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import threading
from scipy.io import wavfile

logger = logging.getLogger(__name__)
main_path = r"./File/server"
SERVER_IP = "127.0.0.1"
SERVER_PORT = 6666


class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server = None
        self.lock = threading.Lock()
        self.database = SQL.SQL()
        self.thread = threading.Thread(target=self.run)

    def start(self):
        self.thread.start()

    def run(self):
        try:
            self.connection()
            self.function_registry()
            self.server.serve_forever()
        except Exception as e:
            logger.error(f'Other exception in server.run: {e}')

    def connection(self):
        try:
            logger.info(f'Starting up server on {self.ip}: {self.port}')
            self.server = ThreadXMLRPCServer((self.ip, self.port), allow_none=True)
            logger.info("Waiting for connection...")
        except Exception as e:
            logger.error(f'Other exception in server.connection: {e}')

    def function_registry(self):
        try:
            logger.info("Registry functions...")
            self.server.register_function(self.login, "login")
            self.server.register_function(self.register, "register")
            self.server.register_function(self.comment, "comment")
            self.server.register_function(self.friend, "friend")
            self.server.register_function(self.get_comment, "get_comment")
            self.server.register_function(self.friend_list, "friend_list")
            self.server.register_function(self.delete, "delete")
            self.server.register_function(self.find_user_id, "find_user_id")
            self.server.register_function(self.find_username, "find_username")
            self.server.register_function(self.get_file, "get_file")
            self.server.register_function(self.receive_file, "receive_file")
            self.server.register_function(self.send_file, "send_file")
            self.server.register_function(self.find_friend, "find_friend")
            self.server.register_function(self.send_friend_request, "send_friend_request")
            self.server.register_function(self.get_friend_request, "get_friend_request")
            self.server.register_function(self.register_directory, "register_directory")
            self.server.register_function(self.find_directory, "find_directory")
            self.server.register_function(self.delete_directory, "delete_directory")
            self.server.register_function(self.delete_whole_directory, "delete_whole_directory")
            logger.info("Function login, register, comment, friend, get_comment, friend_list, delete, find_user_id, "
                        "find_username, get_file, receive_file, send_file, find_friend, send_friend_request, "
                        "find_friend_request, register_directory, find_directory, delete_directory, "
                        "and delete_whole_directory have been registered.")
            # print(self.server.system_listMethods())
        except Exception as e:
            logger.error(f'Other exception in server.function_registry: {e}')

    def login(self, username: str, password: str):
        try:
            with self.lock:
                user_info = self.database.find_info("user_information", "username", username)
                logger.info(f'User login info: {user_info}')
            if not username:
                logger.error("USERNAME CAN'T BE EMPTY.")
                return False
            elif not password:
                logger.error("PASSWORD CAN'T BE EMPTY.")
                return False
            elif len(user_info) == 0:
                logger.error("USERNAME DOES NOT EXIST.")
                return False
            elif password != user_info[0][2]:
                logger.error("PASSWORD INCORRECT.")
                return False
            else:
                logger.info(f'User {user_info[0][1]} login successfully.')
                return True
        except Exception as e:
            logger.error(f'Other exception in server.login: {e}')

    def register(self, username: str, password: str, confirm_password: str):
        try:
            with self.lock:
                user_info = self.database.find_info("user_information", "username", username)
                logger.info(f'User register info: {user_info}')
            if user_info:
                logger.error("USERNAME ALREADY EXIST.")
                return False
            elif not password:
                logger.error("PASSWORD CAN'T BE EMPTY.")
                return False
            elif password != confirm_password:
                logger.error("PASSWORD DOESN'T MATCH.")
                return False
            else:
                with self.lock:
                    self.database.insert_info("user_information", {"username": username, "password": password})
                logger.info(f'User {username} register successfully.')
                return True
        except Exception as e:
            logger.error(f'Other exception in server.register: {e}')

    def comment(self, content: str, author_id: int, reply_id: int):
        try:
            if not content:
                logger.error("COMMENT CAN'T BE EMPTY.")
                return False
            with self.lock:
                self.database.insert_info("comment", {"content": content, "author_id": author_id, "reply_id": reply_id})
            return True
        except Exception as e:
            logger.error(f'Other exception in server.comment: {e}')

    def get_comment(self, author_id, reply_id):
        try:
            with self.lock:
                comment = self.database.get_comment(author_id, reply_id)
            return comment
        except Exception as e:
            print(f'[ERROR] Other exception in server.get_comment: {e}')

    def get_file(self, author_id, reply_id):
        try:
            with self.lock:
                file = self.database.get_file(author_id, reply_id)
            return file
        except Exception as e:
            print(f'[ERROR] Other exception in server.get_file: {e}')

    # Function to receive and save the file on the server
    def receive_file(self, filename, file_type, file_content, author_id, reply_id):
        try:
            logger.info(f"Receive Filename: {filename}, File type: {file_type}")
            with self.lock:
                self.database.insert_info("file",
                                          {"name": filename, "type": file_type, "data": file_content.data,
                                           "author_id": author_id, "reply_id": reply_id})
            return True
        except Exception as e:
            logger.error(f'Other exception in server.receive_file: {e}')

    # Function to send a file content to the client
    def send_file(self, file_id):
        try:
            file_info = self.database.find_info("file", "file_id", file_id)[0]
            return file_info
        except Exception as e:
            logger.error(f'Other exception in server.send_file: {e}')

    def friend(self, user_id, friend_id):
        try:
            self.database.insert_info("friend", {"user_id": user_id, "friend_id": friend_id})
            return True
        except Exception as e:
            logger.error(f'Other exception in server.friend: {e}')

    def friend_list(self, user_id):
        try:
            with self.lock:
                friend = self.database.find_info("friend", "user_id", user_id)
            return friend
        except Exception as e:
            print(f'[ERROR] Other exception in server.friend_list: {e}')

    def delete(self, target: str, target_id: int):
        try:
            with self.lock:
                match target:
                    case "user_information":
                        result = self.database.find_info("user_information", "user_id", target_id)
                        if len(result):
                            self.database.delete_info("user_information", "user_id", target_id)
                            logger.info(f'Delete user_id {target_id} from {target} successfully.')
                            return True
                        else:
                            logger.info(f'Delete user_id {target_id} from {target} failed.')
                            return False
                    case "friend":
                        result = self.database.find_info("friend", "user_id", target_id)
                        if len(result):
                            self.database.delete_info("friend", "user_id", target_id)
                            logger.info(f'Delete user_id {target_id} from {target} successfully.')
                            return True
                        else:
                            logger.info(f'Delete user_id {target_id} from {target} failed.')
                            return False
                    case "comment":
                        result = self.database.find_info("comment", "comment_id", target_id)
                        if len(result):
                            self.database.delete_info("comment", "comment_id", target_id)
                            logger.info(f'Delete comment_id {target_id} from {target} successfully.')
                            return True
                        else:
                            logger.info(f'Delete comment_id {target_id} from {target} failed.')
                            return False
                    case _:
                        logger.error(f'DELETE UNEXPECTED TARGET {target}.')
                        return False
        except Exception as e:
            logger.error(f'Other exception in server.delete: {e}')

    def find_user_id(self, user_id: int):
        return self.database.find_info("user_information", "user_id", user_id)

    def find_username(self, username: str):
        return self.database.find_info("user_information", "username", username)

    def find_friend(self, user_id, username):
        return self.database.find_friend(user_id, username)

    def send_friend_request(self, user_id, friend_id, status):
        try:
            result = self.database.get_friend_info(user_id, friend_id)
            if result:
                result = result[0]
                return self.database.update_friend("status", status, user_id, friend_id)
            else:
                self.database.insert_info("friend", {"user_id": user_id, "friend_id": friend_id, "status": status})
        except Exception as e:
            logger.error(f'Other exception in server.friend_request: {e}')

    def get_friend_request(self, user_id):
        return self.database.get_friend_request(user_id)

    def register_directory(self, user_id, ip, port):
        try:
            return self.database.insert_info("directory", {"user_id": user_id, "ip": ip, "port": port})
        except Exception as e:
            logger.error(f'Other exception in server.register_directory: {e}')

    def find_directory(self, user_id):
        try:
            return self.database.find_directory(user_id)
        except Exception as e:
            logger.error(f'Other exception in server.find_directory: {e}')

    def delete_directory(self, user_id):
        try:
            return self.database.delete_directory(user_id)
        except Exception as e:
            logger.error(f'Other exception in server.delete_directory: {e}')

    def delete_whole_directory(self):
        return self.database.delete_whole_directory()

    def close(self):
        pass


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] - %(message)s (%(name)s / %(funcName)s:%(lineno)d)',
    )

    RPC_server = Server(SERVER_IP, SERVER_PORT)
    RPC_server.start()
