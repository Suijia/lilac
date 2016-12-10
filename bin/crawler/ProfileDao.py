#!/usr/bin/env python
# -*-coding:utf-8-*-
import time
import torndb
import yaml
import random
from utils.CrawlerLogger import CrawlerLogger
from utils.MysqlLogger import MysqlLogger  # 为什么 Daisy 里 utils 的 init里为空也能跑?handler 就不行啊
from model import Profile


class ProfileDao:
    def __init__(self):
        conf = yaml.load(open('conf/service.yaml', 'r'))
        self.db = torndb.Connection(
            host=str(conf['database']['host']) + ':' + str(conf['database']['port']),
            database=str(conf['database']['database']),
            user=str(conf['database']['username']),
            password=str(conf['database']['password']))
        CrawlerLogger.logger.info("connect {0} {1}".format(self.db.host, self.db.database))
        MysqlLogger.logger.info("connect {0} {1}".format(self.db.host, self.db.database))

    def import_from_file(self, file_name):
        """
        从文件录入数据库
        :param file_name: 文件路径、名
        :return:  读取到的记录数量,成功录入的记录数量
        """
        file_path = open(file_name, 'r')
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
            items = line.decode('utf-8').strip().split('\t')  # 数据库接收的是 unicode,所以要解码
            if len(items) < 7:
                CrawlerLogger.logger.info('line format error: {0}'.format(line))
                continue
            tmp_profile = Profile(0, items[0], items[1], items[2], items[3], items[4], items[5], items[6])
            if not self.insert_one_profile(tmp_profile):
                CrawlerLogger.logger.info('insert line failed: {0}'.format(line))
            else:
                succ += 1
        return total, succ

    # def insert_profiles(self, profiles):
    #     """
    #         将多个 Profile 实例录入为数据库记录
    #         :param profiles: 一个或多个 Profile 实例
    #         :return:  录入成功的数量
    #         """
    #     succ = 0
    #     for profile in profiles:
    #         if self.insert_one_profile(profile):
    #             succ += 1
    #     return succ

    def insert_one_profile(self, profile):
        """
            将一个 Profile 实例录入为一条数据库记录
            :param profile: 一个 Profile 实例
            :return:  False 或 True
            """
        if not isinstance(profile, Profile):  # 判断 profile 是不是 Profile 的实例
            CrawlerLogger.logger.error('profile type error: '.format(type(profile)))
            return False

        if self.is_exist(profile.title):
            CrawlerLogger.logger.error('This profile already exists: {0}'.format(profile.title.encode('utf-8')))
            # 从文件读取时转成了 unicode,故写入日志文件要转成 utf-8
            self.update_one_profile(profile)
            return True

        # sql = 'insert into bai_profile(cover, title, snippet, detailUrl, content, author) ' \
        #       'values (%s, %s, %s, %s, %s, %s)'  # 向数据库执行的语句模板
        #
        # sql_str = sql % (profile.cover, profile.title, profile.snippet, profile.detail_url, profile.content,
        #                  profile.author)  # 向数据库执行的完整语句, 这句后半部是 unicode吧? 但是 sql是 utf-8的?
        # CrawlerLogger.logger.info('insert query ' + sql_str)  # 程序里的字符本来就是 utf-8 所以不用编码
        # # MysqlLogger.logger.info('insert query ' + sql_str)
        #
        # try:
        #     self.db.insert(sql, profile.cover, profile.title.encode('utf-8'), profile.snippet.encode('utf-8'),
        #                    profile.detail_url, profile.content.encode('utf-8'), profile.author.encode('utf-8'))
        #     # 咦,数据库不是 unicode 的吗为什么要utf-8?
        #     return True

        sql = 'insert into bai_profile(cover, title,subtitle, snippet, detailUrl, content, author) ' \
              'values (%s, %s, %s, %s, %s, %s, %s);'  # 向数据库执行的语句模板

        sql_str = sql % (profile.cover, profile.title, profile.subtitle, profile.snippet, profile.detail_url, profile.content,
                         profile.author)  # 向数据库执行的完整语句, 这句后半部是 unicode吧? 但是 sql是 utf-8的?
        CrawlerLogger.logger.info('insert query: ' + sql_str)  # 程序里的字符本来就是 utf-8 所以不用编码
        MysqlLogger.logger.info('insert query: ' + sql_str)

        try:
            self.db.insert(sql, profile.cover, profile.title.encode('utf-8'), profile.subtitle.encode('utf-8'), profile.snippet.encode('utf-8'),
                           profile.detail_url, profile.content.encode('utf-8'), profile.author.encode('utf-8'))
            # 咦,数据库不是 unicode 的吗为什么要utf-8?
            return True

        except Exception as e:
            CrawlerLogger.logger.error("insert profile: '{0}' failed\n".format(sql) + str(e))
            MysqlLogger.logger.error("insert profile: '{0}' failed\n".format(sql) + str(e))
            return False

    def is_exist(self, title):
        """
            判断数据库中否已有某篇文章
            :param title: 标题, 编码为 unicode
            :return:  Profile 类的一个实例或 None
            """
        return self.get_profile_by_title(title) is not None

    def get_profile_by_title(self, title):
        """
        根据 title 从数据库表 bai_profile 里取一行(python会自动处理成字典类型),转换成程序中的一篇 profile
        :param title: 一个 key, 编码为 unicode
        :return:  Profile 类的一个实例
        """
        sql = 'select * from bai_profile where title=%s'
        sql_str = sql % title.encode('utf-8')
        CrawlerLogger.logger.info('get: {0}\n'.format(sql_str))
        MysqlLogger.logger.info('get: {0}\n'.format(sql_str))
        profile_record = self.db.get(sql, title)
        if profile_record:
            return Profile.to_profile(profile_record)  # 这里其实不用 return 实例吧?return true 给 is_exist 判断就行了吧?
        return None

    def update_one_profile(self, profile):
        """
            更新数据库表 bai_profile 中已有的一篇文章
            :param profile: Profile 类的一个实例
            :return:  Profile 类的一个实例
            """
        if not isinstance(profile, Profile):
            CrawlerLogger.logger.error('profile type error'.format(type(profile)))
            return False

        update_sql = "update bai_profile set cover='{0}', subtitle='{1}',snippet='{2}', detailUrl='{3}', content='{4}', " \
                     "author='{5}' where title='{6}'" \
            .format(profile.cover, profile.subtitle.encode('utf-8'), profile.snippet.encode('utf-8'), profile.detail_url,
                    profile.content.encode('utf-8'), profile.author.encode('utf-8'), profile.title.encode('utf-8'))
        # 咦,数据库不是 unicode 的吗为什么要utf-8?
        CrawlerLogger.logger.info('update query: ' + update_sql)
        MysqlLogger.logger.info('update query: ' + update_sql)

        try:
            rows = self.db.update(update_sql)  # 返回影响的行数?
            if rows == 0:
                CrawlerLogger.logger.error('update nothing {0}'.format(str(profile)))
                MysqlLogger.logger.error('update nothing {0}'.format(str(profile)))
            return rows > 0
        except Exception as e:
            CrawlerLogger.logger.error('update profile {0} failed\n'.format(update_sql) + str(e))
            MysqlLogger.logger.error('update profile {0} failed\n'.format(update_sql) + str(e))

    # def get_profile_by_id(self, profile_id):
    #     """
    #     从数据库中取出指定 id 的一项(字典类型),并处理成程序中的一条 quiz
    #     :param profile_id: 一个 key
    #     :return:  Profile 类的一个实例
    #     """
    #     sql = 'select * from bai_profile where profileId=%s'
    #     sql_str = sql % profile_id
    #     CrawlerLogger.logger.info('get: {0}\n'.format(sql_str))
    #     MysqlLogger.logger.info('get: {0}\n'.format(sql_str))
    #     profile_record = self.db.get(sql, profile_id)
    #     if profile_record:
    #         return Profile.to_profile(profile_record)
    #     return None

    def get_latest_profiles(self, total=3):
        """

        :param total: 需要的文章数量
        :return: 获取到的文章
        """
        sql = 'SELECT * FROM bai_profile ORDER BY publishTime DESC LIMIT {0}'.format(total)
        CrawlerLogger.logger.info('get latest ' + str(total) + ' profiles: ' + sql)
        MysqlLogger.logger.info('get latest ' + str(total) + ' profiles: ' + sql)
        profile_records = self.db.query(sql)  # db.query 又不是这个类的方法,为什么要 self 而不是 tornado.db.query呢?
        profiles = Profile.to_profiles(profile_records)
        return profiles  # <type 'list'>
        # 待补充 total 超出总记录数的处理?


if __name__ == '__main__':
    CrawlerLogger.set_up('logs/crawler.log')
    MysqlLogger.set_up('logs/mysql.log')
    dao = ProfileDao()
    #dao.import_from_file('docs/bai_profile1')
    one_profile = dao.get_latest_profiles(2)
    print "one_profile's type(expected <type 'list'>):", type(one_profile)
    print "one_profile's type(expected <type 'list'>):", type(one_profile[0])

