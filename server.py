# Student ID: D1166506
# Name: 周嘉禾
from PyQt6.QtCore import pyqtSignal, QThread
from database import sql
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
        self.session = threading.Lock()
        self.database = sql.SQL()

    def run(self):
        self.connection()
        self.registry()
        self.server.serve_forever()

    def connection(self):
        try:
            print("Starting up server on port: %s" % self.port)
            self.server = ThreadXMLRPCServer(("localhost", self.port), allow_none=True)
            print("[SERVER] Waiting for connection...")
        except Exception as e:
            print(f'[ERROR] Other exception in server.connection: {e}')

    def registry(self):
        print("Registry...")
        self.server.register_function(self.login, "login")
        self.server.register_function(self.register, "register")
        self.server.register_function(self.create, "create")
        self.server.register_function(self.subject, "subject")
        self.server.register_function(self.comment, "comment")
        self.server.register_function(self.reply, "reply")
        self.server.register_function(self.discussion, "discussion")
        self.server.register_function(self.delete, "delete")
        self.server.register_function(self.findReplyInfo, "findReplyInfo")
        self.server.register_function(self.user, "user")

    def login(self, username: str, password: str):
        try:
            self.session.acquire()
            user_info = self.database.findInfo("user_information", "username", username)
            self.session.release()
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
                print("[INFO] Login successfully.")
                return True
        except Exception as e:
            print(f'[ERROR] Other exception in server.login: {e}')

    def register(self, username: str, password: str, confirm_password: str):
        try:
            self.session.acquire()
            user_info = self.database.findInfo("user_information", "username", username)
            self.session.release()
            print("User info: ", user_info)
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
                self.session.acquire()
                self.database.insertInfo("user_information", {"username": username, "password": password})
                self.session.release()
                print("[INFO] Register successfully.")
                return True
        except Exception as e:
            print(f'[ERROR] Other exception in server.register: {e}')

    def create(self, title: str, content: str, author: str):
        try:
            if not title:
                print("[ERROR] TITLE CAN'T BE EMPTY.")
                return False
            elif not content:
                print("[ERROR] CONTENT CAN'T BE EMPTY.")
                return False
            else:
                self.session.acquire()
                author_id = self.database.findInfo("user_information", "username", author)
                self.session.release()
                if len(author_id) != 0:
                    author_id = author_id[0][0]
                else:
                    return False
                self.session.acquire()
                self.database.insertInfo("forum", {"title": title, "content": content, "author_id": author_id})
                self.session.release()
                return True
        except Exception as e:
            print(f'[ERROR] Other exception in server.create: {e}')

    def subject(self):
        try:
            return self.database.getTable("forum")
        except Exception as e:
            print(f'[ERROR] Other exception in server.subject: {e}')

    def comment(self, author: str, content: str, post_id: int):
        try:
            if not content:
                return False
            self.session.acquire()
            floor = self.database.findMaxFloor("comment", "post_id", post_id)
            author_id = self.database.findInfo("user_information", "username", author)
            self.session.release()
            if len(author_id) != 0:
                author_id = author_id[0][0]
            else:
                return False
            self.session.acquire()
            self.database.insertInfo("comment", {"floor": floor + 1, "content": content, "author_id": author_id, "post_id": post_id})
            self.session.release()
            return True
        except Exception as e:
            print(f'[ERROR] Other exception in server.comment: {e}')

    def reply(self, author: str, content: str, comment_id: int):
        try:
            if not content:
                return False
            self.session.acquire()
            floor = self.database.findMaxFloor("reply", "comment_id", comment_id)
            author_id = self.database.findInfo("user_information", "username", author)
            self.session.release()
            if len(author_id) != 0:
                author_id = author_id[0][0]
            else:
                return False
            self.session.acquire()
            self.database.insertInfo("reply", {"floor": floor + 1, "content": content, "author_id": author_id, "comment_id": comment_id})
            self.session.release()
            return True
        except Exception as e:
            print(f'[ERROR] Other exception in server.reply: {e}')

    def discussion(self, post_id):
        try:
            discuss = []
            self.session.acquire()
            comments = self.database.findInfo("comment", "post_id", post_id)
            for comment in comments:
                reply = self.database.findInfo("reply", "comment_id", comment[0])
                discuss.append(Discuss(comment, reply))
            discuss = tuple(discuss)
            self.session.release()
            return tuple(discuss)
        except Exception as e:
            print(f'[ERROR] Other exception in server.discussion: {e}')

    def delete(self, target: str, target_id: int):
        try:
            if target == "post":
                self.session.acquire()
                result = self.database.findInfo("comment", "post_id", target_id)
                if len(result) == 0:
                    self.database.deleteInfo("forum", "post_id", target_id)
                    self.session.release()
                    return True
                else:
                    return False
            elif target == "comment":
                self.session.acquire()
                result = self.database.findInfo("reply", "comment_id", target_id)
                if len(result) == 0:
                    self.database.deleteInfo("comment", "comment_id", target_id)
                    self.session.release()
                    return True
                else:
                    return False
            elif target == "reply":
                self.session.acquire()
                comment_id = self.database.findInfo("reply", "reply_id", target_id)
                self.session.release()
                if len(comment_id) != 0:
                    comment_id = comment_id[0][5]
                else:
                    return False
                self.session.acquire()
                result = self.database.findReplyInfo("reply", "comment_id", comment_id, "reply_id", target_id)
                self.session.release()
                if len(result) == 0:
                    self.session.acquire()
                    self.database.deleteInfo("reply", "reply_id", target_id)
                    self.session.release()
                    return True
                else:
                    return False
        except Exception as e:
            print(f'[ERROR] Other exception in server.delete: {e}')

    def findReplyInfo(self, comment_id, reply_id):
        try:
            self.session.acquire()
            result = self.database.findReplyInfo("reply", "comment_id", comment_id, "reply_id", reply_id)
            self.session.release()
            return result
        except Exception as e:
            print(f'[ERROR] Other exception in server.findReplyInfo: {e}')

    def close(self):
        pass

    def user(self, user_id: int):
        return self.database.findInfo("user_information", "id", user_id)


class Discuss:
    def __init__(self, comment, reply):
        self.comment = Comment(comment)
        self.reply = []
        for row in reply:
            self.reply.append(Reply(row))
        self.reply = tuple(self.reply)


class Comment:
    def __init__(self, comment):
        self.comment_id = comment[0]
        self.floor = comment[1]
        self.content = comment[2]
        self.time = comment[3]
        self.author_id = comment[4]
        self.post_id = comment[5]


class Reply:
    def __init__(self, reply):
        self.reply_id = reply[0]
        self.floor = reply[1]
        self.content = reply[2]
        self.time = reply[3]
        self.author_id = reply[4]
        self.comment_id = reply[5]
