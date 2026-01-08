import os
import shutil
from webdriver_manager.chrome import ChromeDriverManager


def download_chromedriver(download_path=None):
    """
    下载ChromeDriver并返回其路径
    
    Args:
        download_path: 自定义下载路径，例如 "driver" 或 "./drivers"
                      如果指定路径，会将driver复制到该目录
                      如果不指定，则使用webdriver_manager的默认缓存路径
    
    Returns:
        str: ChromeDriver的完整路径
    """
    # 首先使用webdriver_manager下载driver到缓存目录
    original_driver_path = ChromeDriverManager().install()
    print(f"ChromeDriver 已下载到缓存: {original_driver_path}")
    
    # 如果指定了自定义路径，复制到该路径
    if download_path:
        # 创建目标目录（如果不存在）
        os.makedirs(download_path, exist_ok=True)
        
        # 获取driver文件名
        driver_filename = os.path.basename(original_driver_path)
        target_path = os.path.join(download_path, driver_filename)
        
        # 复制driver到目标路径
        shutil.copy2(original_driver_path, target_path)
        print(f"ChromeDriver 已复制到: {target_path}")
        return target_path
    
    return original_driver_path


if __name__ == "__main__":
    # 示例：使用自定义路径
    download_chromedriver("driver")
    
    # 或使用默认路径
    # download_chromedriver()