import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import *


url = "http://news.qq.com/"
max_link_number = 1000
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
    print(len(unvisited_url_sequence))
    response = requests.get(target).content.decode('gb2312','ignore')
    visited_url_sequence.append(target) #将访问过的url存储在vus队列中
    soup = BeautifulSoup(response,'lxml')
# 如果页面存在form标签，则将该url（target）放在一个存在潜在漏洞的列表中
    if soup.find("form") is not None:
        form_url_sequence.append(target)

# 收集页面中所有url，将没有被访问访问过的url存在队列中
    for a_tag in soup.find_all("a"):
        if a_tag.has_attr('href'):
            url_parsed = a_tag['href']
            print('a')
            if domain_name_check.match(url_parsed) is not None and url_parsed not in visited_url_sequence and url_parsed not in unvisited_url_sequence:
                unvisited_url_sequence.append(url_parsed)
                link_number = link_number + 1
                print('b')

print("find link numbers: %d" %(len(form_url_sequence)))
for each in form_url_sequence:
    print("The %d link:\t\t %s" %(form_url_sequence.index(each),each))





