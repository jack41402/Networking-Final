from LibraryX.API import SQL

database = SQL.SQL()


def read_file():
    command = "INSERT INTO test(data) VALUES(%s)"
    path = r"D:\GitHub\Networking-Final\File\server\shark.jpg"
    with open(path, "rb") as file:
        content = file.read()
        print(content)
        database.command(command, (content,))


def write_file():
    command = "SELECT * FROM test WHERE id=7"
    path = r"D:\GitHub\Networking-Final\File\client\shark.jpg"
    with open(path, "wb") as file:
        content = database.command(command, ())[0][1]
        print(content)
        file.write(content)


if __name__ == "__main__":
    write_file()
