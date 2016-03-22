import mongo_util2 as db
import time
from bson.objectid import ObjectId

def mv_data():
    conn = db.connect('192.168.241.25', 'zhihu')
    db.create_unique_index(conn, 'author', uniques=['id'])
    db.create_index(conn, 'author', indexs=['tg'])
    
    datas = db.find(conn, 'author_find')
    flag = 0
    tag = 0
    for data in datas:
        url = data['url']
        id = data['id']
        topic_id = data['topic_id']
        if flag%10000==0:
            tg = time.time() - tag*24*3600
            tag += 1
#         o = ObjectId()
        value = {'url':url,'id':id,'topic_id':topic_id,'tg':tg}
        db.insert(conn, 'author', value)
    
    datas = db.find(conn, 'author_tmp')
    for data in datas:
#         url = data['url']
#         id = data['id']
#         topic_id = data['topic_id']
#         tg = data['tg']
#         value = {'url':url,'id':id,'topic_id':topic_id,'tg':tg}
        db.insert(conn, 'author', data)

if __name__ == '__main__':
    mv_data()
        
        
        