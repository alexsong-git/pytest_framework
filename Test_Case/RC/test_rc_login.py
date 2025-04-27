import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from data.rc_data import chromedriver_path, url_resolution
from common.data_tool import read_data
from common.log_tool import log_tool
from common.resolution_login import resolution_login
from datetime import datetime
import allure

"""
@pytest.fixture(scope="session", autouse=True)
def init_log():
    # 初始化日志
    path = '/Users/alex/PycharmProjects/pytest_framework/Test_Log/RC_login_resolution.log'
    name = 'RC_login_resolution'
    log = log_tool(path, name)
    log.info('start')
    yield log
    log.info('finish')
"""

class TestRCLogin:

    @pytest.fixture(scope="session", autouse=True)
    def init_log(self):
        # 初始化日志
        path = './Test_Log/RC_login_resolution.log'
        name = 'RC_login_resolution'
        log = log_tool(path, name)
        log.info('start')
        yield log
        log.info('finish')

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, init_log, request):
        # 将日志对象赋值给测试类的实例
        self.log = init_log

        # 初始化数据
        #self.data = read_data("/Users/alex/登陆数据.xlsx", "RC渠道登陆数据")

        # 初始化浏览器驱动
        self.service = Service(executable_path=chromedriver_path)
        self.driver = webdriver.Chrome(service=self.service)
        self.driver.implicitly_wait(5)

        # 初始化截图路径
        self.screenshot_path = f"/Users/alex/PycharmProjects/pytest_framework/image/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        yield

        # 清理操作
        self.driver.quit()

    @pytest.mark.parametrize("channel, email, order", read_data("/Users/alex/登陆数据.xlsx", "RC渠道登陆数据"))
    @allure.feature("RC 登录功能")
    @allure.story("RC 登录测试")
    def test_login(self, channel, email, order):
        allure.dynamic.title(f"登录测试 - {channel}")
        allure.dynamic.description(f"测试渠道: {channel}, 邮箱: {email}, 订单号: {order}")

        try:
            with allure.step("打开Resolution Center页面"):
                self.driver.get(url_resolution)
                allure.attach(self.driver.get_screenshot_as_png(), name="页面截图", attachment_type=allure.attachment_type.PNG)
                assert "Resolution Center" in self.driver.title

            with allure.step("执行登录操作"):
                element = resolution_login(self.driver, email, order)
                allure.attach(self.driver.get_screenshot_as_png(), name="登录后页面截图", attachment_type=allure.attachment_type.PNG)
                assert "I'm ready to submit" in element

        except AssertionError as ae:
            # 捕获断言失败的异常，记录日志并截图
            self.log.error(f"{channel} FAIL —— data : {email} {order}, error: 断言失败")
            self.driver.save_screenshot(self.screenshot_path)
            allure.attach.file(self.screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)
            raise AssertionError(f"Assertion failed，data: {email} {order}, screenshot: {self.screenshot_path}")

        except NoSuchElementException as ne:
            # 捕获元素未找到的异常，记录日志并截图
            self.log.error(f"{channel} FAIL —— data : {email} {order}, error: 元素未找到")
            self.driver.save_screenshot(self.screenshot_path)
            allure.attach.file(self.screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)
            raise AssertionError(f"元素未找到，data: {email} {order}, screenshot: {self.screenshot_path}")
            #raise NoSuchElementException(f"元素未找到，data: {email} {order}, screenshot: {self.screenshot_path}")

        except Exception as e:
            # 捕获其他异常，记录日志并截图
            self.log.error(f"{channel} FAIL —— data : {email} {order}, error: 其他异常")
            self.driver.save_screenshot(self.screenshot_path)
            allure.attach.file(self.screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)
            raise AssertionError(f"Unexpected error，data: {email} {order}, screenshot: {self.screenshot_path}")
            #raise Exception(f"Unexpected error，data: {email} {order}, screenshot: {self.screenshot_path}")