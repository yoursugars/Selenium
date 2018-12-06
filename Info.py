from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from urllib import parse, request
import json
import requests
import time
import sys
from time import sleep
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


class getInfo():
    def __init__(self):
        # 无界面操作    
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome("D:/software/python/module/chromedriver.exe", chrome_options=chrome_options)

        #self.driver = webdriver.Chrome("D:/software/python/module/chromedriver.exe")
        self.driver.get("http://kns.cnki.net/kns/brief/result.aspx?dbprefix=CDMD")
            
    def getOnePage(self, txtName):
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[0])
        getNumJS = "window.getNum = function(){var obj=document.getElementById('iframeResult').contentWindow;var ifmObj = obj.document.getElementsByClassName('fz14'); return ifmObj.length;}"
        self.driver.execute_script(getNumJS)
        js = "window.a = function(x){var obj=document.getElementById('iframeResult').contentWindow;var ifmObj = obj.document.getElementsByClassName('fz14'); ifmObj.item(x).click();}"        
        print("before getNum()")
        cols = self.driver.execute_script("return getNum()")
        sleep(1)
        print(cols)
        self.driver.execute_script(js)
        for i in range(0, cols):
            print("第"+str(i)+"条检索")
            js2 = 'a('+str(i)+')'     
            self.driver.execute_script(js2)
            sleep(1)
            handles = self.driver.window_handles            
            self.driver.switch_to.window(handles[1])
            try:
                father = self.driver.find_element_by_id('catalog_KEYWORD')
            except:
                pass
            else:
                if father.text[:3] == '关键词':
                    father = self.driver.find_element_by_xpath('//*[@id="mainArea"]/div[2]/div[2]/div[1]/p[2]')
                    keys = father.find_elements_by_tag_name('a')
                    for i in range(0, len(keys)):
                        #print(keys[i].text[:-1])
                        with open(txtName+'.txt', 'a') as f:
                            f.write(keys[i].text[:-1]+'\n')
                else:
                    pass
            self.driver.close()
            self.driver.switch_to.window(handles[0])
        


    def startCheck(self, column, num):
        def cal(num):
            num = int(num)
            if(num < 10):
                return '00'+str(num)
            elif(num < 100):
                return '0'+str(num)
            else:
                return str(num)
        print(column+'first')
        first = self.driver.find_element_by_id(column+'first')
        first.click()
        print(column+cal(num)+'first')
        sleep(1)
        second = self.driver.find_element_by_id(column+cal(num)+'first')
        second.click()
        sleep(1)
        table = self.driver.find_element_by_id(column+cal(num)+'child')
        table_rows = table.find_elements_by_tag_name("dd")
        fourth = table.find_elements_by_tag_name("dl")
        k = 0
        print('table_rows:'+str(len(table_rows)))
        #第几个
        for i in range(0, len(table_rows)):
            span = table_rows[i].find_elements_by_tag_name('span')
            print('span_rows:'+str(len(span)))
            table_cols = table_rows[i].find_elements_by_tag_name('a')
            txtName = table_cols[0].text
            try:
                img = span[0].find_elements_by_tag_name('img')
                if len(img) != 0:
                    print("有多层目录1")
                    if not os.path.exists(table_cols[0].text):
                        os.makedirs(table_cols[0].text)
                    idd = fourth[k].get_attribute('id')
                    idd = idd[:6]+"first";
                    print(idd)
                    span[0].find_element_by_id(idd).click()
                    sleep(1)
                    table_cols = fourth[k].find_elements_by_tag_name('a')
                    print(len(table_cols))
                    k = k+1
                    Name = txtName
                    for j in range(0, len(table_cols)):
                        txtName = Name+'/'+table_cols[j].text
                        #with open(txtName+'.txt', 'a') as f:
                        print(txtName)
            except NoSuchElementException as e:
                print("有多层目录1")
                if not os.path.exists(table_cols[0].text):
                    os.makedirs(table_cols[0].text)
                idd = fourth[k].get_attribute('id')
                idd = idd[:6]+"first";
                span[0].find_element_by_id(idd).click()                    
                table_cols = fourth[k].find_elements_by_tag_name('a')
                print(len(table_cols))
                k = k+1
                Name = txtName
                for j in range(0, len(table_cols)):
                    txtName = Name+'/'+table_cols[j].text
                    #with open(txtName+'.txt', 'a') as f:
                    print(txtName)     
            else:
                print("没有多层目录")
            print(txtName)
            table_cols[0].click()
            iframe = self.driver.find_element_by_xpath("//*[@id='iframeResult']")
            self.driver.switch_to_frame(iframe)
            sleep(2)
            x = self.driver.find_element_by_xpath("//*[@id='id_grid_display_num']/a[3]")
            x.click()
            self.driver.switch_to_default_content()
            sleep(2)
            getNumJS = "window.getNum = function(){var obj=document.getElementById('iframeResult').contentWindow;var ifmObj = obj.document.getElementsByClassName('fz14'); return ifmObj.length;}"
            self.driver.execute_script(getNumJS)
            cols = self.driver.execute_script("return getNum()")
            print("有多少条检索: "+str(cols))
            if cols >= 50:#如果所有检索的文章小于20
                js = "window.c = function(){var obj=document.getElementById('iframeResult').contentWindow; return obj.document.getElementsByClassName('countPageMark').item(0).textContent;}"
                self.driver.execute_script(js)
                pages = self.driver.execute_script("return c()")
                pages = int(pages[2:])
                print("该条检索有多少页："+str(pages))
                #第几页
                for i in range(1, pages-1):
                    sleep(2)
                    self.getOnePage(txtName)
                    print("curpage="+str(i))
                    iframe = self.driver.find_element_by_xpath("//*[@id='iframeResult']")
                    self.driver.switch_to_frame(iframe)
                    self.driver.find_element_by_link_text("下一页").click()
                    handles = self.driver.window_handles
                    self.driver.switch_to.window(handles[0])
            else:
                self.getOnePage(txtName)
                pass


    def getColum(self):
        self.startCheck('A', '001')

    def defaultPage(self, column, num, havechild, item, items, page, end, txtName):
        #child表示第几个栏目
        def cal(num):
            num = int(num)
            if(num < 10):
                return '00'+str(num)
            elif(num < 100):
                return '0'+str(num)
            else:
                return str(num)
        print(column+'first')
        first = self.driver.find_element_by_id(column+'first')
        first.click()
        print(column+cal(num)+'first')
        sleep(3)
        second = self.driver.find_element_by_id(column+cal(num)+'first')
        second.click()
        sleep(1)
        table = self.driver.find_element_by_id(column+cal(num)+'child')
        table_rows = table.find_elements_by_tag_name("dd")
        table_cols = table_rows[int(item)].find_elements_by_tag_name('a')
        fourth = table.find_elements_by_tag_name("dl")#1
        print(len(fourth))
        if int(havechild) == 1:            
            #span = table_rows[int(item)].find_elements_by_tag_name('span')#2
            idd = column+cal(num)+"_"+str(item)+"first"
            print(idd)
            table.find_element_by_id(idd).click()
            sleep(2)
            table_cols = fourth[0].find_elements_by_tag_name('a')
            table_cols[int(items)-1].click()
            print(len(table_cols))
        else:
            table_cols[int(item)-1].click()   
        iframe = self.driver.find_element_by_xpath("//*[@id='iframeResult']")
        self.driver.switch_to_frame(iframe)
        sleep(2)
        x = self.driver.find_element_by_xpath("//*[@id='id_grid_display_num']/a[3]")
        x.click()
        
        for i in range(0, int(page)):
            if i == 0:
                self.driver.find_element_by_link_text("下一页").click()
                handles = self.driver.window_handles
                self.driver.switch_to.window(handles[0])
            else:   
                print("curpage="+str(i+1))
                sleep(3)
                iframe = self.driver.find_element_by_xpath("//*[@id='iframeResult']")
                self.driver.switch_to_frame(iframe)
                self.driver.find_element_by_link_text("下一页").click()
                handles = self.driver.window_handles
                self.driver.switch_to.window(handles[0])
            
        for i in range(int(page), int(end)):
            self.getOnePage(txtName)
            print("curpage="+str(i+1))
            sleep(3)
            iframe = self.driver.find_element_by_xpath("//*[@id='iframeResult']")
            self.driver.switch_to_frame(iframe)
            self.driver.find_element_by_link_text("下一页").click()
            handles = self.driver.window_handles
            self.driver.switch_to.window(handles[0])
        

        
info = getInfo()
info.defaultPage('A', '001', 0, 4, 0, 0, 7, '自然科学研究及自然科学史')
#info.startCheck('A', '002')
