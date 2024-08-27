# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo
import psycopg2

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


class EcommerceWebPipelineUsingPostSQL:

    def __init__(self):
        ## Connection Details
        hostname = 'localhost'
        username = 'postgres'
        password = 'nouman123'  # your password
        database = 'data'

        ## Create/Connect to database
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)

        ## Create cursor, used to execute commands
        self.cur = self.connection.cursor()

        self.cur.execute("""
                CREATE TABLE IF NOT EXISTS data( 
                    name text,
                    original_price int,
                    price int,
                    brand text,
                    description text,
                    product_url text,
                    model_number text,
                    specifications text,
                    image text,
                    available_stock int
                )
                """)

    def process_item(self, item, spider):

        adapter = ItemAdapter(item)
        img_src = adapter.get('image')
        if img_src:
            full_image_url = 'https://www.virginmegastore.sa' + img_src
            adapter['image'] = full_image_url

        ## Define insert statement
        self.cur.execute(
            """
            INSERT INTO data (
                name, original_price, price, brand, description,
                product_url, model_number, specifications, image,
                available_stock
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                item.get("name"),
                item.get("original_price", 0),
                item.get("price", 0),
                item.get("brand", None),
                item.get("description", None),
                item.get("product_url", None),
                item.get("model_number", None),
                item.get("specifications", None),
                item.get("image", None),
                item.get("available_stock", 0)
            )
        )

        ## Execute insert of data into database
        self.connection.commit()
        return item

    def close_spider(self, spider):
        ## Close cursor & connection to database
        self.cur.close()
        self.connection.close()

