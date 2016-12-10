#!/usr/bin/env python
# -*-coding:utf-8-*-
import time
import torndb
import yaml
import random
from utils.CrawlerLogger import CrawlerLogger
from utils.MysqlLogger import MysqlLogger  # 为什么 Daisy 里 utils 的 init里为空也能跑?handler 就不行啊
from model import Article


class ArticleDao:
    def __init__(self):
        conf = yaml.load(open('conf/service.yaml', 'r'))
        self.db = torndb.Connection(
            host=str(conf['database']['host']) + ':' + str(conf['database']['port']),
            database=str(conf['database']['database']),
            user=str(conf['database']['username']),
            password=str(conf['database']['password']))
        CrawlerLogger.logger.info("\n================connect {0} {1}==========\n".format(self.db.host, self.db.database))
        MysqlLogger.logger.info("\n================connect {0} {1}==========\n".format(self.db.host, self.db.database))

    def import_from_file(self, file_name):
        """
        从文件录入数据库
        :param file_name: 文件路径、名
        :return:  读取到的记录数量,成功录入的记录数量
        """
        file_path = open(file_name, 'r')
        return self.import_from_lines(file_path)

    def import_from_lines(self, lines):  # 能单独用吗?为什么不和 import_from_file 一起?
        """
        从多行数据录入数据库
        :param lines: 待处理数据
        :return:  读取到的记录数量,成功录入的记录数量
        """
        (total, succ) = (0, 0)
        for line in lines:  # 哪些结构可以用for in?（list 可以）
            total += 1
            items = line.decode('utf-8').strip().split('\t')   # 从文件到程序,解码为 unicode
            if len(items) < 6:
                CrawlerLogger.logger.error('line format error: {0}'.format(line))
                # format 不接受中文的 unicode, 所以用utf-8的 line
                continue
            tmp_article = Article(0, items[0], items[1], items[2], items[3], items[4], items[5])  # unicode
            if not self.insert_one_article(tmp_article):
                CrawlerLogger.logger.warning('Fail to insert this line: {0}'.format(line))
            else:
                succ += 1
        return total, succ

    def insert_one_article(self, article):
        """
            将一个 Article 实例录入为一条数据库记录
            :param article: 一个 Article 实例
            :return:  False 或 True
        """
        if not isinstance(article, Article):
            CrawlerLogger.logger.error('article type error: {0}'.format(type(article)))
            return False

        if self.is_exist(article.title):
            CrawlerLogger.logger.warning('This article already exists: {0}'.format(article.title.encode('utf-8')))
            self.update_one_article(article)
            return True

        sql = "insert into bai_article(cover, title, snippet, detailUrl, content, author) values ('{0}', '{1}', " \
              "'{2}', '{3}', '{4}', '{5}');"\
            .format(article.cover, article.title.encode('utf-8'), article.snippet.encode('utf-8'), article.detail_url,
                    article.content.encode('utf-8'), article.author.encode('utf-8'))  # 向数据库执行的语句

        CrawlerLogger.logger.info('Try to insert: ' + sql)
        MysqlLogger.logger.info('Try to insert : ' + sql)

        try:
            self.db.insert(sql)
            return True

        except Exception as e:
            CrawlerLogger.logger.error("Fail to execute SQL: '{0}'\n".format(sql) + str(e))
            MysqlLogger.logger.error("Fail to execute SQL: '{0}'\n".format(sql) + str(e))
            return False

    def is_exist(self, title):
        """
            判断数据库中否已有某篇文章
            :param title: 标题, 编码为 unicode
            :return:  Article 类的一个实例或 None
            """
        return self.get_article_by_title(title) is not None

    def get_article_by_title(self, title):
        """
        根据 title 从数据库表 bai_article 里取一行(python会自动处理成字典类型),转换成程序中的一篇 article
        :param title: 一个 key, 编码为 unicode
        :return:  Article 类的一个实例
        """
        sql = 'select * from bai_article where title=%s'
        sql_str = sql % title.encode('utf-8')
        CrawlerLogger.logger.info('get: {0}\n'.format(sql_str))
        MysqlLogger.logger.info('get: {0}\n'.format(sql_str))
        article_record = self.db.get(sql, title)
        if article_record:
            return Article.to_article(article_record)  # 这里其实不用 return 实例吧?return true 给 is_exist 判断就行了吧?
        return None

    def update_one_article(self, article):
        """
            更新数据库表 bai_article 中已有的一篇文章
            :param article: Article 类的一个实例
            :return:  Article 类的一个实例
            """
        if not isinstance(article, Article):
            CrawlerLogger.logger.error('article type error'.format(type(article)))
            return False

        update_sql = "update bai_article set cover='{0}', snippet='{1}', detailUrl='{2}', content='{3}', " \
                     "author='{4}' where title='{5}'" \
            .format(article.cover, article.snippet.encode('utf-8'), article.detail_url,
                    article.content.encode('utf-8'), article.author.encode('utf-8'), article.title.encode('utf-8'))

        # update_sql = "update bai_article set cover='{0}', snippet='{1}', detailUrl='{2}', content='{3}', " \
        #              "author='{4}' where title='{5}'" \
        #     .format(article.cover, article.snippet, article.detail_url,
        #             article.content, article.author, article.title)

        CrawlerLogger.logger.info('update query: ' + update_sql)
        MysqlLogger.logger.info('update query: ' + update_sql)

        try:
            rows = self.db.update(update_sql)  # 返回影响的行数
            if rows == 0:
                CrawlerLogger.logger.info('update nothing {0}'.format(str(article)))
                MysqlLogger.logger.info('update nothing {0}'.format(str(article)))
            return rows > 0
        except Exception as e:
            CrawlerLogger.logger.error('update article {0} failed\n'.format(update_sql) + str(e))
            MysqlLogger.logger.error('update article {0} failed\n'.format(update_sql) + str(e))

    def get_latest_articles(self, total=3):
        """

        :param total: 需要的文章数量
        :return: 获取到的文章
        """
        sql = 'SELECT * FROM bai_article ORDER BY publishTime DESC LIMIT {0}'.format(total)
        CrawlerLogger.logger.info('get latest ' + str(total) + ' articles: ' + sql)
        MysqlLogger.logger.info('get latest ' + str(total) + ' articles: ' + sql)
        article_records = self.db.query(sql)
        articles = Article.to_articles(article_records)
        return articles  # <type 'list'>
        # 待补充 total 超出总记录数的处理


if __name__ == '__main__':

    CrawlerLogger.set_up('logs/crawler.log')
    MysqlLogger.set_up('logs/mysql.log')
    dao = ArticleDao()
    dao.import_from_file('docs/bai_article2')  ## 测试 insert
    # one_article = dao.get_latest_articles(1)
    # print "one_article's type(expected <type 'list'>):", type(one_article)
    # print "one_article's type(expected <type 'list'>):", type(one_article[0])
