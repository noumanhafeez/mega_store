import scrapy
from ecommerce_web.items import EcommerceWebItem
from scrapy.loader import ItemLoader

class CategorySpider(scrapy.Spider):
    """
       Spider for scraping product information from Virgin Megastore.
    """

    name = 'virginmegastore'
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
            Parses the data from a specific size variant product page using ItemLoader.
        """

        loader = ItemLoader(item=EcommerceWebItem(), response=response)

        loader.add_css('name', 'h1.productDetail__descriptionTitle::text')
        loader.add_css('original_price', 'span.price__number.price__number--strike-through.__number.__number--strike-through.gtm-price-num-strike-through::text')
        loader.add_css('price', 'span.price__number.gtm-price-number::text')
        loader.add_css('brand', 'a.product-brandModel__link::text')
        loader.add_css('specifications', 'div.tabsSpecification__table__row')
        loader.add_css('description', 'div.tabContent__paragraph.tabsDescription__longDescription__inner p::text')
        loader.add_css('model_number', 'p.product-brandModel__item::text')
        loader.add_css('product_url', 'link[rel="canonical"]::attr(href)')
        loader.add_css('image', "div.pdp_image-carousel-image.js-zoomImage.c-pointer::attr(style)")
        loader.add_css('available_stock', 'input#pdpAddtoCartInput::attr(data-max)')

        yield loader.load_item()
