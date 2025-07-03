import time
from selenium.webdriver.common.by import By
from Test_Data.md_data import chromedriver_path, url_md_dashboard_dev
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile
from datetime import datetime
import allure

def MD_login(driver, email, order, organization):
    try:
        ele_email = driver.find_element(By.ID, 'email-input')
        ele_email.send_keys(email)
        ele_button_1 = driver.find_element(By.ID, 'submit')
        ele_button_1.click()
        ele_password = driver.find_element(By.ID, 'current-password')
        ele_password.send_keys(order)
        ele_button_2 = driver.find_element(By.ID, 'submit')
        ele_button_2.click()
        ele_org = driver.find_element(By.XPATH, f"//span[text()='{organization}']")
        ele_org.click()
        element = driver.find_element(By.XPATH, "//h1[@class='font-bold text-3xl mr-6']").text
        return element
    except:
        screenshot_path = f"/image/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        driver.save_screenshot(screenshot_path)
        allure.attach.file(screenshot_path, name="失败截图", attachment_type=allure.attachment_type.PNG)
        raise AssertionError(f"Unexpected error，data: {email} {order}, screenshot: {screenshot_path}")


def MD_logout(driver):

    time.sleep(3)
    ele_usercenter = driver.find_element(By.XPATH, "//div[@class='bg-[#645AFF] w-7 h-7 rounded-full flex justify-center items-center text-white font-semibold text-lg leading-7']")
    ele_usercenter.click()
    ele_out = driver.find_element(By.XPATH, "//button[.//span[text()='Sign out']]")
    driver.execute_script("arguments[0].click();", ele_out)


if __name__ == '__main__':

    temp_dir = tempfile.mkdtemp()  # 创建临时目录
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 使用无头模式执行chrome
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')  # 这个一定要加，不加Chrome启动报错
    chrome_options.add_argument(f"--user-data-dir={temp_dir}")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    driver.get(url_md_dashboard_dev)
    MD_login(driver,'yuchen.song+1200@seel.com','12345678ABbc!!1','seel-test-alexsong-1200')
    driver.quit()