# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年03月05日 星期四 09时51分22秒
# 
'''
    A simple file to set settings and load modules
    设置服务器设置与载入模块的简单文件
'''
import os 
import modules

'''
    modules are loaded in the form of key-value like:
        '[MODULE ALIAS]: [MODULE CLASS]'
    to load new modules, the reload of server is required

    模块将会以键值的形式载入：
        '[模块别名]':'[模块类]'
    需要重启服务器以使新模块载入
'''
all_module = {
    'ArticleItem': modules.ArticleItemModule, #文章列表项模块
    'Article': modules.ArticleModule, #文章模块
    'BackTop': modules.BackTopModule, #返回顶部动态模块
    'Logout': modules.LogoutModule, #注销动态模块
    'Collect': modules.CollectModule, #收藏动态模块
    'NewKeyword': modules.NewKeywordModule, #新建关键字动态模块
    'List': modules.ListModule, #下拉刷新动态模块
}

'''
    all server settings could be set here as the form of key-value:
        '[SETTINGS NAME]': '[SETTINGS VALUE]'
    
    所有的服务器设置都以键值对的形式在settings中定义：
        '[设置项]':'[设置值]'
'''
settings = {
    'debug' : True, #调试选项，开启后每一次源文件的更改将会自动重启服务器(而不需要手动操作)
    'xsrf_cookies' : True, #xsrf验证，需要cookie_secret设置项
    'login_url' : '/login', #登陆url，在get_current_user验证失败后的默认页面重定向地址
    'cookie_secret' : 'KPbSmiu/T8OO8T0TQFIwCfN2e1BxFkwQslfliXClLjk=', #cookie加密项
    'static_path' : os.path.join(os.path.dirname(__file__), 'static'), #静态文件地址
    'template_path' : os.path.join(os.path.dirname(__file__), 'templates'), #前端模板文件地址
    #'log_file_prefix': '8888.log',
    'ui_modules':all_module, #模块载入项
}

