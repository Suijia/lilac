#!/usr/bin/env python
# -*-coding:utf-8-*-
import time
import torndb
import yaml
import random
from utils import *
from model import Video


class VideoDao:
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
            items = line.strip().split('\t')
            # 如果所读取的文件编码不为 utf-8,则需要 line.encode('<the_coding_of_str>').decode('utf-8').strip().split('\t')
            if len(items) < 7:
                CrawlerLogger.logger.info('line format error: {0}'.format(line))
                continue
            tmp_video = Video(0, items[0], items[1], items[2], items[3], items[4], items[5], items[6])

            if not self.insert_one_video(tmp_video):
                CrawlerLogger.logger.info('insert line failed: {0}'.format(line))
            else:
                succ += 1
        return total, succ

    def insert_one_video(self, video):
        """
            将一个 Video 实例录入为一条数据库记录
            :type video: object
            :param video: 一个 Video 实例
            :return:  False 或 True
            """

        if not isinstance(video, Video):  # 判断 video 是不是 Video 的实例
            CrawlerLogger.logger.error('video type error: '.format(type(video)))
            return False

        if self.is_exist(video.detail_url):
            CrawlerLogger.logger.error('This video already exists: {0}'.format(video.detail_url))
            self.update_one_video(video)
            return True

        sql = "insert into bai_video(cover, videoTime, detailUrl, title, snippet, tag, author) " \
              "values ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}');"\
            .format(video.cover, video.video_time, video.detail_url, video.title, video.snippet, video.tag, video.author)  # 向数据库执行的语句模板
        CrawlerLogger.logger.info('insert query: ' + sql)
        MysqlLogger.logger.info('insert query: ' + sql)

        try:
            self.db.insert(sql)
            return True

        except Exception as e:
            CrawlerLogger.logger.error("insert video SQL: '{0}' failed\n".format(sql) + str(e))
            MysqlLogger.logger.error("insert video SQL: '{0}' failed\n".format(sql) + str(e))
            return False

    def is_exist(self, url):
        """
            判断数据库中否已有某张图
            :param url: 标题, 编码为 unicode
            :return:  Video 类的一个实例或 None
            """
        return self.get_video_by_url(url) is not None

    def get_video_by_url(self, url):
        """
        根据 url 从数据库表 bai_video 里取一行(python会自动处理成字典类型),转换成程序中的一篇 video
        :param url: 一个 key, 编码为 unicode
        :return:  Video 类的一个实例
        """
        sql = "select * from bai_video where detailUrl='{0}'".format(url)

        CrawlerLogger.logger.info('get video SQL: {0}\n'.format(sql))
        MysqlLogger.logger.info('get video SQL: {0}\n'.format(sql))
        video_record = self.db.get(sql)  # 字典, get 方法会判断是不是有重复的,有重复的会报错
        if video_record:
            return Video.to_video(video_record)  # 这里其实不用 return 实例吧?return true 给 is_exist 判断就行了吧?
        return None

    def update_one_video(self, video):
        """
            更新数据库表 bai_video 中已有的一篇文章
            :param video: Video 类的一个实例
            :return:  Video 类的一个实例
            """
        if not isinstance(video, Video):
            CrawlerLogger.logger.error('video type error'.format(type(video)))
            return False

        update_sql = "update bai_video set cover='{0}', videoTime='{1}', title='{2}', snippet='{3}'," \
                     " tag='{4}', author='{5}' where detailUrl='{6}'" \
            .format(video.cover, video.video_time, video.title, video.snippet, video.tag, video.author, video.detail_url)

        CrawlerLogger.logger.info('update video SQL: ' + update_sql)
        MysqlLogger.logger.info('update video SQL: ' + update_sql)

        try:
            rows = self.db.update(update_sql)  # 返回影响的行数?
            if rows == 0:
                CrawlerLogger.logger.error('update nothing {0}'.format(str(video)))
                MysqlLogger.logger.error('update nothing {0}'.format(str(video)))
            return rows > 0
        except Exception as e:
            CrawlerLogger.logger.error('update video SQL: {0} failed\n'.format(update_sql) + str(e))
            MysqlLogger.logger.error('update video SQL: {0} failed\n'.format(update_sql) + str(e))  # format 只对 str 生效,所以 unicode 不行

    def get_latest_videos(self, total=6):
        """
        :param total: 需要的数量
        :return: 获取到的图
        """
        sql = 'SELECT * FROM bai_video ORDER BY publishTime DESC LIMIT {0}'.format(total)
        CrawlerLogger.logger.info("get latest {0} videos SQL: {1}".format(str(total), sql))
        MysqlLogger.logger.info("get latest {0} videos SQL: {1}".format(str(total), sql))
        video_records = self.db.query(sql)
        videos = Video.to_videos(video_records)
        if len(videos) < total:
            CrawlerLogger.logger.warning('Not enough videos, all videos have been gotten.')
            MysqlLogger.logger.info('Not enough videos, all videos have been gotten.')
        # print '===first video===\n', videos[0].__str__(), '\n======',
        return videos  # <type 'list'>

if __name__ == '__main__':
    CrawlerLogger.set_up('logs/crawler.log')
    MysqlLogger.set_up('logs/mysql.log')
    # video_2 = 2
    dao = VideoDao()
    # dao.import_from_file("docs/bai_video1")
    mydao = dao.get_latest_videos(1)
    print mydao



