# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import time
from datetime import datetime
from bson.objectid import ObjectId
import json

from items import *
import mongo_util2 as db

class KolZhihuPipeline(object):
    
    article = 'article'
    author = 'author'
#     author2 = 'author2'
    topic = 'topic'
    ask = 'ask'
    answer = 'answer'
    post = 'post'
    post_artcile = 'post_article'
    author_topic = 'author_topic'
    author_zl = 'author_zl'
    owerpost = 'owerpost'
    def __init__(self):
        self.conn = db.connect('192.168.241.23', 'zhihu')
        #create index for article
#         db.create_index(self.conn, self.article, indexs=['tg'])
#         db.create_unique_index(self.conn, self.article, uniques=['url'])
        #askinfo
#         db.create_unique_index(self.conn, self.ask, uniques=['url'])
#         db.create_index(self.conn, self.ask, indexs=['tg'])
#         answer
        db.create_unique_index(self.conn, self.answer, uniques=['url'])
        db.create_index(self.conn, self.answer, indexs=['tg'])
        #create index for author
        db.create_unique_index(self.conn, self.author, uniques=['id'])
        #create index for author2
#         db.create_unique_index(self.conn, self.author2, uniques=['id'])
#         db.create_index(self.conn, self.author2, indexs=['tg'])
        #create index for topic
        db.create_unique_index(self.conn, self.topic, uniques=['id'])
        #post
        db.create_unique_index(self.conn, self.post, uniques=['url'])
        db.create_index(self.conn, self.post, indexs=['tg'])
        #author_topic
        db.create_unique_index(self.conn,self.author_topic,uniques=[[('authorid',1),('topic_url',1)]])
        db.create_index(self.conn, self.author_topic,indexs=['authorid'])
        #author_zl
        db.create_unique_index(self.conn, self.author_zl, uniques=[[('authorid',1),('zl_url',1)]])
        db.create_index(self.conn, self.author_zl, indexs=['authorid'])
        #ownerpost
        db.create_unique_index(self.conn, self.owerpost, uniques=[[('authorid',1),('zl_url',1)]])
        db.create_index(self.conn, self.owerpost,indexs=['authorid'])
        #post_article
        db.create_unique_index(self.conn,self.post_artcile,uniques=['url'])
        db.create_index(self.conn, self.post_artcile,indexs=['tg','authorurl','posturl','pubtime'])
        
        self.start = datetime.now()
        
    def process_item(self, item, spider):
        
        if isinstance(item, TopicItem):
            #话题信息
            #zhihu_find_user_spider.py维护
            id = item['id']
            abs = item['abs']
            url = item['url']
            name = item['name']
            category = item['category']
            o = ObjectId()
            topicitem = {'_id':o,\
                    'id':id,\
                    'name':name,\
                    'url':url,\
                    'abs':abs,\
                    'catrgory':category}
            db.insert(self.conn, self.topic, topicitem)
            
        elif isinstance(item,AuthorItem):
            #作者信息
            #通过zhihu_find_user_spider.py维护
            id = item['id']
            url = item['url']
            topic_id = item['topic_id']
            o = ObjectId()
            data_ref = db.find_one(self.conn, self.author, {'id':id})
            if data_ref:
                topic_id_ref = data_ref['topic_id']
                try:
                    topic_id_dict = json.loads(topic_id_ref)
                    if not isinstance(topic_id_dict, dict):
                        topic_id_dict = {}
                except:
                    topic_id_dict = {}
                if topic_id_dict.has_key(topic_id):
                    topic_id_dict[topic_id] = int(topic_id_dict[topic_id]) + 1
                else:
                    topic_id_dict[topic_id] = 1
                topic_ids = json.dumps(topic_id_dict)
                db.update(self.conn, self.author, {'id':id}, {'topic_id':topic_ids})
            else:
                topic_ids = json.dumps({topic_id:1})
                authoritem = {'_id':o,\
                            'id':id,\
                            'url':url,\
                            'tg':time.time(),\
                            'topic_id':topic_ids}
                db.insert(self.conn, self.author, authoritem)
#                     topic_ids = topic_id_ref.split('`')
#                     if topic_id in topic_ids:
#                         topic_id = topic_id_ref
#                     else:
#                         topic_id = topic_id_ref+'`'+topic_id
        
        elif isinstance(item,UpdateAuthorInfo):
            #更新作者信息
            #通过zhihu_authorinfo_spider.py维护
            authorid = item['authorid']
            name = item['name']
            abs = item['abs']
            tag = item['tag']
            image = item['image']
            industry = item['industry']
            gender = item['gender']
            asknum = item['asknum']
            answernum = item['answernum']
            postnum = item['postnum']
            fansnum = item['fansnum']
            follownum = item['follownum']
            hpspan = item['hpspan']
            likenum = item['likenum']
            thanksnum = item['thanksnum']
            favoritenum = item['favoritenum']
            sharenum = item['sharenum']
            job = item['job']
            address = item['address']
            education = item['education']
            weibo = item['weibo']
            hash_id = item['hash_id']
            follow_zl_num = item['follow_zl_num']
            follow_topic_num = item['follow_topic_num']
            authorinfo = {'name':name,\
                          'abs':abs,\
                          'tag':tag,\
                          'image':image,\
                          'industry':industry,\
                          'gender':gender,\
#                           'tg':time.time(),\
                          'asknum':asknum,\
                          'answernum':answernum,\
                          'postnum':postnum,\
                          'fansnum':fansnum,\
                          'follownum':follownum,\
                          'hpspan':hpspan,\
                          'likenum':likenum,\
                          'thanksnum':thanksnum,\
                          'favoritenum':favoritenum,\
                          'sharenum':sharenum,\
                          'job':job,\
                          'address':address,\
                          'education':education,\
                          'weibo':weibo,\
                          'hash_id':hash_id,\
                          'follow_zl_num':follow_zl_num,\
                          'follow_topic_num':follow_topic_num}
            db.update(self.conn, self.author, {'id':authorid}, authorinfo)

        elif isinstance(item, UpAuthorByAnswerSpider):
            #更新作者信息
            #通过zhihu_authorinfo2_spider.py和zhihu_authorinfo3_spider.py以及zhihu_author_answer_spider.py维护
            authorid = item['authorid']
            name = item['name']  
            abs = item['abs']
            tag = item['tag']
            image = item['image']
            industry = item['industry']
            gender = item['gender']
            weibo = item['weibo']
            hash_id = item['hash_id']
            follow_zl_num = item['follow_zl_num']
            follow_topic_num = item['follow_topic_num']
            fansnum = item['fansnum']
            follownum = item['follownum']
            asknum = item['asknum']
            answernum = item['answernum']
            postnum = item['postnum']
            likenum = item['likenum']
            thanksnum = item['thanksnum']
            authorinfo = {'name':name,\
                          'abs':abs,\
                          'tag':tag,\
                          'image':image,\
                          'industry':industry,\
                          'gender':gender,\
                          'weibo':weibo,\
                          'hash_id':hash_id,\
                          'follow_zl_num':follow_zl_num,\
                          'follow_topic_num':follow_topic_num,\
                          'fansnum':fansnum,\
                          'follownum':follownum,\
                          'asknum':asknum,\
                          'answernum':answernum,\
                          'postnum':postnum,\
                          'likenum':likenum,\
                          'thanksnum':thanksnum}
            db.update(self.conn, self.author, {'id':authorid}, authorinfo)
            
        elif isinstance(item,AskInfo):
            #未启用
            #zhihu_post_spider.py
            authorid = item['authorid']
            url = item['url']
            title = item['title']
            spannum = item['spannum']
            answernum = item['answernum']
            follownum = item['follownum']
            o = ObjectId()
            askinfo = {'_id':o,\
                       'authorid':authorid,\
                       'url':url,\
                       'tg':time.time(),\
                       'title':title,\
                       'spannum':spannum,\
                       'answernum':answernum,\
                       'follownum':follownum}
            db.insert(self.conn, self.ask, askinfo)
        
        elif isinstance(item,AnswerInfo):
            #未启用
            #zhihu_post_spider.py
            authorid = item['authorid']
            askurl = item['askurl']
            likenum = item['likenum']
            commnum = item['commnum']
            pubtime = item['pubtime']
            content = item['content']
            o = ObjectId()
            answerinfo = {'_id':o,\
                          'authorid':authorid,\
                          'url':askurl,\
                          'tg':time.time(),\
                          'likenum':likenum,\
                          'commnum':commnum,\
                          'pubtime':pubtime,\
                          'content':content}
            db.insert(self.conn, self.answer, answerinfo)
        
        elif isinstance(item,PostInfo):
            #专栏信息表
            #通过zhihu_author2_spider.py维护
            url =item['url']
            try:
                article_num = item['article_num']
            except:
                article_num = 0
            db.insert(self.conn, self.post, {'url':url,'tg':time.time(),'article_num':article_num})
        
        elif isinstance(item,AuthorTopic):
            #用户关注的话题
            #通过zhihu_author2_spider.py维护
            topic_url = item['topic_url']
            authorid = item['authorid']
            o = ObjectId()
            authortopic = {
                            '_id':o,\
                            'authorid':authorid,\
                            'topic_url':topic_url}
            db.insert(self.conn, self.author_topic, authortopic)
        
        elif isinstance(item,AuthorPost):
            #用户关注的专栏
            #通过zhihu_author2_spider.py维护
            zl_url = item['zl_url']
            authorid = item['authorid']
            o = ObjectId()
            authorPost = {
                          '_id':o,\
                          'authorid':authorid,\
                          'zl_url':zl_url}
            db.insert(self.conn, self.author_zl, authorPost)
            
        elif isinstance(item,OwnerPost):
            #专栏和作者的对应表
            #通过zhihu_author2_spider.py维护
            zl_url = item['zl_url']
            authorid = item['authorid']
            o = ObjectId()
            ownerPost = {
                          '_id':o,\
                          'authorid':authorid,\
                          'zl_url':zl_url}
            db.insert(self.conn, self.owerpost, ownerPost)
        
        elif isinstance(item,AuthorItem2):
            #该类为通过zhihu_explore_spider.py日常运行寻找用户
            #这种方法找到的用户无法统计出其在什么话题出现，所以topic_id全部为unknown
            id = item['id']
            url = item['url']
            topic_id = item['topic_id']
            o = ObjectId()
            authoritem = {'_id':o,\
                    'id':id,\
                    'url':url,\
                    'tg':time.time(),\
                    'topic_id':topic_id}
            db.insert(self.conn, self.author, authoritem)
        
        elif isinstance(item,PostArticleInfo):
            #专栏的文章信息
            #zhihu_post_spider.py维护
            url = item['url']
            posturl = item['posturl']
            authorurl = item['authorurl']
            title = item['title']
            commnum = item['commnum']
            likenum = item['likenum']
            abs = item['abs']
            pubtime = item['pubtime']
            content = item['content']
            postArticle = {'url':url,\
                           'posturl':posturl,\
                           'authorurl':authorurl,\
                           'tg':time.time(),\
                           'title':title,\
                           'commnum':commnum,\
                           'likenum':likenum,\
                           'abs':abs,\
                           'pubtime':pubtime,\
                           'content':content}
            db.insert(self.conn, self.post_artcile, postArticle)
        
        elif isinstance(item,UpdatePostInfo):
            #更新专栏信息
            #zhihu_post_spider.py维护
            url = item['url']
            followersCount = item['followersCount']
            description = item['description']
            name = item['name']
            article_num = item['article_num']
            updatePost = {'followersCount':followersCount,\
                          'description':description,\
                          'name':name,\
                          'article_num':article_num}
            db.update(self.conn, self.post, {'url':url}, updatePost)
        
    def close_spider(self,spider):
        db.close(self.conn)
        f = open('total_time.my','a')
        total = datetime.now() - self.start
        f.write('%s,%s\n'%(spider,total))
        f.flush()
        f.close()
            
            
