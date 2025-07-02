import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from Test_Data.rc_data  import chromedriver_path, url_resolution
from common.data_tool  import read_data
from common.log_tool import log_tool
from common.resolution_login import resolution_login



#path= '/Users/alex/PycharmProjects/Seel_Project/test_report/test_log_resolution.log'
#name='test_log_resolution'
#log=log_tool(path,name)
data = read_txt()
data_twice=[]

class Auto_Test(unittest.TestCase):


    def setUp(self):

        self.path='/Users/alex/PycharmProjects/Seel_Project/test_report/test_log_resolution.log'
        self.name='test_log_resolution'
        self.log = log_tool(self.path, self.name)
        self.log.info('start')
        self.service=Service(executable_path=chromedriver_path)
        self.driver=webdriver.Chrome(service=self.service)
        self.driver.implicitly_wait(3)  # 设置隐式等待时间为3秒

    def test_login(self):

        for channel,email,order in data:
            try:
                self.driver.get(url_resolution)
                self.assertIn("Resolution Center", self.driver.title)
                self.element=resolution_login(self.driver,email,order)
                self.assertIn(self.element,"I'm ready to submit")
                #log.info(i[0] + " " + "PASS")
            except Exception as e:
                self.log.info(self.name+" "+channel + " " + "FAIL —— "+"data : "+ email+" "+order)
                #logger.info(e)
                data_twice.append([channel,email,order])
                continue

        if not data_twice:
            return
        for channel, email, order in data_twice:
            try:
                self.driver.get(url_resolution)
                self.assertIn("Resolution Center", self.driver.title)
                self.element=resolution_login(self.driver,email,order)
                self.assertIn(self.element, "I'm ready to submit")
            except Exception as e:
                self.log.error("twice_fail : " + self.name + " " + channel + " " + "FAIL —— " + "data : " + email + " " + order)
                # logger.info(e)
                continue

    def tearDown(self):
        self.driver.quit()
        self.log.info('finish')

