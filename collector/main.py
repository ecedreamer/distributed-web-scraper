""" scrapes data from web and send it to storage service port """
import os
from lib.WebScraper import WebScraperAsync

''' url_to_scrap =https://www.example.com/story/ if its news can be available on https://www.example.com/story/1/ or 
https://www.example.com/story/2/ '''
source_url_list = (
    {
        "url_to_scrap": "https://www.example.com/story/",
        "html_content_title_class": "news-big-title"
    },
)

URL_TO_SCRAP = source_url_list[0]["url_to_scrap"]
CONTENT_TITLE_CLASS = source_url_list[0]["html_content_title_class"]


def main():
    pid = os.getpid()
    print("Starting web scraping service PID:", pid)
    ss = WebScraperAsync(URL_TO_SCRAP, title_class=CONTENT_TITLE_CLASS, task_count=100)
    ss.start_loop()


if __name__ == "__main__":
    main()
