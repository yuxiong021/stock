#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import time
from libs.common_util import get_pro, get_ts_data
from libs.common_db import DB, MYSQL_DB
db = DB()

def stat_all(tmp_datetime):
    # 存款利率
    # data = ts.get_deposit_rate()
    # common.insert_db(data, "ts_deposit_rate", False, "`date`,`deposit_type`")
    #
    # # 贷款利率
    # data = ts.get_loan_rate()
    # common.insert_db(data, "ts_loan_rate", False, "`date`,`loan_type`")
    #
    # # 存款准备金率
    # data = ts.get_rrr()
    # common.insert_db(data, "ts_rrr", False, "`date`")
    #
    # # 货币供应量
    # data = ts.get_money_supply()
    # common.insert_db(data, "ts_money_supply", False, "`month`")
    #
    # # 货币供应量(年底余额)
    # data = ts.get_money_supply_bal()
    # common.insert_db(data, "ts_money_supply_bal", False, "`year`")
    #
    # # 国内生产总值(年度)
    # data = ts.get_gdp_year()
    # common.insert_db(data, "ts_gdp_year", False, "`year`")
    #
    # # 国内生产总值(季度)
    # data = ts.get_gdp_quarter()
    # common.insert_db(data, "ts_get_gdp_quarter", False, "`quarter`")
    #
    # # 三大需求对GDP贡献
    # data = ts.get_gdp_for()
    # common.insert_db(data, "ts_gdp_for", False, "`year`")
    #
    # # 三大产业对GDP拉动
    # data = ts.get_gdp_pull()
    # common.insert_db(data, "ts_gdp_pull", False, "`year`")
    #
    # # 三大产业贡献率
    # data = ts.get_gdp_contrib()
    # common.insert_db(data, "ts_gdp_contrib", False, "`year`")
    #
    # # 居民消费价格指数
    # data = ts.get_cpi()
    # common.insert_db(data, "ts_cpi", False, "`month`")
    #
    # # 工业品出厂价格指数
    # data = ts.get_ppi()
    # common.insert_db(data, "ts_ppi", False, "`month`")

    #############################基本面数据 http://tushare.org/fundamental.html
    # 股票列表
    pro = get_pro()
    global db

    #交易日历
    data = pro.trade_cal(exchange='SSE')
    data = data.set_index('cal_date')
    db.insert_db(data, "ts_trade_cal", True, "cal_date")


    # data = pro.stock_basic(exchange='', list_status='L',
    #                                          fields='ts_code,symbol,name,area,industry,fullname,enname,market, \
    #                                         exchange,curr_type,list_status,list_date,delist_date,is_hs')
    # data = data.set_index(['ts_code','industry'])
    # db.insert_db(data, "ts_stock_basic", True, "`ts_code`,`industry`")
    #
    # 获取大盘指数基础信息
    # data = pro.index_basic(market='SZSE')
    # data = data.set_index('ts_code')
    # db.insert_db(data, "ts_index_basic", True, "`ts_code`")
    #
    # #获取指数成份股
    # for d in data.index.values.tolist():
    #     iw = get_ts_data(pro, "index_weight(index_code='{}')".format(d))
    #     iw = iw.set_index(['index_code','con_code'])
    #     common.delete("ts_index_weight", 'index_code', d)
    #     common.insert_db(iw, "ts_index_weight", True, "index_code,con_code")

    # 行业分类。
    # data = pro.index_classify()
    # data = data.set_index('index_code')
    # db.insert_db(data, "ts_industry_classify", True, "`index_code`")
    # for d in data.index.values.tolist():
    #     iw = get_ts_data(pro, "index_member(index_code='{}')".format(d), wait_seconds=600)
    #     iw = iw.set_index(['index_code','con_code'])
    #     db.insert_db(iw, "ts_industry_member", True, "index_code,con_code")
    #     time.sleep(1)

    # 概念分类 必须使用 PRO 接口查询。
    # data = pro.ths_index()
    # data = data.set_index('ts_code')
    # db.insert_db(data, "ts_concept_classify", True, "`ts_code`")
    # for d in data.index.values.tolist():
    #     iw = get_ts_data(pro, "ths_member(ts_code='{}')".format(d), wait_seconds=600)
    #     iw = iw.set_index(['ts_code','code'])
    #     db.insert_db(iw, "ts_concept_member", True, "ts_code,code")
    #     time.sleep(1)

    # # 沪深300成份股及权重
    # data = pro.index_weight(index_code='000300.SH')
    # common.insert_db(data, "ts_stock_hs300", True, "`index_code`")
    #
    # data = pro.index_weight(index_code='000016.SH')
    # common.insert_db(data, "ts_stock_sz50", True, "`index_code`")
    #
    # # 中证500成份股
    # data = pro.index_weight(index_code='000905.SH')
    # common.insert_db(data, "ts_stock_zz500", True, "`index_code`")


# 创建新数据库。
def create_new_database():
    global db
    #with MySQLdb.connect(common.MYSQL_HOST, common.MYSQL_USER, common.MYSQL_PWD, "mysql", charset="utf8") as db:
    try:
        create_sql = " CREATE DATABASE IF NOT EXISTS %s CHARACTER SET utf8 COLLATE utf8_general_ci " % MYSQL_DB
        print(create_sql)
        db.conn.autocommit(on=True)
        db.conn.cursor().execute(create_sql)
    except Exception as e:
        print("error CREATE DATABASE :", e)


# main函数入口
if __name__ == '__main__':

    # 检查，如果执行 select 1 失败，说明数据库不存在，然后创建一个新的数据库。
    try:
        connect = db.conn
        # with MySQLdb.connect(common.MYSQL_HOST, common.MYSQL_USER, common.MYSQL_PWD, common.MYSQL_DB,
        #                      charset="utf8") as db:
        connect.autocommit(on=True)
        connect.cursor().execute(" select 1 ")
    except Exception as e:
        print("check  MYSQL_DB error and create new one :", e)
        # 检查数据库失败，
        create_new_database()
    # 执行数据初始化。
    # 使用方法传递。
    tmp_datetime = db.run_with_args(stat_all)
