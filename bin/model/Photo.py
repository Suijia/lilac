#!/usr/bin/env python
# -*-coding:utf-8-*-
import time


class Photo:
    def __init__(self, photo_id, url, title, author, publish_time=None):  # 需要加 None吗? 本来想参数名就是数据库里的字段名,但警告说参数都要小写,就改了
        self.photo_id = photo_id
        self.url = url
        self.title = title
        self.author = author
        self.publish_time = publish_time

    # def __str__(self):  # 只覆盖了 Photo 类的__str__,self 就是 photo
    #     return "photo_id: {0}\nurl: {1}\ntitle: {2}\nauthor: {3}\npublish_time: {4}"\
    #         .format(self.photo_id, self.url.encode('utf-8'), self.title.encode('utf-8'), self.author.encode('utf-8'),
    #                 time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.publish_time)) if self.publish_time else "None")
    # 从数据库出来的是 unicode, 从文件进来的是 utf-8,没有统一,这不行???

    @staticmethod  # 不需要类的实例就能执行,写在其他地方也可以
    def to_photo(photo_record):
        """
        把来自数据库的一条记录（record）即一行,处理成一个Photo类的实例,注意,.get('key1','default_value') 是操作字典的方法
        :param photo_record: 从数据库 self.db.get（） 出来的一条记录, 数据结构为字典,编码为 unicode
        :return: 一个 photo类的实例
        """
        publish_time = int(time.mktime(photo_record.get('publishTime', None).timetuple()) + 8 * 3600)  # 还需要加8*3600吗?
        # AttributeError: 'NoneType' object has no attribute 'timetuple' 这里用 none 不对,要改?
        return Photo(photo_record.get('photoId', None), photo_record.get('url', None),
                     photo_record.get('title', None), photo_record.get('author', None), publish_time)  # get 是字典自带的方法

    @staticmethod
    def to_photos(photo_items):
        photos = list()
        for photo_item in photo_items:
            photos.append(Photo.to_photo(photo_item))  # 静态方法 to_quiz 是属于 Quiz类的,而不属于其实例
        return photos

if __name__ == '__main__':

    test_dict = {"photoId": 123, "url": "http", "title": "啦啦", "author": "pudding", "publishTime": 0}
    photo = Photo.to_photo(test_dict)
    print type(photo)
    print type(photo.title)

