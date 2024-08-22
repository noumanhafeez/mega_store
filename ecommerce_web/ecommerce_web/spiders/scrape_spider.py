import scrapy
from ecommerce_web.items import EcommerceWebItem
from scrapy.loader import ItemLoader

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
            print(f"Category links{link}")
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
        product = EcommerceWebItem()
        product['name'] = response.css('h1.productDetail__descriptionTitle::text').get()
        product['original_price'] = response.css('span.price__number.price__number--strike-through.__number.__number--strike-through.gtm-price-num-strike-through::text').get()
        product['price'] = response.css('span.price__number.gtm-price-number::text').get()
        product['brand'] = response.css('a.product-brandModel__link::text').get()
        product['specifications'] = response.css('div.tabsSpecification__table__row')
        product['description'] = response.css(
            'div.tabContent__paragraph.tabsDescription__longDescription__inner p::text').getall()
        product['model_number'] = response.css('p.product-brandModel__item::text').getall()
        product['image'] = response.css("div.pdp_image-carousel-image.js-zoomImage.c-pointer::attr(style)").get()
        product['product_url'] = response.css('link[rel="canonical"]::attr(href)').get()
        product['available_stock'] = response.css('input#pdpAddtoCartInput::attr(data-max)').get()

        yield product