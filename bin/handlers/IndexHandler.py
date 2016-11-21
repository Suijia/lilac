# !/usr/bin/python
# -*- coding: utf-8 -*-
import tornado.log
from handlers.BaseHandler import BaseHandler

__author__ = 'pudding'


class IndexHandler(BaseHandler):
    def initialize(self, conf):
        super(IndexHandler, self).initialize(conf)

    def get(self):
        title_list = ["I am pudding", "I am snowwolf"]
        self.render_with_user('index.html', title_list=title_list)

    post = get
