import tushare as ts
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')
from pandas.plotting import register_matplotlib_converters
from statsmodels.tsa.seasonal import STL
import datetime
import sys
import time

register_matplotlib_converters()
sns.set_style('darkgrid')
plt.rc('figure', figsize=(16, 12))
plt.rc('font', size=13)
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


class StatsStock:
    def __init__(self):
        with open("token", 'r') as file:
            token = file.readline()
        self.__start_time = datetime.date.today() + datetime.timedelta(-365*0.6)
        self.__x_label_gap = 30
        self.__pro = ts.pro_api(token=token)
        return

    def query(self, ts_code):
        try:
            df_data = self.__pro.daily(ts_code=ts_code, start_date=self.__start_time.strftime("%Y%m%d"))
            # print(df_data)

            df_data = df_data[['trade_date', 'open']]
            df_data = df_data.sort_values('trade_date')
            df_data['trade_date'] = pd.to_datetime(df_data['trade_date']).dt.to_period(freq='D')
            df_data['trade_date'] = df_data['trade_date'].dt.to_timestamp('s').dt.strftime('%Y%m%d')

            data = df_data['open'].tolist()
            data = pd.Series(data,
                             index=pd.date_range(start=self.__start_time.strftime("%d-%m-%Y"), periods=len(data),
                                                 freq='D'),
                             name='open')
            # print(data)

            stl = STL(data)
            res = stl.fit()

            # plt.figure()
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

            ax1.set_title('原始数据')
            ax1.plot(df_data['trade_date'], data)
            for label in ax1.get_xticklabels():
                label.set_visible(False)
            for label in ax1.get_xticklabels()[:-self.__x_label_gap:self.__x_label_gap]:
                label.set_visible(True)
            ax1.get_xticklabels()[-1].set_visible(True)

            ax2.set_title('趋势')
            ax2.plot(df_data['trade_date'], res.trend)
            for label in ax2.get_xticklabels():
                label.set_visible(False)
            for label in ax2.get_xticklabels()[:-self.__x_label_gap:self.__x_label_gap]:
                label.set_visible(True)
            ax2.get_xticklabels()[-1].set_visible(True)

            ax3.set_title('周期')
            ax3.plot(df_data['trade_date'], res.seasonal)
            for label in ax3.get_xticklabels():
                label.set_visible(False)
            for label in ax3.get_xticklabels()[:-self.__x_label_gap:self.__x_label_gap]:
                label.set_visible(True)
            ax3.get_xticklabels()[-1].set_visible(True)

            # plt.show()
            fig.suptitle(ts_code)
            fig.savefig('plot.png')
            return True
        except:
            return False

    def update_time(self):
        self.__start_time = datetime.date.today() + datetime.timedelta(-365)
        return


if __name__ == "__main__":
    stats_stock = StatsStock()

    time_start = time.time()

    stats_stock.query(ts_code=sys.argv[1])

    print('time cost', time.time() - time_start, 's')

    print(datetime.date.today())

    print(matplotlib.get_cachedir())
