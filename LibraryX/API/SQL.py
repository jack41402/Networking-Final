import os

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
            logger.error(f'Other exception in sql.connection: {e}')
            return False
        try:
            self.database = MySQLdb.connect(**config)
        except MySQLdb.Error as e:
            logger.error(f'CANNOT CONNECT TO MySQL DATABASE {config["database"]}: {e}')
            return False
        except Exception as e:
            logger.error(f'Other exception in sql.connection: {e}')
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
            logger.error(f'MySQL error in sql.command {command}: {e}')
        except Exception as e:
            logger.error(f'Other exception in sql.command {command}: {e}')

    def insert_info(self, table: str, info: dict):
        try:
            match table:
                case "user_information":
                    command = "INSERT INTO user_information(username, password) VALUES(%s, %s)"
                    self.command(command, (info["username"], info["password"]))
                    logger.info("Insert into user_information successfully.")
                case "forum":
                    command = "INSERT INTO friend(user_id, friend_id) VALUES(%s, %s)"
                    self.command(command, (info["user_id"], info["friend_id"]))
                    logger.info("Insert into friend successfully.")
                case "comment":
                    command = "INSERT INTO comment(content, time, author_id, reply_id) VALUES(%s, NOW(), %s, %s)"
                    self.command(command, (info["floor"], info["content"], info["author_id"], info["post_id"]))
                    logger.info("Insert into comment successfully.")
                case _:
                    logger.error(f'''TABLE {table} DOES NOT EXIST''')
                    return False
        except Exception as e:
            logger.error(f'Other exception in sql.insert_info: {e}')

    def find_info(self, table: str, key: str, value):
        try:
            command = '''SELECT * FROM %s WHERE %s="%s"'''
            value = str(value)
            command %= table, key, value
            result = self.command(command, ())
            return result
        except Exception as e:
            logger.error(f'Other exception in sql.find_info: {e}')

    def delete_info(self, table: str, key: str, value):
        try:
            command = '''DELETE FROM %s WHERE %s="%s"'''
            value = str(value)
            command %= table, key, value
            result = self.command(command, ())
            return result
        except Exception as e:
            logger.error(f'Other exception in sql.delete_info: {e}')

    def get_table(self, table: str):
        try:
            command = "SELECT * FROM " + table
            result = self.command(command, ())
            if result:
                logger.info(f'Result in table {table}: {result}')
            return result
        except Exception as e:
            logger.error(f'Other exception in sql.get_table: {e}')
