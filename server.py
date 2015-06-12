# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年03月04日 星期三 15时54分30秒
# 

'''
    The main file to start the tornado server
    start server in following steps:
    1. parse argument from command line
    2. start application in default port(80)
    3. create the loop instance and listen to the application
    4. add the hook that release the database connection while server reload
    5. start the instance

    启动服务器的主文件
    按照以下步骤启动tornado 网络服务器：
    1. 从命令行解析参数
    2. 开启监听默认(80)端口的application
    3. 实例化轮询端口的io循环
　　4. 增加自动重启时释放数据库连接的钩子
　　5. 开启实例
'''

import tornado.ioloop
import tornado.autoreload
import application
import database
from tornado.options import define, options


if __name__ == "__main__":
    tornado.options.parse_command_line()
    application.application.listen(80)
    server_instance = tornado.ioloop.IOLoop.instance()
    tornado.autoreload.add_reload_hook(database.release)
    server_instance.start()
