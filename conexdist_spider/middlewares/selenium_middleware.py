from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from scrapy.http import TextResponse
from scrapy.exceptions import CloseSpider
from scrapy import signals
from selenium.webdriver.chrome.options import Options
from datetime import date
import json
import time

class SeleniumMiddleware(object):

    def __init__(self, s):
        # self.exec_path = s.get('PHANTOMJS_PATH', './chromedriver.exe')
        self.exec_path = 'C:/Users/phantomjs.exe'

###########################################################

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler.settings)

        crawler.signals.connect(obj.spider_opened,
                                signal=signals.spider_opened)
        crawler.signals.connect(obj.spider_closed,
                                signal=signals.spider_closed)
        return obj

###########################################################

    def spider_opened(self, spider):
        try:
            self.d = init_driver(self.exec_path)
        except TimeoutException:
            CloseSpider('PhantomJS Timeout Error!!!')

###########################################################

    def spider_closed(self, spider):
        self.d.quit()
###########################################################
    
    def process_request(self, request, spider):
        if spider.use_selenium:
            print "############################ Received url request from scrapy #####"

            try:
                self.d.get(request.url)
                

            except TimeoutException as e:            
                raise CloseSpider('TIMEOUT ERROR')

            if request.url == "http://shop.conexdist.ro/2216-covorase-portbagaj":
                email_edit = self.d.find_element_by_xpath('//*[@id="email"]')
                pw_edit = self.d.find_element_by_xpath('//*[@id="passwd"]')
                login_button = self.d.find_element_by_xpath('//*[@id="SubmitLogin"]')
                if email_edit and pw_edit and login_button:
                    time.sleep(1)
                    email_edit.click()
                    email_edit.send_keys("david@autofarm.ro")
                    time.sleep(1)
                    pw_edit.click()
                    pw_edit.send_keys("yAKm0hgk")
                    time.sleep(1)
                    login_button.click()
                    time.sleep(2)

                lastHeight = self.d.execute_script("return document.body.scrollHeight")
                print "*** Last Height = ", lastHeight
                while True:
                    self.d.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(5)
                    newHeight = self.d.execute_script("return document.body.scrollHeight")
                    if newHeight == lastHeight:
                        break
                    lastHeight = newHeight


            resp1 = TextResponse(url=self.d.current_url,
                                body=self.d.page_source,
                                encoding='utf-8')
            resp1.request = request.copy()
            
            return resp1

###########################################################
###########################################################

def init_driver(path):

    # chrome_options = Options()
    # chrome_options.add_argument("window-size=3000,3000")
    # chrome_options.add_argument("window-position=-10000,0")
    # d = webdriver.Chrome(executable_path=path, chrome_options=chrome_options)
    d = webdriver.Firefox()
    d.set_page_load_timeout(30)

    return d