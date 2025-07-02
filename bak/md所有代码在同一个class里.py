import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from Test_Data.md_data import chromedriver_path, url_md_dashboard_dev
from common.data_tool import read_data
from common.log_tool import log_tool
from common.MD_login import MD_login,MD_logout
import time


class TestMDLogin:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        # 初始化数据和日志
        self.data = read_data("/Users/alex/登陆数据.xlsx", "MD登陆数据")
        self.path = '/test_report/MD_login.log'
        self.name = 'MD_login'
        self.log = log_tool(self.path, self.name)
        self.log.info('start')

        # 初始化浏览器驱动
        self.service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.implicitly_wait(5)

        yield

        # 清理操作
        self.driver.quit()
        self.log.info('finish')

    @pytest.mark.parametrize("channel, email, order", read_data("/Users/alex/登陆数据.xlsx", "MD登陆数据"))
    def test_login(self, channel, email, order):
        try:
            self.driver.get(url_md_dashboard_dev)
            assert "Merchant Dashboard" in self.driver.title
            element = MD_login(self.driver, email, order)
            assert "Protection" in element
        except AssertionError as ae:
            # 捕获断言失败的异常，重新抛出 AssertionError
            self.log.error(f"{self.name} {channel} FAIL —— data : {email} {order}, error: 断言失败")
            raise AssertionError(f"Assertion failed，data: {email} {order}") from None
        except NoSuchElementException as ne:
            self.log.error(f"{self.name} {channel} FAIL —— data : {email} {order}, error: 元素未找到")
            # 转换为 AssertionError 并抛出
            raise NoSuchElementException(f"元素未找到，data: {email} {order}") from None
        except Exception as e:
            # 捕获其他异常，转换为 AssertionError 并抛出
            self.log.error(f"{self.name} {channel} FAIL —— data : {email} {order}, error: 其他异常")
            raise Exception(f"Unexpected error，data: {email} {order}") from None
