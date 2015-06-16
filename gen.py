# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年05月15日 星期五 20时26分21秒
# 

import tornado.httpclient
import tornado.gen
import urllib
import logging
import database

def async(func):
    def wrapper(*args, **kwargs):
        yield func(*args, **kwargs)
    return wrapper

@async
def search(search_id):
    data = {'search_id':search_id}
    body = urllib.urlencode(data)
    response =\
        tornado.httpclient.HTTPClient().fetch(
            "http://scheduler:9000/service/searchEngine/search",
            method='POST',
            body=body,
        )
    logging.info('Search response: {response}'.format(response=response.body))
    if response.body == 'Success':
        return True
    else:
        return False 

@async
def calculate(user_id):
    user = database.User.select(user_id)
    if user is None:
        return 
    data = {'model_id': user.user_model, 'user_id':user_id}
    body = urllib.urlencode(data)
    response =\
        tornado.httpclient.HTTPClient().fetch(
            "http://scheduler:9000/service/model/calculate",
            method='POST',
            body=body,
        )
    logging.info('Calculate response: {response}'.format(response=response.body))
    if response.body == 'Success':
        return True
    else:
        return False 
