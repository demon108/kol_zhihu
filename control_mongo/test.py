import mongo_util2 as db
import time
import redis_api2 as redis
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def move_url_from_mongo_redis():
    #更新到的时间 1431048036
    conn = db.connect('192.168.241.25', 'zhihu')
    redis_conn = redis.redis_connect()
    try:
        start_time = db.find_one(conn, 'record')['time']
    except:
        start_time = 0
    end_time = time.time()
    authorids = db.find(conn, 'author',{'tg':{'$lt':end_time,'$gt':start_time}})
    print 'get from mongo: ',authorids.count()
    num = 0
    for authorid in authorids:
        try: 
            gender = authorid['gender']
            fansnum = authorid['fansnum']
        except:
            redis.add_url(redis_conn, authorid['id'])
            num += 1
    record = db.find_one(conn, 'record',{'id':'1'})
    print record
    if not record:
        db.insert(conn, 'record', {'time':end_time,'id':'1'})
    else:
        db.update(conn, 'record', {'id':'1'}, {'time':end_time})
        
    print 'add to redis: ',num
    db.close(conn)

move_url_from_mongo_redis()
