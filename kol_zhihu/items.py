# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class TopicItem(Item):
    id = Field()
    abs = Field()
    url = Field()
    name = Field()
    category = Field()

class AuthorItem(Item):
    id = Field()
    url = Field()
    topic_id = Field()

class AuthorItem2(Item):
    id = Field()
    url = Field()
    topic_id = Field()

class UpdateAuthorInfo(Item):
    authorid = Field()
    name = Field()   
    abs = Field()
    tag = Field()
    image = Field()
    industry = Field()
    gender = Field()
    asknum = Field()
    answernum = Field()
    postnum = Field()
    fansnum = Field()
    follownum = Field()
    hpspan = Field()
    likenum = Field()
    thanksnum = Field()
    favoritenum = Field()
    sharenum = Field()
    job = Field()
    address = Field()
    education = Field()
    weibo = Field()
    hash_id = Field()
    follow_zl_num = Field()
    follow_topic_num = Field()

class UpAuthorByAnswerSpider(Item):
    authorid = Field()
    name = Field()   
    abs = Field()
    tag = Field()
    image = Field()
    industry = Field()
    gender = Field()
    weibo = Field()
    hash_id = Field()
    follow_zl_num = Field()
    follow_topic_num = Field()
    fansnum = Field()
    follownum = Field()
    asknum = Field()
    answernum = Field()
    postnum = Field()
    likenum = Field()
    thanksnum = Field()
    hpspan = Field()
    
class AskInfo(Item):
    authorid = Field()
    url = Field()
    title = Field()
    spannum = Field()
    answernum = Field()
    follownum = Field()

class AnswerInfo(Item):
    authorid = Field()
    askurl = Field()  #对应AskInfo表的url+'/answer/num'
    likenum = Field()
    commnum = Field()
    content = Field() #回答内容
    pubtime = Field()

class PostInfo(Item):
    url = Field()
    article_num = Field()

class UpdatePostInfo(Item):
    url = Field()             #根据url更新专栏信息
    followersCount = Field()  #专栏的关注者数量
    description = Field()     #专栏简介
    name = Field()            #专栏名称
    article_num = Field()     #专栏文章数量


class PostArticleInfo(Item):
    url = Field()
    posturl = Field()
    authorurl = Field()
    title = Field()
    commnum = Field()
    likenum = Field()
    abs = Field()
    pubtime = Field()
    content = Field()


class AuthorPost(Item):
    authorid = Field()
    zl_url = Field()

class AuthorTopic(Item):
    authorid = Field()
    topic_url = Field()

class OwnerPost(Item):
    authorid = Field()
    zl_url = Field()
    
