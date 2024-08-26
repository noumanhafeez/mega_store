import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join

def clean_text(value):
    return value.strip()

def extract_model_number(value):
    return value.split(':')[-1].strip()

class EcommerceWebItem(scrapy.Item):
    name = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    brand = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    specifications = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=Join())
    product_url = scrapy.Field(output_processor=TakeFirst())
    description = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=Join())
    model_number = scrapy.Field(input_processor=MapCompose(clean_text, extract_model_number), output_processor=TakeFirst())
    available_stock = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    image = scrapy.Field(output_processor=TakeFirst())
    original_price = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
