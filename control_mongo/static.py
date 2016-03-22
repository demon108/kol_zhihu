#encoding:utf-8
import mongo_util2 as db
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

conn = db.connect('192.168.241.25', 'zhihu')
now = time.time()
authors = db.find(conn, 'author',{'tg':{'$lt':now,'$gt':0}})
num_500 = 0
num_1000 = 0
num_2000 = 0
num_5000 = 0
num_10000 = 0
num_20000 = 0
num_50000 = 0
num2 = 0
for author in authors:
    try:
        fansnum = author['fansnum']
        likenum = author['likenum']
        if int(fansnum)>500:
            num_500 += 1
        if int(fansnum)>1000:
            num_1000 += 1
        if int(fansnum)>2000:
            num_2000 += 1
        if int(likenum)>=5000:
            num_5000 += 1
        if int(likenum)>=10000:
            num_10000 += 1
        if int(likenum)>=20000:
            num_20000 += 1
        if int(likenum)>=50000:
            num_50000 += 1
    except:
        num2 += 1
print 'total: ',authors.count()
print 'num_500: ',num_500
print 'num_1000: ',num_1000
print 'num_2000: ',num_2000
print 'num_5000: ',num_5000
print 'num_10000: ',num_10000
print 'num_20000: ',num_20000
print 'num_50000: ',num_50000
print 'unprocess: ',num2
