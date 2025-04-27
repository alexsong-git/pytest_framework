import os
import logging
import logging.config

def log_tool(log_file_path, name):
    # 确保日志文件所在的目录存在
    log_dir = os.path.dirname(log_file_path)
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
            print(f"创建日志目录：{log_dir}")
        except Exception as e:
            print(f"创建日志目录失败：{e}")
    else:
        print(f"日志目录已存在：{log_dir}")

    # 删除旧的日志文件（如果存在）
    if os.path.exists(log_file_path):
        try:
            os.remove(log_file_path)
            print(f"已删除旧的日志文件：{log_file_path}")
        except Exception as e:
            print(f"删除旧的日志文件失败：{e}")
    else:
        print(f"日志文件不存在，无需删除：{log_file_path}")

    # 配置日志
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': log_file_path,
                'formatter': 'standard'
            },
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            }
        },
        'loggers': {
            name: {
                'handlers': ['file', 'console'],
                'level': 'INFO',
                'propagate': False
            }
        }
    })

    # 返回指定名称的日志记录器
    logger = logging.getLogger(name)
    return logger


if __name__ == '__main__':
    path = '/Users/alex/PycharmProjects/pytest_framework/Test_Log/MD_login.log'
    name = 'MD_login.log'
    a = log_tool(path, name)
    a.info('test')