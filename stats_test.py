import tushare as ts
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
from statsmodels.tsa.seasonal import STL
import datetime
import sys
import time

time_start = time.time()

register_matplotlib_converters()
sns.set_style('darkgrid')
plt.rc('figure', figsize=(16, 12))
plt.rc('font', size=13)

with open("token", 'r') as file:
    token = file.readline()
start_time = datetime.date.today() + datetime.timedelta(-365)
ts_code = sys.argv[1]
x_label_gap = 30

pro = ts.pro_api(token=token)
df_data = pro.daily(ts_code=ts_code, start_date=start_time.strftime("%Y%m%d"))

df_data = df_data[['trade_date', 'open']]
df_data = df_data.sort_values('trade_date')
df_data['trade_date'] = pd.to_datetime(df_data['trade_date']).dt.to_period(freq='D')
df_data['trade_date'] = df_data['trade_date'].dt.to_timestamp('s').dt.strftime('%Y%m%d')

data = df_data['open'].tolist()
data = pd.Series(data, index=pd.date_range(start=start_time.strftime("%d-%m-%Y"), periods=len(data), freq='D'),
                 name='open')
# print(data)

stl = STL(data)
res = stl.fit()

plt.figure()
fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

ax1.set_title('trend')
ax1.plot(df_data['trade_date'], res.trend)
for label in ax1.get_xticklabels():
    label.set_visible(False)
for label in ax1.get_xticklabels()[::x_label_gap]:
    label.set_visible(True)

ax2.set_title('seasonal')
ax2.plot(df_data['trade_date'], res.seasonal)
for label in ax2.get_xticklabels():
    label.set_visible(False)
for label in ax2.get_xticklabels()[::x_label_gap]:
    label.set_visible(True)

ax3.set_title('resid')
ax3.scatter(df_data['trade_date'], res.resid)
for label in ax3.get_xticklabels():
    label.set_visible(False)
for label in ax3.get_xticklabels()[::x_label_gap]:
    label.set_visible(True)

# plt.show()
fig.savefig('plot.png')

print('time cost', time.time() - time_start, 's')
