# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy




class EcommerceWebItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    price = scrapy.Field()
    brand = scrapy.Field()
    spec_name = scrapy.Field()
    specifications = scrapy.Field()
    product_url = scrapy.Field()
    description = scrapy.Field()
    model_number = scrapy.Field()
    available_stock = scrapy.Field()
    image = scrapy.Field()
    original_price = scrapy.Field()


