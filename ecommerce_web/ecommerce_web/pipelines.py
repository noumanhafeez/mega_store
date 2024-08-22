# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class EcommerceWebPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        convert_to_floats = ['price', 'available_stock', 'original_price']
        for i in convert_to_floats:
            value = adapter.get(i)
            if value is not None:
                # Remove any currency symbols and commas, then strip any leading/trailing whitespace
                value = value.replace('SAR', '').replace(',', '').strip()
                adapter[i] = float(value)

        model_texts = adapter.get('model_number')
        model_text = model_texts[2]
        model_number = model_text.split(':')[-1].strip()
        adapter['model_number'] = model_number

        img_style = adapter.get('image')
        start_index = img_style.find("url(") + 4  # Find the start index of the URL within the 'url()' string
        end_index = img_style.find(")", start_index)  # Find the end index of the URL
        image_url = img_style[start_index:end_index]  # Extract the URL substring
        adapter['image'] = image_url

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


