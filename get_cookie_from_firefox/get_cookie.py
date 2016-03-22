# -*- encoding:utf-8  -*-
from selenium import webdriver
# https://pypi.python.org/pypi/selenium
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import json



def logins(names,passwd):
    print names
    print passwd
    browser = webdriver.Firefox() # Get local session of firefox
    browser.get('http://www.zhihu.com/#signin')
    #elem = browser.find_element_by_id("idInput") # Find the query box
    elem = browser.find_element_by_xpath("//div[@class='view view-signin ']/form/div[@class='email input-wrapper']/input")
    elem.send_keys(names)
    #elem = browser.find_element_by_id("password") # Find the query box
    elem = browser.find_element_by_xpath("//div[@class='view view-signin ']/form/div[@class='input-wrapper']/input")
#    elem.send_keys(passwd + Keys.RETURN)
    elem.send_keys(passwd)
#    browser.find_element_by_name('rememberme').click()
    browser.find_element_by_xpath("//div[@class='view view-signin ']/form/div[@class='button-wrapper command']/button").click()
    time.sleep(3)
    cookies = browser.get_cookies()
    cookie = {}
    for tmp in cookies:
        cookie[tmp['name']] = tmp['value']
    f = open('cookie.txt','w')
    f.write(json.dumps(cookie))
    f.close()
    browser.close()
    # Let the page load, will be added to the API

def main():
#    names = raw_input( "neme:")
#    password = raw_input("password:")
    names = 'dingyong881205@126.com'
    password = 'yong881205'
    logins(names,password)

if __name__ == '__main__':
    main()
