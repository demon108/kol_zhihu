#encoding:utf-8
import mongo_util2 as db
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

conn = db.connect('192.168.241.25', 'zhihu')
now = time.time()
authors = db.find(conn, 'author',{'tg':{'$lt':now,'$gt':0}})
num = 0
del_num = 0
for author in authors:
    try:
        authorid = author['id']
        pos = authorid.find('?')
        if pos!=-1:
            print authorid
            authorid_tmp = authorid[:pos]
            auth = db.find_one(conn, 'author', {'id':authorid_tmp})
            if not auth:
                db.update(conn, 'author', {'id':authorid}, {'id':authorid_tmp})
                num += 1
            else:
                del_num = db.delete_one(conn, 'author', {'id':authorid})
                del_num += 1
            
    except:
        pass

print 'update num: ',num
print 'del_num: ',del_num