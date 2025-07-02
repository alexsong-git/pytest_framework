from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
download_dir = "driver/windows"  # 修改为你的下载目录
options.add_argument(f"--download-default-directory={download_dir}")
options.add_argument(f"--no-sandbox")
options.add_argument(f"--headless")  # 无头模式，不会打开实际浏览器窗口
prefs = {
    "download.default_directory": download_dir,  # 指定下载目录
    "download.prompt_for_download": False,  # 不弹框
    "directory_upgrade": True,  # 允许覆盖
}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
print("ChromeDriver 路径:", ChromeDriverManager().install())
