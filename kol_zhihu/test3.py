import urllib2

uri="http://www.zhihu.com/people/ma-bo-yong/about"


# "Host": "www.zhihu.com",  
  
# "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
head={"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36",
      "Cookie":'q_c1=02dcb3281ba048ebb8dfc374d1f58402|1428487620000|1428487620000; _ga=GA1.2.1787246182.1428487623; _xsrf=4510fc3de9fe84dca68a7109b5d0fc89; _za=dbdcd5c9-fab8-4122-9c16-d0a29abd6a68; z_c0="QUFDQVdkODJBQUFYQUFBQVlRSlZUVmhDWUZXenlodHFZMnNfcC1PdWlGTjRHOFUwVUdhaWNnPT0=|1429779800|2721a92cf6cf5234db949629d308b39f26f3ef9b"; __utmt=1; __utma=51854390.1787246182.1428487623.1429777737.1429777737.1; __utmb=51854390.39.10.1429777737; __utmc=51854390; __utmz=51854390.1429777737.1.1.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/topic; __utmv=51854390.100-1|2=registration_date=20140909=1^3=entry_date=20140909=1'}
request = urllib2.Request(uri,headers=head)
response = urllib2.urlopen(request)

print response.read()