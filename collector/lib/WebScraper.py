import time

import gevent
from gevent import monkey
monkey.patch_all()

from bs4 import BeautifulSoup
import requests
import logging
import zmq
import json


logging.basicConfig(level=logging.INFO)


class WebScraper:
    def __init__(self, root_url):
        self.root_url = root_url
        self.url = None
        self.count = 0
        self.move_forward = True
        self.last_empty_count = 0
        self.last_empty_data = None

    def prepare_url(self):
        self.count += 1
        return f"{self.root_url}{self.count}/"

    def collect(self):
        """ collect from internet """
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        try:
            result = soup.find(class_='article-head').find("h1")
            return result.text
        except Exception as e:
            print(e)
            if self.last_empty_count == 0:
                self.last_empty_data = self.count - 1
            self.last_empty_count += 1
            if self.last_empty_count >= 100:
                self.move_forward = False
            return None

    def forwarder(self, result):
        """ send to zmq port """
        if result:
            with open("sample.txt", "a") as file_object:
                file_object.write("\n")
                file_object.write(f"{self.count}, {self.url}, {result}")

    def start_service(self):
        if self.move_forward:
            self.url = self.prepare_url()
            result = self.collect()
            self.forwarder(result)
        else:
            return "break"

    def start_loop(self):
        """ start loop """
        while True:
            ret = self.start_service()
            if ret == "break":
                print(self.last_empty_data, self.last_empty_count, self.count)
                break


class WebScraperAsync:
    def __init__(self, root_url, task_count=100):
        self.root_url = root_url
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

    @staticmethod
    def web_request(url):
        resp = requests.get(url)
        if resp.status_code in [404, 429]:
            return
        return url, resp.status_code

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
        tasks = [gevent.spawn(WebScraperAsync.web_request, url) for url in self.urls]
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
        print("Connecting to storage server…")
        self.socket = context.socket(zmq.REQ)
        self.socket.connect("tcp://192.168.1.70:5550")
        while True:
            if self.move_forward:
                self.start_service()
            else:
                break
