import logging
from .DatabaseInterface import DatabaseInterface
import zmq
import json


logging.basicConfig(level=logging.INFO)


class StorageService:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection_timeout = 60 # in second
        self.socket = None

    def connect_db(self):
        self.dbi = DatabaseInterface(self.db_name)

    def validate_data(self):
        # check if exists already in db
        pass

    def add_record(self, data):
        logging.info(data)

    def listen_port(self):
        message = self.socket.recv_json()
        self.add_record(message)
        self.socket.send(b"Received")

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
