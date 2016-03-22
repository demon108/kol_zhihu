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
    key='zhihu_update_post'
    total = 0
    def __init__(self):
        self.init_redis()
        self.move_url_from_mongo_redis()
        #http://zhuanlan.zhihu.com/maboyong
#         self.zl_url_re = re.compile('^http://zhuanlan.zhihu.com/.*(?|/?)')
    def init_redis(self):
        self.redis_conn = redis.redis_connect()
        redis.delete_key(self.redis_conn, self.key)

    def move_url_from_mongo_redis(self):
        conn = db.connect('192.168.241.23', 'zhihu')
        #authors = db.find(conn, 'author',{},{'id':'true','fansnum':'true'})
        authors = db.find(conn, 'kol_author',{},{'id':'true','fansnum':'true'})
        num = 0
        for author in authors:
            redis.add_url(self.redis_conn, author['id'],key=self.key)
            num += 1
        print 'add to redis: ',num
        db.close(conn)
    
    def make_requests(self):
        cnt = self.get_spider_pending_cnt(self.total)
        if cnt>3000:
            return []
        author_ids = redis.get_urls(self.redis_conn, 2000,key=self.key)
        print "get authors num: ",len(author_ids)
        reqs_pool = []
        for author_id in author_ids:
            #作者专栏文章
            post_url = 'http://www.zhihu.com/people/%s/posts'%(author_id)
            post_req = Request(post_url,callback=self.parse_author_post,meta={'author_id':author_id})
            reqs_pool.append(post_req)
            self.total += 1
        return reqs_pool
    
    def start_requests(self):
        reqs = self.make_requests()
        return reqs    
    
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
            if url.find('http://zhuanlan.zhihu.com/')==-1:
                continue
            #专栏所属，存入ownerpost表
            ownerPost = OwnerPost()
            ownerPost['zl_url'] = url
            ownerPost['authorid'] = author_id
            yield ownerPost
            #存入post表
            postinfo = PostInfo()
            postinfo['url'] = url
            yield postinfo
        
        #作者关注的专栏，需要发送post请求
        follow_zl_num = sel.xpath('//div[@class="zm-profile-side-section-title"]/a/strong/text()').extract()[0].replace('个专栏'.decode('utf-8'),'').strip()
        if follow_zl_num.find('个话题'.decode('utf-8'))==-1 and follow_zl_num.find('个话题')==-1:
            hash_id = sel.xpath('//div[@class="zm-profile-header-op-btns clearfix"]/button/@data-id').extract()[0]
            url = 'http://www.zhihu.com/node/ProfileFollowedColumnsListV2'
            formdata = {'method':'next','params':'{"offset":0,"limit":%s,"hash_id":"%s"}'%(int(follow_zl_num),hash_id)}
            method = 'POST'
            yield FormRequest(url,method=method,formdata=formdata,callback=self.parse_author_follow_post)
            self.total += 1
            
        reqs = self.make_requests()
        for req in reqs:
            yield req
        
    def parse_author_follow_post(self,response):
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        sel = Selector(text=content)
        html = json.loads(content)
        datas = html['msg']
        for data in datas:
            sel = Selector(text=data)
            post_url = sel.xpath('//div[@class="zm-profile-section-main"]/a/@href').extract()[0]
            if post_url.find('http://zhuanlan.zhihu.com/')==-1:
                continue
            #存入post表
            postinfo = PostInfo()
            postinfo['url'] = post_url
            yield postinfo
        reqs = self.make_requests()
        for req in reqs:
            yield req
            
    def get_spider_pending_cnt(self,total):
        c_stats = self.crawler.stats.get_stats()
        exception_cnt = 0
        rsp_cnt = 0
        if "downloader/response_count" in c_stats:
            rsp_cnt = c_stats['downloader/response_count']
        if "downloader/exception_count" in c_stats:
            exception_cnt = c_stats['downloader/exception_count']
        return total - rsp_cnt - exception_cnt
    
