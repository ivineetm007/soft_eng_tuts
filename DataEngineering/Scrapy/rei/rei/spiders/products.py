import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class ProductsSpider(scrapy.CrawlSpider):
    name = "products"
    allowed_domains = ["rei.com"]
    start_urls = ["https://www.rei.com/c/camping-and-hiking/f/scd-deals"]

    rules = (
        Rule(LinkExtractor(allow=(r"page=",))),
        Rule(LinkExtractor(allow=(r"product=",)), callback="parse_item"),
    )

    def parse_item(self, response):
        '''
            response.css("h1#product-page-title::text").get()
            response.css("span#buy-box-product-price::text").get()
            response.css("span#product-item-number::text").get()
            response.css("span.cdr-rating__number_13-5-3::text").get()
        '''
        yield {
            "title": response.css("h1#product-page-title::text").get(),
            "price": response.css("span#buy-box-product-price::text").get(),
            "item_no": response.css("span#product-item-number::text").get(),
            "rating": response.css("span.cdr-rating__number_13-5-3::text").get(),
        }
