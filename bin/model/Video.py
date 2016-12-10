#!/usr/bin/env python
# -*-coding:utf-8-*-
import time


class Video:
    def __init__(self, video_id, cover, video_time, detail_url, title, snippet, tag, author, publish_time=None):  # 需要加 None吗? 本来想参数名就是数据库里的字段名,但警告说参数都要小写,就改了
        self.video_id = video_id
        self.cover = cover
        self.video_time = video_time
        self.detail_url = detail_url
        self.title = title
        self.snippet = snippet
        self.tag = tag
        self.author = author
        self.publish_time = publish_time

    # def __str__(self):  # 只覆盖了 Video 类的__str__,self 就是 video
    #     return "video_id: {0}\ncover: {1}\nvideo_time: {2}\ndetail_url: {3}\ntitle: {4}\nsnippet{5}\ntag:{6}\n" \
    #            "author: {7}\npublish_time: {8}"\
    #         .format(self.video_id, self.cover, self.video_time, self.detail_url, self.title, self.snippet,
    #                 self.tag, self.author.encode('utf-8'),
    #                 time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.publish_time)) if self.publish_time else "None")

    @staticmethod  # 不需要类的实例就能执行,写在其他地方也可以
    def to_video(video_record):
        """
        把来自数据库的一条记录（record）即一行,处理成一个Video类的实例,注意,.get('key1','default_value') 是操作字典的方法
        :param video_record: 从数据库 self.db.get（） 出来的一条记录, 数据结构为字典,编码为 unicode
        :return: 一个 video类的实例
        """
        publish_time = int(time.mktime(video_record.get('publishTime', None).timetuple()) + 8 * 3600)  # 还需要加8*3600吗?
        # AttributeError: 'NoneType' object has no attribute 'timetuple' 这里用 none 不对,要改?
        return Video(video_record.get('videoId', None), video_record.get('cover', None),
                     video_record.get('videoTime', None), video_record.get('detailUrl', None),
                     video_record.get('title', None), video_record.get('snippet', None),
                     video_record.get('tag', None), video_record.get('author', None), publish_time)  # get 是字典自带的方法

    @staticmethod
    def to_videos(video_items):
        videos = list()
        for video_item in video_items:
            videos.append(Video.to_video(video_item))  # 静态方法 to_quiz 是属于 Quiz类的,而不属于其实例
        return videos

if __name__ == '__main__':

    test_dict = {"videoId": 123, "url": "http", "title": "啦啦", "author": "pudding", "publishTime": 0}
    video = Video.to_video(test_dict)
    print type(video)
    print type(video.title)

