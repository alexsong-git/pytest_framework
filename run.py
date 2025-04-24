"""统一入口"""
import unittest
import HTMLReport
from Test_Suite import test_suite

# 创建一个总的测试套件
suite = unittest.TestSuite()
# 将各功能模块的测试套件加入到总的套件中
suite.addTests(test_suite.return_suite())

# 运行并生成报告
if __name__ == "__main__":
    suite = test_suite.return_suite()
    HTMLReport.TestRunner(
        title="自动化测试",
        description="自动化测试项目测试报告。",
        report_file_name="test",
        thread_count=4
    ).run(suite)