import datetime
import time
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import NVARCHAR
from sqlalchemy import inspect
import tushare as ts
import pandas as pd
import traceback


os.environ.setdefault('MYSQL_HOST', "localhost")
os.environ.setdefault('MYSQL_USER', "root")
os.environ.setdefault('MYSQL_PWD', "mysqldb")
os.environ.setdefault('MYSQL_DB', "stock_data")

# 使用环境变量获得数据库。兼容开发模式可docker模式。
MYSQL_HOST = os.environ.get('MYSQL_HOST') if (os.environ.get('MYSQL_HOST') != None) else "mariadb"
MYSQL_USER = os.environ.get('MYSQL_USER') if (os.environ.get('MYSQL_USER') != None) else "root"
MYSQL_PWD = os.environ.get('MYSQL_PWD') if (os.environ.get('MYSQL_PWD') != None) else "mariadb"
MYSQL_DB = os.environ.get('MYSQL_DB') if (os.environ.get('MYSQL_DB') != None) else "stock_data"
MYSQL_CONN_URL = "mysql+pymysql://" + MYSQL_USER + ":" + MYSQL_PWD + "@" + MYSQL_HOST + ":3306/" + MYSQL_DB + "?charset=utf8mb4"
BASH_STOCK_TMP = "/data/cache/hist_data_cache/%s/%s/"


class DB:

    def __init__(self):
        self.engine = self._engine()
        self.conn = self._conn()

    def _engine(self):
        engine = create_engine(
            MYSQL_CONN_URL,
            encoding='utf8', convert_unicode=True)
        return engine


    # 通过数据库链接 engine。
    def _conn(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        return session

    def delete(self, table_name, tj_key=None, tj_val=None, is_truncate=False):
        if is_truncate:
            self.conn.execute('TRUNCATE TABLE `%s`;' % table_name)
        else:
            self.conn.execute(
                "DELETE FROM `%s` WHERE `%s`='%s';" % (table_name, tj_key, tj_val))


    # 定义通用方法函数，插入数据库表，并创建数据库主键，保证重跑数据的时候索引唯一。
    def insert_db(self, data, table_name, write_index, primary_keys):
        # 使用 http://docs.sqlalchemy.org/en/latest/core/reflection.html
        # 使用检查检查数据库表是否有主键。
        insp = inspect(self.engine)
        col_name_list = data.columns.tolist()
        # 如果有索引，把索引增加到varchar上面。
        if write_index:
            # 插入到第一个位置：
            for i in range(len(data.index.names)):
                i+=1
                col_name_list.insert(0, data.index.names[len(data.index.names)-i])

        data.to_sql(name=table_name, con=self.engine, if_exists='append',
                    dtype={col_name: NVARCHAR(length=255) for col_name in col_name_list}, index=write_index)

        # 判断是否存在主键
        if insp.get_pk_constraint(table_name) == []:
            try:
                self.conn.execute('ALTER TABLE `%s` ADD PRIMARY KEY (%s);' % (table_name, primary_keys))
            except  Exception as e:
                print("################## ADD PRIMARY KEY ERROR :", e)


    # 插入数据。
    def insert(self, sql, params=()):
        print("insert sql:" + sql)
        try:
            self.conn.execute(sql, params)
        except  Exception as e:
            print("error :", e)


    # 查询数据
    def select(self, sql, params=()):
        print("select sql:" + sql)
        result = self.conn.execute(sql, params)
        return result.fetchall()


    # 计算数量
    def select_count(self, sql, params=()):
        print("select sql:" + sql)
        try:
            res = self.conn.execute(sql, params)
            result = res.fetchall()
            # 只有一个数组中的第一个数据
            if len(result) == 1:
                return int(result[0][0])
            else:
                return 0
        except Exception as e:
            print("error :", e)



    # 通用函数。获得日期参数。
    def run_with_args(self, run_fun):
        tmp_datetime_show = datetime.datetime.now()  # 修改成默认是当日执行 + datetime.timedelta()
        tmp_datetime_str = tmp_datetime_show.strftime("%Y-%m-%d %H:%M:%S.%f")
        str_db = "MYSQL_HOST :" + MYSQL_HOST + ", MYSQL_USER :" + MYSQL_USER + ", MYSQL_DB :" + MYSQL_DB
        print("\n######################### " + str_db + "  ######################### ")
        print("\n######################### begin run %s %s  #########################" % (run_fun, tmp_datetime_str))
        start = time.time()
        # 要支持数据重跑机制，将日期传入。循环次数
        if len(sys.argv) == 3:
            # python xxx.py 2017-07-01 10
            tmp_year, tmp_month, tmp_day = sys.argv[1].split("-")
            loop = int(sys.argv[2])
            tmp_datetime = datetime.datetime(int(tmp_year), int(tmp_month), int(tmp_day))
            for i in range(0, loop):
                # 循环插入多次数据，重复跑历史数据使用。
                # time.sleep(5)
                tmp_datetime_new = tmp_datetime + datetime.timedelta(days=i)
                try:
                    run_fun(tmp_datetime_new)
                except Exception as e:
                    print("error :", e)
                    traceback.print_exc()
        elif len(sys.argv) == 2:
            # python xxx.py 2017-07-01
            tmp_year, tmp_month, tmp_day = sys.argv[1].split("-")
            tmp_datetime = datetime.datetime(int(tmp_year), int(tmp_month), int(tmp_day))
            try:
                run_fun(tmp_datetime)
            except Exception as e:
                print("error :", e)
                traceback.print_exc()
        else:
            # tmp_datetime = datetime.datetime.now() + datetime.timedelta(days=-1)
            try:
                run_fun(tmp_datetime_show)  # 使用当前时间
            except Exception as e:
                print("error :", e)
                traceback.print_exc()
        print("######################### finish %s , use time: %s #########################" % (
            tmp_datetime_str, time.time() - start))





    # 增加读取股票缓存方法。加快处理速度。
    def get_hist_data_cache(self, code, date_start, date_end):
        # 设置基础目录，每次加载使用。
        if not os.path.exists(BASH_STOCK_TMP):
            os.makedirs(BASH_STOCK_TMP)  # 创建多个文件夹结构。
            print("######################### init tmp dir #########################")

        cache_dir = BASH_STOCK_TMP % (date_end[0:6], date_end)
        # 如果没有文件夹创建一个。月文件夹和日文件夹。方便删除。
        # print("cache_dir:", cache_dir)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        cache_file = cache_dir + "%s^%s.gzip.pickle" % (date_end, code)
        # 如果缓存存在就直接返回缓存数据。压缩方式。
        if os.path.isfile(cache_file):
            print("######### read from cache #########", cache_file)
            return pd.read_pickle(cache_file, compression="gzip")
        else:
            print("######### get data, write cache #########", code, date_start, date_end)
            stock = pd.read_sql(sql="SELECT * FROM ts_daily td WHERE ts_code =%(ts_code)s AND trade_date BETWEEN %(date_start)s AND %(date_end)s",
                        con=self.engine, params={'ts_code':code,'date_start':date_start,'date_end':date_end})
            # stock['trade_date'] = pd.to_datetime(stock['trade_date'])
            # stock['trade_date'] = stock['trade_date'].apply(lambda x: x.strftime('%Y-%m-%d'))
            #stock = ts.get_hist_data(code, start=date_start, end=date_end)
            if stock is None:
                return None
            stock = stock.set_index('trade_date', drop=False)
            stock.to_pickle(cache_file, compression="gzip")
            return stock
