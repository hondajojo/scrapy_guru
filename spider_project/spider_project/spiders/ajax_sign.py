# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy.http.request import Request
from ..items import SpiderProjectItem

from six.moves.urllib import parse
from werkzeug.http import parse_cookie
import hashlib


class Basic_extractSpider(scrapy.Spider):
    taskid = "ajax_sign"
    name = taskid
    entry = "content/detail_sign"
    ajax_entry = "/content/ajaxdetail_sign"

    def start_requests(self):
        prefix = self.settings["WEB_APP_PREFIX"]
        result = parse.urlparse(prefix)
        base_url = parse.urlunparse(
            (result.scheme, result.netloc, "", "", "", "")
        )
        url = parse.urljoin(base_url, self.entry)
        yield Request(
            url=url,
            callback=self.parse_detail_page
        )

    def parse_detail_page(self, response):
        description = response.css("section.product-info li::text").extract()
        meta = {'description': description}
        token = self.get_dict_cookies(response)['token']
        m = hashlib.md5()
        m.update(token)
        sign = m.hexdigest()
        query = parse.urlencode({'sign': sign})

        result = parse.urlparse(response.url)
        url = parse.urlunparse(
            (result.scheme, result.netloc, self.ajax_entry, "", query, "")
        )
        headers = {
            "X-Requested-With": "XMLHttpRequest",
        }

        yield Request(
            url=url,
            callback=self.parse_entry_page,
            meta=meta,
            headers=headers,
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
        data['description'] = response.meta['description']

        item["data"] = data
        yield item

    def get_dict_cookies(self, response):
        cookies = {}
        _cookies = response.headers.getlist('Set-Cookie')
        for _cookie in _cookies:
            cookies.update(parse_cookie(_cookie))
        return cookies
