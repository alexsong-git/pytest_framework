import time

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from data.md_data import chromedriver_path, url_md_dashboard_dev
from common.data_tool import read_data
from common.log_tool import log_tool
from common.MD_login import MD_login,MD_logout


# 日志 fixture（不变）
@pytest.fixture(scope="session")
def logger():
    log_path = '/test_report/MD_login.log'
    return log_tool(log_path, 'MD_login')

# 浏览器驱动 fixture（不变）
@pytest.fixture(scope="class")
def driver():
    service = Service(executable_path=chromedriver_path)
    driver_instance = webdriver.Chrome(service=service)
    driver_instance.implicitly_wait(10)
    yield driver_instance
    driver_instance.quit()

class TestMDLogin:
    # 参数化直接使用 fixture 名称（不加括号！），pytest 会自动注入数据
    @pytest.mark.parametrize("channel, email, order", read_data("/Users/alex/登陆数据.xlsx", "MD登陆数据"))
    @pytest.mark.usefixtures("driver", "logger")
    def test_login(self, driver, logger, channel, email, order):
        try:
            driver.get(url_md_dashboard_dev)
            assert "Merchant Dashboard" in driver.title
            element = MD_login(driver, email, order)
            assert "Protection" in element
            print("logout")
            MD_logout(driver)
            logger.info(f"{channel} PASS —— {email} {order}")
        except AssertionError as ae:
            logger.error(f"{channel} FAIL —— {email} {order}, error: 断言失败")
            raise AssertionError(f"Assertion failed，data: {email} {order}") from None
        except NoSuchElementException as ne:
            logger.error(f"{channel} FAIL —— {email} {order}, error: 元素未找到")
            raise NoSuchElementException(f"元素未找到，data: {email} {order}") from None
        except Exception as e:
            logger.error(f"{channel} FAIL —— {email} {order}, error: 其他异常")
            raise Exception(f"Unexpected error，data: {email} {order}") from None
