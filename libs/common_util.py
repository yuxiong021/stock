import time
import os
import tushare as ts
os.environ.setdefault('TUSHARE_TOKEN', "9a742f208532e6301ceb4ddca014e85517c96cdeb7c7d3afa9fe7cf3")


# 定义 获得 token 方法
def get_tushare_token():
    tushare_token = os.environ.get('TUSHARE_TOKEN')
    if tushare_token != None:
        return tushare_token
    else:
        return ""

def set_token(token=None):
    try:
        ts.set_token(get_tushare_token())
    except:
        if token is None:
            print('请设置tushare的token')
        else:
            print('请升级tushare 至最新版本 pip install tushare -U')

def get_pro():
    try:
        set_token()
        pro = ts.pro_api()
    except Exception as e:
        if isinstance(e, NameError):
            print('请设置tushare pro的token凭证码')
        else:
            print('请升级tushare 至最新版本 pip install tushare -U')
            print(e)
        pro = None
    return pro

def get_ts_data(pro, call_str, wait_seconds=61, max_trial=3, trial_count=0):
    '''
    调用tushare接口的通用函数
    '''
    if trial_count >= max_trial:
        raise ValueError("[ERROR]\tEXCEED MAX TRIAL!")
    try:
        print(pro)
        df = eval("pro."+call_str)
        return df
    except Exception as e:
        print(e)
        time.sleep(wait_seconds)
        get_ts_data(call_str, wait_seconds, max_trial, trial_count + 1)