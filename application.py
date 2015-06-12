#u -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年03月04日 星期三 20时34分03秒
# 
'''
    A simple file to create a application instance
    which defined the rules to match request
    and load settings
    
    实例化application的简单文件，
    在这里定义请求的url匹配规则并读取服务器设置
'''
import tornado.web
import handlers
from settings import settings


'''
    rules are defined as a tuple of a list like:
        (r"[RE TEMPLATE]", [HANDLER CLASS])
    规则以列表中的元组形式定义:
        (r"[正则匹配模板]", [handler　类])
'''
application = tornado.web.Application([
    (r"/", handlers.LoginHandler),
    (r"/list/(\w+)", handlers.ListHandler),
    (r"/register", handlers.RegisterHandler),
    (r"/login", handlers.LoginHandler),
    (r"/logout", handlers.LogoutHandler),
    (r"/collection", handlers.CollectionHandler),
    (r"/settings(/\w+)*", handlers.SettingsHandler),
    (r"/search", handlers.SearchHandler),
    (r"/article/(\d+)", handlers.ArticleHandler),
], **settings)
