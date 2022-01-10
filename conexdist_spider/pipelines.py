# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
from scrapy.exporters import XmlItemExporter
from scrapy import signals

class ConexdistSpiderPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='test', charset='utf8')
        self.conn.ping(True)
        self.cursor = self.conn.cursor()
        self.files = {}
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        file = open('temp.xml' , 'w+b')
        self.files[spider] = file
        self.exporter = XmlItemExporter(file, item_element='AUCTION', root_element='OKAZII' )
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()
        with open('temp.xml', 'r') as myfile:
            data = myfile.read().replace('&lt;', '<').replace('&gt;', '>')
            result_file = open('%s_products.xml' % spider.name, 'w+b')
            result_file.write(data)
            result_file.close()


    def process_item(self, item, spider):
        self.exporter.export_item(item)
        try:
            key_txt = ','.join(item.keys()).lower()
            values = ""
            for val in item.values():
                if isinstance(val,float) or isinstance(val,int):
                    val = str(val)
                else:
                    if val == None:
                        val = "''"
                    else:
                        val = "'" + val + "'"
                values = values + ',' + val
            values = values[1:]

            # values = str(','.join(item.values())).encode('utf-8')
            sql = "INSERT INTO products (%s) VALUES (%s)"%(key_txt, values)
            self.cursor.execute(sql)
            self.conn.commit()
            return item
        except MySQLdb.Error, e:
            print ("MYSQL ERROR %d: %s" % (e.args[0], e.args[1]))
            return item

    # def process_item(self, item, spider):
    #     return item

