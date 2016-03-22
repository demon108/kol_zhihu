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

reload(sys)
sys.setdefaultencoding('utf-8')

use_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
cookie = {'q_c1':'02dcb3281ba048ebb8dfc374d1f58402|1428487620000|1428487620000', 
          '_ga':'GA1.2.1787246182.1428487623', 
          '_xsrf':'4510fc3de9fe84dca68a7109b5d0fc89', 
          '_za':'dbdcd5c9-fab8-4122-9c16-d0a29abd6a68', 
          'z_c0':'"QUFDQVdkODJBQUFYQUFBQVlRSlZUVmhDWUZXenlodHFZMnNfcC1PdWlGTjRHOFUwVUdhaWNnPT0=|1429779800|2721a92cf6cf5234db949629d308b39f26f3ef9b"', 
          '__utmt':1,
          '__utma':'51854390.1787246182.1428487623.1429777737.1429777737.1', 
          '__utmb':'51854390.39.10.1429777737',
          '__utmc':'51854390', 
          '__utmz':'51854390.1429777737.1.1.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/topic', 
          '__utmv':'51854390.100-1|2=registration_date=20140909=1^3=entry_date=20140909=1'}
class ZhihuAuthorSpider(Spider):
    
    name = 'zhihu_author'
    
    redis_ask_page = 'askpages'
    total = 0
    def __init__(self):
        self.reqs_pool = []
        
        self.follow_re = re.compile(ur'(?P<num>\d+).*\u4eba\u5173\u6ce8')
        self.answer_re = re.compile(ur'(?P<num>\d+).*\u4e2a\u56de\u7b54')
        
        self.next_ask_page_re = re.compile('http://www.zhihu.com/people/.*/asks\?page=\d+')
        
        #http://zhuanlan.zhihu.com/maboyong
#         self.zl_url_re = re.compile('^http://zhuanlan.zhihu.com/.*(?|/?)')
    def init_redis(self):
        self.redis_conn = redis.redis_connect()
        redis.set_expire_time(self.redis_conn, self.redis_ask_page,  8*60*60*24)
        
    def get_author_from_mongo(self):
        author_ids = []
        conn = db.connect('192.168.241.25', 'zhihu')
        authors = db.find(conn, 'author')
        for author in authors:
#             author_url = author['url']
            author_id = author['id']
            author_ids.append(author_id)
        db.close(conn)
        return author_ids
    
    def get_send_reqs(self):
        cnt = self.get_spider_pending_cnt(self.total)
        if cnt<2000:
            if len(self.reqs)>2000:
                cur_reqs = self.reqs_pool[:5000]
                self.reqs_pool = self.reqs_pool[5000:]
                self.total += 2000
                return cur_reqs
            elif len(self.reqs_pool)!=0:
                cur_reqs = self.reqs_pool
                self.reqs_pool = []
                return cur_reqs
        return []
    
    def start_requests(self):
        author_ids = self.get_author_from_mongo()
        for author_id in author_ids:
            #作者信息
            info_url = 'http://www.zhihu.com/people/%s/about'%(author_id)
            info_req = Request(info_url,callback=self.parse_author_info,headers={'User-Agent':use_agent},cookies=cookie,meta={'id':author_id})
            self.reqs_pool.append(info_req)
            #作者提问
#             ask_url = 'http://www.zhihu.com/people/%s/asks'%(author_id)
#             ask_req = Request(ask_url,callback=self.parse_author_ask,meta={'id':author_id})
#             self.reqs_pool.append(ask_req)
            #作者回答
#             answer_url = 'http://www.zhihu.com/people/%s/answers'%(author_id)
#             answer_req = Request(answer_url,callback=self.parse_author_answer,meta={'id':author_id})
#             self.reqs_pool.append(answer_req)
            #作者专栏文章
            post_url = 'http://www.zhihu.com/people/%s/posts'%(author_id)
            post_req = Request(post_url,callback=self.parse_author_post,meta={'id':author_id})
            self.reqs_pool.append(post_req)
        
        if len(self.reqs)>5000:
            cur_reqs = self.reqs_pool[:5000]
            self.reqs_pool = self.reqs_pool[5000:]
            self.total = 5000
            return cur_reqs
        cur_reqs = self.reqs_pool
        self.reqs_pool = []
        return self.reqs

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
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        sel = Selector(text=content)
        name = sel.xpath('//a[@class="name"]/text()').extract()[0]    
        tag = sel.xpath('//span[@class="bio"]/text()').extract()[0]    
        try:
            abs = sel.xpath('//span[@class="content"]/text()').extract()[0]
        except:
            abs = ''
        try:
            topic_spe = sel.xpath('//span[@class="business item"]/@title').extract()[0]
            topic_spe_url = sel.xpath('//span[@class="business item"]/a/@href').extract()[0]
        except:
            topic_spe= ''
            topic_spe_url = ''
        img = sel.xpath('//div[@class="zm-profile-header-avatar-container "]/img/@src').extract()[0]
        genderinfo = sel.xpath('//span[@class="item gender"]/i/@class').extract()[0]
        if genderinfo.find('profile-male')!=-1:
            gender = 'male'
        elif genderinfo.find('profile-female')!=-1:
            gender = 'female'
        else:
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
        
        job = sel.xpath('//div[@class="zm-profile-module-desc"]')[1].xpath('span/text()').extract()[0]
        address = sel.xpath('//div[@class="zm-profile-module-desc"]')[2].xpath('span/text()').extract()[0]
        education = sel.xpath('//div[@class="zm-profile-module-desc"]')[3].xpath('span/text()').extract()[0]
        try:
            weibo = sel.xpath('//a[@class="zm-profile-header-user-weibo"]/@href').extract()[0]
        except:
            weibo = ''
        
        hash_id = sel.xpath('//div[@class="zm-profile-header-op-btns clearfix"]/button/@data-id').extract()[0]
        follow_zl_num = sel.xpath('//div[@class="zm-profile-side-section-title"]/a/strong/text()').extract()[0].replace('个专栏'.decode('utf-8'),'').strip()  
        follow_topic_num = sel.xpath('//div[@class="zm-profile-side-section-title"]/a/strong/text()').extract()[1].replace('个话题'.decode('utf-8'),'').strip()
        authorInfo = UpdateAuthorInfo()
        authorInfo['authorid'] = author_id
        authorInfo['name'] = name
        authorInfo['tag'] = tag
        authorInfo['topic_spe'] = topic_spe  
        authorInfo['topic_spe_url'] = topic_spe_url 
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
        
        #作者关注的专栏
        zl_url = 'http://www.zhihu.com/people/%s/columns/followed'%(author_id)
        yield Request(zl_url,callback=self.parse_author_zl,headers={'User-Agent':use_agent},cookies=cookie,meta={'author_id':author_id})
        if int(follow_zl_num)>20:
            #作者关注的专栏数大于20，需要发送post请求
            url = 'http://www.zhihu.com/node/ProfileFollowedColumnsListV2'
            user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
            formdata = {'method':'next','params':'{"offset":20,"limit":%s,"hash_id":"%s"}'%((int(follow_zl_num)-20),hash_id)}
            method = 'POST'
            yield FormRequest(url,method=method,formdata=formdata,headers={'User-Agent':user_agent},meta={'author_id':author_id},callback=self.parse_author_zl2)
        #作者关注的话题
        topic_url = 'http://www.zhihu.com/people/%s/topics'%(author_id)
        yield Request(topic_url,callback=self.parse_author_topic,headers={'User-Agent':use_agent},cookies=cookie,meta={'author_id':author_id})
        if int(follow_topic_num)>20:
            #作者关注的话题数大于20，需要发送post请求
            xsrf = sel.xpath('//input[@name="_xsrf"]/@value').extract()[0]
            method = 'POST'
            num = math.ceil(int(follow_topic_num)-20)
            for i in range(num):
                formdata = {'start':0,'offset':(i+1)*20,'_xsrf':'%s'%(xsrf)}
                yield FormRequest(topic_url,method=method,formdata=formdata,headers={'User-Agent':user_agent},cookies=cookie,meta={'author_id':author_id},callback=self.parse_author_topic2)
        
        reqs = self.get_send_reqs()
        for req in reqs:
            yield req
        
    def parse_author_follow_zl(self,response):
        author_id = response.request.meta['author_id']
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        sel = Selector(text=content)
#         links = sel.xpath('//div[@class="zm-profile-section-main"]/a/@href').extract()
        items = sel.xpath('//div[@class="zm-profile-section-main"]')
        for item in items:
#         for link in links:
            link = item.xpath('a/@href').extract()[0]
            authorPost = AuthorPost()
            authorPost['authorid'] = author_id
            authorPost['zl_url'] = link
            yield authorPost
            
            article_num = item.xpath('div/span[@class="zg-gray"]/text()').extract()[0].replace('篇文章'.decode('utf-8'),'').strip()
            postInfo = PostInfo()
            postInfo['url'] = link
            postInfo['article_num'] = article_num
            yield postInfo
        
        reqs = self.get_send_reqs()
        for req in reqs:
            yield req
    
    def parse_author_follow_zl2(self,response):
        author_id = response.request.meta['author_id']
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        content = json.loads(content)
        datas = content.get('msg')
        for data in datas:
            sel = Selector(text=data)
            zl_url = sel.xpath('//strong/text()').extract()[0]
            article_num = sel.xpath('//span[@class="zg-gray"]/text()').extract()[0].replace('篇文章'.decode('utf-8'),'').strip()
            authorPost = AuthorPost()
            authorPost['authorid'] = author_id
            authorPost['zl_url'] = zl_url
            yield authorPost
            
            postInfo = PostInfo()
            postInfo['url'] = zl_url
            postInfo['article_num'] = article_num
            yield postInfo
        
        reqs = self.get_send_reqs()
        for req in reqs:
            yield req
            
    def parse_author_follow_topic(self,response):
        author_id = response.request.meta['author_id']
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        sel = Selector(text=content)
        topic_url = sel.xpath('//div[@class="zm-profile-section-main"]/a/@href').extract()[1]
        topic_url = urlparse.urljoin(response.url, topic_url)
        authorTopic = AuthorTopic()
        authorTopic['authorid'] = author_id
        authorTopic['topic_url'] = topic_url
        yield authorTopic
        
        reqs = self.get_send_reqs()
        for req in reqs:
            yield req
    def parse_author_follow_topic2(self,response):
        author_id = response.request.meta['author_id']
        url = response.url
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        content = json.loads(content)
        datas = content.get('msg')
        print len(datas)
        data = datas[1]
        sel = Selector(text=data)
        items = sel.xpath('//div[@class="zm-profile-section-main"]')
        for item in items:
            topic_link = item.xpath('a/@href').extract()[1]
            topic_url = urlparse.urljoin(url, topic_link)
            authorTopic = AuthorTopic()
            authorTopic['authorid'] = author_id
            authorTopic['topic_url'] = topic_url
            yield authorTopic
        
        reqs = self.get_send_reqs()
        for req in reqs:
            yield req
        
    def parse_author_ask(self,response):
        author_id = response.request.meta['author_id']
        url = response.url
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        sel = Selector(text=content)
        asks = sel.xpath('//div[@class="zm-profile-section-item zg-clear"]')
        for ask in asks:
            spannum = ask.xpath('span/div[@class="zm-profile-vote-num"]/text()').extract()[0]
            if spannum.endswith('K'):
                spannum = spannum.replace('K','000')
            asklink = ask.xpath('div/h2/a[@class="question_link"]/@href').extract()[0]
            asklink = urlparse.urljoin(url, asklink)
            asktitle = ask.xpath('div/h2/a[@class="question_link"]/text()').extract()[0]
            askotherinfo = ask.xpath('div/div[@class="meta zg-gray"]').extract()[0]
            answernum = self.answer_re.search(askotherinfo).groupdict()['num']
            follownum = self.follow_re.search(askotherinfo).groupdict()['num']
            askinfo = AskInfo()
            askinfo['authorid'] = author_id
            askinfo['url'] = asklink
            askinfo['spannum'] = spannum
            askinfo['title'] = asktitle
            askinfo['answernum'] = answernum
            askinfo['follownum'] = follownum
            yield askinfo
        
        next_pages = sel.xpath('//span/a/@href').extract()
        for next_page in next_pages:
            next_url = self.calc_url(url, next_page)
            if not next_url:
                continue
            if not self.next_ask_page_re.search(next_url):
                continue
            if redis.check_set_value(self.redis_conn, self.redis_ask_page, next_url):
                continue
            redis.add_set_value(self.redis_conn, self.redis_ask_page, next_url)
            yield Request(next_url,callback=self.parse_author_ask,meta={'author_id':author_id})
        
    def parse_author_answer(self,response):
        author_id = response.request.meta['author_id']
        url = response.url
        try:
            content = response.body_as_unicode()
        except:
            content = response.body
        
        sel = Selector(text=content)
        items = sel.xpath('//div[@class="zm-item"]')
        for item in items:
            asklink = item.xpath('h2/a[@class="question_link"]/@href').extract()[0]
            asklink = self.calc_url(url, asklink)
            likenum = item.xpath('div/div/button/span[@class="count"]/text()').extract()[0]
            answorinfo = item.xpath('div/div/textarea[@class="content hidden"]/text()').extract()[0]
            commnum = item.xpath('div/div/div[@class="zm-meta-panel"]/a[@name="addcomment"]/text()').extract()
            if len(commnum)==2:
                commnum = commnum[1].replace('条评论'.decode('utf-8'),'').strip()
            elif len(commnum)==1:
                commnum = commnum[0].replace('条评论'.decode('utf-8'),'').strip()
            elif len(commnum)==0:
                commnum = 0
            answerinfo = AnswerInfo()
            answerinfo['authorid'] = author_id
            answerinfo['askurl'] = asklink
            answerinfo['likenum'] = likenum
            answerinfo['commnum'] = commnum
            answerinfo['answorinfo'] = answorinfo
            yield answerinfo
        
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
            try:
                article_num = item.xpath('div[@class="footer"]/text()').extract()[0].replace('查看全部'.decode('utf-8'),'').replace('篇文章'.decode('utf-8'), '').strip()
            except:
                article_num = ''
            ownerPost = OwnerPost()
            ownerPost['url'] = url
            ownerPost['authorid'] = author_id
            yield ownerPost
            
            postinfo = PostInfo()
            postinfo['url'] = url
            postinfo['article_num'] = article_num
            yield postinfo
        
        reqs = self.get_send_reqs()
        for req in reqs:
            yield req
            
#         links = sel.xpath('//a/@href').extract()
#         for link in links:
#             #http://zhuanlan.zhihu.com/sooth
#             zl_url = self.calc_url(url, link)
#             if zl_url.endswith('/'):
#                 zl_url = zl_url[:len(url)-1]
#             url_tmp = urlparse.urlparse(url)
#             if url_tmp.netloc!='zhuanlan.zhihu.com':
#                 continue
#             if len(url_tmp.path.split('/'))!=2:
#                 continue
#             post = PostInfo()
#             post['url'] = zl_url
#             yield post
        
    def get_spider_pending_cnt(self,total):
        c_stats = self.crawler.stats.get_stats()
#         total2 = c_stats['scheduler/enqueued/memory']
#         if "scheduler/disk_enqueued" in c_stats:
#             total2 += c_stats['scheduler/disk_enqueued']

        exception_cnt = 0
        rsp_cnt = 0
        if "downloader/response_count" in c_stats:
            rsp_cnt = c_stats['downloader/response_count']
        if "downloader/exception_count" in c_stats:
            exception_cnt = c_stats['downloader/exception_count']
        return total - rsp_cnt - exception_cnt
    