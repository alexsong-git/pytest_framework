from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tempfile

temp_dir = tempfile.mkdtemp()  # 创建临时目录

chrome_options = Options()
chrome_options.add_argument('--headless') # 使用无头模式执行chrome
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox') # 这个一定要加，不加Chrome启动报错

chrome_options.add_argument(f"--user-data-dir={temp_dir}")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.baidu.com")
print (driver.page_source)
driver.close()