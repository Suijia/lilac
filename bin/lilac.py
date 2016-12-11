#!/usr/bin/env python
#-*-coding:utf-8-*-

import sys
import os
import yaml
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.netutil
import tornado.process
import tornado.log

import tornado.autoreload

from handlers import *

def get_project_path(conf):
    """
    :param conf:
    :return: project 的绝对路径 (current working directory)
    """
    cwd_path = os.getcwd()
    return cwd_path


def get_template_path(conf):
    """
    :param conf:
    :return: html 模版文件夹
    """
    related_template_path = conf.get('templatePath')
    return get_project_path(conf) + '/' + related_template_path


def is_online(conf):
    return conf.get('default_profile', 'staging') == 'online'


def get_static_path(conf):
    """
    :param conf:
    :return: static 文件夹的绝对路径
    """
    related_static_path = conf.get('staticPath')
    return get_project_path(conf) + '/' + related_static_path


def setup_logger(access_log_file, app_log_file):
    import logging.handlers
    formatter = logging.Formatter("[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s")
    fileHandlerApp = logging.handlers.WatchedFileHandler(app_log_file)
    fileHandlerApp.setFormatter(formatter)
    fileHandlerAccess = logging.handlers.WatchedFileHandler(access_log_file)
    fileHandlerAccess.setFormatter(formatter)
    tornado.log.app_log.addHandler(fileHandlerApp)
    tornado.log.app_log.setLevel(logging.INFO)
    tornado.log.access_log.addHandler(fileHandlerAccess)
    tornado.log.access_log.setLevel(logging.INFO)


if __name__ == '__main__':
    conf = yaml.load(open('conf/service.yaml', 'r'))
    setup_logger(conf['log']['access'], conf['log']['app'])
    port = conf.get('port', 8080)
    process_num = conf.get('processNum', 1)

    ui_modules = {
    }
    settings = {
        'static_path': get_static_path(conf),
        'static_url_prefix': '/static/',
        'template_path': get_template_path(conf),
        'gzip': False,
        'debug': not is_online(conf),  # 调试时为 true
        'ui_modules': ui_modules,
        "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        "login_url": "/login"
    }

    print "static_path: " + get_static_path(conf)
    print "template_path: " + get_template_path(conf)

    application = tornado.web.Application([
        # This part is Evaluation Functions
        # EvaluationHandlers -> ListHandlers
        (r'/(google4e92208f413c96e2\.html)', tornado.web.StaticFileHandler, {'path': get_static_path(conf)}),
        (r'/$', IndexHandler, dict(conf=conf)),
        # (r'/.*', ErrorHandler, dict(conf=conf)),
        ],
        **settings)
    tornado.log.app_log.info('Try to start server...')
    server = tornado.httpserver.HTTPServer(application)
    server.bind(port)

    if is_online(conf):

        # 这里需要注意, start 之后的代码都是多进程的, 不需要多进程的代码写在start之前
        server.start(num_processes=process_num)
    else:
        server.start()  # for debug

    tornado.log.app_log.info("to start server")
    tornado.ioloop.IOLoop.instance().start()
    print "start done"

