import logging
from .DatabaseInterface import DatabaseInterface
import zmq


logging.basicConfig(level=logging.INFO)


class StorageService:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection_timeout = 60 # in second
        self.socket = None
        self.dbi = DatabaseInterface(self.db_name)
        self.dbi.connect()

    def validate_data(self):
        # check if exists already in db
        pass

    def add_record(self, data):
        self.dbi.add_many(data)

    def listen_port(self):
        message = self.socket.recv_json()
        if message:
            self.socket.send(b"Received")
            self.add_record(message)


    def start_loop(self):
        logging.info("Starting storage service")
        context = zmq.Context()
        self.socket = context.socket(zmq.REP)
        logging.info("Starting zmq server on port 5550")
        try:
            self.socket.bind("tcp://192.168.1.70:5550")
        except Exception as e:
            print(e)
            return
        while True:
            self.listen_port()
