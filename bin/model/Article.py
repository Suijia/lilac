#!/usr/bin/env python
# -*-coding:utf-8-*-
import time
import chardet
__author__ = 'pudding'


class Article:
    def __init__(self, article_id, cover, title, snippet, detail_url, content, author, publish_time=None):  # 需要加 None吗? 本来想参数名就是数据库里的字段名,但警告说参数都要小写,就改了
        self.article_id = article_id
        self.cover = cover
        self.title = title
        self.snippet = snippet
        self.detail_url = detail_url
        self.content = content
        self.author = author
        self.publish_time = publish_time

    # def __str__(self):  # 只覆盖了 Article类的__str__,self 就是 quiz
    #     return "article_id: {0}\ncover: {1}\ntitle: {2}\nsnippet: {3}\ndetail_url: {4}\ncontent: {5}\nauthor: {6}\n" \
    #            "publish_time:{7}"\
    #         .format(self.article_id, self.cover, self.title.encode('utf-8'), self.snippet.encode('utf-8'),
    #                 self.detail_url, self.author.encode('utf-8'),
    #                 time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.publish_time)) if self.publish_time else "None")

    @staticmethod  # 属于这个类
    def to_article(article_record):
        """
        把来自数据库的一条记录（record）即一行,处理成程序中的一个 Article类的实例
        :param article_record: 实际上是字典,所以可以用.get('key1','default_value'),通常是一条数据库记录（<class 'torndb.Row'>）,编码为 unicode, 故中文内容需要编码,为什么中文不用??
        :return: 一个Article的实例
        """
        publish_time = int(time.mktime(article_record.get('publishTime', None).timetuple()) + 8 * 3600)  # 还需要加8*3600吗?

        return Article(article_record.get('articleId', None), article_record.get('cover', None),
                       article_record.get('title', None), article_record.get('snippet', None),
                       article_record.get('detailUrl', None), article_record.get('content', None),
                       article_record.get('author', None), publish_time)

    @staticmethod
    def to_articles(article_records):
        """
            把来自数据库的多条记录（record）即一行,处理成多个Article类的实例
            :param article_records: 多条数据库记录
            :return: 多个 Article 实例
        """
        articles = list()
        for article_record in article_records:
            articles.append(Article.to_article(article_record))
        return articles

if __name__ == '__main__':
    test_dict = {'articleId': 'id', 'cover': 'cover', 'title': '标题', 'snippet': '缩略', 'detailUrl': 'url', 'content': 'content', 'author': 'author'}
    one_article = Article.to_article(test_dict)

    # su = u'哈哈'.encode('utf-8')
    # s = 'haha'.decode('ascii')
    # result = "sql %s, %s"
    # print result
    # print type(result)



    # su = u'我们'.encode('utf-16')
    # su8 = u'我们'.encode('utf-8')
    # result_format = "中文,%s" % ('English')
    # print result_format
    # #
    # print chardet.detect(result_format)
    # # print type(type(su))

    # result_s = "heh我们,%s" % (su)
    # print type(result_s)
    # print chardet.detect(result_s)
    # print result_s
