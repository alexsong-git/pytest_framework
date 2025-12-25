import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from Test_Data.rc_data  import chromedriver_path,url_resolve
from common.data_tool import read_data
from common.log_tool import log_tool
from common.resolve_login import resolve_login
import time


class Auto_Test(unittest.TestCase):


    def setUp(self):

        self.data = read_data("/Users/alex/PycharmProjects/pytest_framework/Test_Data/登陆数据.xlsx","RC渠道登陆数据")
        self.data_twice = []
        self.path = '/Users/alex/PycharmProjects/pytest_framework/Test_Log/RC_login_resolve.log'
        self.name = 'RC_login_resolve'
        self.log = log_tool(self.path, self.name)
        self.log.info('start')
        #self.gray = input("Is gray? 1=Yes 0=No : ")
        self.service=Service(executable_path=chromedriver_path)
        self.driver=webdriver.Chrome(service=self.service)
        self.driver.implicitly_wait(3)  # 设置隐式等待时间为10秒

    def tearDown(self):
        self.driver.quit()
        self.log.info('finish')

    def testlogin(self):

        for channel,email,order in self.data:
            try:
                self.driver.get(url_resolve)
                self.assertIn("Resolution Center", self.driver.title)
                self.driver=resolve_login(self.driver,email,order)
                time.sleep(3)
                self.element = self.driver.find_element(By.XPATH, "//h1[@class='text-2xl font-bold text-rc5-primary-title']/span[@class='break-all']").text
                self.assertIn(self.element, "00003195")
                """
                if self.gray == "0":
                    self.element = self.driver.find_element(By.ID, "ready_to_submit").text
                    self.assertIn(self.element,"I'm ready to submit")
                elif self.gray == "1":
                    self.element = self.driver.find_element(By.XPATH, "//div[text()='Seel protection overview']").text
                    self.assertIn(self.element, "Seel protection overview")
                else:
                    print("illegal input")
                    break
                """
                #log.info(i[0] + " " + "PASS")
            except Exception as e:
                #self.log.info(self.name+" "+channel + " " + "FAIL —— "+"data : " + email + " " + order)
                #logger.info(e)
                self.data_twice.append([channel,email,order])
                continue

        if not self.data_twice:
            return
        for channel, email, order in self.data_twice:
            try:
                self.driver.get(url_resolve)
                self.assertIn("Resolution Center", self.driver.title)
                self.driver=resolve_login(self.driver,email,order)
                time.sleep(3)
                self.element = self.driver.find_element(By.XPATH, "//h1[@class='text-2xl font-bold text-rc5-primary-title']/span[@class='break-all']").text
                self.assertIn(self.element, "00003195")
                """
                if self.gray == "0":
                    self.element = self.driver.find_element(By.ID, "ready_to_submit").text
                    self.assertIn(self.element,"I'm ready to submit")
                elif self.gray == "1":
                    self.element = self.driver.find_element(By.XPATH, "//div[text()='Seel protection overview']").text
                    self.assertIn(self.element, "Seel protection overview")
                """

            except Exception as e:
                self.log.error("twice_fail : " + " " + channel + " " + "FAIL —— " + "data : " + email + " " + order)
                # logger.info(e)
                continue

if __name__ == '__main__':
    # 执行测试并生成测试报告（更规范的执行方式）
    unittest.main(verbosity=2)