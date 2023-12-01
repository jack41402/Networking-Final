# Student ID: D1166506
# Name: 周嘉禾
import xmlrpc.client
from PyQt6.QtCore import pyqtSignal, QThread
import datetime


class Client(QThread):
    client_error_signal = pyqtSignal(str)

    def __init__(self, ip: str, port: int):
        super().__init__()
        self.ip = ip
        self.port = port
        # CHECK HTTPS
        self.address = f'http://{self.ip}:{self.port}/'
        self.proxy = None
        self.username = None

    def run(self):
        self.connection()

    def connection(self):
        print("Connecting to %s port %s" % (self.ip, self.port))
        self.proxy = xmlrpc.client.ServerProxy(self.address, allow_none=True)
        print("[CLIENT] Connected successfully.")

    def login(self, username: str, password: str):
        try:
            print("Username: ", username)
            self.username = username
            return self.proxy.login(username, password)
        except Exception as e:
            print(f'[ERROR] Other exception in client.login: {e}')

    def register(self, username: str, password: str, confirm_password: str):
        try:
            return self.proxy.register(username, password, confirm_password)
        except Exception as e:
            print(f'[ERROR] Other exception in client.register: {e}')

    def post(self, title: str, content: str):
        try:
            return self.proxy.create(title, content, self.username)
        except Exception as e:
            print(f'[ERROR] Other exception in client.post: {e}')

    def subject(self):
        try:
            result = self.proxy.subject()
            for row in result:
                row[3] = datetime.datetime.strptime(str(row[3]), '%Y%m%dT%H:%M:%S')
            return result
        except Exception as e:
            print(f'[ERROR] Other exception in client.subject: {e}')

    def send(self, info):
        try:
            if info["type"] == "comment":
                return self.proxy.comment(info["author"], info["content"], info["post_id"])
            elif info["type"] == "reply":
                return self.proxy.reply(info["author"], info["content"], info["comment_id"])
        except Exception as e:
            print(f'[ERROR] Other exception in client.send: {e}')

    def comment(self, author: str, content: str, post_id: int):
        try:
            return self.proxy.comment(author, content, post_id)
        except Exception as e:
            print(f'[ERROR] Other exception in client.comment: {e}')

    def reply(self, author: str, content: str, comment_id: int):
        try:
            return self.proxy.reply(content, author, comment_id)
        except Exception as e:
            print(f'[ERROR] Other exception in client.reply: {e}')

    def discussion(self, post_id):
        try:
            result = self.proxy.discussion(post_id)
            for row in result:
                comment = row["comment"]
                comment["time"] = datetime.datetime.strptime(str(comment["time"]), '%Y%m%dT%H:%M:%S')
                for reply in row["reply"]:
                    reply["time"] = datetime.datetime.strptime(str(reply["time"]), '%Y%m%dT%H:%M:%S')
            return result
        except Exception as e:
            print(f'[ERROR] Other exception in client.discussion: {e}')

    def delete(self, info):
        try:
            target = info["type"]
            if target == "post":
                target_id = info["post_id"]
            elif target == "comment":
                target_id = info["comment_id"]
            elif target == "reply":
                target_id = info["reply_id"]
            else:
                return False
            return self.proxy.delete(target, target_id)
        except Exception as e:
            print(f'[ERROR] Other exception in client.delete: {e}')

    def findReplyInfo(self, comment_id, reply_id):
        try:
            result = self.proxy.findReplyInfo(comment_id, reply_id)
            return result
        except Exception as e:
            print(f'[ERROR] Other exception in server.findReplyInfo: {e}')

    def user(self, user_id: int):
        return self.proxy.user(user_id)

    def close(self):
        pass
