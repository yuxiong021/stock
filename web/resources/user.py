import pyrestful.rest

from pyrestful import mediatypes
from pyrestful.rest import get, post, put, delete
import os

from libs.common_db import DB
from web.resources.base import BaseResource

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


class User(object):
    username = str
    password = str


class UserResource(BaseResource):

    def set_default_headers(self):
        super().set_default_headers()

    @get(_path="/user/info", _types=[str], _consumes=mediatypes.APPLICATION_JSON, _produces=mediatypes.APPLICATION_JSON)
    def info(self, token):
        print('start info!')
        user = User()
        user.username = token
        print(token)

        self.set_default_headers()
        return {'code': 20000, 'data': {
            'roles': ['admin'],
            'introduction': 'I am a super administrator',
            'avatar': 'https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif',
            'name': 'Super Admin'
        }}

    @post("/user/login", {'format': 'json'}, _catch_fire=True)
    def login(self, user):
        userinfo = self.request.body
        print(user)
        self.set_default_headers()
        return {"code": 20000, "data": {"token": "admin-token"}}

    def options(self):
        pass

