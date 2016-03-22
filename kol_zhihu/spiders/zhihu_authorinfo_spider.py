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
from kol_zhihu.get_cookie import get_cookie
# import kol_zhihu.mxutil as util

reload(sys)
sys.setdefaultencoding('utf-8')

user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'

class ZhihuAuthorSpider(Spider):
    
    name = 'zhihu_authorinfo'
    
    total = 0
    start_flag = 0
    def __init__(self):
        self.f = open('author_info_ids.dat','w')
        self.init_redis()
        self.move_url_from_mongo_redis()
        #http://zhuanlan.zhihu.com/maboyong
#         self.zl_url_re = re.compile('^http://zhuanlan.zhihu.com/.*(?|/?)')
    def init_redis(self):
        self.redis_conn = redis.redis_connect()
#         redis.set_expire_time(self.redis_conn,self.redis_key_list,1*60*60*24)
#         redis.set_expire_time(self.redis_conn,self.redis_key_unfetch,30*60*60*24)

    def move_url_from_mongo_redis(self):
        #更新到的时间 1431048036
        conn = db.connect('192.168.241.23', 'zhihu')
        authorids = db.find(conn, 'kol_author')
        print 'get from mongo: ',authorids.count()
        num = 0
        for authorid in authorids:
            redis.add_url(self.redis_conn, authorid['id'])
            num += 1
        print 'add to redis: ',num
        db.close(conn)
    
    def make_requests(self):
        cookie = get_cookie()
        cnt = self.get_spider_pending_cnt(self.total)
        print 'request pool: ',cnt
        if cnt>3000:
            return []
        author_ids = redis.get_urls(self.redis_conn, 2000)
        print "get authors num: ",len(author_ids)
        reqs_pool = []
        for author_id in author_ids:
            #作者信息
            info_url = 'http://www.zhihu.com/people/%s/about'%(author_id)
            info_req = Request(info_url,callback=self.parse_author_info,headers={'User-Agent':user_agent},cookies=cookie,meta={'author_id':author_id})
            reqs_pool.append(info_req)
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
        
    def parse_author_info(self,response):
        author_id = response.request.meta['author_id']
        self.f.write('%s\n'%(author_id))
        self.f.flush()
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        sel = Selector(text=content)
        name = sel.xpath('//a[@class="name"]/text()').extract()[0]    
        try:
            tag = sel.xpath('//span[@class="bio"]/text()').extract()[0]
        except:
            tag = ''    
        try:
            abs = sel.xpath('//span[@class="content"]/text()').extract()[0]
        except:
            abs = ''
        try:
            industry = sel.xpath('//span[@class="business item"]/@title').extract()[0]
        except:
            industry= ''
        img = sel.xpath('//div[@class="zm-profile-header-avatar-container "]/img/@src').extract()[0]
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
        asknum = sel.xpath('//span[@class="num"]/text()').extract()[0]      
        answernum = sel.xpath('//span[@class="num"]/text()').extract()[1]    
        postnum = sel.xpath('//span[@class="num"]/text()').extract()[2]
             
        fansnum = sel.xpath('//a[@class="item"]/strong/text()').extract()[1]      
        follownum = sel.xpath('//a[@class="item"]/strong/text()').extract()[0]
        hpspan = sel.xpath('//span[@class="zg-gray-normal"]/strong/text()').extract()[0]
        
        author_descs = sel.xpath('//div[@class="zm-profile-module-desc"]')
        likenum = author_descs[0].xpath('span/strong/text()').extract()[0]
        thanksnum = author_descs[0].xpath('span/strong/text()').extract()[1]
        favoritenum = author_descs[0].xpath('span/strong/text()').extract()[2]
        sharenum = author_descs[0].xpath('span/strong/text()').extract()[3]     
        
        try:
            job = sel.xpath('//div[@class="zm-profile-module-desc"]')[1].xpath('span/text()').extract()[0]
        except:
            try:
                job = sel.xpath('//div[@class="zm-profile-module-desc"]')[1].xpath('ul/li/div/strong/a/text()').extract()[0]
            except:
                job = sel.xpath('//div[@class="zm-profile-module-desc"]')[1].xpath('ul/li/div/strong/text()').extract()[0]
        try:
            address = sel.xpath('//div[@class="zm-profile-module-desc"]')[2].xpath('span/text()').extract()[0]
        except:
            try:
                address = sel.xpath('//div[@class="zm-profile-module-desc"]')[2].xpath('ul/li/div/strong/a/text()').extract()[0]
            except:
                address = sel.xpath('//div[@class="zm-profile-module-desc"]')[2].xpath('ul/li/div/strong/text()').extract()[0]
        try:
            education = sel.xpath('//div[@class="zm-profile-module-desc"]')[3].xpath('span/text()').extract()[0]
        except:
            try:
                education = sel.xpath('//div[@class="zm-profile-module-desc"]')[3].xpath('ul/li/div/strong/a/text()').extract()[0]
            except:
                education = sel.xpath('//div[@class="zm-profile-module-desc"]')[3].xpath('ul/li/div/strong/text()').extract()[0]
        try:
            weibo = sel.xpath('//a[@class="zm-profile-header-user-weibo"]/@href').extract()[0]
        except:
            weibo = ''
        
        hash_id = sel.xpath('//div[@class="zm-profile-header-op-btns clearfix"]/button/@data-id').extract()[0]
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
        authorInfo = UpdateAuthorInfo()
        authorInfo['authorid'] = author_id
        authorInfo['name'] = name
        authorInfo['tag'] = tag
        authorInfo['industry'] = industry
        authorInfo['abs'] = abs
        authorInfo['image'] = img 
        authorInfo['gender'] = gender
        authorInfo['asknum'] = asknum
        authorInfo['answernum'] = answernum
        authorInfo['postnum'] = postnum
        authorInfo['fansnum'] = fansnum
        authorInfo['follownum'] = follownum
        authorInfo['hpspan'] = hpspan
        authorInfo['likenum'] = likenum
        authorInfo['thanksnum'] = thanksnum
        authorInfo['favoritenum'] = favoritenum
        authorInfo['sharenum'] = sharenum
        authorInfo['job'] = job
        authorInfo['address'] = address
        authorInfo['education'] = education
        authorInfo['weibo'] = weibo
        authorInfo['hash_id'] = hash_id
        authorInfo['follow_zl_num'] = follow_zl_num
        authorInfo['follow_topic_num'] = follow_topic_num
        yield authorInfo
        
        reqs = self.make_requests()
        for req in reqs:
            self.total += 1
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
    
