#encoding:utf-8
import urlparse
import codecs
import sys
import json
import re
import math

from scrapy.selector import Selector
from scrapy.http import Request,FormRequest
from scrapy.spider import Spider

from kol_zhihu.items import *
from kol_zhihu import redis_api2 as redis 
import kol_zhihu.mongo_util2 as db
# import kol_zhihu.mxutil as util

reload(sys)
sys.setdefaultencoding('utf-8')

class ZhihuAuthorSpider(Spider):
    
    name = 'zhihu_find_post'
    
    total = 0
    def __init__(self):
        self.init_redis()
        self.move_url_from_mongo_redis()
        #http://zhuanlan.zhihu.com/maboyong
#         self.zl_url_re = re.compile('^http://zhuanlan.zhihu.com/.*(?|/?)')
    def init_redis(self):
        self.redis_conn = redis.redis_connect()

    def move_url_from_mongo_redis(self):
        conn = db.connect('192.168.241.25', 'zhihu')
        authors = db.find(conn, 'author',{},{'id':'true','fansnum':'true'})
        num = 0
        for author in authors:
            try:
                fansnum = author['fansnum']
                if int(fansnum)>=500:
                    redis.add_url(self.redis_conn, author['id'],key='zhihu_update_post')
                    num += 1
            except:
                pass
        print 'add to redis: ',num
        db.close(conn)
    
    def make_requests(self):
        cnt = self.get_spider_pending_cnt(self.total)
        if cnt>3000:
            return []
        author_ids = redis.get_urls(self.redis_conn, 2000,key='zhihu_update_post')
        print "get authors num: ",len(author_ids)
        reqs_pool = []
        for author_id in author_ids:
            #作者专栏文章
            post_url = 'http://www.zhihu.com/people/%s/posts'%(author_id)
            post_req = Request(post_url,callback=self.parse_author_post,meta={'author_id':author_id})
            reqs_pool.append(post_req)
        return reqs_pool
    
    def calc_url(self,base,url):
        if not url:
            return ''
        if url.startswith('javascript') or url.startswith('#'):
            return ''
        elif url.startswith('http://') or url.startswith('https://'):
            return url
        url = urlparse.urljoin(base, url)
        return url
    
    def parse_author_post(self,response):
        author_id = response.request.meta['author_id']
        url = response.url
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        sel = Selector(text=content)
        items = sel.xpath('//div[@class="column"]')
        for item in items:
            url = item.xpath('div[@class="header"]/a/@href').extract()[0]
            ownerPost = OwnerPost()
            ownerPost['zl_url'] = url
            ownerPost['authorid'] = author_id
            yield ownerPost
            
        reqs = self.make_requests()
        for req in reqs:
            self.total += 1
            yield req
            
        links = sel.xpath('//a/@href').extract()
        for link in links:
            #http://zhuanlan.zhihu.com/sooth
            zl_url = self.calc_url(url, link)
            if zl_url.endswith('/'):
                zl_url = zl_url[:len(url)-1]
            url_tmp = urlparse.urlparse(url)
            if url_tmp.netloc!='zhuanlan.zhihu.com':
                continue
            if len(url_tmp.path.split('/'))!=2:
                continue
            post = PostInfo()
            post['url'] = zl_url
            yield post

    def get_spider_pending_cnt(self,total):
        c_stats = self.crawler.stats.get_stats()
        exception_cnt = 0
        rsp_cnt = 0
        if "downloader/response_count" in c_stats:
            rsp_cnt = c_stats['downloader/response_count']
        if "downloader/exception_count" in c_stats:
            exception_cnt = c_stats['downloader/exception_count']
        return total - rsp_cnt - exception_cnt
    