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
from kol_zhihu.get_cookie import get_cookie 
# import kol_zhihu.mxutil as util

reload(sys)
sys.setdefaultencoding('utf-8')

user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'

class ZhihuAuthorSpider(Spider):
    
    name = 'zhihu_author_follow'
    
    total = 0
    def __init__(self):
        self.follow_user_next = open('follow_user_next.dat','w')
        
        self.init_redis()
        self.move_url_from_mongo_redis()
    def init_redis(self):
        self.redis_conn = redis.redis_connect()

    def move_url_from_mongo_redis(self):
        conn = db.connect('192.168.241.25', 'zhihu')
        num = 0
        num1 = 0
#         authors = db.find(conn, 'author',{},{'id':'true','fansnum':'true','follownum':'true','hash_id':'true'})
        authors = db.find(conn, 'author',{'id':'liao-qi-can'},{'id':'true','fansnum':'true','follownum':'true','hash_id':'true'})
        for author in authors:
            try:
                fansnum = author['fansnum']
                if int(fansnum)>=1000:
                    data = author['id']+'`$`'+author['hash_id']+'`$`'+author['follownum']
                    num1 += 1
                    redis.add_url(self.redis_conn, data)
                    num += 1
            except:
                pass
        print 'filter num: ' ,num1
        print 'authors num: ',num
        db.close(conn)
    
    def make_requests(self):
        cnt = self.get_spider_pending_cnt(self.total)
        if cnt>5000:
            return []
        datas = redis.get_urls(self.redis_conn, 2000)
        print "get authors num: ",len(datas)
        reqs = []
        cookie = get_cookie()
        for data in datas:
            author_id,hash_id,follownum = data.split('`$`')
            print 'author_id: ',author_id
            print 'hash_id: ',hash_id
            print 'follownum: ',follownum
            #作者关注
            url = 'http://www.zhihu.com/people/%s/followees'%(author_id)
            req = Request(url,callback=self.parse_author_follow,cookies=cookie,meta={'hash_id':hash_id,'follownum':follownum})
            reqs.append(req)
            self.total += 1
        return reqs
    
    def start_requests(self):
        reqs = self.make_requests()
        return reqs
#         author_id = 'liao-qi-can'
#         url = 'http://www.zhihu.com/people/%s/followees'%(author_id)
#         cookie = get_cookie()
#         print cookie
#         req = Request(url,callback=self.parse_author_follow,cookies=cookie,meta={'hash_id':"8792e312d3c796318ce049e5e039f377",'follownum':"42"})
#         yield req
        
    def calc_url(self,base,url):
        if not url:
            return ''
        if url.startswith('javascript') or url.startswith('#'):
            return ''
        elif url.startswith('http://') or url.startswith('https://'):
            return url
        url = urlparse.urljoin(base, url)
        return url
    
    def parse_author_follow(self,response):
        hash_id = response.request.meta.get('hash_id')
        follownum = response.request.meta.get('follownum')
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        sel = Selector(text=content)
        author_urls = sel.xpath('//h2[@class="zm-list-content-title"]/a/@href').extract()
        for author_url in author_urls:
            print 'author_url: ',author_url
            author_id = author_url.split('/')[4]
            topic_id = 'unknow'
            authorItem = AuthorItem()
            authorItem['id'] = author_id
            authorItem['url'] = author_url
            authorItem['topic_id'] = topic_id
#             yield authorItem
        
        url_next = 'http://www.zhihu.com/node/ProfileFolloweesListV2'
        _xsrf = sel.xpath('//input[@name="_xsrf"]/@value').extract()[0]
        print '_xsrf: ',_xsrf
        num = math.ceil(int(follownum)/20.0)
        if num>1:
            cookie = get_cookie()
            for i in range(int(num-1)):
                offset = (i+1)*20
#             formdata = {'method':'next','params':'{"offset":20,"order_by":"created","hash_id":"0970f947b898ecc0ec035f9126dd4e08"}','_xsrf':'e8fa1f894af86dfb1aa8040bbe4fb29a'}
                formdata = {'method':'next','params':'{"offset":%s,"order_by":"created","hash_id":"%s"}'%(offset,hash_id),'_xsrf':'%s'%(_xsrf)}
                print 'formdata: ',formdata
                method = 'POST'
                req = FormRequest(url_next,method=method,formdata=formdata,cookies=cookie,headers={'User-Agent':user_agent},callback=self.parse_author_follow_next)
                self.total += 1
                yield req
    
    def parse_author_follow_next(self,response):
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        self.follow_user_next.write('%s\n'%(content))
        self.follow_user_next.flush()
        datas = json.loads(content)
        msg = datas['msg']
        for data in msg:
            sel = Selector(text=data)
            author_url = sel.xpath('//h2[@class="zm-list-content-title"]/a/@href').extract()[0]
            print 'author_url2: ',author_url
            author_id = author_url.split('/')[4]
            topic_id = 'unknow'
            authorItem = AuthorItem()
            authorItem['id'] = author_id
            authorItem['url'] = author_url
            authorItem['topic_id'] = topic_id
#             yield authorItem
        
    def get_spider_pending_cnt(self,total):
        c_stats = self.crawler.stats.get_stats()
        exception_cnt = 0
        rsp_cnt = 0
        if "downloader/response_count" in c_stats:
            rsp_cnt = c_stats['downloader/response_count']
        if "downloader/exception_count" in c_stats:
            exception_cnt = c_stats['downloader/exception_count']
        return total - rsp_cnt - exception_cnt
    