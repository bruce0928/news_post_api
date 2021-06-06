import re
import sys
from selenium import webdriver
from bs4 import BeautifulSoup as Soup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from flask import Flask,request,jsonify

app = Flask(__name__)
global q
global n
global w
global add_flag
global news_list
global driver

def get_news():
    global n
    global driver
    count = 0
    current_n = 0
    while(current_n<n):
        global add_flag
        add_flag = 0
        xpath = '//*[@id="stream-container-scroll-template"]/li['+str(count+1)+']/div/div/div/div[2]/h3/a'
        load_page(xpath)
        if(add_flag==1):
            current_n = current_n+1
        count = count+1

def load_page(xpath):
    try:
        global driver
        link = driver.find_element_by_xpath(xpath)
        ActionChains(driver).key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
        #利用ActionChains在新分頁開啟，不然每次回去原來頁面都要重新scroll一次
        driver.switch_to.window(driver.window_handles[-1])
        #跳到新開的分頁
        news_data = get_content()
        global news_list
        news_list.append(news_data)
        global add_flag
        add_flag = 1
        #抓取內容並儲存到news_list裡
        driver.close()
        #關閉新分頁
        driver.switch_to.window(driver.window_handles[-1])
        #跳回原頁面
    except:
        pass
        #碰到廣告頁面會跳錯誤，剛好可以跳過

def get_content():
    global w
    global driver
    html = driver.page_source
    soup = Soup(html,'lxml')
    for article in soup.select('.caas-container'):
        title = article.select('.caas-title-wrapper')[0].text
        text_num = 0
        current_paragrah = 0
        content=""
        while(text_num<w):
            text = soup.select('div div div div div div div p')[current_paragrah].text
            if((text_num+len(text))<=w):
                content = content+text
                text_num = text_num+len(text)
            else:
                need_text_num = w-text_num
                text = soup.select('div div div div div div div p')[0].text[:need_text_num]
                content = content+text
                text_num = text_num+len(text)
        news_data = {'title': title, 'content': content}
    return news_data

@app.route("/", methods=['GET'])
def home():
    return "This is news_api. Please provide the value of q,n,w."

@app.route("/news_api", methods=['GET'])
def api_news():
    global q,n,w,news_list
    news_list = []
    q = request.args.get('q', None)
    q = q.replace(',', ' ')
    n= request.args.get('n', None)
    w = request.args.get('w', None)

    global driver 
    driver = webdriver.Chrome(executable_path=r'C:\chromedriver.exe')
    driver.get("https://tw.news.yahoo.com/entertainment")
    driver.find_element_by_id("ybar-sbq").send_keys(q)
    driver.find_element_by_id("ybar-sbq").send_keys(Keys.ENTER)
    time.sleep(10)
    n_scroll=100
    for i in range(n_scroll):
        driver.find_element_by_xpath('//*[@id="ybar-sbq"]').send_keys(Keys.PAGE_DOWN)
    get_news()
    return jsonify(news_list)

if __name__=="__main__":
    app.run()
