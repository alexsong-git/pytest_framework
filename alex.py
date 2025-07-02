from datetime import datetime
import pytz

timestamp_start = 1747584000000 / 1000
timestamp_end = 1747670399000 / 1000

# 设置北京时间时区
beijing_tz = pytz.timezone('Asia/Shanghai')

# 转换为北京时间
beijing_time_start = datetime.fromtimestamp(timestamp_start, tz=beijing_tz)
beijing_time_end = datetime.fromtimestamp(timestamp_end, tz=beijing_tz)

print(beijing_time_start)
print(beijing_time_end)
