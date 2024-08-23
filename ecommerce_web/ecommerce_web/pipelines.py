# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class EcommerceWebPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        specifications = {}
        specs = adapter.get('specifications')
        if specs:
            for spec in specs:
                spec_key = spec.css('div.tabsSpecification__table__cell::text').get()
                spec_value = spec.css('div.tabsSpecification__table__cell::text').getall()[1]
                if spec_key and spec_value:
                    specifications[spec_key] = spec_value
        if not specifications:
            adapter.pop('specifications', None)

        brand = adapter.get('brand')
        if not brand:
            adapter.pop('brand', None)

        desc = adapter.get('description')
        if not desc:
            adapter.pop('description', None)

        original_price = adapter.get('original_price')
        if not original_price:
            adapter.pop('original_price', None)

        return item


