import scrapy
from urlparse import urlparse
from scrapy import Request
from scrapy.utils.response import open_in_browser
from collections import OrderedDict
import csv

class CategoriesOfabcdin_cl(scrapy.Spider):

	name = "conexdist"
	f = open('./categorii_conext.csv')
	csv_items1 = csv.DictReader(f)
	start_urls=[]
	for i, row in enumerate(csv_items1):
		start_urls.append(row['Link'])
	#start_urls = ('http://shop.conexdist.ro/2216-covorase-portbagaj',)

	use_selenium = True

	def start_requests(self):
		for url in self.start_urls:
			yield Request(url, callback=self.parse)

	def parse(self, response):
		products = response.xpath('//div[contains(@class, "product-row")]')
		parent_category = response.xpath('//div[contains(@class, "breadcrumb")]/a[2]/text()').extract_first()
		category = response.xpath('//div[contains(@class, "container")]/h2/text()').extract_first()
		for div_product in products:
			candiate = div_product.xpath('.//span[@class="product-list-quantity"]/strong/text()').extract_first()
			if candiate and int(candiate.replace('>', '')) < 1:
				continue
			item = OrderedDict()
			# code = div_product.xpath('.//span[@class="product-list-cod-producator"]/strong/text()').extract_first()
			# code_len = len(code)
			# new_code_int = int(code) + 99
			# new_code = str(new_code_int)
			# new_code_len = len(str(new_code_int))
			# if code_len > new_code_len:
			# 	for i in range(code_len - new_code_len):
			# 		new_code = "0" + new_code
			brand = div_product.xpath('.//span[@class="product-list-brand"]/strong/text()').extract_first()
			item['UNIQUEID'] = div_product.xpath('.//span[@class="product-list-cod-producator"]/strong/text()').extract_first()
			item['TITLE'] = "<![CDATA[" + div_product.xpath('.//h5[@class="product-list-name"]/a/text()').extract_first()+ " " + brand + "]]>"
			item['CATEGORY'] = "<![CDATA[" + parent_category + " | " + category + "]]>"
			item['DESCRIPTION'] = "<![CDATA[" + div_product.xpath('.//div[@class="product-list-description"]/text()').extract_first() + "]]>"
			item['PRICE'] = float(div_product.xpath('.//span[@class="price"]/text()').extract_first().replace('lei', '').replace(',', '.'))
			item['CURRENCY'] = "RON"
			item["AMOUNT"] = 10
			item["BRAND"] = "<![CDATA[" + div_product.xpath('.//span[@class="product-list-brand"]/strong/text()').extract_first() + "]]>"
			item['PHOTOS'] = div_product.xpath('.//a[@class="fancybox thickbox shown"]/@href').extract_first()
			item['STATE'] = 1
			item['INVOICE'] = 1
			item['WARRANTY'] = 1
			item['FORUM'] = 2
			item['REPOST'] = 2

			item_url = div_product.xpath('.//h5[@class="product-list-name"]/a/@href').extract_first()

			yield Request(item_url, callback=self.final_parse, meta={'item': item})

	def final_parse(self, response):
		item = response.meta['item']
		parent_category = response.xpath('//div[contains(@id, "idTab1")]/ul/li/text()').extract()
		if len(parent_category) > 0:
			description = '<br>'.join(parent_category)
			item['DESCRIPTION'] = description

		table_headers = response.xpath('//table[@class="table table-bordered table-condensed tabel-vehicule"]/thead/tr/th/text()').extract()
		table_rows= response.xpath('//table[@class="table table-bordered table-condensed tabel-vehicule"]/tbody/tr')
		for row in table_rows:
			values = row.xpath('.//td/text()').extract()
			for i, val in enumerate(table_headers):
				item[table_headers[i].replace(' ', '_')] = row.xpath('.//td['+ str(i+1) +']/text()').extract_first()
			yield item