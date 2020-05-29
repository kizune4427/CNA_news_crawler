from time import sleep
import urllib.request as req
from urllib.parse import urljoin
import json
import bs4
import csv
import re
import os
from datetime import datetime, timedelta

base_url = "https://www.cna.com.tw/news/aall/"

index_start = 2


def date_format(date, index):
    return date.strftime('%Y%m%d') + "{:04d}.aspx".format(index)


def write_to_csv(date, category, title, content):
    with open("cna_news.csv", "a", encoding="utf-8") as f:
        csv_file = csv.writer(f)
        csv_file.writerow([date, category, title, content])


def get_news(year_start, month_start, day_start, n_days):
    date_start = datetime(year_start, month_start, day_start)
    days_count = 0
    current_date = date_start

    while (days_count < n_days):  # 730 days limit
        current_index = index_start
        news_count = 0

        # while this index can be found
        while True:
            tail_url = date_format(current_date, current_index)
            target_url = urljoin(base_url, tail_url)

            request = req.Request(target_url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
            })

            try:
                with req.urlopen(request) as response:
                    mainPage = response.read().decode("utf-8")
            except:  # current index missing
                current_index += 1
                continue

            root = bs4.BeautifulSoup(mainPage, "html.parser")

            # date
            date = current_date.strftime('%Y-%m-%d')

            # title, category
            raw_title = root.find("title").get_text().strip()
            raw_title = raw_title.split("|")

            title = raw_title[0].strip()
            # exclude these titles
            title_exclude_list = ["大樂透", "今彩", "威力彩", "雙贏彩"]
            for t in title_exclude_list:
                if t in title:
                    continue

            category = raw_title[1].strip()
            # not going to get these categories
            cat_exclude_list = ["證券", "娛樂", "產經"]
            if category in cat_exclude_list:
                continue

            # content
            contents = []

            # find div, class_="paragraph"
            paragraphs = root.find('div', class_="paragraph").find_all('p')
            for p in paragraphs:
                text = p.get_text()

                # clean the text
                text = re.sub(r"（.*報導）", "", text)
                text = re.sub(r"（中央社.*）", "", text)
                text = re.sub(r"（\w+：.*\d+", "", text)

                contents.append(text)
            content = " ".join(contents)

            write_to_csv(date, category, title, content)
            news_count += 1

            if (current_index % 10 == 0):
                sleep(2)

            # get first 240 for now
            if (current_index > 240):
                break

            current_index += 1

        print("total news:", news_count)
        current_date = current_date - timedelta(days=1)
        days_count += 1


if __name__ == "__main__":
    get_news(2020, 5, 12, 1)
    print("Complete!")
