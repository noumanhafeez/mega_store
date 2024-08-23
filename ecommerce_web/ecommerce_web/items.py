import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join

def clean_text(value):
    return value.strip()

def convert_to_float(value):
    return float(value.replace('SAR', '').replace(',', '').strip())

def extract_model_number(value):
    return value.split(':')[-1].strip()

def extract_image_url(style_attr):
    start_index = style_attr.find("url(") + 4
    end_index = style_attr.find(")", start_index)
    return style_attr[start_index:end_index]

class EcommerceWebItem(scrapy.Item):
    name = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(clean_text, convert_to_float), output_processor=TakeFirst())
    brand = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    specifications = scrapy.Field(output_processor=TakeFirst())
    product_url = scrapy.Field(output_processor=TakeFirst())
    description = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=Join())
    model_number = scrapy.Field(input_processor=MapCompose(clean_text, extract_model_number), output_processor=TakeFirst())
    available_stock = scrapy.Field(input_processor=MapCompose(clean_text, convert_to_float), output_processor=TakeFirst())
    image = scrapy.Field(input_processor=MapCompose(extract_image_url), output_processor=TakeFirst())
    original_price = scrapy.Field(input_processor=MapCompose(clean_text, convert_to_float), output_processor=TakeFirst())
