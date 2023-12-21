import MySQLdb
import yaml
import logging

logger = logging.getLogger(__name__)


class SQL:
    def __init__(self):
        self.database = None
        self.connection()

    def connection(self):
        try:
            with open("./LibraryX/API/config.yaml", 'r') as stream:
                config = yaml.load(stream, Loader=yaml.FullLoader)
        except FileNotFoundError:
            logger.error("FILE config.yaml NOT FOUND.")
            return False
        except yaml.YAMLError:
            logger.error("CONFIG FORMAT ERROR.")
            return False
        except Exception as e:
            logger.error(f'Other exception in SQL.connection: {e}')
            return False
        try:
            self.database = MySQLdb.connect(**config)
        except MySQLdb.Error as e:
            logger.error(f'CANNOT CONNECT TO MySQL DATABASE {config["database"]}: {e}')
            return False
        except Exception as e:
            logger.error(f'Other exception in SQL.connection: {e}')
            return False

    def command(self, command: str, value: tuple):
        try:
            with self.database.cursor() as cursor:
                cursor.execute(command, value)
                self.database.commit()
                result = cursor.fetchall()
                return result
        except MySQLdb.Error as e:
            self.database.rollback()
            logger.error(f'MySQL error in SQL.command {command}: {e}')
        except Exception as e:
            logger.error(f'Other exception in SQL.command {command}: {e}')

    def insert_info(self, table: str, info: dict):
        try:
            match table:
                case "user_information":
                    command = "INSERT INTO user_information(username, password) VALUES(%s, %s)"
                    self.command(command, (info["username"], info["password"]))
                    logger.info("Insert into user_information successfully.")
                case "friend":
                    command = "INSERT INTO friend(user_id, friend_id, status) VALUES(%s, %s, %s)"
                    self.command(command, (info["user_id"], info["friend_id"], info["status"]))
                    logger.info(f"Insert status {info['status']} into friend successfully.")
                case "comment":
                    command = "INSERT INTO comment(content, time, author_id, reply_id) VALUES(%s, NOW(), %s, %s)"
                    self.command(command, (info["content"], info["author_id"], info["reply_id"]))
                    logger.info("Insert into comment successfully.")
                case "file":
                    command = "INSERT INTO file(name, type, data, time, author_id, reply_id) VALUES(%s, %s, %s, NOW(), %s, %s)"
                    self.command(command,(info["name"], info["type"], info["data"], info["author_id"], info["reply_id"]))
                    logger.info("Insert into file successfully.")
                case "directory":
                    command = "INSERT INTO directory(user_id, ip, port) VALUES(%s, %s, %s)"
                    self.command(command, (info["user_id"], info["ip"], info["port"]))
                    logger.info("Insert into directory successfully.")
                case _:
                    logger.error(f'''TABLE {table} DOES NOT EXIST.''')
                    return False
            return True
        except Exception as e:
            logger.error(f'Other exception in SQL.insert_info: {e}')

    def find_info(self, table: str, key: str, value):
        try:
            command = '''SELECT * FROM %s WHERE %s="%s"'''
            value = str(value)
            command %= table, key, value
            result = self.command(command, ())
            return result
        except Exception as e:
            logger.error(f'Other exception in SQL.find_info: {e}')

    def delete_info(self, table: str, key: str, value):
        try:
            command = '''DELETE FROM %s WHERE %s="%s"'''
            value = str(value)
            command %= table, key, value
            result = self.command(command, ())
            return result
        except Exception as e:
            logger.error(f'Other exception in SQL.delete_info: {e}')

    def get_table(self, table: str):
        try:
            command = "SELECT * FROM " + table
            result = self.command(command, ())
            if result:
                logger.info(f'Result in table {table}: {result}')
            return result
        except Exception as e:
            logger.error(f'Other exception in SQL.get_table: {e}')

    # Comment
    def get_comment(self, author_id, reply_id):
        try:
            command = '''SELECT * FROM comment WHERE (author_id, reply_id) IN ((%s, %s), (%s, %s))  ORDER BY time ASC'''
            author_id = str(author_id)
            reply_id = str(reply_id)
            result = self.command(command, (author_id, reply_id, reply_id, author_id))
            return result
        except Exception as e:
            logger.error(f'Other exception in SQL.get_comment: {e}')

    # File
    def get_file(self, author_id, reply_id):
        try:
            command = '''SELECT * FROM file WHERE (author_id, reply_id) IN ((%s, %s), (%s, %s))  ORDER BY time ASC'''
            author_id = str(author_id)
            reply_id = str(reply_id)
            result = self.command(command, (author_id, reply_id, reply_id, author_id))
            return result
        except Exception as e:
            logger.error(f'Other exception in SQL.get_file: {e}')

    # Friend
    def get_friend_status(self, user_id, friend_id):
        try:
            command = '''SELECT * FROM friend WHERE (user_id, friend_id) IN ((%s, %s), (%s, %s))'''
            user_id = str(user_id)
            friend_id = str(friend_id)
            result = self.command(command, (user_id, friend_id, friend_id, user_id))
            if len(result) == 2:
                return True
            else:
                return False
        except Exception as e:
            logger.error(f'Other exception in SQL.get_friend_status: {e}')

    def get_friend_info(self, user_id, friend_id):
        try:
            command = '''SELECT * FROM friend WHERE user_id=%s AND friend_id=%s'''
            user_id = str(user_id)
            friend_id = str(friend_id)
            result = self.command(command, (user_id, friend_id))
            return result
        except Exception as e:
            logger.error(f'Other exception in SQL.get_friend_info: {e}')

    def find_friend(self, user_id, username):
        try:
            result = []
            command = '''SELECT * FROM user_information WHERE LOCATE("%s", username)'''
            user_id = str(user_id)
            username = str(username)
            command %= username
            users = self.command(command, ())
            for user in users:
                friend_id = str(user[0])
                if user_id != friend_id:
                    command = '''SELECT * FROM friend WHERE user_id=%s AND friend_id=%s'''
                    command %= user_id, friend_id
                    row = self.command(command, ())
                    if row:
                        row = row[0]
                        if row[2] == 'R':
                            result.append(user)
                    else:
                        result.append(user)
            return tuple(result)
        except Exception as e:
            logger.error(f'Other exception in SQL.find_friend: {e}')

    def delete_friend(self, user_id, friend_id):
        try:
            command = '''DELETE FROM comment WHERE (user_id, friend_id) IN ((%s, %s), (%s, %s))'''
            user_id = str(user_id)
            friend_id = str(friend_id)
            result = self.command(command, (user_id, friend_id, friend_id, user_id))
            return result
        except Exception as e:
            logger.error(f'Other exception in SQL.delete_friend: {e}')

    def update_friend(self, key, value, user_id, friend_id):
        try:
            command = '''UPDATE friend SET %s="%s" WHERE user_id=%s AND friend_id=%s'''
            user_id = str(user_id)
            friend_id = str(friend_id)
            command %= key, value, user_id, friend_id
            result = self.command(command, ())
            return result
        except Exception as e:
            logger.error(f'Other exception in SQL.update_friend: {e}')

    def get_friend_request(self, user_id):
        try:
            user_id = str(user_id)
            command = '''SELECT * FROM friend WHERE user_id=%s AND status="P"'''
            user_request = self.command(command, (user_id,))
            command = '''SELECT * FROM friend WHERE friend_id=%s AND status="P"'''
            friend_request = self.command(command, (user_id,))
            return user_request, friend_request
        except Exception as e:
            logger.error(f'Other exception in SQL.get_friend_request: {e}')

    # Voice Call
    def find_directory(self, user_id):
        try:
            command = '''SELECT * FROM directory WHERE user_id=%s'''
            user_id = str(user_id)
            result = self.command(command, (user_id,))
            print(result)
            if result:
                info = result[0]
                return info[2], info[3]
            else:
                return False
        except Exception as e:
            logger.error(f'Other exception in SQL.find_directory: {e}')

    def delete_directory(self, user_id):
        try:
            command = '''DELETE FROM directory WHERE user_id=%s'''
            user_id = str(user_id)
            result = self.command(command, (user_id,))
            return result
        except Exception as e:
            logger.error(f'Other exception in SQL.delete_directory: {e}')

    def delete_whole_directory(self):
        try:
            command = '''DELETE FROM directory'''
            result = self.command(command, ())
            return result
        except Exception as e:
            logger.error(f'Other exception in SQL.delete_whole_directory: {e}')
