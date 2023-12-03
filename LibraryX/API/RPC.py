# Seems like the client RPC API
# Student ID: D1166506
# Name: 周嘉禾

import logging
import re
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
        self.user_id = None
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
            if self.proxy.login(username, password):
                user_info = self.find_username(username)[0]
                self.user_id = user_info[0]
                self.username = user_info[1]
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f'Other exception in RPC.login: {e}')

    def register(self, username: str, password: str, confirm_password: str):
        try:
            return self.proxy.register(username, password, confirm_password)
        except Exception as e:
            self.logger.error(f'Other exception in RPC.register: {e}')

    def send(self, info):
        try:
            return self.proxy.comment(info["author"], info["content"], info["reply_id"], info["is_file"])
        except Exception as e:
            self.logger.error(f'Other exception in RPC.send: {e}')

    def delete(self, info):
        try:
            target = info["type"]
            match target:
                case "post":
                    target_id = info["post_id"]
                case "comment":
                    target_id = info["comment_id"]
                case "reply":
                    target_id = info["reply_id"]
                case _:
                    return False
            return self.proxy.delete(target, target_id)
        except Exception as e:
            self.logger.error(f'Other exception in RPC.delete: {e}')

    def get_friend(self, user_id):
        try:
            friend_info = []
            friends = self.proxy.friend_list(user_id)
            for friend in friends:
                if friend[3] == 'A':
                    info = self.find_user_id(friend[2])[0]
                    friend_info.append({"user_id": info[0], "username": info[1]})
            return tuple(friend_info)

        except Exception as e:
            self.logger.error(f'Other exception in RPC.get_friend: {e}')

    def get_comment(self, author_id, reply_id):
        try:
            return self.proxy.get_comment(author_id, reply_id)
        except Exception as e:
            self.logger.error(f'Other exception in RPC.get_comment: {e}')

    def find_user_id(self, user_id: int):
        return self.proxy.find_user_id(user_id)

    def find_username(self, username: str):
        return self.proxy.find_username(username)

    def receive_file(self, file_path, file_id):
        try:
            file_content = self.proxy.send_file(file_id)
            with open(file_path, 'wb') as received_file:
                received_file.write(file_content.data)
        except Exception as e:
            self.logger.error(f'Other exception in RPC.receive_file: {e}')

    def send_file(self, file_path):
        try:
            self.logger.info(f"File path: {file_path}")
            filename = re.split(r"/", file_path)[-1]
            with open(file_path, 'rb') as file:
                file_content = file.read()
                self.logger.info(f"File content: {file_content}")
                self.proxy.receive_file(filename, xmlrpc.client.Binary(file_content))
        except Exception as e:
            self.logger.error(f'Other exception in RPC.send_file: {e}')

    def insert_directory(self):
        return self.proxy.insert_directory(self.user_id, self.ip, self.port)

    def find_directory(self, user_id):
        user_id, (ip, port) = self.proxy.find_directory(user_id)
        return user_id, (ip, port)

    def find_friend(self, user_id, username):
        return self.proxy.find_friend(user_id, username)

    def send_friend_request(self, user_id, friend, status):
        return self.proxy.send_friend_request(user_id, friend, status)

    def find_friend_request(self, user_id):
        return self.proxy.find_friend_request(user_id)

    def friend_list(self, user_id):
        return self.proxy.friend_list(user_id)

<<<<<<< HEAD
=======
    def register_directory(self, user_id, ip, port):
        return self.proxy.register_directory(user_id, ip, port)

    def find_directory(self, user_id):
        return self.proxy.find_directory(user_id)

    def delete_directory(self, user_id):
        return self.proxy.delete_directory(user_id)

>>>>>>> Voice-call
    def close(self):
        self.delete_directory(self.user_id)
        self.close()
