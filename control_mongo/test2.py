import mongo_util2 as db

conn = db.connect('192.168.241.25', 'zhihu')

authors = db.find(conn, 'author',{},{'id':'true','fansnum':'true','follownum':'true','hash_id':'true'})
num = 0
for author in authors:
    try:
        fansnum = author['fansnum']
	if int(fansnum)>=1000:
	    data = author['id']+'`$`'+author['hash_id']+'`$`'+author['follownum']
	    num += 1
    except:
	pass
print num
