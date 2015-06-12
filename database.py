# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年03月06日 星期五 16时36分19秒
# 

'''
    The file create the database connection instance
    and predefined the functions to handler database

    文件创建了连接数据库的实例并预定义了对数据库的操作函数
'''

import torndb
import logging
import json
import tornado.web
import os


'''
    create the MySQL connection instance using torndb as:
        torndb.Connection([ADDR],[DATABASE],user=[USER],password=[PASSWORD])

    以以下形式创建了MySQL数据库连接：
        torndb.Connection([数据库地址],[访问数据库],user=[用户名],password=[密码])
'''

try:
    COMPANY_SERVICE =\
        torndb.Connection(
            'mysql.service.consul',
            'company_service',
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWD'),
        )
    CONTRIBUTE_CRAWLER =\
        torndb.Connection(
            'mysql.service.consul',
            'contribute_crawler',
            user=os.getenv('DATABASE_USER'),
            password=os.getenv('DATABASE_PASSWD'),
        )
except torndb.OperationalError:
    logging.exception()
    raise tornado.web.send_error(404)

def release():
    '''
        Function to release the connection
        释放数据库连接函数
    '''
    COMPANY_SERVICE.close()
    CONTRIBUTE_CRAWLER.close()

class User(object):

    @staticmethod
    def select(user_id=None, user_name=None):
        sql =\
            (
                'SELECT '
                'user_id, '
                'user_name, '
                'user_password, '
                'user_model '
                'FROM user '
            )
        result = None

        if user_id is not None:
            sql += 'WHERE user_id = {user_id}'.format(user_id=user_id)
            result = COMPANY_SERVICE.get(sql)
        elif user_name is not None:
            sql += 'WHERE user_name = %s'
            logging.error(sql)
            result = COMPANY_SERVICE.get(sql, user_name)
        

        if result is None:
            return
        
        return result

    @staticmethod
    def login(user_name, user_password):
        user = User.select(user_name=user_name)
        if user.user_password == user_password:
            return True
        return False

    @staticmethod
    def check(user_name):
        user = User.select(user_name=user_name)
        logging.error(user)
        if user is None:
            return True
        return False

    @staticmethod
    def new(user_name, user_password, user_model):
        sql =\
            (
                'INSERT INTO user VALUES('
                'null, '
                '%s, '
                '%s, '
                '{user_model}, '
                'null )'
            ).format(user_model=user_model)
        return COMPANY_SERVICE.insert(sql, user_name, user_password)

    @staticmethod
    def score(user_id):
        sql =\
            (
                'SELECT user_score '
                'FROM user '
                'WHERE user_id = {user_id}'
            ).format(user_id=user_id)
        result = COMPANY_SERVICE.get(sql)
        return result.user_score if result is not None else result

class Page(object):
    __slots__ = [
        'page_index',
        'bunch_index',
        'page_size',
        'bunch_num',
    ]
    
    def __init__(self, page_index=0, bunch_index=0, page_size=200, bunch_num=10):
        self.page_index = page_index
        self.bunch_index = bunch_index
        self.page_size = page_size
        self.bunch_num = bunch_num

    def paging(self, user_id, data_range=None, refresh=False):
        user_score = User.score(user_id)
        bunch_size = self.page_size / self.bunch_num
        start_index = self.page_index * self.page_size
        end_index = start_index + (self.bunch_index + 1) * bunch_size
        if refresh:
            start_index += self.bunch_index * bunch_size

        try:
            user_score = json.loads(user_score)
        except ValueError, e:
            logging.exception(e)
            user_score = {}
        
        if data_range is not None:
            user_score = [(k, user_score.get(str(k), 0)) for k in data_range]
        
        elif end_index > len(user_score):
            load_num = len(user_score) - end_index
            start_num = load_num - bunch_size if load_num > bunch_size else 0
            load_data = Data.query_in_id(start_num, load_num)
            load_data = [(data, 0) for data in load_data if data not in user_score]
            user_score.extend(load_data)
        
        user_score.sort(key=lambda x:x[1], reverse=True)
        
        return user_score[start_index:end_index]
            
class Action(object):
    COLLECT = 1

    @staticmethod    
    def check(data_id, user_id, action_score):
        sql =\
            (
                'SELECT * '
                'FROM action '
                'WHERE data_id = {data_id} '
                'AND user_id = {user_id} '
                'AND action_score = {action_score}'
            ).format(
                data_id=data_id,
                user_id=user_id,
                action_score=action_score,
            )
        result = COMPANY_SERVICE.get(sql)
        if result is None:
            return False
        return True

    @staticmethod    
    def selectmany(user_id, action_score):
        sql =\
            (
                'SELECT * '
                'FROM action '
                'WHERE user_id = {user_id} '
                'AND action_score = {action_score}'
            ).format(
                user_id = user_id,
                action_score = action_score,
            )
        return COMPANY_SERVICE.query(sql)

    @staticmethod    
    def new(data_id, user_id, action_score):
        sql =\
            (
                'INSERT INTO action '
                'VALUES({data_id}, {user_id}, {action_score})'
            ).format(
                data_id=data_id,
                user_id=user_id,
                action_score=action_score,
            )
        return COMPANY_SERVICE.insert(sql)
    
    @staticmethod    
    def delete(data_id, user_id, action_score):
        sql =\
            (
                'DELETE FROM action '
                'WHERE data_id = {data_id} '
                'AND user_id = {user_id} '
                'AND action_score = {action_score}'
            ).format(
                data_id=data_id,
                user_id=user_id,
                action_score=action_score,
            )
        COMPANY_SERVICE.execute(sql)
        
class Data(object):

    @staticmethod
    def select(data_id):
        sql =\
            (
                'SELECT * '
                'FROM contribute_crawler.data '
                'WHERE data_id = {data_id}'
            ).format(data_id=data_id)
        result = CONTRIBUTE_CRAWLER.get(sql)
        if result is None:
            return
        return result

    @staticmethod
    def query_in_id(start=0, end=-1):
        sql =\
            (
                'SELECT data_id '
                'FROM contribute_crawler.data '
                'LIMIT {start}, {end}'
            ).format(
                start=start,
                end=end,
            )
        return CONTRIBUTE_CRAWLER.query(sql)

    @staticmethod
    def query(data_dict, collected_search=None):
        data_list = []
        for key, value in data_dict:
            one_data = Data.select(key)
            one_data.data_score = value
            if collected_search is None:
                one_data.data_ifcollected = True
            else:
                one_data.data_ifcollected =\
                    Action.check(
                        data_id=one_data.data_id,
                        user_id=collected_search,
                        action_score=Action.COLLECT,
                    )
            data_list.append(one_data)
        return data_list
    
class Model(object):

    @staticmethod    
    def select(model_id):
        sql =\
            (
                'SELECT * '
                'FROM model '
                'WHERE model_id = {model_id}'
            ).format(
                model_id=model_id,
            )
        return COMPANY_SERVICE.get(sql)
   
    @staticmethod 
    def selectall():
        sql =\
            (
                'SELECT * '
                'FROM model '
            )
        return COMPANY_SERVICE.query(sql)

class Keyword(object):
    
    @staticmethod
    def select(user_id):
        sql =\
            (
                'SELECT * '
                'FROM keyword '
                'WHERE user_id = {user_id}'
            ).format(user_id=user_id)
        return COMPANY_SERVICE.query(sql)

    @staticmethod
    def new(keyword, user_id):
        sql =\
            (
                'INSERT INTO keyword '
                'VALUES('
                '%s, '
                '{user_id})'
            ).format(user_id=user_id)
        return COMPANY_SERVICE.insert(sql, keyword)

    @staticmethod
    def delete(keyword, user_id):
        sql =\
            (
                'DELETE FROM keyword '
                'WHERE keyword = %s '
                'AND user_id = {user_id}'
            ).format(user_id=user_id)
        COMPANY_SERVICE.execute(sql)

class Search(object):
    
    @staticmethod
    def new(search_word):
        sql =\
            (
                'INSERT INTO search '
                'VALUES('
                'null, '
                '%s, '
                'null, '
                'null)'
            )
        return COMPANY_SERVICE.insert(sql, search_word)

    @staticmethod
    def select(search_id):
        sql =\
            (
                'SELECT * '
                'FROM search '
                'WHERE search_id = {search_id}'
            ).format(search_id=search_id)
        return COMPANY_SERVICE.get(sql)
