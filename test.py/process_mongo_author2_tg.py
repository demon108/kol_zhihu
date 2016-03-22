#encoding:utf-8
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

def connect(host,dbname):
    client = MongoClient(host, 27017)
    conndb = client[dbname]
    return conndb

#handle: handle = connect(host,dbname)
def create_unique_index(handle,tablename,uniques=[]):
    conn_table = handle[tablename]
    for unique in uniques:
        #unique参数说明：
        #1、unique的值为：key，则等价于[(key,1)]
        #2、unique的值为：[(key1,1),(key2,1)]，则会创建key1和key2的联合唯一索引
        # 1 表示升序，-1 表示降序
        conn_table.ensure_index(unique,unique=True)

def create_index(handle,tablename,indexs=[]):
    conn_table = handle[tablename]
    for index in indexs:
        conn_table.ensure_index(index,unique=False)

def insert(handle,tablename,value={}):
    conn_table = handle[tablename]
    try:
        conn_table.insert(value)
    except DuplicateKeyError:
        pass

def update(handle,tablename,query_dict,new_dict):
    conn_table = handle[tablename]
    conn_table.update(query_dict,{'$set':new_dict})

'''
if res.count()==0:
    print can`t find res
'''
def find(handle,tablename,query_dict={},query_field={}):
    conn_table = handle[tablename]
    if query_dict and not query_field:
        res = conn_table.find(query_dict)
    elif query_dict and query_field:
        res = conn_table.find(query_dict,query_field)
    elif not query_dict and query_field:
        res = conn_table.find({},query_field)
    else:
        res = conn_table.find()
    return res

def find_one(handle,tablename,query_dict={}):
    conn_table = handle[tablename]
    return conn_table.find_one(query_dict)
    
def close(handle):
    handle.connection.close()

if __name__=='__main__':
    import time
    handle = connect('localhost','zhihu')
    tablename = 'author2'
    datas = find(handle,tablename)
    for data in datas:
        update(handle, tablename, {'id':data['id']}, {'tg':time.time()})
    close(handle)
    
    