#encoding:utf-8
import redis


class RedisUtil(object):
    
    db = redis.StrictRedis('127.0.0.1',port=6379,db='0')
    #'kjson.com'
    def __init__(self,article_key='',author_key='',topic_key=''):
        self.article_key = article_key
        self.author_key = author_key
        self.topic_key = topic_key
        
        self.db.expire(self.article_key, 30*60*60*24)
        self.db.expire(self.topic_key, 30*60*60*24)
        self.db.expire(self.author_key, 30*60*60*24)
    
    def delete_keys(self):
        self.db.delete(self.article_key)
        self.db.delete(self.author_key)
   
    def add_article(self,url):
        self.db.sadd(self.article_key,url)     
       
    def check_article(self,url):
        return self.db.sismember(self.article_key,url)
     
    def add_author(self,url):
        self.db.sadd(self.author_key,url)
      
    def check_author(self,url):
        return self.db.sismember(self.author_key, url)
    
    def add_topic(self,url):
        self.db.sadd(self.topic_key,url)
    
    def check_topic(self,url):
        return self.db.sismember(self.topic_key, url)

if __name__ == '__main__':
    db = RedisUtil()
    db.delete_keys()
