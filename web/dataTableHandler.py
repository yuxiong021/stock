#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import json
from tornado import gen
import libs.stock_web_dic as stock_web_dic
import web.base as webBase
import logging
import datetime
import pandas as pd

# info 蓝色 云财经
# success 绿色
#  danger 红色 东方财富
#  warning 黄色
WEB_EASTMONEY_URL = u"""
    <a class='btn btn-danger btn-xs tooltip-danger' data-rel="tooltip" data-placement="right" data-original-title="东方财富，股票详细地址，新窗口跳转。"
    href='http://quote.eastmoney.com/%s.html' target='_blank'>东财</a>
    
    <a class='btn btn-success btn-xs tooltip-success' data-rel="tooltip" data-placement="right" data-original-title="本地MACD，KDJ等指标，本地弹窗窗口，数据加载中，请稍候。"
    onclick="showIndicatorsWindow('%s');">指标</a>
    
    <a class='btn btn-warning btn-xs tooltip-warning' data-rel="tooltip" data-placement="right" data-original-title="东方财富，研报地址，本地弹窗窗口。"
    onclick="showDFCFWindow('%s');">东研</a>
    
    
    """
# 和在dic中的字符串一致。字符串前面都不特别声明是u""
eastmoney_name = "查看股票"


# 获得页面数据。
class GetStockHtmlHandler(webBase.BaseHandler):
    def initialize(self, database):
        self.database = database

    @gen.coroutine
    def get(self):
        name = self.get_argument("table_name", default=None, strip=False)
        stockWeb = stock_web_dic.STOCK_WEB_DATA_MAP[name]
        # self.uri_ = ("self.request.url:", self.request.uri)
        # print self.uri_
        date_now = datetime.datetime.now()
        date_now_str = date_now.strftime("%Y%m%d")
        # 每天的 16 点前显示昨天数据。
        if date_now.hour < 16:
            date_now_str = (date_now + datetime.timedelta(days=-1)).strftime("%Y%m%d")

        try:
            # 增加columns 字段中的【查看股票 东方财富】
            logging.info(eastmoney_name in stockWeb.column_names)
            if eastmoney_name in stockWeb.column_names:
                tmp_idx = stockWeb.column_names.index(eastmoney_name)
                logging.info(tmp_idx)
                try:
                    # 防止重复插入数据。可能会报错。
                    stockWeb.columns.remove("eastmoney_url")
                except Exception as e:
                    print("error :", e)
                stockWeb.columns.insert(tmp_idx, "eastmoney_url")
        except Exception as e:
            print("error :", e)
        logging.info("####################GetStockHtmlHandlerEnd")
        self.render("stock_web.html", stockWeb=stockWeb, date_now=date_now_str,
                    leftMenu=webBase.GetLeftMenu(self.request.uri))


# 获得股票数据内容。
class GetStockDataHandler(webBase.BaseHandler):
    def initialize(self, database):
        self.database = database

    def get(self):

        # 获得分页参数。
        start_param = self.get_argument("start", default=0, strip=False)
        length_param = self.get_argument("length", default=10, strip=False)
        print("page param:", length_param, start_param)

        name_param = self.get_argument("name", default=None, strip=False)
        type_param = self.get_argument("type", default=None, strip=False)

        stock_web = stock_web_dic.STOCK_WEB_DATA_MAP[name_param]

        # https://datatables.net/manual/server-side
        self.set_header('Content-Type', 'application/json;charset=UTF-8')
        order_by_column = []
        order_by_dir = []
        # 支持多排序。使用shift+鼠标左键。
        for item, val in self.request.arguments.items():
            # logging.info("item: %s, val: %s" % (item, val) )
            if str(item).startswith("order["):
                print("order:", item, ",val:", val[0])
            if str(item).startswith("order[") and str(item).endswith("[column]"):
                order_by_column.append(int(val[0]))
            if str(item).startswith("order[") and str(item).endswith("[dir]"):
                order_by_dir.append(val[0].decode("utf-8"))  # bytes转换字符串

        search_by_column = []
        search_by_data = []

        # 返回search字段。
        for item, val in self.request.arguments.items():
            # logging.info("item: %s, val: %s" % (item, val))
            if str(item).startswith("columns[") and str(item).endswith("[search][value]"):
                logging.info("item: %s, val: %s" % (item, val))
                str_idx = item.replace("columns[", "").replace("][search][value]", "")
                int_idx = int(str_idx)
                # 找到字符串
                str_val = val[0].decode("utf-8")
                if str_val != "":  # 字符串。
                    search_by_column.append(stock_web.columns[int_idx])
                    search_by_data.append(val[0].decode("utf-8"))  # bytes转换字符串

        # 打印日志。
        search_sql = ""
        search_idx = 0
        logging.info(search_by_column)
        logging.info(search_by_data)
        for item in search_by_column:
            val = search_by_data[search_idx]
            logging.info("idx: %s, column: %s, value: %s " % (search_idx, item, val))
            # 查询sql
            if search_idx == 0:
                search_sql = " WHERE %s = '%s' " % (item, val)
            else:
                search_sql = search_sql + " AND %s = '%s' " % (item, val)
            search_idx = search_idx + 1

        # print("stockWeb :", stock_web)
        order_by_sql = ""
        # 增加排序。
        if len(order_by_column) != 0 and len(order_by_dir) != 0:
            order_by_sql = "  ORDER BY "
            idx = 0
            for key in order_by_column:
                # 找到排序字段和dir。
                col_tmp = stock_web.columns[key]
                dir_tmp = order_by_dir[idx]
                if idx != 0:
                    order_by_sql += " ,cast(%s as decimal) %s" % (col_tmp, dir_tmp)
                else:
                    order_by_sql += " cast(%s as decimal) %s" % (col_tmp, dir_tmp)
                idx += 1
        # 查询数据库。
        limit_sql = ""
        if int(length_param) > 0:
            limit_sql = " LIMIT %s , %s " % (start_param, length_param)
        count_sql = " SELECT count(1) as num FROM `%s` %s " % (stock_web.table_name, search_sql)

        sql = " SELECT * FROM `%s` %s %s %s " % (
            stock_web.table_name, search_sql, order_by_sql, limit_sql)

        if stock_web.table_name == 'ts_stock_basics':
            trade_date_sql = " tdb.trade_date=(SELECT MAX(trade_date) FROM ts_daily_basic WHERE ts_code=tsb.ts_code)"
            if search_sql == "":
                search_sql = " WHERE " + trade_date_sql
            else:
                search_sql += " AND " + trade_date_sql

            column_sql = ""
            i=1
            for column in stock_web.columns:
                column_sql += column + " as '" + column + "'"
                if i!=len(stock_web.columns):
                    column_sql += ', '
                i+=1
            sql = " SELECT %s FROM ts_stock_basics as tsb LEFT JOIN ts_daily_basic as tdb ON tsb.ts_code=tdb.ts_code  %s %s %s " % (column_sql, search_sql, order_by_sql, limit_sql)

        logging.info("select sql : " + sql)
        logging.info("count sql : " + count_sql)
        #stock_web_list = self.db.execute(sql).fetchall()
        stock_web_list = pd.read_sql_query(sql, self.db.engine)
        stock_web_list["DT_RowId"] = stock_web_list.index.values
        def _func(x):
            code = x[0:6]
            code_tmp = x[7:9]+code
            eastmoney_url = WEB_EASTMONEY_URL % (code, code, code_tmp)
            return eastmoney_url
        stock_web_list["eastmoney_url"] = stock_web_list['tsb.ts_code'].apply(_func)
        stock_web_size = self.db.select(count_sql)
        logging.info("stockWebList size : %s " % stock_web_size)

        obj = {
            "draw": 0,
            "recordsTotal": stock_web_list.shape[0], #stock_web_size[0]._row[0],#stock_web_list.shape[0],
            "recordsFiltered": stock_web_list.shape[0],
            "data": stock_web_list.to_json()
        }
        # logging.info("####################")
        # logging.info(obj)
        self.write(json.dumps(obj))
