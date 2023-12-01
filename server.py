# Student ID: D1166506
# Name: 周嘉禾
from PyQt6.QtCore import pyqtSignal, QThread
from LibraryX.API import sql
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import threading


class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class Server(QThread):
    server_signal = pyqtSignal(str)

    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port
        self.server = None
        self.lock = threading.Lock()
        self.database = sql.SQL()

    def run(self):
        self.connection()
        self.function_registry()
        self.server.serve_forever()

    def connection(self):
        try:
            print("[SERVER] Starting up server on port: %s" % self.port)
            self.server = ThreadXMLRPCServer(("localhost", self.port), allow_none=True)
            print("[SERVER] Waiting for connection...")
        except Exception as e:
            print(f'[ERROR] Other exception in server.connection: {e}')

    def function_registry(self):
        print("[SERVER] Registry functions...")
        self.server.register_function(self.login, "login")
        self.server.register_function(self.register, "register")
        self.server.register_function(self.comment, "comment")
        self.server.register_function(self.delete, "delete")
        self.server.register_function(self.user, "user")
        print("[SERVER] Function login, register, comment, delete, and user have been registered.")

    def login(self, username: str, password: str):
        try:
            with self.lock:
                user_info = self.database.find_info("user_information", "username", username)
                print("[SERVER] User login info: ", user_info)
            if not username:
                print("[ERROR] USERNAME CAN'T BE EMPTY.")
                return False
            elif not password:
                print("[ERROR] PASSWORD CAN'T BE EMPTY.")
                return False
            elif len(user_info) == 0:
                print("[ERROR] USERNAME DOES NOT EXIST.")
                return False
            elif password != user_info[0][2]:
                print("[ERROR] PASSWORD INCORRECT.")
                return False
            else:
                print("[INFO] User %s login successfully." % user_info[0][1])
                return True
        except Exception as e:
            print(f'[ERROR] Other exception in server.login: {e}')

    def register(self, username: str, password: str, confirm_password: str):
        try:
            with self.lock:
                user_info = self.database.find_info("user_information", "username", username)
                print("[SERVER] User register info: ", user_info)
            if user_info:
                print("[ERROR] USERNAME ALREADY EXIST.")
                return False
            elif not password:
                print("[ERROR] PASSWORD CAN'T BE EMPTY.")
                return False
            elif password != confirm_password:
                print("[ERROR] PASSWORD DOESN'T MATCH.")
                return False
            else:
                with self.lock:
                    self.database.insert_info("user_information", {"username": username, "password": password})
                print("[INFO] User %s register successfully." % username)
                return True
        except Exception as e:
            print(f'[ERROR] Other exception in server.register: {e}')

    def comment(self, author: str, content: str, reply_id: int):
        try:
            if not content:
                print("[ERROR] COMMENT CAN'T BE EMPTY.")
                return False
            with self.lock:
                author_id = self.database.find_info("user_information", "username", author)
            if len(author_id) != 0:
                author_id = author_id[0][0]
            else:
                print("[ERROR] UNEXPECTED USER %s." % author)
                return False
            with self.lock:
                self.database.insert_info("comment", {"content": content, "author_id": author_id, "reply_id": reply_id})
            return True
        except Exception as e:
            print(f'[ERROR] Other exception in server.comment: {e}')

    def delete(self, target: str, target_id: int):
        try:
            with self.lock:
                match target:
                    case "user_information":
                        result = self.database.find_info("user_information", "user_id", target_id)
                        if len(result):
                            self.database.delete_info("user_information", "user_id", target_id)
                            return True
                        else:
                            return False
                    case "friend":
                        result = self.database.find_info("friend", "user_id", target_id)
                        if len(result):
                            self.database.delete_info("friend", "user_id", target_id)
                            return True
                        else:
                            return False
                    case "comment":
                        result = self.database.find_info("comment", "comment_id", target_id)
                        if len(result):
                            self.database.delete_info("comment", "comment_id", target_id)
                            return True
                        else:
                            return False
                    case _:
                        print("[ERROR] UNEXPECTED DELETE TARGET %s." % target)
                        return False
        except Exception as e:
            print(f'[ERROR] Other exception in server.delete: {e}')

    def user(self, user_id: int):
        return self.database.find_info("user_information", "id", user_id)

    def close(self):
        pass
