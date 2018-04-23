import re
import requests
import time
import random
import argparse
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import *
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

parse = argparse.ArgumentParser(description='A Damn Small Vul Scanner')
parse.add_argument('-u',action='store',dest='url',required=True,help='The URL you want to scan(http[s]://netloc/...)')
parse.add_argument('--username',action='store',dest='USE_PWD',nargs='+',help='input your username password')
parse.add_argument('--maxlink',action='store',dest='MaxLinkNumber',type=int,help='The max number of links allowed')
args = parse.parse_args()
url = args.url


mys = requests.Session()

if args.MaxLinkNumber:
    max_link_number = args.MaxLinkNumber
else:
    max_link_number = 10000
# 如果有账户密码登录的窗口，利用cookie进行登陆
if args.USE_PWD:
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('window-size=1920x3000')
    chrome_options.add_argument('blink-settings=imagesEnabled=false')

    br = webdriver.Chrome(chrome_options=chrome_options)
    br.get(url)
    user = br.find_element_by_name('username')
    passwd = br.find_element_by_name('password')
    user.send_keys(args.USE_PWD[0])
    passwd.send_keys(args.USE_PWD[1]+Keys.RETURN)
    cookies = br.get_cookies()

    myCookies = {}
    # 通过webdriver对其进行验证，然后
    for cookie in cookies:
        myCookies[cookie['name']] = cookie['value']

    mys.cookies = requests.utils.cookiejar_from_dict(myCookies)
    br.quit()

link_number = 1
form_url_sequence = []
visited_url_sequence = []
unvisited_url_sequence = [url]
url_parsed = urlparse(url)
domain_name = url_parsed.netloc
# params = parse_qsl(url_parsed.query)
domain_name_check = re.compile('http[s]?://.*?'+domain_name+".*")



while (len(unvisited_url_sequence) != 0 and link_number < max_link_number):
    target = unvisited_url_sequence.pop(0)
    path = re.sub('\w+\.\w+','',target)
    print("Now The unvisited_sequence is:")
    for each in unvisited_url_sequence:
        print(each)
    print("Now the visited_sequence is:")
    for each in visited_url_sequence:
        print(each)
    try:
        response = mys.get(target,timeout=0.1).content.decode('gb2312','ignore')
        time.sleep(random.random()/10)
        print("request finished")
        visited_url_sequence.append(target) #将访问过的url存储在vus队列中
        soup = BeautifulSoup(response,'lxml')
    except:
        continue
# 如果页面存在form标签，则将该url（target）放在一个存在潜在漏洞的列表中
    if soup.find("form") is not None:
        form_url_sequence.append(target)

# 收集页面中所有url，将没有被访问访问过的url存在队列中
    for a_tag in soup.find_all("a"):
        if a_tag.has_attr('href'):
            url_parsed = a_tag['href']
            # 对url进行解析：
            # if url_parsed is '.':
            #     url_parsed = target
            if url_parsed[:4] != 'http':
                url_parsed = urljoin(path,url_parsed)
            while( '../' in url_parsed):
                re.sub('/\w+/\.\.','',url_parsed,1)

            if url_parsed not in visited_url_sequence and url_parsed not in unvisited_url_sequence: #没有被访问过的url如果已经出现在需要访问的列表中，也不予讨论
                link_number = link_number + 1
                print('Link Number %d' %(link_number))
                if domain_name_check.match(url_parsed) is not None:
                    unvisited_url_sequence.append(url_parsed)
            else:
                continue

print("find link numbers: %d" %(len(form_url_sequence)))
with open('testdata.txt','w') as f:
    for each in form_url_sequence:
        print("The %3d link:\t\t\t%s" %(form_url_sequence.index(each),each))
        f.write(each + '\n')


