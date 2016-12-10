#!/usr/bin/env python
# -*-coding:utf-8-*-
import time
import torndb
import yaml
import random
from utils import *
from model import Photo


class PhotoDao:
    def __init__(self):
        conf = yaml.load(open('conf/service.yaml', 'r'))
        self.db = torndb.Connection(
            host=str(conf['database']['host']) + ':' + str(conf['database']['port']),
            database=str(conf['database']['database']),
            user=str(conf['database']['username']),
            password=str(conf['database']['password']))
        CrawlerLogger.logger.info("\n================connect {0} {1}==========\n".format(self.db.host, self.db.database))
        MysqlLogger.logger.info("\n=================connect {0} {1}==========\n".format(self.db.host, self.db.database))

    def import_from_file(self, file_name):
        """
        从文件录入数据库
        :param file_name: 文件路径、名
        :return:  读取到的记录数量,成功录入的记录数量
        """
        file_path = open(file_name, 'r')  # 'file' object
        return self.import_from_lines(file_path)  # import_from_lines 方法属于这个对象,所以前面要加 self

    def import_from_lines(self, lines):
        """
        从多行数据录入数据库
        :param lines: 待处理数据
        :return:  读取到的记录数量,成功录入的记录数量
        """
        (total, succ) = (0, 0)

        for line in lines:
            total += 1
            items = line.decode('utf-8').strip().split('\t')
            if len(items) < 3:
                CrawlerLogger.logger.info('line format error: {0}'.format(line))
                continue
            tmp_photo = Photo(0, items[0], items[1], items[2])

            if not self.insert_one_photo(tmp_photo):
                CrawlerLogger.logger.info('insert line failed: {0}'.format(line))
            else:
                succ += 1
        return total, succ

    def insert_one_photo(self, photo):
        """
            将一个 Photo 实例录入为一条数据库记录
            :param photo: 一个 Photo 实例
            :return:  False 或 True
            """

        if not isinstance(photo, Photo):  # 判断 photo 是不是 Photo 的实例
            CrawlerLogger.logger.error('photo type error: '.format(type(photo)))
            return False

        if self.is_exist(photo.url):
            CrawlerLogger.logger.error('This photo already exists: {0}'.format(photo.url.encode('utf-8')))
            # 输出到日志是到 utf-8文件,所以要编码
            self.update_one_photo(photo)
            return True

        sql = "insert into bai_photo(url, title, author) values ('{0}', '{1}', '{2}');"\
            .format(photo.url.encode('utf-8'), photo.title.encode('utf-8'), photo.author.encode('utf-8'))  # 向数据库执行的语句模板
        CrawlerLogger.logger.info('insert query: ' + sql)
        MysqlLogger.logger.info('insert query: ' + sql)

        try:
            self.db.insert(sql)
            return True

        except Exception as e:
            CrawlerLogger.logger.error("insert photo SQL: '{0}' failed\n".format(sql) + str(e))
            MysqlLogger.logger.error("insert photo SQL: '{0}' failed\n".format(sql) + str(e))
            return False

    def is_exist(self, url):
        """
            判断数据库中否已有某张图
            :param url: 标题, 编码为 unicode
            :return:  Photo 类的一个实例或 None
            """
        return self.get_photo_by_url(url) is not None

    def get_photo_by_url(self, url):
        """
        根据 url 从数据库表 bai_photo 里取一行(python会自动处理成字典类型),转换成程序中的一篇 photo
        :param url: 一个 key, 编码为 unicode
        :return:  Photo 类的一个实例
        """
        sql = "select * from bai_photo where url='{0}'".format(url)

        CrawlerLogger.logger.info('get photo SQL: {0}\n'.format(sql))
        MysqlLogger.logger.info('get photo SQL: {0}\n'.format(sql))
        photo_record = self.db.get(sql)  # 字典, get 方法会判断是不是有重复的,有重复的会报错
        if photo_record:
            return Photo.to_photo(photo_record)  # 这里其实不用 return 实例吧?return true 给 is_exist 判断就行了吧?
        return None

    def update_one_photo(self, photo):
        """
            更新数据库表 bai_photo 中已有的一篇文章
            :param photo: Photo 类的一个实例
            :return:  Photo 类的一个实例
            """
        if not isinstance(photo, Photo):
            CrawlerLogger.logger.error('photo type error'.format(type(photo)))
            return False

        update_sql = "update bai_photo set title='{0}', author='{1}' where url='{2}'" \
            .format(photo.title, photo.author, photo.url)

        CrawlerLogger.logger.info('update photo SQL: ' + update_sql)
        MysqlLogger.logger.info('update photo SQL: ' + update_sql)

        try:
            rows = self.db.update(update_sql)  # 返回影响的行数?
            if rows == 0:
                CrawlerLogger.logger.error('update nothing {0}'.format(str(photo)))
                MysqlLogger.logger.error('update nothing {0}'.format(str(photo)))
            return rows > 0
        except Exception as e:
            CrawlerLogger.logger.error('update photo {0} failed\n'.format(update_sql) + str(e))
            MysqlLogger.logger.error('update photo {0} failed\n'.format(update_sql) + str(e))  # format 只对 str 生效,所以 unicode 不行

    def get_latest_photos(self, total=6):
        """
        :param total: 需要的数量
        :return: 获取到的图
        """
        sql = 'SELECT * FROM bai_photo ORDER BY publishTime DESC LIMIT {0}'.format(total)
        CrawlerLogger.logger.info("get latest {0} photos SQL: {1}".format(str(total), sql))
        MysqlLogger.logger.info("get latest {0} photos SQL: {1}".format(str(total), sql))
        photo_records = self.db.query(sql)
        photos = Photo.to_photos(photo_records)
        if len(photos) < total:
            CrawlerLogger.logger.warning('Not enough photos, all photos have been gotten.')
            MysqlLogger.logger.info('Not enough photos, all photos have been gotten.')
        # print '===first photo===\n', photos[0].__str__(), '\n======',
        return photos  # <type 'list'>

if __name__ == '__main__':
    CrawlerLogger.set_up('logs/crawler.log')
    MysqlLogger.set_up('logs/mysql.log')
    photo_1 = Photo(0, '标题', '中文呢','author')
    # photo_2 = 2
    dao = PhotoDao()
    # dao.insert_one_photo(photo_1)
    dao.get_latest_photos(1)


