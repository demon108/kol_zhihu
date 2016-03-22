# -*- coding: utf-8 -*-

# Scrapy settings for kol_txdj project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'kol_zhihu'

SPIDER_MODULES = ['kol_zhihu.spiders']
NEWSPIDER_MODULE = 'kol_zhihu.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'kol_txdj (+http://www.yourdomain.com)'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'scrapy_sinazhuanlan (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19'

ITEM_PIPELINES = {
    'kol_zhihu.pipelines.KolZhihuPipeline':0
}

RANDOMIZE_DOWNLOAD_DELAY=True
#(0.5-1.5)*DOWNLOAD_DELAY, second
DOWNLOAD_DELAY = 3

DOWNLOAD_TIMEOUT = 60

RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [400,408,502,504]


CONCURRENT_REQUESTS = 100
CONCURRENT_ITEMS = 200
#CONCURRENT_REQUESTS_PER_DOMAIN = 2
CONCURRENT_REQUESTS_PER_IP = 2

LOG_LEVEL='INFO'
#LOG_LEVEL='DEBUG'
LOG_FILE='scrapy.log'
LOG_ENCODING='utf-8'

REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 20

# COOKIES_ENABLES = False

