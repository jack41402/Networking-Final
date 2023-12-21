from LibraryX.API import SQL

database = SQL.SQL()


def read_file():
    command = "INSERT INTO test(data) VALUES(%s)"
    path = r"D:\GitHub\Networking-Final\File\client\test60.wav"
    with open(path, "rb") as file:
        content = file.read()
        print(content)
        database.command(command, (content,))


def write_file():
    command = "SELECT * FROM test WHERE id=6"
    path = r"D:\GitHub\Networking-Final\File\server\test60.wav"
    with open(path, "wb") as file:
        content = database.command(command, ())[0][1]
        print(content)
        file.write(content)


if __name__ == "__main__":
    from datetime import datetime


    class TimeInfo:
        def __init__(self, time, num):
            self.time = time
            self.num = num

        def __lt__(self, other):
            return self.time < other.time


    # Create a list of TimeInfo instances
    time_list = [
        TimeInfo(datetime(2023, 12, 1, 10, 30), 2),
        TimeInfo(datetime(2022, 1, 1, 9, 30), 3),
        TimeInfo(datetime(2023, 1, 1, 11, 30), 1)
    ]

    # Sort the list using the __lt__ method defined in the TimeInfo class
    time_list.sort()

    # Printing the sorted list
    for time_info in time_list:
        print(time_info.time)
