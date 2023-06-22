import sys

import scrapy
from scrapy.crawler import CrawlerProcess
from w3lib.html import remove_tags


class JudicialYuanQASpider(scrapy.Spider):
    name = "judicial-yuan-qa"
    allowed_domains = ["www.judicial.gov.tw"]
    start_urls = ["https://www.judicial.gov.tw/tw/lp-1303-1.html"]

    def parse(self, response):
        qa_list = response.css("div.qa_list > ul > li")
        for qa in qa_list:
            yield {
                "question": qa.css("div.question a::attr(title)").get(),
                "answer": remove_tags(qa.css("div.answer > div.text").get()),
            }
        next_page = response.css('li.next a::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)


def main(saved_json):
    process = CrawlerProcess(
        {
            "USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
            "FEEDS": {saved_json: {"format": "json", "overwrite": True}},
            "FEED_EXPORT_ENCODING": "UTF-8",
        },
    )
    process.crawl(JudicialYuanQASpider)
    process.start()  # the script will block here until the crawling is finished


if __name__ == "__main__":
    main(sys.argv[1])
