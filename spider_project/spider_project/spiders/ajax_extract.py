# -*- coding: utf-8 -*-
"""
http://scrapy-guru.readthedocs.io/en/latest/tasks/ajax_extract.html
"""
import json

import scrapy
from scrapy.http.request import Request
from ..items import SpiderProjectItem

from six.moves.urllib import parse


class Basic_extractSpider(scrapy.Spider):
    taskid = "ajax_extract"
    name = taskid
    entry = "content/detail_ajax"
    ajax_entry = "content/ajaxdetail"

    def start_requests(self):
        prefix = self.settings["WEB_APP_PREFIX"]
        result = parse.urlparse(prefix)
        base_url = parse.urlunparse(
            (result.scheme, result.netloc, "", "", "", "")
        )
        url = parse.urljoin(base_url, self.ajax_entry)
        yield Request(
            url=url,
            callback=self.parse_entry_page
        )

    def parse_entry_page(self, response):
        item = SpiderProjectItem()
        item["taskid"] = self.taskid
        data = {}
        json_data = json.loads(response.body)
        price = json_data['price']
        title = json_data['title']
        data["price"] = price
        data["title"] = title

        item["data"] = data
        yield item

