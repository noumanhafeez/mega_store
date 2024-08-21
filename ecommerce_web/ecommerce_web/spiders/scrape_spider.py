import scrapy
from ecommerce_web.items import EcommerceWebItem

class CategorySpider(scrapy.Spider):
    """
       Spider for scraping product information from Virgin Megastore.
    """

    name = 'product_scrape'
    start_urls = ['https://www.virginmegastore.sa/en']

    def parse(self, response):
        """
            Parses the main page to find category links and follows them.
        """

        for link in response.css('a.mainNavigation__subLink.mainNavigation__subLink--l3::attr(href)'):
            full_link = response.urljoin(link.get())
            yield response.follow(url=full_link, callback=self.parse_product_page)

    def parse_product_page(self, response):
        """
            Parses product listing pages to find individual product links and follows them.
        """

        for item in response.css('li.product-list__item.g-elem.m2.md2.g-row--margin-x.product-item'):
            product = item.css('li.product-list__item.g-elem.m2.md2.g-row--margin-x.product-item a::attr(href)').get()
            full_product_link = f"https://www.virginmegastore.sa{product}"
            yield response.follow(url=full_product_link, callback=self.product_data)

        next_page = response.css('a.pagination__link::attr(href)').get()
        if next_page:
            full_link = response.urljoin(next_page)
            yield response.follow(full_link, callback=self.parse_product_page)

    def product_data(self, response):
        """
            Extracts data from individual product pages and yields it as an item.
        """

        # Extract the third item from the model text list (which is assumed to be in the format "Key: Value").
        # Split the text by ':' and get the part after the last ':' as the model number.
        model_text = response.css('p.product-brandModel__item::text').getall()[2]
        model_number = model_text.split(':')[-1].strip()

        # Extract the 'style' attribute value from the image element.
        style_attribute_img = response.css("div.pdp_image-carousel-image.js-zoomImage.c-pointer::attr(style)").get()
        # Extract the URL from the 'style' attribute value.
        # The URL is enclosed in 'url()' which we need to locate and extract.
        start_index = style_attribute_img.find("url(") + 4  # Find the start index of the URL within the 'url()' string
        end_index = style_attribute_img.find(")", start_index)  # Find the end index of the URL
        image_url = style_attribute_img[start_index:end_index]  # Extract the URL substring

        product = EcommerceWebItem()
        product['name'] = response.css('h1.productDetail__descriptionTitle::text').get()
        product['price'] = response.css('span.price__number.gtm-price-number::text').get()
        brand = response.css('a.product-brandModel__link::text').get()
        if brand:
            product['brand'] = brand

        specifications = {}
        specs = response.css('div.tabsSpecification__table__row')
        for spec in specs:
            spec_key = spec.css('div.tabsSpecification__table__cell::text').get()
            spec_value = spec.css('div.tabsSpecification__table__cell::text').getall()[1]
            if spec_key and spec_value:  # Check if both spec_name and spec_value are not empty
                specifications[spec_key] = spec_value
        if specifications:
            product['specifications'] = specifications

        description = response.css('div.tabContent__paragraph.tabsDescription__longDescription__inner p::text').getall()
        if description:
            product['description'] = description

        product['model_number'] = model_number
        product['image'] = image_url
        product['product_url'] = response.css('link[rel="canonical"]::attr(href)').get()
        product['available_stock'] = response.css('input#pdpAddtoCartInput::attr(data-max)').get()

        yield product
