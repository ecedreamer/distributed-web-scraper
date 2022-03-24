import gevent
from gevent import monkey
monkey.patch_all()

from bs4 import BeautifulSoup
import requests
import logging
import zmq
import time


logging.basicConfig(level=logging.INFO)


class WebScraperAsync:
    def __init__(self, root_url, title_class, task_count=100):
        self.root_url = root_url
        self.title_class = title_class
        self.urls = None
        self.count = 0
        self.task_count = task_count
        self.socket = None
        self.move_forward = True

    def prepare_urls(self):
        start = self.count * self.task_count + 1
        end = start + self.task_count
        self.count += 1
        self.urls = [f"{self.root_url}{i}/" for i in range(start, end)]

    def web_request(self, url):
        resp = requests.get(url)
        if resp.status_code in [404, 429]:
            return
        try:
            soup = BeautifulSoup(resp.content, "html.parser")
            title = soup.find(class_=self.title_class)
            pub_date = soup.find(class_="pub-date")
            return title.text, url, pub_date.text
        except Exception as e:
            print(e)
            return

    def forward_data(self, result):
        logging.info("Sending message to the server")
        if len(result) > 0:
            self.socket.send_json(result)
            message = self.socket.recv()
            logging.info(message)
        else:
            logging.info("Data ended")
            self.move_forward = False

    def prepare_tasks(self):
        self.prepare_urls()
        tasks = [gevent.spawn(self.web_request, url) for url in self.urls]
        return tasks

    def start_service(self):
        t1 = time.time()
        tasks = self.prepare_tasks()
        gevent.joinall(tasks)
        result = [task.value for task in tasks if task.value]
        self.forward_data(result)
        t2 = time.time()
        logging.info(f"Time taken: {t2-t1}")

    def start_loop(self):
        logging.info("Starting service")
        context = zmq.Context()
        #  Socket to talk to server
        logging.info("Connecting to storage server…")
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://192.168.1.70:5550")
        while True:
            if self.move_forward:
                self.start_service()
            else:
                break
