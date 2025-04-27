import pytest

if __name__ == "__main__":
    test_files = [
        "Test_Case/RC/test_rc_login.py",
        "Test_Case/MD/test_md_login.py"
    ]
    pytest_args = test_files + [
        "--alluredir", "./Test_Report/",  # 指定 allure 结果输出目录
        "--clean-alluredir"  # 清理之前的 allure 结果目录
    ]
    pytest.main(pytest_args)
#allure serve ./allure-results