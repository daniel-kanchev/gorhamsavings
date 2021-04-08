import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from gorhamsavings.items import Article


class gorhamsavingsSpider(scrapy.Spider):
    name = 'gorhamsavings'
    start_urls = ['https://www.gorhamsavings.bank/gsb-news-and-events/']

    def parse(self, response):
        links = response.xpath('//a[@class="read-more"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//div[@class="nav-previous"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="post-text"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
