#!/usr/local/bin/python3
# -*- coding: utf-8 -*-


from libs.common_db import DB, BASH_STOCK_TMP
import sys
import os
import time
import pandas as pd
import tushare as ts
from sqlalchemy.types import NVARCHAR
from sqlalchemy import inspect
import datetime
import shutil


####### 使用 5.pdf，先做 基本面数据 的数据，然后在做交易数据。
#
from libs.common_util import get_pro
from libs.date_util import strdate_to_datetime


def stat_all(tmp_datetime):
    datetime_str = (tmp_datetime).strftime("%Y-%m-%d")
    datetime_int = (tmp_datetime).strftime("%Y%m%d")

    cache_dir = BASH_STOCK_TMP % (datetime_str[0:7], datetime_str)
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        print("remove cache dir force :", cache_dir)

    print("datetime_str:", datetime_str)
    print("datetime_int:", datetime_int)
    pro = get_pro()
    data = pro.top_list(trade_date=datetime_int)
    # 处理重复数据，保存最新一条数据。最后一步处理，否则concat有问题。

    global db
    if not data is None and len(data) > 0:
        # 插入数据库。
        # del data["reason"]
        # data["date"] = datetime_int  # 修改时间成为int类型。
        # data = data.drop_duplicates(subset="code", keep="last")
        # data.head(n=1)
        data = data.set_index(['trade_date', 'ts_code'])
        db.insert_db(data, "ts_top_list", True, "`trade_date`,`ts_code`")
    else:
        print("no data .")

    print(datetime_str)


# main函数入口
if __name__ == '__main__':
    db = DB()
    # 使用方法传递。
    tmp_datetime = db.run_with_args(stat_all)
    #dt = strdate_to_datetime('2021-03-26')
    #stat_all(dt)
