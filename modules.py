# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年03月05日 星期四 20时15分38秒
# 
'''
    Modules
    模块
'''
import tornado.web

class ArticleItemModule(tornado.web.UIModule):
    def render(self, article_item):
        return self.render_string('module/articleItem.html', article_item=article_item)
    def embedded_css(self):
        return\
            '''
                .list-group-item {
                    color:#958976;
                    height:100px;
                    padding:20px 10px
                }
                .list-group-item-heading{
                    margin-bottom:10px;
                    font-size:1.5em
                }
                .right-info{
                    text-align: right
                }
                .collection{
                    margin-left: 10px;
                    color: #611427;
                }
            '''


    def embedded_javascript(self):
        return\
            '''
                $(".collection").click(
                    function(e){
                        var cSpan = $(this);
                        e.preventDefault();
                        var ifcollected = true;
                        if(cSpan.hasClass("uncollected")){
                            ifcollected = false;
                        }
                        collect(cSpan, ifcollected, cSpan.parents("a").prev().attr("name"));
                    }
                    
                );
            '''

    def javascript_files(self):
        return '/static/js/collect.js'

class ArticleModule(tornado.web.UIModule):
    def render(self, article):
        return self.render_string('module/article.html', article=article)
    def embedded_css(self):
        return\
            '''
                .article-body{
                    padding:40px;
                }                
                .article-body-title{
                    text-align:center;
                    margin-bottom: 50px;
                }
                li#backTop{
                }
                .score{
                    width: 150px;
                    height: 150px;
                    border-radius: 400px;
                    background-color: #611427;
                    color: #fff;
                    line-height: 150px;
                    text-align: center;
                    font-size: 3em;
                }
                .info{
                    margin-top: 20px;
                }
                .info .info-title{
                    font-size: 1.2em;
                    font-weight: bold;
                }
                .info .info-li{
                    margin-top: 10px;
                    margin-bottom: 15px;
                }
            '''
    def embedded_javascript(self):
        return\
            '''
                $("div#leftMain ul li:eq(2) a").attr("href", '/#'+$("div.article-body").data("id"));    
                $("div#leftMain ul li:eq(4) a").attr("href", '/collected#'+$("div.article-body").data("id"));    
            '''

class BackTopModule(tornado.web.UIModule):
    def render(self):
        return self.render_string('module/backtop.html')
    
    def embedded_css(self):
        return\
            '''
                #backTop{
                    bottom:40px;
                    color: #1d2326;
                }
            '''
    
    def embedded_javascript(self):
        return\
            '''
                $("#backTop").click(function(){
                    $("#rightMain").scrollTop(0);
                });
            '''

class CollectModule(tornado.web.UIModule):
    def render(self, ifcollected):
        return self.render_string('module/collect.html', ifcollected=ifcollected)
    
    def embedded_css(self):
        return\
            '''
                #collect{
                    bottom: 80px;
                    color: #611427;
                }
            '''
    
    def embedded_javascript(self):
        return\
            '''
                $("#collect").click(
                    function(e){
                        var cSpan = $(this).find("span");
                        var ifcollected = true;
                        if(cSpan.hasClass("uncollected")){
                            ifcollected = false;
                        }
                        collect(cSpan, ifcollected, $(".article-body").data("id"));
                    }
                );
            '''
    
    def javascript_files(self):
        return '/static/js/collect.js'
    

class LogoutModule(tornado.web.UIModule):
    def render(self):
        return self.render_string('module/logout.html')

    def embedded_javascript(self):
        return\
            '''
                $('#sureForLogout').click(function(){
                    var $btn = $(this).button('loading');
                    $.post(
                        '/logout', 
                        {'_xsrf':getCookie("_xsrf")},
                        function(){
                            $btn.button('reset');
                            window.location.reload(); 
                        }
                    );
                });
                
            '''

class NewKeywordModule(tornado.web.UIModule):
    def render(self):
        return self.render_string('module/newkeyword.html')

    def embedded_javascript(self):
        return\
            '''
                $('#sureForNewKeyword').click(function(){
                    var $btn = $(this).button('loading');
                    $.post(
                        '/settings/new_keyword', 
                        $("#newKeywordForm").serialize(),
                        function(){
                            $btn.button('reset');
                            window.location.reload(); 
                        }
                    );
                });
                $(".keyword span").click(function(){
                    $.post(
                        '/settings/delete_keyword',
                        {
                            '_xsrf': getCookie('_xsrf'),
                            keyword: $(this).parent().text(),
                        },
                        function(){
                            window.location.reload();
                        }
                    );
                });
            '''

class ListModule(tornado.web.UIModule):
    def render(self):
        return self.render_string('module/list.html')
    
    def embedded_javascript(self):
        return\
            ''' 
            function list(refresh){
                if(refresh&&$("#ArticleList").data("bunch")>9){
                    $("#ArticleList").data("scroll", "true");
                    return;
                }
                $.post(
                    "#", 
                    {
                        _xsrf:getCookie("_xsrf"),
                        page_index:$("#ArticleList").data("page"),
                        bunch_index:$("#ArticleList").data("bunch"),
                        refresh:refresh,
                    }, 
                    function(data){
                        if(data.search("Error") != -1){
                            alerting(data, "error");
                        }
                        if(!refresh){
                            var page_index = $("#ArticleList").data("page");
                            $("#ArticleList").data("page", page_index+1);
                            $("#ArticleList").data("bunch", 0);
                            $("#ArticleList").empty();
                        }
                        else{
                            var bunch_index = $("#ArticleList").data("bunch");
                            $("#ArticleList").data("bunch", bunch_index+1);
                        }
                        
                        $("#ArticleList").append(data);
                        $("#ArticleList").data("scroll", true);
                    }
                );
            }
            var windowHeight = $("#rightMain").height();
            $(document).ready(function(){
                list(true);
            });
            $("#rightMain").scroll(function(){
                var scrollLen = $("#rightMain").scrollTop();
                var documentHeight = $("#rightMain>div").height();
                if(windowHeight + scrollLen>documentHeight){
                    if(!$("#ArticleList").data("scroll")) return;
                    $("#ArticleList").data("scroll", false);
                    list(true);
                }
            });
                
            '''
