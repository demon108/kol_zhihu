#encoding:utf-8
import urlparse
import codecs
import sys
import json
import re
import math
import time

from scrapy.selector import Selector
from scrapy.http import Request,FormRequest
from scrapy.spider import Spider

from kol_zhihu.items import *
from kol_zhihu import redis_api2 as redis 
import kol_zhihu.mongo_util2 as db
# import kol_zhihu.mxutil as util

reload(sys)
sys.setdefaultencoding('utf-8')

'''
抓取用户主页，不需要cookie
'''

class ZhihuAuthorSpider(Spider):
    
    name = 'zhihu_authorinfo3'
    
    total = 0
    rediskey = 'zhihu_author3'
    def __init__(self):
        self.init_redis()
        self.move_url_from_mongo_redis()
        self.f = open('author_info3_ids.dat','w')
        
    def init_redis(self):
        self.redis_conn = redis.redis_connect()
        redis.delete_key(self.redis_conn, self.rediskey)

    def move_url_from_mongo_redis(self):
        #更新到的时间 1431048036
        conn = db.connect('192.168.241.23', 'zhihu')
#         try:
#             start_time = db.find_one(conn, 'record')['time']
#         except:
#             start_time = 0
        start_time = 0
        end_time = time.time()
        authorids = db.find(conn, 'author',{'tg':{'$lt':end_time,'$gt':start_time}})
        print 'get from mongo: ',authorids.count()
        num = 0
        for authorid in authorids:
            redis.add_url(self.redis_conn, authorid['id'],key=self.rediskey)
            num += 1
        record = db.find_one(conn, 'record',{'id':'1'})
        print "record: ",record
        if not record:
            db.insert(conn, 'record', {'time':end_time,'id':'1'})
        else:
            db.update(conn, 'record', {'id':'1'}, {'time':end_time})
        print 'add to redis: ',num
        db.close(conn)
    
    def make_requests(self):
        cnt = self.get_spider_pending_cnt(self.total)
        #print 'cnt: ',cnt
        if cnt>5000:
            return []
        author_ids = redis.get_urls(self.redis_conn, 2000, key=self.rediskey)
        #print "get authors num: ",len(author_ids)
        reqs_pool = []
        for author_id in author_ids:
            #作者主页
            author_url = 'http://www.zhihu.com/people/%s'%(author_id)
            author_req = Request(author_url,callback=self.parse_author_info,meta={'author_id':author_id})
            reqs_pool.append(author_req)
            self.total += 1
        return reqs_pool
    
    def start_requests(self):
        print 'request pool: ',self.get_spider_pending_cnt(self.total)
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
            
    def parse_author_info(self,response):
        author_id = response.request.meta['author_id']
        self.f.write('%s\n'%(author_id))
        self.f.flush()
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        
        sel = Selector(text=content)
	name = sel.xpath('//span[@class="name"]/text()').extract()[0].strip()    
        try:
            tag = sel.xpath('//span[@class="bio"]/text()').extract()[0].strip()
        except:
            tag = ''    
        try:
            abs = sel.xpath('//span[@class="content"]/text()').extract()[0].strip()
        except:
            abs = ''
        try:
            industry = sel.xpath('//span[@class="business item"]/@title').extract()[0].strip()
        except:
            industry= ''
        img = sel.xpath('//div[@class="zm-profile-header-avatar-container "]/img/@src').extract()[0].strip()
        try:
            genderinfo = sel.xpath('//span[@class="item gender"]/i/@class').extract()[0]
            if genderinfo.find('profile-male')!=-1:
                gender = 'male'
            elif genderinfo.find('profile-female')!=-1:
                gender = 'female'
            else:
                gender = 'unknow'
        except:
            gender = 'unknow'
        
        fansnum = sel.xpath('//a[@class="item"]/strong/text()').extract()[1].strip()      
        follownum = sel.xpath('//a[@class="item"]/strong/text()').extract()[0].strip()
        asknum = sel.xpath('//span[@class="num"]/text()').extract()[0].strip()   
        answernum = sel.xpath('//span[@class="num"]/text()').extract()[1].strip()
        postnum = sel.xpath('//span[@class="num"]/text()').extract()[2].strip()
        likenum2 = sel.xpath('//span[@class="zm-profile-header-user-agree"]/child::strong/text()').extract()[0].strip()
        thanksnum = sel.xpath('//span[@class="zm-profile-header-user-thanks"]/child::strong/text()').extract()[0].strip()
        hpspan = sel.xpath('//span[@class="zg-gray-normal"]/strong/text()').extract()[0].strip()
        try:
            weibo = sel.xpath('//a[@class="zm-profile-header-user-weibo"]/@href').extract()[0].strip()
        except:
            weibo = ''
        try:
            follow_zl_num = sel.xpath('//div[@class="zm-profile-side-section-title"]/a/strong/text()').extract()[0].replace('个专栏'.decode('utf-8'),'').strip()
            follow_topic_num = sel.xpath('//div[@class="zm-profile-side-section-title"]/a/strong/text()').extract()[1].replace('个话题'.decode('utf-8'),'').strip()
        except:
            follow_num = sel.xpath('//div[@class="zm-profile-side-section-title"]/a/strong/text()').extract()[0]
            if follow_num.find('个专栏'.decode('utf-8'))!=-1:
                follow_zl_num = follow_num.replace('个专栏'.decode('utf-8'),'').strip()
                follow_topic_num = 0
            elif follow_num.find('个话题'.decode('utf-8'))!=-1:
                follow_topic_num = follow_num.replace('个话题'.decode('utf-8'),'').strip()
                follow_zl_num = 0
        hash_id = sel.xpath('//div[@class="zm-profile-header-op-btns clearfix"]/button/@data-id').extract()[0].strip()
        upAuthorByAnswerSpider = UpAuthorByAnswerSpider()
        upAuthorByAnswerSpider['authorid'] = author_id
        upAuthorByAnswerSpider['name'] = name
        upAuthorByAnswerSpider['tag'] = tag
        upAuthorByAnswerSpider['abs'] = abs
        upAuthorByAnswerSpider['industry'] = industry
        upAuthorByAnswerSpider['image'] = img
        upAuthorByAnswerSpider['gender'] = gender
        upAuthorByAnswerSpider['weibo'] = weibo
        upAuthorByAnswerSpider['follow_zl_num'] = follow_zl_num
        upAuthorByAnswerSpider['follow_topic_num'] = follow_topic_num
        upAuthorByAnswerSpider['hash_id'] = hash_id
        upAuthorByAnswerSpider['fansnum'] = fansnum
        upAuthorByAnswerSpider['follownum'] = follownum
        upAuthorByAnswerSpider['asknum'] = asknum
        upAuthorByAnswerSpider['answernum'] = answernum
        upAuthorByAnswerSpider['postnum'] = postnum
        upAuthorByAnswerSpider['likenum'] = likenum2
        upAuthorByAnswerSpider['thanksnum'] = thanksnum
        upAuthorByAnswerSpider['hpspan'] = hpspan
        yield upAuthorByAnswerSpider

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
    
