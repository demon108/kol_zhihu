#encoding:utf-8
import mongo_util2 as db
import time
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

conn = db.connect('192.168.241.25', 'zhihu')
# start_time = 0
# end_time = time.time() - 20*24*3600
# authorids = db.find(conn, 'author',{'tg':{'$lt':end_time,'$gt':start_time}},{'id':'true'}).count()
# print authorids
# 
# start_time = end_time
# end_time = time.time()
# authorids = db.find(conn, 'author',{'tg':{'$lt':end_time,'$gt':start_time}},{'id':'true'}).count()
# print authorids
# 
# start_time = 0
# end_time = time.time()
# authorids = db.find(conn, 'author',{'tg':{'$lt':end_time,'$gt':start_time}},{'id':'true'}).count()
# print authorids

now = time.time() 
print now-20*24*3600
print now-21*24*3600
start_time = 0
end_time = now - 32*24*3600
authorids = db.find(conn, 'author',{'tg':{'$lt':end_time,'$gt':start_time}},{'id':'true'}).count()
print 'get from mongo1: ',authorids

start_time = now - 32*24*3600
end_time = now - 26*24*3600
authorids = db.find(conn, 'author',{'tg':{'$lt':end_time,'$gt':start_time}},{'id':'true'})
print 'get from mongo2: ',authorids.count()

start_time = now - 26*24*3600
end_time = now - 20*24*3600
authorids = db.find(conn, 'author',{'tg':{'$lt':end_time,'$gt':start_time}},{'id':'true'})
print 'get from mongo3: ',authorids.count()

start_time = now - 20*24*3600
end_time = now - 14*24*3600
authorids = db.find(conn, 'author',{'tg':{'$lt':end_time,'$gt':start_time}},{'id':'true'})
print 'get from mongo4: ',authorids.count()

start_time = now - 14*24*3600
end_time = now - 8*24*3600
authorids = db.find(conn, 'author',{'tg':{'$lt':end_time,'$gt':start_time}},{'id':'true'})
print 'get from mongo5: ',authorids.count()


start_time = now - 8*24*3600
end_time = now
authorids = db.find(conn, 'author',{'tg':{'$lt':end_time,'$gt':start_time}},{'id':'true'})
print 'get from mongo6: ',authorids.count()


start_time = 0
end_time = now
authorids = db.find(conn, 'author',{'tg':{'$lt':end_time,'$gt':start_time}},{'id':'true'})
print 'get from mongo7: ',authorids.count()


authors = db.find(conn, 'author',{'tg':{'$lt':end_time,'$gt':start_time}})
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
print 'num_500: ',num_500
print 'num_1000: ',num_1000
print 'num_2000: ',num_2000
print 'num_5000: ',num_5000
print 'num_10000: ',num_10000
print 'num_20000: ',num_20000
print 'num_50000: ',num_50000
print 'unprocess: ',num2



# f = open('tg.dat','w')
# authorids = db.find(conn, 'author')
# datas = []
# for author in authorids:
#     tg = author['tg']
#     if isinstance(tg, float) or isinstance(tg, int):
#         continue
#     else:
#     if tg<0:
#         if flag%10000==0:
#             tg = time.time() - tag*24*3600
#             tag += 1
#         id = author['id']
#         f.write('%s, tg:%s\n'%(id,tg))
#         f.flush()
#     if tg<0:
#         datas.append(author['id'])
#         
# flag = 0
# tag = 0
# tg = 0
# for id in datas:
#     if flag%10000==0:
#         print '----'
#         print "flag: ",flag
#         print 'tag: ',tag
#         tg = time.time() - tag*24*3600
# #         print 'tg: ',tg
#         tag += 1
#     if flag%11111==0:
#         print 'tg: ',tg
#     flag += 1
#     db.update(conn, 'author', {'id':id}, {'tg':tg})
#     
