"""
__project_ = 'Phoenix'
__file_name__ = 'DateUtil'
__author__ = 'yuxiong'
__time__ = '2021/3/18 9:51'
__product_name = PyCharm
"""
# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
通过datetime和dateutil进行常用日期的获取
如：
今年，去年，明年
当前季度
本月，上月，去年同期，今年一月
今天，昨天，明天，
本周、本月、本季度、本年第一天，
本周、本月、本季度、本年最后一天
"""
import datetime
import time
import calendar
from dateutil import relativedelta

def get_today():
    return datetime.date.today()

def get_yesterday():
    today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    yestoday = today-oneday
    return yestoday

def get_agodate(ago=120):
    today = datetime.date.today()
    oneday = datetime.timedelta(days=ago)
    yestoday = today-oneday
    return yestoday

def strdate_to_datetime(time):
    """
    explanation:
        转换字符串格式的日期为datetime

    params:
        * time->
            含义: 日期
            类型: str
            参数支持: []

    return:
        datetime
    """
    if len(str(time)) == 10:
        _time = '{} 00:00:00'.format(time)
    elif len(str(time)) == 19:
        _time = str(time)
    else:
        print('WRONG DATETIME FORMAT {}'.format(time))
    return datetime.datetime.strptime(_time, '%Y-%m-%d %H:%M:%S')

def date_compare(date1, date2, fmt='%Y-%m-%d') -> bool:
    """
    比较两个真实日期之间的大小，date1 > date2 则返回True
    :param date1:
    :param date2:
    :param fmt:
    :return:
    """

    zero = datetime.datetime.fromtimestamp(0)

    try:
        d1 = datetime.datetime.strptime(str(date1), fmt)
    except:
        d1 = zero
    try:
        d2 = datetime.datetime.strptime(str(date2), fmt)
    except:
        d2 = zero
    return d1 > d2


def last_date(lastMonth=12, partten='{}{:0>2d}{:0>2d}'):
    now = datetime.datetime.now()
    now = now - relativedelta.relativedelta(months=lastMonth)
    return partten.format(now.year, now.month, now.day)

def current_quarter(pattern='{}Q{}'):
    '''
    获取当前季度
    :return:
    '''
    today = datetime.date.today()
    quarter = (today.month - 1) // 3 + 1
    if pattern=='{}Q{}':
        return pattern.format(today.year, quarter)  # out: '2019Q1'
    elif quarter==1:
            return str(today.year)+'-03-31'
    elif quarter==2:
            return str(today.year)+'-06-30'
    elif quarter==3:
            return str(today.year)+'-09-30'
    else:
        return str(today.year) + '-12-31'


def getBetweenMonth(begin_date, end_date=None):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = end_date if end_date else datetime.datetime.strptime(
        time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m")
        date_list.append(date_str)
        begin_date = add_months(begin_date, 1)
    return date_list



def add_months(dt, months):
    month = dt.month - 1 + months
    year = int(dt.year + month / 12)
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def get_quarter(month_list):
    '''
    根据月份获取季度
    :param month_list: ['2018-11', '2018-12']
    :return:日期所在季度月末值
    '''
    quarter_list = []
    for value in month_list:
        temp_value = value.split("-")
        if temp_value[1] in ['01', '02', '03']:
            quarter_list.append(temp_value[0] + "0331")
        elif temp_value[1] in ['04', '05', '06']:
            quarter_list.append(temp_value[0] + "0630")
        elif temp_value[1] in ['07', '08', '09']:
            quarter_list.append(temp_value[0] + "0930")
        elif temp_value[1] in ['10', '11', '12']:
            quarter_list.append(temp_value[0] + "1231")
        quarter_set = set(quarter_list)
        quarter_list = list(quarter_set)
        quarter_list.sort()
    return quarter_list


def getBetweenQuarter(begin_date, end_date=None):
    '''
    获取两个时间之间的季度时间
    :param begin_date: 起始时间
    :param end_date: 默认当前时间
    :return:  日期所在季度月末值
    '''
    month_list = getBetweenMonth(begin_date, end_date)
    quarter_list = get_quarter(month_list)
    return quarter_list

def get_last_quarter(forward=8):
    '''
    取当前财报日期，往前forward个财报日期
    :param forward:
    :return:
    '''
    today = datetime.datetime.now()
    last = today - relativedelta.relativedelta(months=36)
    begin_date = '{}-{:0>2d}-{:0>2d}'.format(last.year, last.month, last.day)

    quarter_list = getBetweenQuarter(begin_date, today)
    quarter_list.sort(reverse=True)
    quarter_end = datetime.datetime.strptime('{}-{:0>2d}-{:0>2d} 00:00:00'.format(today.year, 5, 1), '%Y-%m-%d %H:%M:%S')
    if today < quarter_end:
        if today.month == 4:
            quarter_list = quarter_list[3:3+forward]
        else:
            quarter_list = quarter_list[2:2+forward]
    else:
        quarter_list = quarter_list[1:1+forward]
    return quarter_list