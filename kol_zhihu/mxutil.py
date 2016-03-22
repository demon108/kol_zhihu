import redis

key = 'zhihu'
score = 0

def get_db():
    db = redis.StrictRedis('127.0.0.1',port=6379,db='0')
    return db

def add_url(db,url):
    db.zadd(key,score,url)

def delete_url(db,url):
    db.zrem(key,url)

def get_urls(db,num):
    urls = db.zrevrange(key,0,num)
    for url in urls:
        delete_url(db, url)
    return urls

if __name__ == '__main__':
    db = get_db()
    add_url(db,'http://www.baidu.com')
    urls = get_urls(db, 100)
    print urls
