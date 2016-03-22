#encoding:utf-8
import urlparse
import codecs
import sys
import json

from scrapy.selector import Selector
from scrapy.http import Request,FormRequest
from scrapy.spider import Spider
from bs4 import BeautifulSoup

from kol_zhihu.items import *
from kol_zhihu.redis_api import RedisUtil
from kol_zhihu import redis_api2 as redis 
import kol_zhihu.mongo_util2 as db

reload(sys)
sys.setdefaultencoding('utf-8')

'''
抓取专栏的信息和专栏里的文章
'''
class ZhihuPostSpider(Spider):
    
    name = 'zhihu_post'
    
    store_req_urls_redis_key = 'zhihu_posts' 
    
    total = 0
    def __init__(self):
        self.init_redis()
        self.move_url_from_mongo_redis()
        self.post_info = open('post_info_urls.dat','w')
    
    def start_requests(self):
        reqs = self.make_requests()
        return reqs
    
    def init_redis(self):
        self.redis_conn = redis.redis_connect()
    
    def move_url_from_mongo_redis(self):
        conn = db.connect('192.168.241.23', 'zhihu')
        post_urls = db.find(conn, 'post',{},{'url':'true'})
        num = 0 
        key=self.store_req_urls_redis_key
        redis.delete_key(self.redis_conn,key )
        for post_url in post_urls:
            redis.add_url(self.redis_conn, post_url['url'],key=key)
            num += 1
        print 'add to redis: ',num
        db.close(conn)
        
    def make_requests(self):
        cnt = self.get_spider_pending_cnt(self.total)
        if cnt>2000:
            return []
        post_urls = redis.get_urls(self.redis_conn, 2000,self.store_req_urls_redis_key)
        print "get post_urls num: ",len(post_urls)
        reqs = []
        for post_url in post_urls:
            #http://zhuanlan.zhihu.com/queen
            #http://zhuanlan.zhihu.com/api/columns/queen/posts?limit=10&offset=0
	    print post_url
            post_key = urlparse.urlparse(post_url).path.split('/')[1]
            url = 'http://zhuanlan.zhihu.com/api/columns/%s/posts?limit=10&offset=0'%(post_key)
            req = Request(url,callback=self.parse,meta={'offset':0,'post_url':post_url})
            reqs.append(req)
            #http://zhuanlan.zhihu.com/api/columns/queen
            url_post_info = 'http://zhuanlan.zhihu.com/api/columns/%s'%(post_key)
            req_post_info = Request(url_post_info,callback=self.parse_post_info,meta={'post_url':post_url})
            reqs.append(req_post_info)
            self.total += 2
        return reqs

    def parse(self,response):
        offset = response.request.meta.get('offset')
        post_url = response.request.meta.get('post_url')
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        datas = json.loads(content)
        itemnum = len(datas)
        for item in datas:
            title = item['title']
            commnum = item['commentsCount']
            likenum = item['likesCount']
            authorurl = item['author']['profileUrl']
            article_url_tmp = item['url']
            article_url = 'http://zhuanlan.zhihu.com'+article_url_tmp
            summary = item['summary']
            summary = ''.join(BeautifulSoup(summary).findAll(text=True))
            pubtime = item['publishedTime'].replace('T',' ').split('+')[0]
            text = item['content']
            text = '\n'.join(BeautifulSoup(text).findAll(text=True))
            postArticle = PostArticleInfo()
            postArticle['url'] = article_url
            postArticle['posturl'] = post_url
            postArticle['authorurl'] = authorurl
            postArticle['title'] = title
            postArticle['commnum'] = commnum
            postArticle['likenum'] = likenum
            postArticle['abs'] = summary
            postArticle['pubtime'] = pubtime
            postArticle['content'] = text
            yield postArticle
        
        if itemnum==10:
            url_tmp = response.url.split('&')[0]
            cur_offset = str(int(offset)+10)
            url = url_tmp+'&offset=%s'%(cur_offset) 
            req = Request(url,callback=self.parse,meta={'offset':cur_offset,'post_url':post_url})
            yield req
        
        reqs = self.make_requests()
        for req in reqs:
            yield req
            
    def parse_post_info(self,response):
        post_url = response.request.meta.get('post_url')
        self.post_info.write('%s\n'%(post_url))
        self.post_info.flush()
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        data = json.loads(content)
        if not data:
            followersCount = data['followersCount']
            description = data['description']
            name = data['name']
            article_num = data['postsCount']
            updatePost = UpdatePostInfo()
            updatePost['followersCount'] = followersCount
            updatePost['description'] = description
            updatePost['name'] = name
            updatePost['article_num'] = article_num
            updatePost['url'] = post_url
            yield updatePost
    
    def get_spider_pending_cnt(self,total):
        c_stats = self.crawler.stats.get_stats()
        exception_cnt = 0
        rsp_cnt = 0
        if "downloader/response_count" in c_stats:
            rsp_cnt = c_stats['downloader/response_count']
        if "downloader/exception_count" in c_stats:
            exception_cnt = c_stats['downloader/exception_count']
        return total - rsp_cnt - exception_cnt


