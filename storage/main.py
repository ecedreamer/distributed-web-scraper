""" get data from collector and stores it to sqlite3 database """
from lib.StorageService import StorageService


def main():
    service = StorageService(db_name="news.db")
    service.start_loop()


if __name__ == "__main__":
    main()
