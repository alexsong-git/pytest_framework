import openpyxl

def read_data(file_path, sheet_name):
    """
    读取Excel文件中指定工作表的数据
    :param file_path: Excel文件路径
    :param sheet_name: 工作表名称
    :return: 包含指定工作表所有行数据的列表
    """
    all_results = []
    workbook = openpyxl.load_workbook(file_path)
    try:
        sheet = workbook[sheet_name]  # 获取指定名称的工作表
        for row in sheet.iter_rows(min_row=2, values_only=True):  # 从第二行开始读取数据
            result = list(row)  # 将每一行的数据存储在一个小列表中
            all_results.append(result)  # 将小列表添加到大列表中
    except KeyError:
        print(f"工作表 '{sheet_name}' 不存在，请检查工作表名称是否正确。")
    finally:
        workbook.close()
    return all_results

if __name__ == '__main__':
    file_path = "/Users/alex/PycharmProjects/pytest_framework/data/登陆数据.xlsx"
    sheet_name = "RC渠道登陆数据"  # 指定要读取的工作表名称
    data = read_data(file_path, sheet_name)
    print(data)