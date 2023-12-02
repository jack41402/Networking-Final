# Student ID: D1166506
# Name: 周嘉禾

import logging
import xmlrpc.client
import datetime
import threading


class Client(threading.Thread):
    def __init__(self, ip: str, port: int):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.ip = ip
        self.port = port
        # CHECK HTTPS
        self.address = f'http://{self.ip}:{self.port}/'
        self.proxy = None
        self.username = None

    def run(self):
        self.connection()

    def connection(self):
        self.logger.info("Connecting to %s port %s" % (self.ip, self.port))
        self.proxy = xmlrpc.client.ServerProxy(self.address, allow_none=True)
        self.logger.info("Connected successfully.")

    def login(self, username: str, password: str):
        try:
            self.logger.info(f"Username: {username}")
            self.username = username
            return self.proxy.login(username, password)
        except Exception as e:
            self.logger.error(f'Other exception in client.login: {e}')

    def register(self, username: str, password: str, confirm_password: str):
        try:
            return self.proxy.register(username, password, confirm_password)
        except Exception as e:
            self.logger.error(f'Other exception in client.register: {e}')

    def send(self, info):
        try:
            if info["type"] == "comment":
                return self.proxy.comment(info["author"], info["content"], info["post_id"])
            elif info["type"] == "reply":
                return self.proxy.reply(info["author"], info["content"], info["comment_id"])
        except Exception as e:
            self.logger.error(f'Other exception in client.send: {e}')

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
            self.logger.error(f'Other exception in client.delete: {e}')
    
    def user(self, user_id: int):
        return self.proxy.user(user_id)

    def close(self):
        pass
