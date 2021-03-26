from libs.common_util import get_pro
import libs.common_db as db

def save_index():
    pro = get_pro()
    data = pro.index_basic()
    db.insert_db(data, "ts_index_basic", True, "`ts_code`")