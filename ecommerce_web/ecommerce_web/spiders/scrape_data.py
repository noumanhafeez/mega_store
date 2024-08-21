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

        model_text = response.css('p.product-brandModel__item::text').getall()[2]
        model_number = model_text.split(':')[-1].strip()

        style_attribute = response.css("div.pdp_image-carousel-image.js-zoomImage.c-pointer::attr(style)").get()
        start_index = style_attribute.find("url(") + 4
        end_index = style_attribute.find(")", start_index)
        url = style_attribute[start_index:end_index]

        product = EcommerceWebItem()
        product['name'] = response.css('h1.productDetail__descriptionTitle::text').get()
        product['price'] = response.css('span.price__number.gtm-price-number::text').get()
        product['brand'] = response.css('a.product-brandModel__link::text').get()
        product['color'] = response.xpath("//div[@class='tabsSpecification__table__row']/div[2]/text()").get()
        product['description'] = ' '.join(response.css('div.tabContent__paragraph.tabsDescription__longDescription__inner p::text').getall())
        product['model_number'] = model_number
        product['image'] = url
        yield product
