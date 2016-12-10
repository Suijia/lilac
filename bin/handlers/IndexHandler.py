# !/usr/bin/python
# -*- coding: utf-8 -*-
import tornado.log
from handlers.BaseHandler import BaseHandler
from crawler import *

__author__ = 'pudding'


class IndexHandler(BaseHandler):

    TOTAL_ARTICLE = 3
    TOTAL_VIDEO = 3
    TOTAL_PHOTO = 6
    TOTAL_PROFILE = 3
    MAX_TITLE = 25
    MAX_SNIPPET = 76

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

        video_dao = VideoDao()
        videos = video_dao.get_latest_videos(IndexHandler.TOTAL_VIDEO)

        photo_dao = PhotoDao()
        photos = photo_dao.get_latest_photos(IndexHandler.TOTAL_PHOTO)

        profile_dao = ProfileDao()
        profiles = profile_dao.get_latest_profiles(IndexHandler.TOTAL_PROFILE)
        for profile in profiles:
            if len(profile.title) >= IndexHandler.MAX_TITLE:
                profile.cover = profile.cover[0: IndexHandler.MAX_TITLE] + "..."
            if len(profile.snippet) >= IndexHandler.MAX_SNIPPET:
                profile.snippet = profile.snippet[0: IndexHandler.MAX_SNIPPET] + "..."

        self.render_with_user('index.html', articles=articles, videos=videos, photos=photos, profiles=profiles)

    post = get
