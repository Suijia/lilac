# !/usr/bin/python
# -*- coding: utf-8 -*-
import tornado.log
from handlers.BaseHandler import BaseHandler
from crawler.ArticleDao import ArticleDao

__author__ = 'pudding'


class IndexHandler(BaseHandler):

    TOTAL_ARTICLE = 3
    MAX_TITLE = 25
    MAX_SNIPPET = 87

    def initialize(self, conf):
        super(IndexHandler, self).initialize(conf)

    def get(self):
        article_dao = ArticleDao()
        articles = article_dao.get_latest_articles(IndexHandler.TOTAL_ARTICLE)
        for article in articles:
            if len(article.title) >= IndexHandler.MAX_TITLE:
                article.cover = article.cover[0: IndexHandler.MAX_TITLE] + "..."
            if len(article.snippet) >= IndexHandler.MAX_SNIPPET:
                article.snippet = article.snippet[0: IndexHandler.MAX_SNIPPET] + "..."

        self.render_with_user('index.html', articles=articles)

    post = get
