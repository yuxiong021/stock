#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import os.path
import pyrestful
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import web.dataTableHandler as dataTableHandler
import web.dataEditorHandler as dataEditorHandler
import web.dataIndicatorsHandler as dataIndicatorsHandler
from web.resources.permission import PermissionResource
from web.resources.user import UserResource
#
# class Application(tornado.web.Application):
#     def __init__(self, db):
#         handlers = [
#             # 设置路由
#             # 使用datatable 展示报表数据模块。
#             (r"/stock/api_data", dataTableHandler.GetStockDataHandler,dict(database=db)),
#             (r"/stock/data", dataTableHandler.GetStockHtmlHandler,dict(database=db)),
#             # 数据修改dataEditor。
#             (r"/data/editor", dataEditorHandler.GetEditorHtmlHandler),
#             (r"/data/editor/save", dataEditorHandler.SaveEditorHandler),
#             # 获得股票指标数据。
#             (r"/data/indicators", dataIndicatorsHandler.GetDataIndicatorsHandler),
#         ]
#         settings = dict(  # 配置
#             template_path=os.path.join(os.path.dirname(__file__), "templates"),
#             static_path=os.path.join(os.path.dirname(__file__), "static"),
#             xsrf_cookies=False,  # True,
#             # cookie加密
#             cookie_secret="027bb1b670eddf0392cdda8709268a17b58b7",
#             debug=True,
#         )
#         super(Application, self).__init__(handlers, **settings)
#         self.db = db

#
# def main():
#     db = DB()
#     tornado.options.parse_command_line()
#     http_server = tornado.httpserver.HTTPServer(Application(db=db))
#     port = 9999
#     http_server.listen(port)
#     # tornado.options.options.logging = "debug"
#     tornado.options.parse_command_line()
#
#     tornado.ioloop.IOLoop.current().start()

def main():
    try:
        print("Start the service")
        app = pyrestful.rest.RestService([UserResource, PermissionResource])
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(8090)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        print("\nStop the service")


if __name__ == "__main__":
    main()
