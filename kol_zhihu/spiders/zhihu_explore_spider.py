#encoding:utf-8
import urlparse

from scrapy.selector import Selector
from scrapy.http import Request,FormRequest
from scrapy.spider import Spider


from kol_zhihu.items import *

user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
class ZhihuExploreSpider(Spider):
    
    name = 'zhihu_explore'
    def __init__(self):
        pass
    
    def start_requests(self):
        explore_url = 'http://www.zhihu.com/explore'
        yield Request(explore_url,headers={'User-Agent':user_agent})
        
        #          http://www.zhihu.com/node/ExploreAnswerListV2?params={"offset":5,"type":"day"}
        tmp_url = 'http://www.zhihu.com/node/ExploreAnswerListV2?params=%s'
        params = '{"offset":%s,"type":"day"}'
        for i in range(9):
            url = tmp_url%(params%((i+1)*5))
            yield Request(url,headers={'User-Agent':user_agent})
        
        
    def parse(self,response):
        url = response.url
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        sel = Selector(text=content)
        
        links = sel.xpath('//a[@class="question_link"]/@href').extract()
        for link in links:
            link = urlparse.urljoin(url, link)
            yield Request(link,callback=self.parse_question)
    
    def parse_question(self,response):
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
                    yield Request(link,callback=self.parse_author_spe)
                else:
                    item = AuthorItem2()
                    item['id'] = userid
                    item['url'] = link
                    item['topic_id'] = 'unkown'
                    yield item
    
    def parse_author_spe(self,response):
        url = response.url
        userid = url.split('/')[4]
        item = AuthorItem2()
        item['id'] = userid
        item['url'] = url
        item['topic_id'] = 'unkown'
        yield item
        
        
        
        
        
        
            
