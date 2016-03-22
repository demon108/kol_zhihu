#encoding:utf-8
import urlparse
import codecs
import sys
import json

from scrapy.selector import Selector
from scrapy.http import Request,FormRequest
from scrapy.spider import Spider

from kol_zhihu.items import *
from kol_zhihu.redis_api import RedisUtil

reload(sys)
sys.setdefaultencoding('utf-8')

class ZhiHuSpider(Spider):
    
    name = "zhihu_find_urser"
    def __init__(self):
        self.redis = RedisUtil(article_key='article_zhihu',author_key='author_zhihu',topic_key='topic_zhihu')
        
        self.f = open('topic.dat','w')
        self.pages_urls = open('pages.dat','w')
        self.article_urls = open('articles.dat','w')
    def make_reqs(self,topic_id,offset,category):
        reqs = []
        #"hash_id":"4c62f91c46aa6fa3f225d932bd647582"
        for i in range(offset):
            url = 'http://www.zhihu.com/node/TopicsPlazzaListV2'
            user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
            formdata = {'method':'next','params':'{"topic_id":%s,"offset":%s,"hash_id":""}'%(topic_id,i*20),'_xsrf':'7b30b13f5fe7fa41e66dee162f864891'}
            method = 'POST'
            req = FormRequest(url,method=method,formdata=formdata,headers={'User-Agent':user_agent},meta={'category':category.decode('utf-8')},callback=self.parse_topic)
            reqs.append(req)
        return reqs
    
    def start_requests(self):
#wget --header="User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36" --post-data='method=next&params={"topic_id":1538,"offset":0,"hash_id":"4c62f91c46aa6fa3f225d932bd647582"}&_xsrf=7b30b13f5fe7fa41e66dee162f864891' "http://www.zhihu.com/node/TopicsPlazzaListV2"
        reqs = []
        #http://www.zhihu.com/topics
        #体育
        reqs_item = self.make_reqs(1538, 15, '体育')
        reqs.extend(reqs_item)
        #投资
        reqs_item = self.make_reqs(395, 2, '投资')
        reqs.extend(reqs_item)
        # 美食
        reqs_item = self.make_reqs(304, 9, '美食')
        reqs.extend(reqs_item)
        # 生活
        reqs_item = self.make_reqs(307, 66, '生活')
        reqs.extend(reqs_item)
        # 汽车
        reqs_item = self.make_reqs(570, 12, '汽车')
        reqs.extend(reqs_item)
        # 运动
        reqs_item = self.make_reqs(833, 15, '运动')
        reqs.extend(reqs_item)
        # 电影
        reqs_item = self.make_reqs(68, 29, '电影')
        reqs.extend(reqs_item)
        # 商业
        reqs_item = self.make_reqs(1740, 25, '商业')
        reqs.extend(reqs_item)
        # 金融
        reqs_item = self.make_reqs(19800, 36, '金融')
        reqs.extend(reqs_item)
        # 科技
        reqs_item = self.make_reqs(2143, 97, '科技')
        reqs.extend(reqs_item)
        # 互联网
        reqs_item = self.make_reqs(99, 77, '互联网')
        reqs.extend(reqs_item)
        # 健康
        reqs_item = self.make_reqs(237, 27, '健康')
        reqs.extend(reqs_item)
        print 'seeds: ',len(reqs)
        return reqs
        
    
    def parse_topic(self,response):
        category = response.request.meta.get('category','')
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        
        content = json.loads(content)
        msgs = content['msg']
        if msgs:
            for msg in msgs:
                sel = Selector(text=msg)
                topic_url = sel.xpath('//div/div/a/@href').extract()[0]
                topic_url = urlparse.urljoin(response.url, topic_url)
                topic_name = sel.xpath('//div/div/a/strong/text()').extract()[0]
                topic_id = topic_url.split('/')[4]
                try:
                    abs = sel.xpath('//div/div/p/text()').extract()[0]
                except:
                    abs = ''
                self.f.write('%s,%s,%s\n'%(topic_name,topic_url,abs))
                self.f.flush()
                item = TopicItem()
                item['id'] = str(topic_id)
                item['abs'] = abs
                item['url'] = topic_url
                item['name'] = topic_name
                item['category'] = category
                yield item
                
                topic_questions_url = topic_url + '/questions'
                if not self.redis.check_topic(topic_questions_url):
                    self.redis.add_topic(topic_questions_url)
                    req = Request(topic_questions_url,callback=self.parse_questions_list,meta={'topic_id':topic_id})
                    yield req

                
    def parse_questions_list(self,response):
        topic_id = response.request.meta.get('topic_id','')
        url = response.url
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        sel = Selector(text=content)
        pages = sel.xpath('//div[@class="zm-invite-pager"]/span/a/@href').extract()
        for page in pages:
            page_url = urlparse.urljoin(url, page)
            if not self.redis.check_topic(page_url):
                self.pages_urls.write('%s\n'%(page_url))
                self.pages_urls.flush()
                self.redis.add_topic(page_url)
                yield Request(page_url,callback=self.parse_questions_list,meta={'topic_id':topic_id})
        question_items = sel.xpath('//h2[@class="question-item-title"]/a/@href').extract()
        for item in question_items:
            item_url = urlparse.urljoin(url, item)
            if not self.redis.check_article(item_url):
                self.redis.add_article(item_url)
                self.article_urls.write('%s\n'%(item_url))
                self.article_urls.flush()
                yield Request(item_url,callback=self.parse_arcticle,meta={'topic_id':topic_id})
        
    def parse_arcticle(self,response):
        topic_id = response.request.meta.get('topic_id','')
        url = response.url
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        sel = Selector(text=content)
        links = sel.xpath('//a/@href').extract()
        for link in links:
            link = urlparse.urljoin(url, link)
            #http://www.zhihu.com/people/fbe4f66a164260a9b457ade8b34d7462 这种不要
            if link.find('http://www.zhihu.com/people/')!=-1:
                userid = link.split('/')[4]
                if len(userid)==32:
                    yield Request(link,callback=self.parse_author_spe,meta={'topic_id':topic_id})
                else:
                    item = AuthorItem()
                    item['id'] = userid
                    item['url'] = link
                    item['topic_id'] = topic_id
                    yield item
    
    def parse_author_spe(self,response):
        topic_id = response.request.meta['topic_id']
        url = response.url
        userid = url.split('/')[4]
        item = AuthorItem()
        item['id'] = userid
        item['url'] = url
        item['topic_id'] = topic_id
        yield item
        
    
'''<div class=\"item\">
     <div class=\"blk\">\n
       <a target=\"_blank\" href=\"\/topic\/19690458\">\n
         <img src=\"http:\/\/pic1.zhimg.com\/e82bab09c_xs.jpg\" alt=\"\u90ed\u6676\u6676\">\n
         <strong>\u90ed\u6676\u6676<\/strong>\n
        <\/a>\n
        <p><\/p>\n\n
      <a id=\"t::-46860\" href=\"javascript:;\" class=\"follow meta-item zg-follow\">
        <i class=\"z-icon-follow\"><\/i>\u5173\u6ce8<\/a>\n\n<\/div><\/div>'''

'''
<div class=\"item\">
  <div class=\"blk\">\n
    <a target=\"_blank\" href=\"\/topic\/19562832\">\n
      <img src=\"http:\/\/pic4.zhimg.com\/f85294643_xs.jpg\" alt=\"\u7bee\u7403\">\n
        <strong>\u7bee\u7403<\/strong>\n
    <\/a>\n
    <p>\u7bee\u7403\u662f\u4e00\u4e2a\u7531\u4e24\u961f\u53c2\u4e0e\u7684\u7403\u7c7b\u8fd0\u52a8\uff0c\u6bcf\u961f\u51fa\u573a5\u540d\u961f\u5458\u3002\u76ee\u7684\u662f\u5c06\u7403\u8fdb\u2026<\/p>\n\n
    <a id=\"t::-4196\" href=\"javascript:;\" class=\"follow meta-item zg-follow\"><i class=\"z-icon-follow\"><\/i>\u5173\u6ce8<\/a>\n\n
    <\/div><\/div>
'''
            
            
            
            
        
        
        