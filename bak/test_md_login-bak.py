import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from Test_Data.md_data import chromedriver_path, url_md_dashboard_dev
from common.data_tool import read_data
from common.log_tool import log_tool
from common.MD_login import MD_login
from datetime import datetime
import allure

"""
@pytest.fixture(scope="session", autouse=True)
def init_log():
    # 初始化日志
    path = '/Users/alex/PycharmProjects/pytest_framework/Test_Log/MD_login.log'
    name = 'MD_login'
    log = log_tool(path, name)
    log.info('start')
    yield log
    log.info('finish')
"""

class TestMDLogin:

    @pytest.fixture(scope="session", autouse=True)
    def init_log(self):
        # 初始化日志
        path = './Test_Log/MD_login.log'
        name = 'MD_login'
        log = log_tool(path, name)
        log.info('start')
        yield log
        log.info('finish')

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, init_log, request):
        # 将日志对象赋值给测试类的实例
        self.log = init_log

        # 初始化数据
        #self.data = read_data("/Users/alex/登陆数据.xlsx", "MD登陆数据")

        # 初始化浏览器驱动
        self.service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.implicitly_wait(10)

        # 初始化截图路径
        self.screenshot_path = f"image/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        yield

        # 清理操作
        self.driver.quit()

    @pytest.mark.parametrize("url, domain, email, order, channel, organization", read_data("Test_Data/登陆数据.xlsx", "MD登陆数据"))
    @allure.feature("MD 登录功能")
    @allure.story("MD 登录测试")
    def test_login(self, url, domain, email, order, channel, organization):
        allure.dynamic.title(f"登录测试 - {domain}")
        allure.dynamic.description(f"测试渠道: {domain}, 邮箱: {email}, 订单号: {order}")

        try:
            with allure.step("打开MD Dashboard页面"):
                self.driver.get(url)
                allure.attach(self.driver.get_screenshot_as_png(), name="页面截图", attachment_type=allure.attachment_type.PNG)
                assert "Merchant Dashboard" in self.driver.title

            with allure.step("执行登录操作"):
                element = MD_login(self.driver, email, order,organization)
                allure.attach(self.driver.get_screenshot_as_png(), name="登录后页面截图", attachment_type=allure.attachment_type.PNG)
                assert "Protection" in element

        except AssertionError as ae:
            # 捕获断言失败的异常，记录日志并截图
            self.log.error(f"{domain} FAIL —— data : {email} {order}, error: 断言失败")
            self.driver.save_screenshot(self.screenshot_path)
            allure.attach.file(self.screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)
            raise AssertionError(f"Assertion failed，data: {email} {order}, screenshot: {self.screenshot_path}")

        except NoSuchElementException as ne:
            # 捕获元素未找到的异常，记录日志并截图
            self.log.error(f"{domain} FAIL —— data : {email} {order}, error: 元素未找到")
            self.driver.save_screenshot(self.screenshot_path)
            allure.attach.file(self.screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)
            raise AssertionError(f"元素未找到，data: {email} {order}, screenshot: {self.screenshot_path}")

        except Exception as e:
            # 捕获其他异常，记录日志并截图
            self.log.error(f"{domain} FAIL —— data : {email} {order}, error: 其他异常")
            self.driver.save_screenshot(self.screenshot_path)
            allure.attach.file(self.screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)
            raise AssertionError(f"Unexpected error，data: {email} {order}, screenshot: {self.screenshot_path}")