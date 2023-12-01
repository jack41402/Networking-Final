import MySQLdb
import yaml


class SQL:
    def __init__(self):
        self.database = None
        self.connection()

    def connection(self):
        try:
            with open("./database/config.yaml", 'r') as stream:
                config = yaml.load(stream, Loader=yaml.FullLoader)
        except FileNotFoundError:
            print("[ERROR] FILE config.yaml NOT FOUND.")
            return False
        except yaml.YAMLError:
            print("[ERROR] CONFIG FORMAT ERROR.")
            return False
        try:
            self.database = MySQLdb.connect(**config)
        except MySQLdb.Error as e:
            print(f'[ERROR] CANNOT CONNECT TO MySQL DATABASE {config["database"]}: {e}')
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
            print(f'[ERROR] MySQL error in sql.command {command}: {e}')
        except Exception as e:
            print(f'[ERROR] Other exception in sql.command {command}: {e}')

    def insert_info(self, table: str, info: dict):
        try:
            if table == "user_information":
                command = "INSERT INTO user_information(username, password) VALUES(%s, %s)"
                self.command(command, (info["username"], info["password"]))
                print("[INFO] Insert into user_information successfully.")
            elif table == "forum":
                command = "INSERT INTO friend(user_id, friend_id) VALUES(%s, %s)"
                self.command(command, (info["user_id"], info["friend_id"]))
                print("[INFO] Insert into forum successfully.")
            elif table == "comment":
                command = "INSERT INTO comment(content, time, author_id, reply_id) VALUES(%s, NOW(), %s, %s)"
                self.command(command, (info["floor"], info["content"], info["author_id"], info["post_id"]))
                print("[INFO] Insert into comment successfully.")
            else:
                return False
        except Exception as e:
            print(f'[ERROR] Other exception in sql.insertInfo: {e}')

    def find_info(self, table: str, key: str, value):
        try:
            command = '''SELECT * FROM %s WHERE %s="%s"'''
            value = str(value)
            command %= table, key, value
            result = self.command(command, ())
            return result
        except Exception as e:
            print(f'[ERROR] Other exception in sql.findInfo: {e}')

    def delete_info(self, table: str, key: str, value):
        try:
            command = '''DELETE FROM %s WHERE %s="%s"'''
            value = str(value)
            command %= table, key, value
            result = self.command(command, ())
            return result
        except Exception as e:
            print(f'[ERROR] Other exception in sql.deleteInfo: {e}')

    def get_table(self, table: str):
        try:
            command = "SELECT * FROM " + table
            result = self.command(command, ())
            if result:
                print("result in getTable: ",  result)
            return result
        except Exception as e:
            print(f'[ERROR] Other exception in sql.getTable: {e}')
