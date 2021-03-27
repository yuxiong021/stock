#!/usr/local/bin/python3
# -*- coding: utf-8 -*-


from libs.common_db import DB
import sys
import time
import pandas as pd
import tushare as ts
from sqlalchemy.types import NVARCHAR
from sqlalchemy import inspect
import datetime

from libs.common_util import get_pro, get_ts_data

"""
交易数据

http://tushare.org/trading.html#id2

股市交易时间为每周一到周五上午时段9:30-11:30，下午时段13:00-15:00。 周六、周日上海证券交易所、深圳证券交易所公告的休市日不交易。

"""

def stat_index_all(tmp_datetime):
    datetime_str = (tmp_datetime).strftime("%Y-%m-%d")
    datetime_int = (tmp_datetime).strftime("%Y%m%d")
    print("datetime_str:", datetime_str)
    print("datetime_int:", datetime_int)

    pro = get_pro()
    global db

    def _save_data(data):
        # 处理重复数据，保存最新一条数据。最后一步处理，否则concat有问题。
        if not data is None and len(data) > 0:
            data = data.set_index(['ts_code','trade_date'])
            db.insert_db(data, "ts_index_daily", False, "`ts_code`,`trade_date`")
        else:
            print("no data .")
        time.sleep(1)
    _save_data(pro.index_daily(ts_code='000001.SH'))
    _save_data(pro.index_daily(ts_code='000688.SH')) #科创50
    _save_data(pro.index_daily(ts_code='000300.SH')) #沪深300
    _save_data(pro.index_daily(ts_code='000905.SH')) #中证500
    _save_data(pro.index_daily(ts_code='399001.SZ'))
    _save_data(pro.index_daily(ts_code='399006.SZ'))

    print(datetime_str)

def stat_today_all(tmp_datetime):
    datetime_str = (tmp_datetime).strftime("%Y-%m-%d")
    datetime_int = (tmp_datetime).strftime("%Y%m%d")
    print("datetime_str:", datetime_str)
    print("datetime_int:", datetime_int)
    pro = get_pro()
    global db

    #先去查询所有的股票代码: 上市状态的
    stock_codes = db.select("SELECT ts_code FROM ts_stock_basic WHERE list_status='L'")
    # for ts_code in stock_codes:
    #     data = pro.daily(ts_code=ts_code._data[0],
    #                                    fields='ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount')
    #     # 处理重复数据，保存最新一条数据。最后一步处理，否则concat有问题。
    #     if not data is None and len(data) > 0:
    #         data = data.set_index('ts_code')
    #         db.insert_db(data, "ts_daily", True, "`ts_code`,`trade_date`")
    #     else:
    #         print("no data .")
    #     print(ts_code._data[0])
    for ts_code in stock_codes:
        #data = pro.daily_basic(ts_code=ts_code._data[0],
                                       # fields='ts_code,trade_date,close,turnover_rate,turnover_rate_f,volume_ratio,pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_share,float_share,free_share,total_mv,circ_mv')
        call_str = "daily_basic(ts_code='{}',fields='ts_code,trade_date,close,turnover_rate,turnover_rate_f,volume_ratio," \
                   "pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_share,float_share,free_share,total_mv,circ_mv')".format(ts_code._data[0])
        data = get_ts_data(pro, call_str, wait_seconds=600, max_trial=3)
        # 处理重复数据，保存最新一条数据。最后一步处理，否则concat有问题。
        if not data is None and len(data) > 0:
            data = data.set_index(['ts_code','trade_date'])
            db.insert_db(data, "ts_daily_basic", True, "`ts_code`,`trade_date`")
            print(ts_code._data[0])
        else:
            print("no data .-->"+ts_code._data[0])

        #time.sleep(1)

    #
    # data = ts.get_index()
    # # 处理重复数据，保存最新一条数据。最后一步处理，否则concat有问题。
    # if not data is None and len(data) > 0:
    #     # 插入数据库。
    #     # del data["reason"]
    #     data["date"] = datetime_int  # 修改时间成为int类型。
    #     data = data.drop_duplicates(subset="code", keep="last")
    #     data.head(n=1)
    #     db.insert_db(data, "ts_index_all", False, "`date`,`code`")
    # else:
    #     print("no data .")

    print(datetime_str)


# main函数入口
if __name__ == '__main__':
    db = DB()
    # 使用方法传递。
    #tmp_datetime = db.run_with_args(stat_index_all)
    #time.sleep(5)  # 停止5秒
    tmp_datetime = db.run_with_args(stat_today_all)
