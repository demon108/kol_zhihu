from pymongo import MongoClient
def mongoapi(dbname='zhihu',tablename='author'):
    client = MongoClient('192.168.241.25', 27017)
    db = client[dbname]
    conn = db[tablename]
    return conn


conn = mongoapi()
# print conn.find({},{'url':'true'})

import json
id = 'wu-chang-qing'
data_ref = conn.find_one({'id':id})
print data_ref
topic_id = '19816145'
if data_ref:
    topic_id_ref = data_ref['topic_id']
    if topic_id_ref:
        try:
            topic_ids = json.loads(topic_id_ref)
        except:
            topic_ids = {}
        if topic_ids.has_key(topic_id):
            topic_ids[topic_id] += 1
        else:
            topic_ids[topic_id] = 1
        topic_ids = json.dumps(topic_ids)
conn.update({'id':id},{'$set':{'topic_id':topic_ids}})