# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo

class EcommerceWebPipeline:

    def __init__(self):
        self.conn = pymongo.MongoClient(
            'localhost',
            27017
        )
        db = self.conn['virginmegastore']
        self.collection = db['data']

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        convert_to_floats = ['price', 'available_stock', 'original_price']
        for i in convert_to_floats:
            value = adapter.get(i)
            if value is not None:
                # Remove any currency symbols and commas, then strip any leading/trailing whitespace
                value = value.replace('SAR', '').replace(',', '').strip()
                adapter[i] = float(value)

        img_src = adapter.get('image')
        if img_src:
            full_image_url = 'https://www.virginmegastore.sa' + img_src
            adapter['image'] = full_image_url

        brand = adapter.get('brand')
        if not brand:
            adapter.pop('brand', None)

        desc = adapter.get('description')
        if not desc:
            adapter.pop('description', None)

        original_price = adapter.get('original_price')
        if not original_price:
            adapter.pop('original_price', None)

        self.collection.insert_one(dict(item))
        return item

