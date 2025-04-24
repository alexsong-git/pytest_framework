import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from data.rc_data  import chromedriver_path, url_resolution
from common.data_tool import read_data
from common.log_tool import log_tool
from common.resolution_login import resolution_login


class Auto_Test(unittest.TestCase):


    def setUp(self):

        self.data = read_data("/Users/alex/登陆数据.xlsx","RC渠道登陆数据")
        self.data_twice = []
        self.path= '/Users/alex/PycharmProjects/pytest_framework/test_report/RC_login_resolution.log'
        self.name='RC_login_resolution'
        self.log = log_tool(self.path, self.name)
        self.log.info('start')
        self.service=Service(executable_path=chromedriver_path)
        self.driver=webdriver.Chrome(service=self.service)
        self.driver.implicitly_wait(3)  # 设置隐式等待时间为3秒

    def tearDown(self):
        self.driver.quit()
        self.log.info('finish')

    def test_login(self):

        for channel,email,order in self.data:
            try:
                self.driver.get(url_resolution)
                self.assertIn("Resolution Center", self.driver.title)
                self.element=resolution_login(self.driver,email,order)
                self.assertIn(self.element,"I'm ready to submit")
                #log.info(i[0] + " " + "PASS")
            except Exception as e:
                #self.log.info(self.name+" "+channel + " " + "FAIL —— "+"data : "+ email+" "+order)
                #logger.info(e)
                self.data_twice.append([channel,email,order])
                continue

        if not self.data_twice:
            return
        for channel, email, order in self.data_twice:
            try:
                self.driver.get(url_resolution)
                self.assertIn("Resolution Center", self.driver.title)
                self.element=resolution_login(self.driver,email,order)
                self.assertIn(self.element, "I'm ready to submit")
            except Exception as e:
                self.log.error("twice_fail : " + " " + channel + " " + "FAIL —— " + "data : " + email + " " + order)
                # logger.info(e)
                continue


