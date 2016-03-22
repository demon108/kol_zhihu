#encoding:utf-8
import json
#_ga=GA1.2.1787246182.1428487623; _za=dbdcd5c9-fab8-4122-9c16-d0a29abd6a68; q_c1=02dcb3281ba048ebb8dfc374d1f58402|1431321244000|1428487620000; z_c0="QUFDQVdkODJBQUFYQUFBQVlRSlZUVHBYZlZWU0tzWFVGdkMzRkJjTHN4dXZYdUZaWEM4bkF3PT0=|1431685690|321f0890fb2fdbc70d65c8bfb7253f5253c0d358"; _xsrf=e8fa1f894af86dfb1aa8040bbe4fb29a; __utmt=1; __utma=51854390.1619831530.1431921409.1431929978.1431932853.3; __utmb=51854390.2.10.1431932853; __utmc=51854390; __utmz=51854390.1431932853.3.6.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/people/incredible-vczh; __utmv=51854390.100-1|2=registration_date=20140909=1^3=entry_date=20140909=1
#z_c0="QUFDQVdkODJBQUFYQUFBQVlRSlZUVHBYZlZWU0tzWFVGdkMzRkJjTHN4dXZYdUZaWEM4bkF3PT0=|1431685690|321f0890fb2fdbc70d65c8bfb7253f5253c0d358"

def get_cookie(filename='cookie.txt'):
    f = open(filename,'r')
    tmp = f.read().strip()
    f.close()
    try:
        cookie = json.loads(tmp)
    except:
        cookie = dict()
        items = tmp.split(';')
        for item in items:
            kv = item.split('=')
            if len(kv)>2:
                for i in range(len(kv)-2):
                    kv[1] = kv[1] + '=' + kv[i+2]
            cookie[kv[0].strip()] = kv[1]
    return cookie

if __name__ == '__main__':
    cookie = get_cookie('cookie.txt')
    print type(cookie)
    print cookie
    
    