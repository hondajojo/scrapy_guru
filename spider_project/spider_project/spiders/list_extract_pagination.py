# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy.http.request import Request
from ..items import SpiderProjectItem

from six.moves.urllib import parse
import re


class Basic_extractSpider(scrapy.Spider):
    taskid = "list_extract_pagination"
    name = taskid
    entry = "content/list_basic/1"

    def start_requests(self):
        prefix = self.settings["WEB_APP_PREFIX"]
        result = parse.urlparse(prefix)
        base_url = parse.urlunparse(
            (result.scheme, result.netloc, "", "", "", "")
        )
        url = parse.urljoin(base_url, self.entry)
        yield Request(
            url=url,
            callback=self.list_page
        )

    def list_page(self, response):
        for each in response.css('tbody td a::attr(href)').extract():
            sku = re.findall(r'\d+', each)[0]
            meta = {'sku': sku}
            url = response.urljoin(each)
            yield Request(
                url=url,
                callback=self.parse_entry_page,
                meta=meta,
            )

        page_data = json.loads(response.css('#page_data::text').extract_first())
        now_page = page_data['page']
        pages = page_data['pages']
        if now_page < pages:
            page_entry = "/content/list_basic/%s" % str(int(now_page) + 1)
            next_url = response.urljoin(page_entry)
            yield Request(
                url=next_url,
                callback=self.list_page,
            )

    def parse_entry_page(self, response):
        item = SpiderProjectItem()
        item["taskid"] = self.taskid
        data = {}
        price = response.css('.product-price::text').extract()
        title = response.css('.product-title::text').extract()
        data["price"] = price
        data["title"] = title
        data['sku'] = response.meta['sku']

        item["data"] = data
        yield item

