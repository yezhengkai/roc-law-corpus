# References:
# - https://stackoverflow.com/questions/71060808/how-to-use-scrapy-to-parse-pdfs-without-a-specific-pdf-link
# - https://stackoverflow.com/questions/57245315/using-scrapy-how-to-download-pdf-files-from-some-extracted-links
import sys
from urllib.parse import parse_qs, urlparse

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.pipelines.files import FilesPipeline

# 106~111年 公務人員特種考試司法官考試（第一試）、專門職業及技術人員高等考試律師考試（第一試）
START_URLS = [
    f"https://wwwq.moex.gov.tw/exam/wFrmExamQandASearch.aspx?y={year}&e={year - 1911}120"
    for year in range(2017, 2022 + 1)
]


class PDFPipeline(FilesPipeline):
    # to save with the name of the pdf from the website instead of hash
    def file_path(self, request, response=None, info=None, *, item=None):
        return item["filename"]


class MOEXAnswerSpider(scrapy.Spider):
    name = "moex-answer"
    allowed_domains = ["wwwq.moex.gov.tw/"]
    start_urls = START_URLS

    def parse(self, response):
        row_list = response.xpath(
            '//*[@id="ctl00_holderContent_tblExamQand"]/tr[position() > 1]'
        )
        for row in row_list:
            if row.xpath("td[@class]//label/text()").get() is not None:
                category = row.xpath("td[@class]//label/text()").get().replace("_", "-")
                continue

            subject = row.xpath("td/table/tr/td/label/text()").get()
            # Download only the exams held in 2022(111) years and related to law
            if "法" not in subject:
                continue

            question_uri = response.urljoin(
                row.xpath('td/table/tr/td[@class="exam-question-ans"]')[0]
                .xpath("a/@href")
                .get()
            )
            # Download the pre-revision answer as it is easier to extract the text
            answer_uri = response.urljoin(
                row.xpath('td/table/tr/td[@class="exam-question-ans"]')[1]
                .xpath("a/@href")
                .get()
            )  # 答案的PDF連結
            # answer_uri = response.urljoin(
            #     row.xpath('td/table/tr/td[@class="exam-question-ans"]')[2]
            #     .xpath("a/@href")
            #     .get()
            # )  # 更正答案的PDF連結
            if answer_uri is None:
                continue

            roc_year = parse_qs(urlparse(response.url).query)["e"][0][0:3]

            yield {
                "filename": f"{roc_year}_{category}_{subject}_question.pdf",
                "file_urls": [question_uri],
            }

            yield {
                "filename": f"{roc_year}_{category}_{subject}_answer.pdf",
                "file_urls": [answer_uri],
            }


def main(storage_dir):
    process = CrawlerProcess(
        {
            "ITEM_PIPELINES": {PDFPipeline: 100},
            "FILES_STORE": storage_dir,
            "MEDIA_ALLOW_REDIRECTS": True,
        },
    )
    process.crawl(MOEXAnswerSpider)
    process.start()  # the script will block here until the crawling is finished


if __name__ == "__main__":
    main(sys.argv[1])
