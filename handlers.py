# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年03月05日 星期四 09时49分35秒
# 
'''
    Handlers dealing with requests
    处理请求的handlers
'''
import tornado.web
import tornado.template
import handlers
import logging
import database
import gen
import json

class BaseHandler(tornado.web.RequestHandler):
    '''
        base handler, the base class of other handlers
        handle the requests which do not be matched by any rules in application
        which raise an 404 error
        
        基础handler，是其他handler的基类，将404错误即未被规则匹配的请求重定向到404网页
    '''
    def get(self):
        self.write_error(404)
    
    def write_error(self, status_code, **kwargs):
        self.render('404.html', title="404")
    
class SafeHandler(BaseHandler):
    '''
        This handler is designed to define the get_current_user method 
        which is the default method called by methods 
        decorated by @tornado.web.authenticated
        
        handler 用来定义get_current_user方法，该方法在其他方法请求检查用户是否登陆时被调用
    '''
    
    def get_current_user(self):
        return self.get_secure_cookie("user_id")

class RegisterHandler(BaseHandler):
    def get(self):
        self.render(
            "register.html",
            title="企业信息服务平台－用户注册",
            models=database.Model.selectall(),
        )

    def post(self):
        user_name = self.get_argument("username")
        #检查用户名是否存在
        if not database.User.check(user_name):
            self.write("用户名已存在！")
        else:
            password = self.get_argument("password")
            user_model = self.get_argument("model")
            keywords = self.get_argument("keyword")
            user_id = database.User.new(user_name, password, user_model)
            if keywords:
                keywords = keywords.split(';')
                for keyword in keywords:
                    database.Keyword.new(keyword, user_id) 
            self.write("Success")

class LoginHandler(BaseHandler):
    def get(self):
        self.render(
            "login.html",
            title="企业信息服务平台-用户登录",
        )
    
    def post(self):
        user_name = self.get_argument('username')
        user_password = self.get_argument('password')
        if not database.User.login(user_name, user_password):
            #密码错误
            self.redirect('/login')
        else:
            remember_me = self.get_argument('remember', None)
            expires = 7 #cookie过期时间
            if remember_me is None:
                expires = None
            self.set_secure_cookie(
                'user_id', 
                str(database.User.select(user_name=user_name).user_id), 
                expires_days=expires,
            )
            self.redirect('/search')

class SearchHandler(SafeHandler):
    @tornado.web.authenticated
    def get(self):
        self.render(
            "search.html",
            title="企业信息服务平台-搜索"
        )

    @tornado.web.authenticated
    def post(self):
        search_word = json.dumps(self.get_argument('keyword').split())
        search_id = database.Search.new(search_word)
        self.set_secure_cookie(
            'search_id',
            str(search_id),
        )
        if gen.search(search_id).next(): 
            redirect_url =\
                (
                    '/list/search?'
                    'search_id={search_id}'
                ).format(search_id=search_id)
            self.redirect(redirect_url)
        else:
            self.send_error(404) 

class ListHandler(SafeHandler):
    list_actives = {
        'search': 2,
        'collected': 4,
    }

    @tornado.web.authenticated
    def get(self, list_type):
        user_id = self.get_current_user()
        self.render(
            "list.html", 
            title="企业信息服务平台", 
            active_index=self.list_actives[list_type],
        )

    @tornado.web.authenticated
    def post(self, list_type):
        user_id = self.get_secure_cookie('user_id')
        page_index = int(self.get_argument('page_index'))
        bunch_index = int(self.get_argument('bunch_index'))
        refresh = True if self.get_argument('refresh') == 'true' else False 

        page = database.Page(bunch_index=bunch_index, page_index=page_index)
        collected_search = user_id

        if list_type == 'search':
            search_id = self.get_argument('search_id')
            search_result = database.Search.select(search_id)
            if search_result.search_status != 'Success':
                self.write(str(search_result.search_status))
                return
            data_range = json.loads(search_result.search_result)
            def inter(listA, listB):
                return list(set(listA).intersection(set(listB)))
            data_range = reduce(inter, data_range)

        if list_type == 'collected':
            data_range = database.Action.selectmany(user_id)
            collected_search = None 

        page = page.paging(user_id, data_range=data_range, refresh=refresh)
        print page
        
        page_data = database.Data.query(page, collected_search=collected_search)

        def get_title(data):
            data.data_title = json.loads(data.data_content)['title']
        map(get_title, page_data)
        self.write(''.join(
            [
                self.render_string(
                    "module/articleItem.html", 
                    article_item=data,
                ) for data in page_data
            ]
        ))

class SettingsHandler(SafeHandler):
    @tornado.web.authenticated
    def get(self, null):
        user_id = self.get_current_user()
        user = database.User.select(user_id=user_id)       
        keywords = database.Keyword.select(user_id)
        self.render(
            "settings.html", 
            title="企业信息服务平台-用户设置", 
            user_info=user_info,
            keywords=keywords,
            active_index=5,
        )
    
    @tornado.web.authenticated
    def post(self, string):
        keyword = self.get_argument('keyword')
        keyword = keyword.encode('utf-8')
        user_id = self.get_current_user()
        if string == '/delete_keyword':
            database.Keyword.delete(keyword, user_id)
        if string == '/new_keyword':
            database.Keyword.new(keyword, user_id)

class LogoutHandler(SafeHandler):
    @tornado.web.authenticated
    def post(self):
        self.clear_all_cookies()

class ArticleHandler(SafeHandler):
    @tornado.web.authenticated
    def get(self, data_id):
        user_id = self.get_current_user()
        all_data = database.Data.select(data_id)
        if all_data is None:
            self.raise_error(404)
        data = json.loads(all_data.data_content)
        data['data_id'] = all_data.data_id
#        data["data_score"] = self.get_argument('data_score')
        data["data_score"] = 0
        ifcollected =\
            database.Action.check(
                data_id,
                user_id,
                action_score=database.Action.COLLECT,
            )
        self.render(
            'article.html',
            title=data["title"], 
            article=data,
            ifcollected=ifcollected,
            active_index=None,
        )

class CollectionHandler(SafeHandler):
    @tornado.web.authenticated
    def post(self):
        user_id = self.get_current_user()
        ifcollected = False\
            if self.get_argument("collected") == 'false' else True 
        data_id = self.get_argument("data_id")
        if self.get_argument("collected") == 'false':
            database.Action.new(data_id, user_id, database.Action.COLLECT)
        else:
            database.Action.delete(data_id, user_id, database.Action.COLLECT)
        self.write("success")
