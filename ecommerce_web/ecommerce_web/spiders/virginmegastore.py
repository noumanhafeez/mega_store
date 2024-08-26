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
        base_url = 'https://www.virginmegastore.sa'

        # Find all category links in the navigation
        category_links = response.css('a.mainNavigation__subLink.mainNavigation__subLink--l3::attr(href)').getall()

        # Define a list of patterns or exact links to ignore
        ignore_patterns = ['/en/apple-shop', '/en/sale']

        # Loop through each category link and follow it, ignoring unwanted links
        for link in category_links:
            if any(pattern in link for pattern in ignore_patterns):
                continue  # Skip this link if it matches any pattern in ignore_patterns

            full_link = f"https://www.virginmegastore.sa/en{link}"
            yield response.follow(url=full_link, callback=self.parse_product_page)

    def parse_product_page(self, response):
        """
            Parses product listing pages to find individual product links and follows them.
        """

        for item in response.css('li.product-list__item.g-elem.m2.md2.g-row--margin-x.product-item'):
            product = item.css('li.product-list__item.g-elem.m2.md2.g-row--margin-x.product-item a::attr(href)').get()
            full_product_link = f"https://www.virginmegastore.sa{product}"
            yield response.follow(url=full_product_link, callback=self.product_data)

        if response.css('a.pagination__link::attr(href)'):
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
        loader.add_css('description', 'div.tabContent__paragraph.tabsDescription__longDescription__inner p::text')
        loader.add_css('product_url', 'link[rel="canonical"]::attr(href)')
        loader.add_css('model_number', 'p.product-brandModel__item::text')
        loader.add_css('specifications', 'div.tabsSpecification__table__cell::text')
        loader.add_css('image', 'img.pdp-thumbs__image.w-100::attr(src)')
        loader.add_css('available_stock', 'input#pdpAddtoCartInput::attr(data-max)')

        size_links = response.css('a.productDetail__variantItem::attr(href)').getall()
        for size_link in size_links:
            full_size_link = response.urljoin(size_link)
            yield response.follow(full_size_link, callback=self.product_data)

        yield loader.load_item()
