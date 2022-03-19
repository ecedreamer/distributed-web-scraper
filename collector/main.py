""" scrapes data from web and send it to storage service port """
import os
from lib.WebScraper import WebScraper, WebScraperAsync


def main():
    pid = os.getpid()
    print("Starting web scraping service PID:", pid)
    ss = WebScraperAsync("https://ratopati.com/story/", task_count=100)
    ss.start_loop()


if __name__ == "__main__":
    main()
