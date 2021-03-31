import pyrestful.rest


class BaseResource(pyrestful.rest.RestHandler):

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', 'application/json; charset=UTF-8')
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Headers', 'Content-Type, x-token')  # 后增加’ x-token‘
