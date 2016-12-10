#!/usr/bin/env python
# -*-coding:utf-8-*-
import time
__author__ = 'pudding'


class Profile:
    def __init__(self, profile_id, cover, title, subtitle, snippet, detail_url, content, author, publish_time=None):  # 需要加 None吗? 本来想参数名就是数据库里的字段名,但警告说参数都要小写,就改了
        self.profile_id = profile_id
        self.cover = cover
        self.title = title
        self.subtitle = subtitle
        self.snippet = snippet
        self.detail_url = detail_url
        self.content = content
        self.author = author
        self.publish_time = publish_time

    def __str__(self):  # 只覆盖了 Profile类的__str__,self 就是 quiz
        return "profile_id: {0}\ncover: {1}\ntitle: {2}\nsubtitle: {3}\nsnippet: {4}\ndetail_url: {5}\ncontent: {6}\n" \
               "author: {7}\npublish_time:{8}"\
            .format(self.profile_id, self.cover, self.title.encode('utf-8'), self.subtitle.encode('utf-8'), self.snippet.encode('utf-8'),
                    self.detail_url, self.author.encode('utf-8'),
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.publish_time)) if self.publish_time else "None")

    @staticmethod  # 不需要类的实例就能执行,写在其他地方也可以
    def to_profile(profile_record):
        """
        把来自数据库的一条记录（record）即一行,处理成程序中的一个 Profile类的实例
        :param profile_record: 从数据库 get 出来的一条 item, 格式为字典,编码为 unicode, 故中文内容需要编码
        :return: .get('key1','default_value') 是操作字典的方法
        """
        publish_time = int(time.mktime(profile_record.get('publishTime', None).timetuple()) + 8 * 3600)  # 还需要加8*3600吗?

        return Profile(profile_record.get('profileId', None), profile_record.get('cover', None),
                       profile_record.get('title', None), profile_record.get('subtitle'), profile_record.get('snippet', None),
                       profile_record.get('detailUrl', None), profile_record.get('content', None),
                       profile_record.get('author', None), publish_time)  # get 是字典自带的方法

    @staticmethod
    def to_profiles(profile_items):
        profiles = list()
        for profile_item in profile_items:
            profiles.append(Profile.to_profile(profile_item))  # 静态方法属于类,而不属于其实例
        return profiles

if __name__ == '__main__':

    test_dict = {"photoId": 123, "url": "http", "title": "啦啦", "author": "pudding", "publishTime": 0}
    photo = Profile.to_profile(test_dict)
    print type(photo)
    print type(photo.title)
